"""insert_sample_news.py - Insère une news de test."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_CONFIG
import psycopg

conn = psycopg.connect(**DB_CONFIG)
cur  = conn.cursor()
cur.execute("""
    INSERT INTO news (news_uid, title, summary, source, publication_date,
                      event_date, verification_status, confidence_score)
    VALUES ('test-001', 'Tesla ouvre une nouvelle usine',
            'Expansion de la production en Europe',
            'AFP', NOW(), NOW(), 'verified', 0.98)
    ON CONFLICT (news_uid) DO NOTHING;
""")
conn.commit()
print("News de test insérée.")
cur.close(); conn.close()
