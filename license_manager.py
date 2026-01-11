from datetime import datetime, timedelta

TRIAL_DAYS = 30

# In-memory DB (Railway restarts safe for demo; DB can be added later)
USERS = {}

ACTIVATION_CODES = {
    "CHARTINK-001": False,
    "CHARTINK-002": False,
    "CHARTINK-003": False,
}


def check_status(device_id: str):
    if device_id not in USERS:
        USERS[device_id] = {
            "start_date": datetime.utcnow(),
            "activated": False
        }
        return {"status": "TRIAL", "days_left": TRIAL_DAYS}

    user = USERS[device_id]

    if user["activated"]:
        return {"status": "ACTIVE"}

    days_used = (datetime.utcnow() - user["start_date"]).days
    days_left = TRIAL_DAYS - days_used

    if days_left <= 0:
        return {"status": "EXPIRED"}

    return {"status": "TRIAL", "days_left": days_left}


def activate(device_id: str, code: str):
    if code not in ACTIVATION_CODES:
        return False

    if ACTIVATION_CODES[code]:
        return False  # already used

    USERS.setdefault(device_id, {
        "start_date": datetime.utcnow(),
        "activated": False
    })

    USERS[device_id]["activated"] = True
    ACTIVATION_CODES[code] = True
    return True
