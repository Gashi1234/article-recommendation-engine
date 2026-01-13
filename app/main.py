from app.config.config import Config
from flask import Flask, render_template, jsonify, request
from app.services.article_service import ArticleService
from app.services.interaction_event_service import InteractionEventService
from app.models.interaction_event import InteractionEvent
from app.data.schema import init_db
from app.data.seed import seed_if_empty
from app.services.recommendation_factory import RecommendationFactory
from dataclasses import replace
from sklearn.feature_extraction.text import TfidfVectorizer
import logging



def create_app():

    app = Flask(__name__)

    app.json.sort_keys = False

    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    logger = logging.getLogger("article_engine")

    # Initialize DB and seed
    init_db()
    seed_if_empty()

    # Services
    service = ArticleService()
    event_service = InteractionEventService()
    
    import sqlite3

    def get_category_name(category_id):
        if not category_id:
            return "Unknown"
        conn = sqlite3.connect(Config.DB_PATH)
        try:
            row = conn.execute(
                "SELECT name FROM categories WHERE id = ?",
                (category_id,)
            ).fetchone()
            return row[0] if row else "Unknown"
        finally:
            conn.close()


    
    # Web routes
  
    @app.route("/")
    def home():
        articles = service.list_articles()
        return render_template("home.html", articles=articles)

    @app.route("/articles/<int:article_id>")
    def article_detail(article_id: int):
        article = service.get_article(article_id)
        if not article:
            return "Article not found", 404

        # NEW: attach category name to the main article
        article = replace(
            article,
            category_name=get_category_name(article.category_id)
        )
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

        strategy_name = request.args.get("strategy", "popular")

        strategy = RecommendationFactory.create(
            strategy_name=strategy_name,
            article_service=service,
            event_service=event_service,
        )

        recommendations = strategy.recommend(article_id=article_id, limit=8)

        # NEW: attach category names and exclude current article
        recommendations = [
            replace(a, category_name=get_category_name(a.category_id))
            for a in recommendations
            if a.id != article_id
        ]


        return render_template(
            "article_detail.html",
            article=article,
            views=views,
            likes=likes,
            recommendations=recommendations,
            rec_strategy=strategy_name
        )


    def get_top_keywords_for_article_id(article_id: int, top_n: int = 3) -> str:
        articles = service.list_articles()
        if not articles:
            return "-"

        def build_text(a) -> str:
            title = (getattr(a, "title", "") or "").strip()
            content = (getattr(a, "content", "") or "").strip()
            category_name = get_category_name(getattr(a, "category_id", None))
            return f"{title} {content} {category_name}".strip()

        texts = [build_text(a) for a in articles]

        if not any(t.strip() for t in texts):
            return "-"

        vectorizer = TfidfVectorizer(
            lowercase=True,
            max_features=5000,
            stop_words="english"
        )
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()

        id_to_index = {a.id: i for i, a in enumerate(articles)}
        idx = id_to_index.get(article_id)

        if idx is None:
            return "-"

        row_vec = tfidf_matrix[idx]
        if row_vec.nnz == 0:
            return "-"

        indices = row_vec.indices
        data = row_vec.data

        top_pairs = sorted(zip(indices, data), key=lambda x: x[1], reverse=True)[:top_n]
        words = [feature_names[i] for i, _ in top_pairs]

        return ", ".join(words) if words else "-"

   
    # API routes

    @app.route("/api/recommendations/<int:article_id>")
    def recommendations(article_id: int):
        requested = request.args.get("strategy", "popular")

        strategy = RecommendationFactory.create(
            strategy_name=requested,
            article_service=service,
            event_service=event_service,
        )

        results = strategy.recommend(article_id=article_id, limit=8)

        actual = strategy.__class__.__name__

        return jsonify({
            "requested_strategy": requested,
            "actual_strategy": actual,
            "recommendations": [{"id": a.id, "title": a.title} for a in results]
        })


    @app.route("/recommendations")
    def recommendations_page():
        article_id = request.args.get("article_id", type=int)
        strategy_name = request.args.get("strategy", "popular")

        articles = service.list_articles()
        recommendations = []

        if article_id:
            strategy = RecommendationFactory.create(
                strategy_name=strategy_name,
                article_service=service,
                event_service=event_service,
            )
            recommendations = strategy.recommend(
                article_id=article_id,
                limit=8
            )

        return render_template(
            "recommendations.html",
            articles=articles,
            selected_article_id=article_id,
            strategy=strategy_name,
            recommendations=recommendations
        )

    @app.route("/api/analytics/<int:article_id>")
    def analytics(article_id: int):
        total_ms = event_service.total_duration_ms_for_article(article_id, "time_spent")
        total_seconds = round(total_ms / 1000.0, 2)
        total_minutes = round(total_ms / 60000.0, 2)

        article = service.get_article(article_id)
        category_name = get_category_name(getattr(article, "category_id", None)) if article else "Unknown"
        top_keywords = get_top_keywords_for_article_id(article_id, top_n=3)

        requested = request.args.get("strategy")  # optional, for consistency with your URL

        data = {
            "article_id": article_id,
            "views": event_service.count_for_article(article_id, "view"),
            "likes": event_service.count_for_article(article_id, "like"),
            "time_spent_minutes": total_minutes,
            "time_spent_seconds": total_seconds,
            "category": category_name,
            "top_keywords": top_keywords,
            "requested_strategy": requested
        }
        return jsonify(data)

    
    @app.route("/analytics")
    def analytics_page():
        articles = service.list_articles()

        # Build the text used by content recommendation: title + content + category_name
        def build_text(a) -> str:
            title = (getattr(a, "title", "") or "").strip()
            content = (getattr(a, "content", "") or "").strip()
            category_name = get_category_name(getattr(a, "category_id", None))
            return f"{title} {content} {category_name}".strip()

        texts = [build_text(a) for a in articles]

        # Compute TF-IDF and pick Top 3 keywords for each article
        top_keywords = [""] * len(articles)

        if articles and any(t.strip() for t in texts):
            vectorizer = TfidfVectorizer(
                lowercase=True,
                max_features=5000,
                stop_words="english"
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()

            for i in range(len(articles)):
                row_vec = tfidf_matrix[i]
                if row_vec.nnz == 0:
                    top_keywords[i] = ""
                    continue

                # get indices of non-zero weights for this doc
                indices = row_vec.indices
                data = row_vec.data

                # sort by tf-idf weight descending and take top 3
                top_pairs = sorted(zip(indices, data), key=lambda x: x[1], reverse=True)[:3]
                words = [feature_names[idx] for idx, _ in top_pairs]

                # store as a string for easy display in template
                top_keywords[i] = ", ".join(words)


        analytics_data = []
        category_counts = {}

        for idx, article in enumerate(articles):
            total_ms = event_service.total_duration_ms_for_article(article.id, "time_spent")
            total_seconds = round(total_ms / 1000, 2)
            total_minutes = round(total_ms / 60000, 2)

            category_name = get_category_name(getattr(article, "category_id", None))
            category_counts[category_name] = category_counts.get(category_name, 0) + 1

            kw = top_keywords[idx] or "-"


            analytics_data.append({
                "article": article,
                "category": category_name,
                "views": event_service.count_for_article(article.id, "view"),
                "likes": event_service.count_for_article(article.id, "like"),
                "time_spent_seconds": total_seconds,
                "time_spent_minutes": total_minutes,
                "top_keywords": kw,
            })

        category_labels = list(category_counts.keys())
        category_values = [category_counts[k] for k in category_labels]

        return render_template(
            "analytics.html",
            analytics_data=analytics_data,
            category_labels=category_labels,
            category_values=category_values
        )


    @app.route("/api/events", methods=["POST"])
    def log_event():
        try:
            data = request.get_json(silent=True) or {}

            event_type = data.get("event_type")
            article_id = data.get("article_id")
            duration = data.get("duration_ms")

            allowed_types = {"view", "like", "time_spent"}

            errors = []
            if event_type not in allowed_types:
                errors.append("event_type must be one of: view, like, time_spent")
            if not isinstance(article_id, int):
                errors.append("article_id must be an integer")
            if event_type == "time_spent" and duration is not None and not isinstance(duration, int):
                errors.append("duration_ms must be an integer (milliseconds)")

            if errors:
                logger.warning(f"Bad /api/events payload: {data} errors={errors}")
                return jsonify({"status": "error", "errors": errors, "received": data}), 400

            event_service.log(
                InteractionEvent(
                    id=None,
                    article_id=article_id,
                    user_id=data.get("user_id"),
                    event_type=event_type,
                    duration_ms=duration,
                    created_at=None
                )
            )

            logger.info(f"Event logged: article_id={article_id} type={event_type} duration_ms={duration}")
            return jsonify({"status": "ok"}), 201

        except Exception:
            logger.exception("Unhandled error in /api/events")
            return jsonify({"status": "error", "message": "internal server error"}), 500


    return app
