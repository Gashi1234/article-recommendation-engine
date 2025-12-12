from app.repositories.sample_data import SAMPLE_ARTICLES


class ArticleRepository:
    def list_all(self) -> list[dict]:
        return SAMPLE_ARTICLES

    def get_by_id(self, article_id: int) -> dict | None:
        for a in SAMPLE_ARTICLES:
            if a["id"] == article_id:
                return a
        return None
