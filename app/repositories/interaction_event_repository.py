import sqlite3
from app.data.db import get_connection
from app.models.interaction_event import InteractionEvent

class InteractionEventRepository:
    def log_event(self, event: InteractionEvent) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO interaction_events (user_id, article_id, event_type, duration_ms)
            VALUES (?, ?, ?, ?)
        """, (event.user_id, event.article_id, event.event_type, event.duration_ms))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    def count_events(self, article_id: int, event_type: str) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM interaction_events
            WHERE article_id = ? AND event_type = ?
        """, (article_id, event_type))
        (n,) = cur.fetchone()
        conn.close()
        return n
