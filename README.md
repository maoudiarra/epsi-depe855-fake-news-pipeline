# Projet DEPE855 - Pipeline Big Data

# DEPE855 - Pipeline Big Data de Détection de Fake News

## Objectif

Déployer un pipeline Big Data permettant :

- Collecte automatique de news
- Vérification des informations
- Détection de fake news
- Stockage dans un Data Lake Hadoop
- Analyse pour les équipes BI et Data Science

## Technologies

- Docker
- Apache Kafka
- Apache Spark
- Hadoop HDFS
- PostgreSQL
- Airflow
- Python
- Prometheus
- Grafana
- Power BI

## Architecture

Sources → Kafka → Spark → ML → PostgreSQL
                       ↓
                     HDFS

## Auteur

Maou DIARRA
EPSI - Mastère Expert en Ingénierie des Données