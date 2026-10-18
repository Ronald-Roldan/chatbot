from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import joblib

from app.config import settings
from app.ollama import OllamaUnavailable, chat
from app.retrieval import Evidence

ALLOWED = {"respaldada", "contradicha", "insuficiente"}


@lru_cache
def _trained_model():
    path = Path(settings().verifier_model_path)
    return joblib.load(path)["pipeline"] if path.exists() else None


def _model_verify(answer: str, evidence: list[Evidence]) -> tuple[str, str] | None:
    model = _trained_model()
    if model is None:
        return None
    text = "AFIRMACIÓN: " + answer + " EVIDENCIA: " + " ".join(item.content for item in evidence)
    probabilities = model.predict_proba([text])[0]
    index = int(probabilities.argmax())
    label, confidence = str(model.classes_[index]), float(probabilities[index])
    if confidence < settings().verification_threshold:
        return "insuficiente", f"El clasificador propio no alcanzó el umbral de confianza ({confidence:.2f})."
    return label, f"Clasificador propio: {label} con confianza {confidence:.2f}."


def verify(answer: str, evidence: list[Evidence]) -> tuple[str, str]:
    trained = _model_verify(answer, evidence)
    if trained is not None:
        return trained
    context = "\n\n".join(f"E{i + 1}: {item.content}" for i, item in enumerate(evidence))
    system = (
        "Eres un evaluador de respaldo documental. Solo usas la evidencia entregada. "
        "Clasifica la afirmación como respaldada, contradicha o insuficiente. "
        "Devuelve JSON válido con las claves etiqueta y razon."
    )
    user = f"AFIRMACIÓN:\n{answer}\n\nEVIDENCIA:\n{context}"
    try:
        raw = chat(system, user)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        parsed = json.loads(match.group(0) if match else raw)
        label = str(parsed.get("etiqueta", "insuficiente")).lower().strip()
        if label not in ALLOWED:
            label = "insuficiente"
        return label, str(parsed.get("razon", "No se obtuvo una justificación válida."))
    except (OllamaUnavailable, json.JSONDecodeError):
        return "insuficiente", "Veredicto no disponible: revise el modelo local y etiquete este caso manualmente."
