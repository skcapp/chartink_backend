from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests

app = FastAPI()

# -----------------------------
# Activation system
# -----------------------------
TRIAL_DAYS = 30
activation_codes = {
    "CHARTINK-001": False,
    "CHARTINK-002": False,
    "CHARTINK-003": False,
}
devices = {}  # device_id -> expiry_date


class ActivateRequest(BaseModel):
    device_id: str
    code: str

# -----------------------------
# Root & Health
# -----------------------------


@app.get("/")
def root():
    return {"ok": True, "service": "Chartink Backend"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/status/{device_id}")
def status(device_id: str):
    if device_id not in devices:
        return {"status": "TRIAL", "days_left": TRIAL_DAYS}
    expiry = devices[device_id]
    if datetime.utcnow() > expiry:
        return {"status": "EXPIRED"}
    days_left = (expiry - datetime.utcnow()).days
    return {"status": "ACTIVE", "days_left": days_left}


@app.post("/activate")
def activate(req: ActivateRequest):
    code = req.code.strip()
    device_id = req.device_id.strip()

    if code not in activation_codes:
        raise HTTPException(status_code=400, detail="Invalid code")

    if activation_codes[code]:
        raise HTTPException(status_code=400, detail="Code already used")

    expiry = datetime.utcnow() + timedelta(days=TRIAL_DAYS)
    devices[device_id] = expiry
    activation_codes[code] = True

    return {"status": "ACTIVE", "expiry": expiry.isoformat()}


# -----------------------------
# Chartink Scraper
# -----------------------------
# Replace this formula with any Chartink formula you want
FORMULA = """
[0] 5 minute Close Greater than [-1] 5 minute Max (20, [0] 5 minute Close)
AND
[0] 5 minute Volume Greater than [0] 5 minute Sma(volume,20)
AND
[-1] 5 minute Close Greater than [-2] 5 minute Max (20, [0] 5 minute Close)
AND
[-1] 5 minute Volume Greater than [-1] 5 minute Sma(volume,20)
AND
Daily Volume Greater than 100000
"""


@app.get("/stocks")
def stocks():
    try:
        session = requests.Session()

        # Step 1: Open Chartink homepage to get session cookies
        session.get(
            "https://chartink.com/screener",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        # Step 2: Submit screener formula
        response = session.post(
            "https://chartink.com/screener/process",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://chartink.com/screener"
            },
            data={"scan_clause": FORMULA},
            timeout=10
        )

        data = response.json()
        # Return top 10 stocks
        return data.get("data", [])[:10]

    except Exception as e:
        print("Chartink scraping error:", e)
        # Return empty list on error to avoid Flutter crash
        return []
