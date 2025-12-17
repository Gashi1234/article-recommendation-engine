from flask import Flask, render_template
from app.services.article_service import ArticleService
from app.services.interaction_event_service import InteractionEventService
from app.models.interaction_event import InteractionEvent
from app.data.schema import init_db
from app.data.seed import seed_if_empty


def create_app():
    app = Flask(__name__)

    # Initialize database and seed data
    init_db()
    seed_if_empty()

    # Services
    service = ArticleService()
    event_service = InteractionEventService()

    @app.route("/")
    def home():
        articles = service.list_articles()
        return render_template("home.html", articles=articles)

    @app.route("/articles/<int:article_id>")
    def article_detail(article_id: int):
        article = service.get_article(article_id)
        if not article:
            return "Article not found", 404

        # Log a view event when article is opened
        event_service.log(
            InteractionEvent(
                id=None,
                article_id=article_id,
                user_id=None,
                event_type="view",
                duration_ms=None,
                created_at=None,
            )
        )
        views = event_service.count_for_article(article_id, "view")
        return render_template("article_detail.html", article=article, views=views)


        return render_template("article_detail.html", article=article)

    return app
