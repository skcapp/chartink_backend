from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from license_manager import init_db, check_status, activate
from chartink_fetcher import fetch_stocks

app = FastAPI()

init_db()  # VERY IMPORTANT

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "RUNNING"}


@app.get("/status/{device_id}")
def status(device_id: str):
    return check_status(device_id)


@app.post("/activate")
def activate_device(data: dict):
    device_id = data.get("device_id")
    code = data.get("code")

    if not device_id or not code:
        raise HTTPException(400, "Missing data")

    if not activate(device_id, code):
        raise HTTPException(400, "Invalid or already used code")

    return {"status": "ACTIVE"}


@app.get("/stocks")
def stocks(device_id: str):
    state = check_status(device_id)
    if state["status"] == "EXPIRED":
        raise HTTPException(403, "Trial expired")
    return fetch_stocks()
