"""
train_model.py - Entraînement du modèle de détection de fake news - DEPE855
Sauvegarde le modèle dans ml/model.pkl (exclu du Git via .gitignore).
"""

import os
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

SAMPLES = [
    ("La BCE maintient ses taux directeurs inchangés", "verified"),
    ("L'inflation recule à 2,3% en zone euro", "verified"),
    ("Le CAC 40 progresse de 1,2% à l'ouverture", "verified"),
    ("Tesla annonce des bénéfices records au T3", "verified"),
    ("La Fed relève ses taux d'un quart de point", "verified"),
    ("Apple présente l'iPhone 16 lors de sa keynote annuelle", "verified"),
    ("BNP Paribas rachète une filiale de Deutsche Bank", "verified"),
    ("Le chômage tombe à 7,1% en France au premier trimestre", "verified"),
    ("L'or franchit les 2 400 dollars l'once", "verified"),
    ("Airbus livre un nombre record d'A320 en 2024", "verified"),
    ("La Chine injecte 500 milliards de yuans pour soutenir sa croissance", "verified"),
    ("La Bourse de Paris clôture en hausse malgré les tensions géopolitiques", "verified"),
    ("Le gouvernement va supprimer toutes les retraites dès janvier", "fake"),
    ("Les vaccins contiennent des puces 5G selon des experts", "fake"),
    ("Emmanuel Macron démissionne ce soir en direct", "fake"),
    ("L'eau du robinet provoque le cancer selon une étude secrète", "fake"),
    ("Les banques vont fermer tous leurs comptes la semaine prochaine", "fake"),
    ("Bitcoin va atteindre 10 millions de dollars selon Elon Musk", "fake"),
    ("La France va rejoindre la Russie selon des sources internes", "fake"),
    ("Le Gorafi révèle que les élections sont annulées", "fake"),
    ("Un astéroïde va frapper Paris vendredi selon la NASA", "fake"),
    ("Tous les Français recevront 1000€ ce mois-ci", "fake"),
]

df = pd.DataFrame(SAMPLES, columns=["text", "label"])
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)),
    ("clf",   LogisticRegression(max_iter=500, C=1.0, random_state=42)),
])
pipeline.fit(X_train, y_train)

print("=== Rapport de classification ===")
print(classification_report(y_test, pipeline.predict(X_test)))

model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(pipeline, f)
print(f"Modèle sauvegardé : {model_path}")
