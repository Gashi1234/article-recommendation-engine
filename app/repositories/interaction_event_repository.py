from typing import List, Optional
from app.data.db import get_connection
from app.models.interaction_event import InteractionEvent


class InteractionEventRepository:
    def log_event(self, event: InteractionEvent) -> int:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO interaction_events(article_id, user_id, event_type, duration_ms)
            VALUES (?, ?, ?, ?)
            """,
            (event.article_id, event.user_id, event.event_type, event.duration_ms),
        )

        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return int(new_id)

    def create(self, event: InteractionEvent) -> int:
        return self.log_event(event)

    def list_by_article(self, article_id: int, limit: int = 100) -> List[InteractionEvent]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, article_id, user_id, event_type, duration_ms, created_at
            FROM interaction_events
            WHERE article_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (article_id, limit),
        )

        rows = cur.fetchall()
        conn.close()

        events: List[InteractionEvent] = []
        for r in rows:
            events.append(
                InteractionEvent(
                    id=r["id"],
                    article_id=r["article_id"],
                    user_id=r["user_id"],
                    event_type=r["event_type"],
                    duration_ms=r["duration_ms"],
                    created_at=r["created_at"],
                )
            )
        return events

    def count_for_article(self, article_id: int, event_type: Optional[str] = None) -> int:
        conn = get_connection()
        cur = conn.cursor()

        if event_type:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM interaction_events
                WHERE article_id = ? AND event_type = ?
                """,
                (article_id, event_type),
            )
        else:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM interaction_events
                WHERE article_id = ?
                """,
                (article_id,),
            )

        (n,) = cur.fetchone()
        conn.close()
        return int(n)
