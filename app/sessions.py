from __future__ import annotations

import uuid

import psycopg

from app.config import settings


def ensure_session(session_id: str | None, channel: str) -> str:
    """Crea o renueva una sesión anónima; no almacena identidad de la persona."""
    try:
        parsed = uuid.UUID(session_id) if session_id else uuid.uuid4()
    except ValueError:
        parsed = uuid.uuid4()
    with psycopg.connect(settings().database_url) as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO sessions (id, channel) VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET last_seen_at = now()""",
            (parsed, channel),
        )
        conn.commit()
    return str(parsed)


def save_message(session_id: str, role: str, content: str) -> None:
    with psycopg.connect(settings().database_url) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO messages (id, session_id, role, content) VALUES (%s, %s, %s, %s)",
            (uuid.uuid4(), uuid.UUID(session_id), role, content),
        )
        conn.commit()
