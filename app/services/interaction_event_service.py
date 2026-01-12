from typing import List
from app.models.interaction_event import InteractionEvent
from app.data.db import get_connection

class InteractionEventService:

    def log(self, event: InteractionEvent):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO interaction_events(article_id, user_id, event_type, duration_ms) VALUES (?, ?, ?, ?)",
            (event.article_id, event.user_id, event.event_type, event.duration_ms)
        )
        conn.commit()
        conn.close()
        return event

    def list_for_article(self, article_id: int) -> List[InteractionEvent]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM interaction_events WHERE article_id = ? ORDER BY id DESC",
            (article_id,)
        )
        rows = cur.fetchall()
        conn.close()
        events: List[InteractionEvent] = []
        for row in rows:
            events.append(InteractionEvent(
                id=row["id"],
                article_id=row["article_id"],
                user_id=row["user_id"],
                event_type=row["event_type"],
                duration_ms=row["duration_ms"],
                created_at=row["created_at"]
            ))
        return events

    def count_for_article(self, article_id: int, event_type: str) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM interaction_events WHERE article_id = ? AND event_type = ?",
            (article_id, event_type)
        )
        (n,) = cur.fetchone()
        conn.close()
        return int(n)
    
    def total_duration_ms_for_article(self, article_id: int, event_type: str) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(SUM(duration_ms), 0)
            FROM interaction_events
            WHERE article_id = ? AND event_type = ? AND duration_ms IS NOT NULL
            """,
            (article_id, event_type)
        )
        (total,) = cur.fetchone()
        conn.close()
        return int(total or 0)

