"""
producer.py - Producteur Kafka DEPE855
Collecte les news via flux RSS (AFP, Le Monde, Gorafi) et les envoie dans Kafka.
Retraitement automatique toutes les 6 heures.
"""

import sys
import os
import json
import time

from kafka import KafkaProducer

# Config centrale (lit le .env)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import KAFKA_BOOTSTRAP, KAFKA_TOPIC
from scraper.afp_scraper     import scrape as scrape_afp
from scraper.lemonde_scraper import scrape as scrape_lemonde
from scraper.gorafi_scraper  import scrape as scrape_gorafi

# ── Producteur Kafka ──────────────────────────────────────────────────────────
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)


def run():
    print(f"=== Producteur Kafka démarré → topic '{KAFKA_TOPIC}' ===")
    while True:
        print("--- Collecte en cours... ---")
        all_news = scrape_afp(10) + scrape_lemonde(10) + scrape_gorafi(5)

        if not all_news:
            print("⚠️  Aucun article collecté. Vérifiez votre connexion.")
        else:
            for article in all_news:
                producer.send(KAFKA_TOPIC, value=article).get(timeout=10)
                icon = {"verified": "✅", "fake": "❌", "pending": "⏳"}.get(
                    article["verification_status"], "?"
                )
                print(f"  {icon} [{article['source']}] {article['title'][:80]}")
            producer.flush()

        print(f"--- {len(all_news)} articles envoyés. Prochaine collecte dans 6h. ---\n")
        time.sleep(6 * 3600)


if __name__ == "__main__":
    run()
