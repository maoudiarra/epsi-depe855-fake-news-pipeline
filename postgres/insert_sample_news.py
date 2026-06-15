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
INSERT INTO news (
    title,
    summary,
    source,
    publication_date,
    event_date,
    label,
    confidence_score
)
VALUES (
    'Tesla ouvre une nouvelle usine',
    'Expansion de la production en Europe',
    'AFP',
    NOW(),
    NOW(),
    'verified',
    0.98
)
""")

conn.commit()

print("News insérée avec succès")

cur.close()
conn.close()