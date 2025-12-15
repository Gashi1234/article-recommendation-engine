from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class InteractionEvent:
    id: Optional[int]
    article_id: int
    event_type: str
    created_at: str
    user_id: Optional[int] = None
    duration_ms: Optional[int] = None
