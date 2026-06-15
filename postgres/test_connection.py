import psycopg2

print("Début connexion...")

conn = psycopg2.connect(
    "dbname=news_db user=admin password=admin123 host=127.0.0.1 port=5432"
)

print("Connexion OK")

conn.close()

print("Connexion fermée")