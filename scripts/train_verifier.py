"""Entrena el clasificador propio de respaldo documental con datos adjudicados."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

LABELS = {"respaldada", "contradicha", "insuficiente"}


def joined(frame: pd.DataFrame) -> pd.Series:
    return "AFIRMACIÓN: " + frame["answer_claim"].fillna("") + " EVIDENCIA: " + frame["evidence_text"].fillna("")


parser = argparse.ArgumentParser(description="Entrena y evalúa un clasificador TF-IDF + regresión logística.")
parser.add_argument("--input", required=True, type=Path)
parser.add_argument("--out", default=Path("models/verifier.joblib"), type=Path)
parser.add_argument("--label-column", default="adjudicated_label")
args = parser.parse_args()

df = pd.read_csv(args.input)
df = df[df[args.label_column].isin(LABELS)].copy()
if len(df) < 90:
    raise SystemExit("Se requieren al menos 90 pares adjudicados, con representación de las tres clases.")
if df[args.label_column].nunique() != 3:
    raise SystemExit("El conjunto debe contener respaldada, contradicha e insuficiente.")
x_train, x_test, y_train, y_test = train_test_split(
    joined(df), df[args.label_column], test_size=0.20, random_state=42, stratify=df[args.label_column]
)
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True, max_features=30000)),
    ("classifier", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42)),
])
pipeline.fit(x_train, y_train)
prediction = pipeline.predict(x_test)
print(f"Pares: {len(df)} | entrenamiento: {len(x_train)} | prueba: {len(x_test)}")
print(f"F1 macro de prueba: {f1_score(y_test, prediction, average='macro'):.4f}")
print(classification_report(y_test, prediction, digits=4))
args.out.parent.mkdir(parents=True, exist_ok=True)
joblib.dump({"pipeline": pipeline, "labels": sorted(LABELS), "training_rows": len(x_train)}, args.out)
print(f"Modelo guardado en: {args.out}")
