from flask import Flask, render_template
from app.services.article_service import ArticleService


def create_app():
    app = Flask(__name__)
    service = ArticleService()

    @app.route("/")
    def home():
        articles = service.list_articles()
        return render_template("home.html", articles=articles)

    return app
