"""Elimina mensajes y sesiones inactivas fuera del periodo de retención definido."""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import settings

cfg = settings()
with psycopg.connect(cfg.database_url) as conn, conn.cursor() as cur:
    cur.execute("DELETE FROM sessions WHERE last_seen_at < now() - (%s * interval '1 day')", (cfg.retention_days,))
    print(f"Sesiones eliminadas: {cur.rowcount}; retención configurada: {cfg.retention_days} días.")
    conn.commit()
