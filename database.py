import sqlite3
import os

DB_PATH = os.path.join("database", "attendance.db")
os.makedirs("database", exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id   TEXT NOT NULL,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        PRIMARY KEY (id, date)
    )
    """)

    conn.commit()
    conn.close()


def insert_attendance(person_id, name, date, time):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO attendance (id, name, date, time)
        VALUES (?, ?, ?, ?)
    """, (str(person_id), str(name), str(date), str(time)))

    conn.commit()
    conn.close()


def already_marked(person_id, date):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM attendance WHERE id=? AND date=? LIMIT 1", (str(person_id), str(date)))
    row = cur.fetchone()
    conn.close()
    return row is not None


def id_exists_in_dataset(person_id):
    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir):
        return False

    pid = str(person_id).strip()
    for folder in os.listdir(dataset_dir):
        if folder.startswith(pid + "_"):
            return True
    return False
