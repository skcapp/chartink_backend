from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from license_manager import check_status, activate_device
from chartink_fetcher import fetch_stocks

app = FastAPI()

# Allow Flutter apps from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status/{device_id}")
def status(device_id: str):
    return check_status(device_id)


@app.post("/activate")
def activate(data: dict):
    device_id = data.get("device_id")
    code = data.get("code")
    if not device_id or not code:
        raise HTTPException(400, "Missing device_id or code")
    if not activate_device(device_id, code):
        raise HTTPException(400, "Invalid or already used code")
    return {"status": "ACTIVE"}


@app.get("/stocks")
def stocks(device_id: str = None):
    if device_id:
        status_info = check_status(device_id)
        if status_info["status"] == "EXPIRED":
            raise HTTPException(403, "Trial expired")
    return fetch_stocks()
