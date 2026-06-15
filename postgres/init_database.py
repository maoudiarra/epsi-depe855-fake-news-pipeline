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
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    source VARCHAR(100),
    publication_date TIMESTAMP,
    event_date TIMESTAMP,
    label VARCHAR(20),
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

print("Table news créée avec succès")

cur.close()
conn.close()