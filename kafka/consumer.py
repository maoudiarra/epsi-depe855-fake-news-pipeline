"""
consumer.py - Consommateur Kafka DEPE855
Lit le topic Kafka, applique la détection ML et insère dans PostgreSQL.
"""

import sys
import os
import json
import psycopg
from kafka import KafkaConsumer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_CONFIG, KAFKA_BOOTSTRAP, KAFKA_TOPIC
from ml.predict import predict_fake_news

# ── Connexions ────────────────────────────────────────────────────────────────
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP,
    auto_offset_reset="earliest",
    group_id="depe855-consumer",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

conn = psycopg.connect(**DB_CONFIG)
cur  = conn.cursor()

UPSERT_SQL = """
INSERT INTO news (
    news_uid, title, summary, source,
    publication_date, event_date,
    verification_status, confidence_score,
    processing_date, last_seen
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
ON CONFLICT (news_uid) DO UPDATE SET
    last_seen           = NOW(),
    processing_date     = NOW(),
    verification_status = EXCLUDED.verification_status,
    confidence_score    = EXCLUDED.confidence_score;
"""

ICONS = {"verified": "✅", "fake": "❌", "pending": "⏳"}


def process(news: dict) -> None:
    # Appel ML si le score n'est pas déjà connu
    if news.get("confidence_score") is None:
        label, score = predict_fake_news(
            news.get("title", ""), news.get("summary", "")
        )
        news["verification_status"] = label
        news["confidence_score"]    = score

    cur.execute(UPSERT_SQL, (
        news.get("news_uid"),
        news.get("title"),
        news.get("summary"),
        news.get("source"),
        news.get("publication_date"),
        news.get("event_date"),
        news.get("verification_status"),
        news.get("confidence_score"),
    ))
    conn.commit()

    icon = ICONS.get(news.get("verification_status", "pending"), "?")
    print(f"{icon} [{news['source']}] {news['title'][:80]} "
          f"(score={news['confidence_score']})")


# ── Boucle principale ─────────────────────────────────────────────────────────
print(f"=== Consommateur Kafka démarré → topic '{KAFKA_TOPIC}' ===")
try:
    for message in consumer:
        try:
            process(message.value)
        except Exception as e:
            print(f"[ERREUR] {e}")
            conn.rollback()
except KeyboardInterrupt:
    print("\nArrêt propre du consommateur.")
finally:
    cur.close()
    conn.close()
    consumer.close()
