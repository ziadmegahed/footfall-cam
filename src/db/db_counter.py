import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "footfall.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                up_count INTEGER,
                down_count INTEGER,
                total_count INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crossings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                track_id INTEGER NOT NULL,
                direction TEXT NOT NULL CHECK (direction IN ('up', 'down')),
                video_time_s REAL,
                recorded_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def get_connection():
    init_db()
    return sqlite3.connect(DB_PATH)


def start_run(conn, video_name):
    cur = conn.execute(
        "INSERT INTO runs (video, started_at) VALUES (?, ?)",
        (video_name, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    return cur.lastrowid


def log_crossing(conn, run_id, track_id, direction, video_time_s):
    conn.execute(
        "INSERT INTO crossings (run_id, track_id, direction, video_time_s, recorded_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (run_id, int(track_id), direction, round(video_time_s, 2),
         datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()

def finish_run(conn, run_id, up_count, down_count):
    conn.execute(
        "UPDATE runs SET finished_at = ?, up_count = ?, down_count = ?, total_count = ? "
        "WHERE id = ?",
        (datetime.now().isoformat(timespec="seconds"),
         up_count, down_count, up_count - down_count, run_id),
    )
    conn.commit()