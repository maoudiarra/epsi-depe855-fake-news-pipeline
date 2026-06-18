"""
spark_job.py - Job Spark DEPE855
Lit les news depuis PostgreSQL, calcule des statistiques
et écrit les résultats en CSV dans /opt/spark-output (volume Docker).
Les credentials sont injectés via variables d'environnement.
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ── Config depuis variables d'environnement ───────────────────────────────────
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB   = os.environ.get("POSTGRES_DB",   "news_db")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "admin")
POSTGRES_PASS = os.environ.get("POSTGRES_PASSWORD", "")

JDBC_URL   = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
JDBC_PROPS = {
    "user":     POSTGRES_USER,
    "password": POSTGRES_PASS,
    "driver":   "org.postgresql.Driver",
}

OUTPUT_DIR = "/opt/spark-output"

# ── Session Spark ─────────────────────────────────────────────────────────────
spark = SparkSession.builder \
    .appName("DEPE855_NewsPipeline") \
    .config("spark.jars", "/opt/bitnami/spark/jars/extra/postgresql-42.7.3.jar") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ── Lecture PostgreSQL ────────────────────────────────────────────────────────
print("=== Lecture des news depuis PostgreSQL ===")
df = spark.read.jdbc(url=JDBC_URL, table="news", properties=JDBC_PROPS)
total = df.count()
print(f"Total articles : {total}")

# ── Nettoyage ─────────────────────────────────────────────────────────────────
df_clean = (
    df
    .dropDuplicates(["news_uid"])
    .filter(F.col("title").isNotNull() & (F.length("title") > 5))
    .withColumn("title_clean", F.trim(F.regexp_replace("title", r"\s+", " ")))
)

# ── Stats par source ──────────────────────────────────────────────────────────
print("\n=== Statistiques par source ===")
stats_source = (
    df_clean.groupBy("source", "verification_status")
    .agg(
        F.count("*").alias("count"),
        F.round(F.avg("confidence_score"), 3).alias("avg_confidence"),
    )
    .orderBy("source", "verification_status")
)
stats_source.show(truncate=False)

# ── Stats journalières ────────────────────────────────────────────────────────
print("\n=== Évolution journalière ===")
stats_daily = (
    df_clean
    .filter(F.col("publication_date").isNotNull())
    .withColumn("day", F.to_date("publication_date"))
    .groupBy("day", "verification_status")
    .agg(F.count("*").alias("count"))
    .orderBy("day")
)
stats_daily.show(30, truncate=False)

# ── Écriture CSV dans le volume Docker ───────────────────────────────────────
print(f"\n=== Écriture des résultats dans {OUTPUT_DIR} ===")

df_clean.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/news_clean")

stats_source.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/stats_source")

stats_daily.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(f"{OUTPUT_DIR}/stats_daily")

print("=== Job Spark terminé avec succès ===")
spark.stop()