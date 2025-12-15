from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.repositories.category_repository import CategoryRepository

def seed_if_empty() -> None:
    article_repo = ArticleRepository()
    if article_repo.count() > 0:
        return

    cat_repo = CategoryRepository()

    tech_id = cat_repo.create_or_get_id("Technology")
    life_id = cat_repo.create_or_get_id("Lifestyle")
    travel_id = cat_repo.create_or_get_id("Travel")

    article_repo.create(Article(None, "AI in Everyday Apps", tech_id,
                                "AI is increasingly used to personalize user experiences in mobile and web applications."))
    article_repo.create(Article(None, "Healthy Habits for Better Productivity", life_id,
                                "Small daily habits can have a big impact on energy, focus, and productivity."))
    article_repo.create(Article(None, "Understanding AR and VR Basics", tech_id,
                                "AR overlays information on the real world, while VR immerses users in a fully virtual environment."))
    article_repo.create(Article(None, "Travel Tips for Budget Explorers", travel_id,
                                "Planning ahead and using local options can significantly reduce travel costs."))
