from typing import List, Optional
from app.models.interaction_event import InteractionEvent
from app.repositories.interaction_event_repository import InteractionEventRepository


class InteractionEventService:
    def __init__(self):
        self.repo = InteractionEventRepository()

    def log(self, event: InteractionEvent) -> int:
        return self.repo.create(event)

    def list_for_article(self, article_id: int, limit: int = 100) -> List[InteractionEvent]:
        return self.repo.list_by_article(article_id, limit)

    def count_for_article(self, article_id: int, event_type: Optional[str] = None) -> int:
        return self.repo.count_for_article(article_id, event_type)
