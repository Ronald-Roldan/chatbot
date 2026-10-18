"""Comprueba que PostgreSQL local esté listo antes de ejecutar la ingesta."""
import sys
import time
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import settings

for attempt in range(30):
    try:
        with psycopg.connect(settings().database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        print("Base de datos lista.")
        raise SystemExit(0)
    except psycopg.OperationalError:
        print(f"Esperando PostgreSQL ({attempt + 1}/30)...")
        time.sleep(2)
raise SystemExit("PostgreSQL no respondió. Compruebe: docker compose ps")
