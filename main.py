import requests
from fastapi import FastAPI

app = FastAPI()

CHARTINK_URL = "https://chartink.com/screener/process"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://chartink.com/screener"
}

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
def get_stocks():
    payload = {
        "scan_clause": FORMULA
    }

    try:
        r = requests.post(CHARTINK_URL, headers=HEADERS,
                          data=payload, timeout=10)
        data = r.json()
        return data.get("data", [])[:10]
    except Exception as e:
        return []
