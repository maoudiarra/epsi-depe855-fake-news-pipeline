"""
config.py - Configuration centralisée DEPE855
Toutes les variables sensibles sont lues depuis le fichier .env
"""

import os
from dotenv import load_dotenv

# Charge le fichier .env situé à la racine du projet
load_dotenv()


def _require(key: str) -> str:
    """Récupère une variable d'environnement obligatoire."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Variable d'environnement manquante : '{key}'\n"
            "Vérifiez votre fichier .env (copiez .env.example en .env)."
        )
    return value


# ── PostgreSQL ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     _require("POSTGRES_HOST"),
    "port":     int(_require("POSTGRES_PORT")),
    "dbname":   _require("POSTGRES_DB"),
    "user":     _require("POSTGRES_USER"),
    "password": _require("POSTGRES_PASSWORD"),
}

# ── Kafka ─────────────────────────────────────────────────────────────────────
KAFKA_BOOTSTRAP = _require("KAFKA_BOOTSTRAP")
KAFKA_TOPIC     = _require("KAFKA_TOPIC")
