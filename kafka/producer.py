from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

news = {
    "title": "Tesla ouvre une nouvelle usine",
    "summary": "Expansion de la production en Europe",
    "source": "AFP",
    "label": "verified",
    "confidence_score": 0.98
}

producer.send(
    "news-topic",
    value=news
)

producer.flush()

print("News envoyée dans Kafka")