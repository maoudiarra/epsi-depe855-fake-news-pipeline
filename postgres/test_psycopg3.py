import psycopg

print("Connexion PostgreSQL Docker...")

conn = psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname="news_db",
    user="admin",
    password="admin123"
)

print("Connexion OK")

with conn.cursor() as cur:
    cur.execute("SELECT current_user;")
    print("Utilisateur :", cur.fetchone()[0])

conn.close()

print("Connexion fermée")