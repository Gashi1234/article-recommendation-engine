from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class InteractionEvent:
    id: Optional[int]
    article_id: int
    user_id: Optional[int]
    event_type: str  # "view", "like", "time_spent"
    duration_ms: Optional[int] = None
    created_at: Optional[str] = None
