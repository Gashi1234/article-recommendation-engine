from app.models.article import Article
from app.repositories.article_repository import ArticleRepository

class ArticleService:
    def __init__(self):
        self.repo = ArticleRepository()

    def list_articles(self):
        return self.repo.list_all()

    def get_article(self, article_id: int):
        return self.repo.get_by_id(article_id)
