"""Adaptador opcional de WhatsApp Cloud API; requiere variables de Meta en .env."""
from __future__ import annotations

import hashlib
import hmac

import requests

from app.config import settings


def configured() -> bool:
    cfg = settings()
    return bool(cfg.whatsapp_access_token and cfg.whatsapp_phone_number_id)


def send_text(recipient: str, text: str) -> None:
    cfg = settings()
    if not configured():
        raise RuntimeError("WhatsApp Cloud API no está configurada.")
    response = requests.post(
        f"https://graph.facebook.com/v22.0/{cfg.whatsapp_phone_number_id}/messages",
        headers={"Authorization": f"Bearer {cfg.whatsapp_access_token}"},
        json={"messaging_product": "whatsapp", "to": recipient, "type": "text", "text": {"body": text}},
        timeout=30,
    )
    response.raise_for_status()


def valid_signature(body: bytes, signature: str | None) -> bool:
    secret = settings().whatsapp_app_secret
    if not secret or not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature.removeprefix("sha256="), expected)


def pseudonymous_session(sender: str) -> str:
    digest = hashlib.sha256((settings().session_secret + sender).encode()).hexdigest()
    return f"{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}"
