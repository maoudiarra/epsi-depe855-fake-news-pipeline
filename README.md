# DEPE855 - Pipeline Big Data de Détection de Fake News

## Objectif

Déployer un pipeline Big Data permettant :
- Collecte automatique de news (AFP, Le Monde, Gorafi)
- Détection de fake news via Machine Learning
- Stockage structuré dans PostgreSQL
- Retraitement batch toutes les 6 heures via Airflow
- Analyse pour les équipes BI et Data Science

## Architecture

```
AFP / Le Monde / Gorafi
        ↓
   [producer.py]  ← scraping
        ↓
      Kafka
        ↓
   [consumer.py]  ← ML predict
        ↓
    PostgreSQL
        ↓
   [spark_job.py] ← batch
        ↓
      HDFS
```

## Installation

### 1. Configurer l'environnement

```bash
cp .env.example .env
# Editez .env avec vos valeurs
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Démarrer l'infrastructure Docker

```bash
docker compose up -d
```

### 4. Entraîner le modèle ML

```bash
python ml/train_model.py
```

### 5. Lancer le pipeline

```bash
# Terminal 1 - Producer (scraping toutes les 6h)
python kafka/producer.py

# Terminal 2 - Consumer (traitement temps réel)
python kafka/consumer.py
```

### 6. Vérifier les données

```bash
python postgres/count_news.py
python postgres/read_news.py
```

## Structure du projet

```
EID_DEPE855_PIPELINE/
├── .env.example          # Template de configuration (à copier en .env)
├── .gitignore
├── config.py             # Config centralisée (lit le .env)
├── compose.yml           # Docker Compose (Kafka + PostgreSQL)
├── requirements.txt
├── kafka/
│   ├── producer.py       # Scraping → Kafka
│   └── consumer.py       # Kafka → ML → PostgreSQL
├── ml/
│   ├── train_model.py    # Entraînement TF-IDF + LogisticRegression
│   └── predict.py        # Prédiction fake/verified
├── scraper/
│   ├── afp_scraper.py
│   ├── lemonde_scraper.py
│   └── gorafi_scraper.py
├── spark/
│   └── spark_job.py      # Retraitement batch → HDFS Parquet
├── airflow/
│   └── dags/
│       └── pipeline_dag.py  # Orchestration toutes les 6h
└── postgres/
    ├── initdb/
    │   └── 01_create_tables.sql
    ├── init_database.py
    ├── insert_sample_news.py
    ├── read_news.py
    └── count_news.py
```

## Sécurité

- Les credentials ne sont **jamais** écrits dans le code
- Toutes les variables sensibles passent par le fichier `.env`
- Le fichier `.env` est exclu du Git via `.gitignore`
- Partagez uniquement `.env.example` avec votre équipe

## Auteur

Maou DIARRA — EPSI Mastère Expert en Ingénierie des Données
