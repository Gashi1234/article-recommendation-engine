from __future__ import annotations

from app.services.recommendation_strategies import (
    PopularityStrategy,
    ContentBasedStrategy,
    RecommendationStrategy,
)


class RecommendationFactory:
    @staticmethod
    def create(strategy_name: str, article_service, event_service) -> RecommendationStrategy:
        name = (strategy_name or "").strip().lower()

        if name in ["content", "content_based", "content-based"]:
            return ContentBasedStrategy(article_service=article_service)

        return PopularityStrategy(article_service=article_service, event_service=event_service)
