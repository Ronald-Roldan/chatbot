"""Ingesta reproducible de planes de trabajo y sus metadatos oficiales."""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import uuid
from pathlib import Path

import fitz
import psycopg
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import settings
from app.ollama import embed

try:
    import pytesseract
except ImportError:  # La dependencia se instala con requirements, pero Tesseract es opcional.
    pytesseract = None


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def page_text(page: fitz.Page) -> str:
    text = normalize(page.get_text("text"))
    if len(text) >= 80:
        return text
    if not pytesseract:
        return ""
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return normalize(pytesseract.image_to_string(image, lang="spa"))


def chunks_from_pdf(path: Path, words_per_chunk: int = 420, overlap: int = 80) -> list[tuple[int, int, str]]:
    pdf = fitz.open(path)
    pages = [(number + 1, page_text(page)) for number, page in enumerate(pdf)]
    units: list[tuple[int, str]] = []
    for page_number, text in pages:
        units.extend((page_number, sentence) for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence)
    result: list[tuple[int, int, str]] = []
    current: list[tuple[int, str]] = []
    count = 0
    for item in units:
        current.append(item)
        count += len(item[1].split())
        if count >= words_per_chunk:
            result.append((current[0][0], current[-1][0], " ".join(sentence for _, sentence in current)))
            retained: list[tuple[int, str]] = []
            retained_words = 0
            for previous in reversed(current):
                retained.insert(0, previous)
                retained_words += len(previous[1].split())
                if retained_words >= overlap:
                    break
            current, count = retained, retained_words
    if current:
        result.append((current[0][0], current[-1][0], " ".join(sentence for _, sentence in current)))
    return result


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


def ingest(row: dict[str, str], raw_dir: Path) -> int:
    required = {"filename", "source_url", "election_year", "dignity", "candidate_name"}
    missing = [key for key in required if not row.get(key)]
    if missing:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(missing)}")
    path = raw_dir / row["filename"]
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    prepared_chunks = chunks_from_pdf(path)
    if not prepared_chunks:
        raise ValueError(f"No se extrajo texto de {path.name}; instale Tesseract y revise el PDF.")
    cfg = settings()
    document_id = uuid.uuid4()
    with psycopg.connect(cfg.database_url) as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM documents WHERE sha256 = %s", (source_hash,))
        if cur.fetchone():
            print(f"Omitido (ya existe): {path.name}")
            return 0
        cur.execute(
            """INSERT INTO documents (id, filename, source_url, election_year, dignity, canton, candidate_name, organization, sha256)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (document_id, row["filename"], row["source_url"], int(row["election_year"]), row["dignity"],
             row.get("canton") or None, row["candidate_name"], row.get("organization") or None, source_hash),
        )
        for index, (start, end, content) in enumerate(prepared_chunks):
            cur.execute(
                """INSERT INTO chunks (id, document_id, page_start, page_end, chunk_index, content, embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s::vector)""",
                (uuid.uuid4(), document_id, start, end, index, content, vector_literal(embed(content))),
            )
        conn.commit()
    return len(prepared_chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    with args.metadata.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    total = sum(ingest(row, args.raw_dir) for row in rows)
    print(f"Ingesta terminada: {total} fragmentos nuevos.")


if __name__ == "__main__":
    main()
