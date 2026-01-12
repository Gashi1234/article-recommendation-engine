from app.data.db import get_connection
from app.models.category import Category
from typing import List

class CategoryRepository:

    def create_or_get_id(self, name: str) -> int:
        """
        Krijon një kategori nëse nuk ekziston, ose kthen ID-në e saj ekzistuese.
        """
        conn = get_connection()
        cur = conn.cursor()

        # Insert only if not exists
        cur.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
        conn.commit()

        # Get ID
        cur.execute("SELECT id FROM categories WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()
        return int(row["id"])

    def list_all(self) -> List[Category]:
        """
        Kthen të gjitha kategoritë si lista objektesh Category
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        rows = cur.fetchall()
        conn.close()
        return [Category(id=r["id"], name=r["name"]) for r in rows]
    
    def get_by_id(self, category_id: int):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name FROM categories WHERE id = ?",
                (category_id,)
            ).fetchone()

        if not row:
            return None

        return Category(id=row[0], name=row[1])

