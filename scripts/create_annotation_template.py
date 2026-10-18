"""Crea una plantilla CSV para doble anotación de respaldo documental."""
import argparse
import csv
from pathlib import Path

FIELDS = [
    "id", "question", "answer_claim", "evidence_id", "evidence_text", "source_url",
    "annotator_1", "annotator_2", "adjudicated_label", "notes",
]

parser = argparse.ArgumentParser()
parser.add_argument("--out", type=Path, default=Path("research/annotation_pairs.csv"))
parser.add_argument("--rows", type=int, default=400)
args = parser.parse_args()
args.out.parent.mkdir(parents=True, exist_ok=True)
with args.out.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDS)
    writer.writeheader()
    for index in range(1, args.rows + 1):
        writer.writerow({"id": f"P{index:04d}"})
print(f"Plantilla creada: {args.out}")
