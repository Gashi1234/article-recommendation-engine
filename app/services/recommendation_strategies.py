from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from app.models.article import Article


class RecommendationStrategy(Protocol):
    def recommend(self, article_id: int, limit: int = 5) -> List[Article]:
        ...


@dataclass
class PopularityStrategy:
    article_service: any
    event_service: any

    def recommend(self, article_id: int, limit: int = 5) -> List[Article]:
        all_articles = self.article_service.list_articles()

        scored = []
        for a in all_articles:
            if a.id == article_id:
                continue

            views = self.event_service.count_for_article(a.id, "view")
            likes = self.event_service.count_for_article(a.id, "like")
            time_spent = self.event_service.count_for_article(a.id, "time_spent")

            score = (views * 1) + (likes * 3) + (time_spent * 2)
            scored.append((score, a))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [a for score, a in scored[:limit]]


@dataclass
class ContentBasedStrategy:
    article_service: any

    def recommend(self, article_id: int, limit: int = 5) -> List[Article]:
        current = self.article_service.get_article(article_id)
        if not current:
            return []

        all_articles = self.article_service.list_articles()

        current_category = getattr(current, "category", None)
        current_category_id = getattr(current, "category_id", None)

        same_category = []
        other = []

        for a in all_articles:
            if a.id == article_id:
                continue

            cat = getattr(a, "category", None)
            cat_id = getattr(a, "category_id", None)

            if current_category_id is not None and cat_id == current_category_id:
                same_category.append(a)
            elif current_category is not None and cat == current_category:
                same_category.append(a)
            else:
                other.append(a)

        return (same_category + other)[:limit]
