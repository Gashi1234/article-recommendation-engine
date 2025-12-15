from flask import Flask, render_template
from app.services.article_service import ArticleService
from app.data.schema import init_db
from app.data.seed import seed_if_empty



def create_app():
    app = Flask(__name__)

    init_db()
    
    seed_if_empty()

    service = ArticleService()

    @app.route("/")
    def home():
        articles = service.list_articles()
        return render_template("home.html", articles=articles)
        
    @app.route("/articles/<int:article_id>")
    def article_detail(article_id: int):
        article = service.get_article(article_id)
        if not article:
            return "Article not found", 404
        return render_template("article_detail.html", article=article)
    
    return app
