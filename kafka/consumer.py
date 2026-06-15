from kafka import KafkaConsumer
import psycopg
import json

consumer = KafkaConsumer(
    "news-topic",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

conn = psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname="news_db",
    user="admin",
    password="admin123"
)

cur = conn.cursor()

print("Consumer démarré...")

for message in consumer:

    news = message.value

    print(f"Réception : {news['title']}")

    cur.execute("""
        INSERT INTO news (
            title,
            summary,
            source,
            publication_date,
            event_date,
            label,
            confidence_score
        )
        VALUES (
            %s,%s,%s,NOW(),NOW(),%s,%s
        )
    """,
    (
        news["title"],
        news["summary"],
        news["source"],
        news["label"],
        news["confidence_score"]
    ))

    conn.commit()

    print("Insertion PostgreSQL OK")