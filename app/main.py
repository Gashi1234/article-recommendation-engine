from flask import Flask, render_template
from app.services.article_service import ArticleService
from app.data.schema import init_db



def create_app():
    app = Flask(__name__)

    init_db()
    
    service = ArticleService()

    @app.route("/")
    def home():
        articles = service.list_articles()
        return render_template("home.html", articles=articles)

    return app
