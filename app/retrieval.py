from __future__ import annotations

from dataclasses import dataclass

import psycopg

from app.config import settings
from app.ollama import embed


@dataclass
class Evidence:
    content: str
    page_start: int
    page_end: int
    source_url: str
    filename: str
    candidate_name: str
    dignity: str
    canton: str | None
    score: float


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


def retrieve(question: str, dignity: str | None = None, canton: str | None = None) -> list[Evidence]:
    cfg = settings()
    query_vector = _vector_literal(embed(question))
    filters: list[str] = []
    params: list[object] = [query_vector, question]
    if dignity:
        filters.append("d.dignity = %s")
        params.append(dignity)
    if canton:
        filters.append("d.canton = %s")
        params.append(canton)
    where = " AND ".join(filters) if filters else "TRUE"
    params.append(cfg.top_k)
    sql = f"""
        WITH ranked AS (
          SELECT c.content, c.page_start, c.page_end, d.source_url, d.filename,
                 d.candidate_name, d.dignity, d.canton,
                 (1 - (c.embedding <=> %s::vector)) AS semantic_score,
                 ts_rank_cd(to_tsvector('spanish', c.content), websearch_to_tsquery('spanish', %s)) AS lexical_score
          FROM chunks c JOIN documents d ON d.id = c.document_id
          WHERE {where}
        )
        SELECT *, (0.75 * semantic_score + 0.25 * lexical_score) AS score
        FROM ranked
        ORDER BY score DESC
        LIMIT %s
    """
    with psycopg.connect(cfg.database_url) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return [Evidence(*row) for row in cur.fetchall()]
