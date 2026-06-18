"""count_news.py - Compte les news par statut."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_CONFIG
import psycopg

conn = psycopg.connect(**DB_CONFIG)
cur  = conn.cursor()
cur.execute("SELECT verification_status, COUNT(*) FROM news GROUP BY verification_status")
print("=== Bilan des news ===")
for status, count in cur.fetchall():
    print(f"  {status}: {count}")
cur.close(); conn.close()
