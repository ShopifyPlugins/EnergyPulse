import logging
import sqlite3
from pathlib import Path

from src.config import DB_PATH

logger = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS admins (
                chat_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
    logger.info("Database initialized at %s", DB_PATH)


# ---- Knowledge ----

def add_knowledge(title: str, content: str) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO knowledge (title, content) VALUES (?, ?)",
            (title, content),
        )
        return cur.lastrowid


def list_knowledge() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title, LENGTH(content) as chars FROM knowledge ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_knowledge() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT id, title, content FROM knowledge").fetchall()
        return [dict(r) for r in rows]


def delete_knowledge(entry_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM knowledge WHERE id = ?", (entry_id,))
        return cur.rowcount > 0


# ---- Conversations ----

def save_message(chat_id: int, role: str, message: str):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations (chat_id, role, message) VALUES (?, ?, ?)",
            (chat_id, role, message),
        )


def get_history(chat_id: int, limit: int = 10) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, message FROM conversations "
            "WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
            (chat_id, limit),
        ).fetchall()
        return [dict(r) for r in reversed(rows)]


# ---- Admins ----

def is_admin(chat_id: int) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM admins WHERE chat_id = ?", (chat_id,)
        ).fetchone()
        return row is not None


def add_admin(chat_id: int):
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO admins (chat_id) VALUES (?)", (chat_id,)
        )


def get_admin_ids() -> list[int]:
    with _connect() as conn:
        rows = conn.execute("SELECT chat_id FROM admins").fetchall()
        return [r["chat_id"] for r in rows]


# ---- Settings ----

def get_setting(key: str, default: str = "") -> str:
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str):
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )


# ---- Stats ----

def get_stats() -> dict:
    with _connect() as conn:
        total_msgs = conn.execute(
            "SELECT COUNT(*) as c FROM conversations WHERE role = 'user'"
        ).fetchone()["c"]
        unique_users = conn.execute(
            "SELECT COUNT(DISTINCT chat_id) as c FROM conversations"
        ).fetchone()["c"]
        kb_entries = conn.execute(
            "SELECT COUNT(*) as c FROM knowledge"
        ).fetchone()["c"]
        today_msgs = conn.execute(
            "SELECT COUNT(*) as c FROM conversations "
            "WHERE role = 'user' AND DATE(created_at) = DATE('now')"
        ).fetchone()["c"]
        return {
            "total_messages": total_msgs,
            "unique_users": unique_users,
            "kb_entries": kb_entries,
            "today_messages": today_msgs,
        }
