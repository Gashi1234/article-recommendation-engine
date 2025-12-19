from app.data.db import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT * FROM interaction_events")
rows = cur.fetchall()
for row in rows:
    print(dict(row))
