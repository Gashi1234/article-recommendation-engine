from typing import Optional, List
from app.data.db import get_connection
from app.models.user import User

class UserRepository:
    def create(self, user: User) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(name) VALUES (?)",
            (user.name,)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return int(new_id)

    def get_by_id(self, user_id: int) -> Optional[User]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return User(id=row["id"], name=row["name"])

    def get_by_name(self, name: str) -> Optional[User]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return User(id=row["id"], name=row["name"])

    def list_all(self) -> List[User]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [User(id=r["id"], name=r["name"]) for r in rows]
