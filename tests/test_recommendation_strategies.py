from app.services.recommendation_strategies import PopularityStrategy, ContentBasedStrategy

class FakeArticle:
    def __init__(self, id):
        self.id = id
        self.title = "Test"
        self.content = "Test content"
        self.category_name = "Tech"
        self.category_id = 1

class FakeArticleService:
    def list_articles(self):
        return [FakeArticle(1), FakeArticle(2), FakeArticle(3)]

    def get_article(self, article_id):
        return FakeArticle(article_id)

class FakeEventService:
    def count_for_article(self, article_id, event_type):
        return 1

    def total_duration_ms_for_article(self, article_id, event_type):
        return 60000

def test_popularity_strategy_returns_results():
    strategy = PopularityStrategy(
        article_service=FakeArticleService(),
        event_service=FakeEventService()
    )
    results = strategy.recommend(article_id=1, limit=2)
    assert len(results) == 2

def test_content_strategy_returns_results():
    strategy = ContentBasedStrategy(article_service=FakeArticleService())
    results = strategy.recommend(article_id=1, limit=2)
    assert len(results) == 2
