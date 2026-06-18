"""init_database.py - Crée les tables manuellement si besoin."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_CONFIG
import psycopg

conn = psycopg.connect(**DB_CONFIG)
cur  = conn.cursor()
with open(os.path.join(os.path.dirname(__file__), "init.sql")) as f:
    cur.execute(f.read())
conn.commit()
print("Tables créées avec succès.")
cur.close(); conn.close()
