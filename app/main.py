from flask import Flask, render_template, jsonify, request
from app.services.article_service import ArticleService
from app.services.interaction_event_service import InteractionEventService
from app.models.interaction_event import InteractionEvent
from app.data.schema import init_db
from app.data.seed import seed_if_empty
from app.services.recommendation_factory import RecommendationFactory
from dataclasses import replace
from sklearn.feature_extraction.text import TfidfVectorizer



def create_app():

    app = Flask(__name__)

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
        conn = sqlite3.connect("app/data/app.db")
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

        recommendations = strategy.recommend(article_id=article_id, limit=5)

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


   
    # API routes

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
                limit=5
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

        return jsonify({
            "article_id": article_id,
            "views": event_service.count_for_article(article_id, "view"),
            "likes": event_service.count_for_article(article_id, "like"),
            "time_spent_seconds": total_seconds,
            "time_spent_minutes": total_minutes,
        })

    
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
