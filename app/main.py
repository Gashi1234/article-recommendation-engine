from flask import Flask, render_template, jsonify, request
from app.services.article_service import ArticleService
from app.services.interaction_event_service import InteractionEventService
from app.models.interaction_event import InteractionEvent
from app.data.schema import init_db
from app.data.seed import seed_if_empty
from app.services.recommendation_factory import RecommendationFactory

def create_app():
    app = Flask(__name__)

    # Initialize DB and seed
    init_db()
    seed_if_empty()

    # Services
    service = ArticleService()
    event_service = InteractionEventService()

    # --------------------
    # Web routes
    # --------------------
    @app.route("/")
    def home():
        articles = service.list_articles()
        return render_template("home.html", articles=articles)

    @app.route("/articles/<int:article_id>")
    def article_detail(article_id: int):
        article = service.get_article(article_id)
        if not article:
            return "Article not found", 404

        # Log view event automatically
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
        likes = event_service.count_for_article(article_id, "like")
        return render_template(
            "article_detail.html",
            article=article,
            views=views,
            likes=likes
        )

    # --------------------
    # API routes
    # --------------------
    @app.route("/api/recommendations/<int:article_id>")
    def recommendations(article_id: int):
        strategy_name = request.args.get("strategy", "popular")

        strategy = RecommendationFactory.create(
            strategy_name=strategy_name,
            article_service=service,
            event_service=event_service,
        )

        results = strategy.recommend(article_id=article_id, limit=5)

        return jsonify({
            "strategy": strategy_name,
            "recommendations": [
                {"id": a.id, "title": a.title} for a in results
            ]
        })


    @app.route("/api/analytics/<int:article_id>")
    def analytics(article_id: int):
        return jsonify({
            "article_id": article_id,
            "views": event_service.count_for_article(article_id, "view"),
            "likes": event_service.count_for_article(article_id, "like"),
            "time_spent_events": event_service.count_for_article(article_id, "time_spent"),
        })

    @app.route("/api/events", methods=["POST"])
    def log_event():
        data = request.json
        event_type = data["event_type"]
        duration = data.get("duration_ms")
        event_service.log(
            InteractionEvent(
                id=None,
                article_id=data["article_id"],
                user_id=data.get("user_id"),
                event_type=event_type,
                duration_ms=duration,
                created_at=None
            )
        )
        return jsonify({"status": "ok"})

    return app
