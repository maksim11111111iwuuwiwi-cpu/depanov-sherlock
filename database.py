
import sqlite3
from datetime import date

DB_NAME = "sherlock.db"


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                requests INTEGER DEFAULT 0,
                daily_requests INTEGER DEFAULT 0,
                request_date TEXT,
                unlimited INTEGER DEFAULT 0
            )
        """)
        db.commit()


def add_user(user_id, username=None):
    with connect() as db:
        db.execute("""
            INSERT OR IGNORE INTO users
            (user_id, username, request_date)
            VALUES (?, ?, ?)
        """, (user_id, username, str(date.today())))
        db.commit()


def get_user(user_id):
    with connect() as db:
        return db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()


def set_unlimited(user_id, status=True):
    with connect() as db:
        db.execute("""
            UPDATE users SET unlimited = ?
            WHERE user_id = ?
        """, (int(status), user_id))
        db.commit()


def set_limit(user_id, amount):
    with connect() as db:
        db.execute("""
            UPDATE users SET daily_requests = ?
            WHERE user_id = ?
        """, (amount, user_id))
        db.commit()


def use_request(user_id, daily_limit=10):
    with connect() as db:
        user = db.execute(
            "SELECT unlimited, daily_requests, request_date "
            "FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            return False

        unlimited, used, request_date = user

        if unlimited:
            db.execute(
                "UPDATE users SET requests = requests + 1 "
                "WHERE user_id = ?",
                (user_id,)
            )
            db.commit()
            return True

        today = str(date.today())

        if request_date != today:
            used = 0

        if used >= daily_limit:
            return False

        db.execute("""
            UPDATE users
            SET requests = requests + 1,
                daily_requests = ?,
                request_date = ?
            WHERE user_id = ?
        """, (used + 1, today, user_id))

        db.commit()
        return True


def get_stats():
    with connect() as db:
        users = db.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        requests = db.execute(
            "SELECT SUM(requests) FROM users"
        ).fetchone()[0] or 0

        return users, requests
      
