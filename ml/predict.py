"""
predict.py - Module de prédiction fake news - DEPE855
"""

import os
import pickle

_model = None
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                f"Modèle introuvable : {_MODEL_PATH}\n"
                "Lancez d'abord : python ml/train_model.py"
            )
        with open(_MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


def predict_fake_news(title: str, summary: str = "") -> tuple[str, float]:
    """
    Retourne (label, confidence_score)
    label ∈ {'verified', 'fake', 'pending'}
    """
    model = _load_model()
    text  = f"{title} {summary}".strip()
    if not text:
        return "pending", 0.5

    proba     = model.predict_proba([text])[0]
    label_idx = proba.argmax()
    label     = model.classes_[label_idx]
    score     = round(float(proba[label_idx]), 4)

    # Trop incertain → on laisse en attente de vérification manuelle
    if score < 0.65:
        return "pending", score

    return label, score
