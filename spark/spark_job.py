"""
spark_job.py - Job Spark DEPE855
Retraitement batch : lit PostgreSQL, transforme, écrit dans HDFS en Parquet.
Les credentials sont injectés via les variables d'environnement du système.
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Lecture sécurisée des variables d'environnement
POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]
POSTGRES_DB   = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASS = os.environ["POSTGRES_PASSWORD"]

JDBC_URL   = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
JDBC_PROPS = {
    "user":     POSTGRES_USER,
    "password": POSTGRES_PASS,
    "driver":   "org.postgresql.Driver",
}
HDFS_BASE = "hdfs://namenode:9000/depe855"

# ── Session Spark ─────────────────────────────────────────────────────────────
spark = SparkSession.builder \
    .appName("DEPE855_NewsPipeline") \
    .config("spark.jars", "/opt/spark/jars/postgresql-42.7.3.jar") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# ── Lecture ───────────────────────────────────────────────────────────────────
print("=== Lecture des news depuis PostgreSQL ===")
df = spark.read.jdbc(url=JDBC_URL, table="news", properties=JDBC_PROPS)
print(f"Total articles : {df.count()}")

# ── Nettoyage & déduplication ─────────────────────────────────────────────────
df_clean = (
    df
    .dropDuplicates(["news_uid"])
    .filter(F.col("title").isNotNull() & (F.length("title") > 5))
    .withColumn("title_clean", F.trim(F.regexp_replace("title", r"\s+", " ")))
)

# ── Statistiques par source ───────────────────────────────────────────────────
stats_source = (
    df_clean.groupBy("source", "verification_status")
    .agg(F.count("*").alias("count"),
         F.round(F.avg("confidence_score"), 3).alias("avg_confidence"))
    .orderBy("source", "verification_status")
)
stats_source.show(truncate=False)

# ── Statistiques journalières ─────────────────────────────────────────────────
stats_daily = (
    df_clean.filter(F.col("publication_date").isNotNull())
    .withColumn("day", F.to_date("publication_date"))
    .groupBy("day", "verification_status")
    .agg(F.count("*").alias("count"))
    .orderBy("day")
)
stats_daily.show(30, truncate=False)

# ── Écriture HDFS (Parquet) ───────────────────────────────────────────────────
df_clean.write.mode("overwrite") \
    .partitionBy("verification_status") \
    .parquet(f"{HDFS_BASE}/news_clean")

stats_source.write.mode("overwrite").parquet(f"{HDFS_BASE}/stats_source")
stats_daily.write.mode("overwrite").parquet(f"{HDFS_BASE}/stats_daily")

print(f"\n=== Données écrites dans HDFS : {HDFS_BASE} ===")
spark.stop()
