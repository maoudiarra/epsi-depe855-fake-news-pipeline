"""
pipeline_dag.py - DAG Airflow DEPE855
Orchestre le pipeline complet toutes les 6 heures.
Les credentials sont lus depuis les variables d'environnement Airflow
(définies dans l'interface Airflow > Admin > Variables ou via .env).
"""

import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "depe855",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ── Helpers config ────────────────────────────────────────────────────────────
def _db_config() -> dict:
    """Lit la config DB depuis les variables d'environnement Airflow."""
    return {
        "host":     os.environ["POSTGRES_HOST"],
        "port":     int(os.environ["POSTGRES_PORT"]),
        "dbname":   os.environ["POSTGRES_DB"],
        "user":     os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
    }

def _kafka_config() -> tuple[str, str]:
    return os.environ["KAFKA_BOOTSTRAP"], os.environ["KAFKA_TOPIC"]


# ── Tâche 1 : Scraping + production Kafka ────────────────────────────────────
def task_scrape_and_produce(**context):
    import sys, json
    sys.path.insert(0, "/opt/airflow")
    from scraper.afp_scraper    import scrape as scrape_afp
    from scraper.lemonde_scraper import scrape as scrape_lemonde
    from scraper.gorafi_scraper  import scrape as scrape_gorafi
    from kafka import KafkaProducer

    bootstrap, topic = _kafka_config()
    producer = KafkaProducer(
        bootstrap_servers=bootstrap,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    )
    all_news = scrape_afp(10) + scrape_lemonde(10) + scrape_gorafi(5)
    for article in all_news:
        producer.send(topic, value=article)
    producer.flush()
    producer.close()
    print(f"[DAG] {len(all_news)} articles produits.")
    return len(all_news)


# ── Tâche 2 : Consommation Kafka → PostgreSQL ────────────────────────────────
def task_consume_and_store(**context):
    import sys, json
    import psycopg
    from kafka import KafkaConsumer

    sys.path.insert(0, "/opt/airflow")
    from ml.predict import predict_fake_news

    bootstrap, topic = _kafka_config()
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap,
        auto_offset_reset="earliest",
        group_id=f"airflow-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        consumer_timeout_ms=15000,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    conn = psycopg.connect(**_db_config())
    cur  = conn.cursor()
    inserted = 0

    for msg in consumer:
        news = msg.value
        if news.get("confidence_score") is None:
            label, score = predict_fake_news(news.get("title",""), news.get("summary",""))
            news["verification_status"] = label
            news["confidence_score"]    = score
        cur.execute("""
            INSERT INTO news (
                news_uid, title, summary, source,
                publication_date, event_date,
                verification_status, confidence_score,
                processing_date, last_seen
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
            ON CONFLICT (news_uid) DO UPDATE SET
                last_seen=NOW(), processing_date=NOW(),
                verification_status=EXCLUDED.verification_status,
                confidence_score=EXCLUDED.confidence_score;
        """, (
            news.get("news_uid"), news.get("title"), news.get("summary"),
            news.get("source"), news.get("publication_date"), news.get("event_date"),
            news.get("verification_status"), news.get("confidence_score"),
        ))
        conn.commit()
        inserted += 1

    cur.close(); conn.close(); consumer.close()
    print(f"[DAG] {inserted} articles traités.")
    return inserted


# ── Tâche 3 : Contrôle intégrité ─────────────────────────────────────────────
def task_check_integrity(**context):
    import psycopg
    conn = psycopg.connect(**_db_config())
    cur  = conn.cursor()
    cur.execute("""
        SELECT verification_status, COUNT(*)
        FROM news
        WHERE processing_date >= NOW() - INTERVAL '7 hours'
        GROUP BY verification_status
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    print("[DAG] Bilan du run :")
    for status, count in rows:
        print(f"  {status}: {count}")
    return dict(rows)


# ── Définition du DAG ─────────────────────────────────────────────────────────
with DAG(
    dag_id="depe855_news_pipeline",
    default_args=default_args,
    description="Pipeline Big Data détection fake news - DEPE855",
    schedule_interval="0 */6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["depe855", "big-data", "fake-news"],
) as dag:

    t1 = PythonOperator(task_id="scrape_and_produce",  python_callable=task_scrape_and_produce)
    t2 = PythonOperator(task_id="consume_and_store",   python_callable=task_consume_and_store)
    t3 = PythonOperator(task_id="check_integrity",     python_callable=task_check_integrity)
    t4 = BashOperator(  task_id="log_completion",
                        bash_command='echo "Pipeline DEPE855 terminé à $(date)"')

    t1 >> t2 >> t3 >> t4
