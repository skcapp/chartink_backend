from datetime import datetime, timedelta

# Hardcoded secure activation codes (single-use)
ACTIVATION_CODES = {
    "CHARTINK-001": False,
    "CHARTINK-002": False,
    "CHARTINK-003": False,
}

USERS = {}
TRIAL_DAYS = 30


def check_status(device_id: str):
    user = USERS.get(device_id)
    if not user:
        USERS[device_id] = {"start": datetime.utcnow(), "active": False}
        return {"status": "TRIAL", "days_left": TRIAL_DAYS}

    if user["active"]:
        return {"status": "ACTIVE"}

    days_left = TRIAL_DAYS - (datetime.utcnow() - user["start"]).days
    if days_left <= 0:
        return {"status": "EXPIRED"}

    return {"status": "TRIAL", "days_left": days_left}


def activate_device(device_id: str, code: str):
    # Check if code exists and unused
    if code not in ACTIVATION_CODES:
        return False
    if ACTIVATION_CODES[code]:
        return False  # already used

    USERS[device_id]["active"] = True
    ACTIVATION_CODES[code] = True
    return True
