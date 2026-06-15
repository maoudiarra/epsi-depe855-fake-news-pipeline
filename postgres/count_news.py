import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname="news_db",
    user="admin",
    password="admin123"
)

cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM news")

print("Nombre de news :", cur.fetchone()[0])

cur.close()
conn.close()