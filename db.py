import sqlite3
from config import DB_PATH


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS seen (
                id TEXT PRIMARY KEY,
                seen_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def is_seen(listing_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT 1 FROM seen WHERE id = ?", (listing_id,)).fetchone()
        return row is not None


def mark_seen(listing_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO seen (id) VALUES (?)", (listing_id,))
