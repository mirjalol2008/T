import sqlite3
from datetime import datetime

DB_NAME = "subscriptions.db"

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            expire_date TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

def add_subscription(user_id: int, months: int):
    conn, cursor = connect_db()
    cursor.execute("SELECT expire_date FROM subscriptions WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    now = datetime.now()
    if row:
        old_expire = datetime.fromisoformat(row[0])
        # Agar muddati tugagan bo'lsa, hozirgi sanadan hisoblaymiz
        start_date = max(old_expire, now)
    else:
        start_date = now

    # Yangi muddat
    new_expire = start_date.replace(microsecond=0) + timedelta(days=30*months)
    expire_str = new_expire.isoformat()

    if row:
        cursor.execute("UPDATE subscriptions SET expire_date=? WHERE user_id=?", (expire_str, user_id))
    else:
        cursor.execute("INSERT INTO subscriptions (user_id, expire_date) VALUES (?, ?)", (user_id, expire_str))

    conn.commit()
    conn.close()
    return new_expire

def get_subscription(user_id: int):
    conn, cursor = connect_db()
    cursor.execute("SELECT expire_date FROM subscriptions WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return datetime.fromisoformat(row[0])
    return None

def remove_subscription(user_id: int):
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM subscriptions WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_all_subscriptions():
    conn, cursor = connect_db()
    cursor.execute("SELECT user_id, expire_date FROM subscriptions")
    rows = cursor.fetchall()
    conn.close()
    return [(user_id, datetime.fromisoformat(exp)) for user_id, exp in rows]