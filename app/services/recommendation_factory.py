from app.services.recommendation_strategies import (
    PopularityStrategy,
    ContentBasedStrategy,
    HybridStrategy,
    RecommendationStrategy,
)

class RecommendationFactory:
    @staticmethod
    def create(strategy_name: str, article_service, event_service) -> RecommendationStrategy:
        name = (strategy_name or "").strip().lower()

        if name in ["content", "content_based", "content-based"]:
            return ContentBasedStrategy(article_service=article_service)

        if name in ["hybrid", "mixed", "mix", "combined"]:
            content = ContentBasedStrategy(article_service=article_service)
            popularity = PopularityStrategy(article_service=article_service, event_service=event_service)
            return HybridStrategy(content_strategy=content, popularity_strategy=popularity)

        return PopularityStrategy(article_service=article_service, event_service=event_service)
