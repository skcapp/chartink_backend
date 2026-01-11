import sqlite3
from datetime import datetime

DB = "license.db"
TRIAL_DAYS = 30


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        device_id TEXT PRIMARY KEY,
        start_date TEXT,
        activated INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS codes (
        code TEXT PRIMARY KEY,
        used INTEGER
    )
    """)

    # insert activation codes if not exist
    for code in ["CHARTINK-001", "CHARTINK-002", "CHARTINK-003"]:
        c.execute(
            "INSERT OR IGNORE INTO codes VALUES (?, ?)",
            (code, 0)
        )

    conn.commit()
    conn.close()


def check_status(device_id: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT start_date, activated FROM users WHERE device_id=?", (device_id,))
    row = c.fetchone()

    if not row:
        now = datetime.utcnow().isoformat()
        c.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (device_id, now, 0)
        )
        conn.commit()
        conn.close()
        return {"status": "TRIAL", "days_left": TRIAL_DAYS}

    start_date, activated = row
    if activated:
        conn.close()
        return {"status": "ACTIVE"}

    days_used = (datetime.utcnow() - datetime.fromisoformat(start_date)).days
    days_left = TRIAL_DAYS - days_used

    conn.close()
    if days_left <= 0:
        return {"status": "EXPIRED"}

    return {"status": "TRIAL", "days_left": days_left}


def activate(device_id: str, code: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT used FROM codes WHERE code=?", (code,))
    row = c.fetchone()

    if not row or row[0] == 1:
        conn.close()
        return False

    c.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
        (device_id, datetime.utcnow().isoformat(), 1)
    )
    c.execute(
        "UPDATE users SET activated=1 WHERE device_id=?",
        (device_id,)
    )
    c.execute(
        "UPDATE codes SET used=1 WHERE code=?",
        (code,)
    )

    conn.commit()
    conn.close()
    return True
