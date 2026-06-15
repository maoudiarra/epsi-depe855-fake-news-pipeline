# test_psycopg3_testuser.py

import psycopg

try:
    print("Connexion PostgreSQL...")

    conn = psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="news_db",
        user="testuser",
        password="test123"
    )

    print("Connexion réussie !")

    with conn.cursor() as cur:
        cur.execute("SELECT current_user;")
        print("Utilisateur :", cur.fetchone()[0])

    conn.close()

except Exception as e:
    print("Erreur :", e)