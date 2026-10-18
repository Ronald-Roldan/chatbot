from __future__ import annotations

import requests

from app.config import settings


class OllamaUnavailable(RuntimeError):
    pass


def embed(text: str) -> list[float]:
    cfg = settings()
    try:
        response = requests.post(
            f"{cfg.ollama_base_url}/api/embed",
            json={"model": cfg.embedding_model, "input": text},
            timeout=120,
        )
        response.raise_for_status()
        vector = response.json()["embeddings"][0]
    except (requests.RequestException, KeyError, IndexError) as exc:
        raise OllamaUnavailable("Ollama no está disponible o falta el modelo de embeddings.") from exc
    if len(vector) != 768:
        raise OllamaUnavailable("El modelo de embeddings debe producir vectores de 768 dimensiones.")
    return vector


def chat(system: str, user: str) -> str:
    cfg = settings()
    try:
        response = requests.post(
            f"{cfg.ollama_base_url}/api/chat",
            json={
                "model": cfg.generation_model,
                "stream": False,
                "options": {"temperature": 0},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except (requests.RequestException, KeyError) as exc:
        raise OllamaUnavailable("Ollama no está disponible o falta el modelo generativo.") from exc
