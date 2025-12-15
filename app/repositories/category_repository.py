from app.data.db import get_connection
from app.models.category import Category

class CategoryRepository:
    def create_or_get_id(self, name: str) -> int:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
        conn.commit()

        cur.execute("SELECT id FROM categories WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()

        return int(row["id"])

    def list_all(self) -> list[Category]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        rows = cur.fetchall()
        conn.close()
        return [Category(id=r["id"], name=r["name"]) for r in rows]
