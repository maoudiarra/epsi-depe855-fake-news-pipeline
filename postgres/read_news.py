"""read_news.py - Affiche les news en base."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_CONFIG
import psycopg

conn = psycopg.connect(**DB_CONFIG)
cur  = conn.cursor()
cur.execute("SELECT id, title, source, verification_status, confidence_score FROM news ORDER BY id DESC LIMIT 20")
for row in cur.fetchall():
    print(row)
cur.close(); conn.close()
