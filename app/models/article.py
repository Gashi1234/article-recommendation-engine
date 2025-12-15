from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Article:
    id: Optional[int]
    title: str
    category_id: Optional[int]
    content: str
    category_name: Optional[str] = None
