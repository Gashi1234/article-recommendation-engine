from app.repositories.article_repository import ArticleRepository


class ArticleService:
    def __init__(self, repo: ArticleRepository | None = None):
        self.repo = repo or ArticleRepository()

    def list_articles(self) -> list[dict]:
        return self.repo.list_all()

    def get_article(self, article_id: int) -> dict | None:
        return self.repo.get_by_id(article_id)
