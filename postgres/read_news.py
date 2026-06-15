import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname="news_db",
    user="admin",
    password="admin123"
)

cur = conn.cursor()

cur.execute("""
SELECT
    id,
    title,
    source,
    label,
    confidence_score
FROM news
""")

for row in cur.fetchall():
    print(row)

cur.close()
conn.close()