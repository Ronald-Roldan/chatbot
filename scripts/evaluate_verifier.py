"""Calcula métricas reproducibles sobre etiquetas adjudicadas y predicciones."""
import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

LABELS = ["respaldada", "contradicha", "insuficiente"]
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, type=Path)
parser.add_argument("--gold", default="adjudicated_label")
parser.add_argument("--prediction", default="predicted_label")
args = parser.parse_args()
df = pd.read_csv(args.input)
df = df[df[args.gold].isin(LABELS) & df[args.prediction].isin(LABELS)]
if df.empty:
    raise SystemExit("No hay filas válidas con etiqueta adjudicada y predicción.")
print(f"Casos evaluados: {len(df)}")
print(f"Accuracy: {accuracy_score(df[args.gold], df[args.prediction]):.4f}")
print(f"F1 macro: {f1_score(df[args.gold], df[args.prediction], labels=LABELS, average='macro'):.4f}")
print("\nMatriz de confusión (filas=real, columnas=predicción):")
print(pd.DataFrame(confusion_matrix(df[args.gold], df[args.prediction], labels=LABELS), index=LABELS, columns=LABELS))
print("\nReporte por clase:")
print(classification_report(df[args.gold], df[args.prediction], labels=LABELS, zero_division=0))
