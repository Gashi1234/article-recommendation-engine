from app.data.db import get_connection
from app.config.config import Config
import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category_id INTEGER,
    content TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS interaction_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    user_id INTEGER,
    event_type TEXT NOT NULL,
    duration_ms INTEGER,
    experiment_group TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (article_id) REFERENCES articles(id)
);
"""

def ensure_experiment_group_column():
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        conn.execute("ALTER TABLE interaction_events ADD COLUMN experiment_group TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

def init_db() -> None:
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

    ensure_experiment_group_column()
