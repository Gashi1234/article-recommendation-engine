from typing import List, Optional
from app.data.db import get_connection
from app.models.article import Article

class ArticleRepository:

    def count(self) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM articles")
        (n,) = cur.fetchone()
        conn.close()
        return int(n)

    def create(self, article: Article) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO articles(title, category_id, content) VALUES (?, ?, ?)",
            (article.title, article.category_id, article.content),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return int(new_id)

    def list_all(self) -> List[Article]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT a.id, a.title, a.category_id, a.content, c.name
            FROM articles a
            LEFT JOIN categories c ON c.id = a.category_id
            ORDER BY a.id DESC
        """)

        rows = cur.fetchall()
        conn.close()

        articles: List[Article] = []
        for (id_, title, category_id, content, category_name) in rows:
            articles.append(
                Article(
                    id=id_,
                    title=title,
                    category_id=category_id,
                    content=content,
                    category_name=category_name,
                )
            )
        return articles

    def get_by_id(self, article_id: int) -> Optional[Article]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT a.id, a.title, a.category_id, a.content, c.name
            FROM articles a
            LEFT JOIN categories c ON c.id = a.category_id
            WHERE a.id = ?
        """, (article_id,))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        (id_, title, category_id, content, category_name) = row
        return Article(
            id=id_,
            title=title,
            category_id=category_id,
            content=content,
            category_name=category_name,
        )
