# servidor.py
import os
import threading
import logging
import time
from typing import Optional, Tuple, Dict, Any

import requests
from flask import Flask, jsonify, redirect, send_from_directory, url_for

# -------------------------------------------------
# Paths & App
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder="static")
logging.basicConfig(level=logging.INFO)
logger = app.logger

# -------------------------------------------------
# OneSignal (v2 por padrão)
# -------------------------------------------------
ONESIGNAL_APP_ID = os.getenv(
    "ONESIGNAL_APP_ID",
    "2525d779-4ba0-490c-9ac7-b117167053f7",
).strip()

ONESIGNAL_API_KEY = os.getenv(
    "ONESIGNAL_API_KEY",
    "os_v2_app_eus5o6klubeqzgwhwelrm4ct65566bcsffnuzqvqsbq3mutv6xslnbka2wxtt6znkniq3tqdmmopgvdalfhsytwltvp3hct7vf2hmiy",
).strip()

# endpoint v2
ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"


def _auth_header(key: str) -> Dict[str, str]:
    """
    Se a chave começar com 'os_v2_', usa Authorization: Key ...
    Caso contrário, usa Authorization: Basic ... (legado).
    """
    scheme = "Key" if key.startswith("os_v2_") else "Basic"
    return {"Authorization": f"{scheme} {key}"}


def _mask_key(key: str) -> str:
    if not key:
        return "<empty>"
    if len(key) <= 10:
        return key[:3] + "…"
    return key[:6] + "…" + key[-4:]


# -------------------------------------------------
# Envio com diagnóstico e retry simples
# -------------------------------------------------
def _post_onesignal_payload(
    payload: Dict[str, Any],
    tries: int = 2,
    wait: float = 0.8,
) -> Tuple[bool, int, Dict[str, Any]]:
    """
    Posta o payload para a OneSignal e retorna (ok, status, body_json).
    Faz retry leve para erros transitórios (5xx / conexão).
    """
    if not ONESIGNAL_APP_ID or not ONESIGNAL_API_KEY:
        msg = "ONESIGNAL_APP_ID/ONESIGNAL_API_KEY ausentes"
        logger.error(f"OneSignal: {msg}")
        return False, 500, {"error": msg}

    headers = {
        **_auth_header(ONESIGNAL_API_KEY),
        "Content-Type": "application/json; charset=utf-8",
    }

    attempt = 0
    last_exc = None
    while attempt < tries:
        attempt += 1
        try:
            r = requests.post(
                ONESIGNAL_API_URL, headers=headers, json=payload, timeout=15
            )
            try:
                body = r.json()
            except Exception:
                body = {"raw": r.text}

            recipients = body.get("recipients")
            errors = body.get("errors")
            logger.info(
                f"[OneSignal] try={attempt} status={r.status_code} recipients={recipients} errors={errors}"
            )
            return r.ok, r.status_code, body
        except Exception as exc:
            last_exc = exc
            logger.warning(f"[OneSignal] try={attempt} exception={exc}")
            time.sleep(wait)

    return False, 500, {"error": f"Exception after retries: {last_exc}"})


def notify_admins(
    title: str, message: str, url: Optional[str] = None
) -> Tuple[bool, int, Dict[str, Any]]:
    """Envia push para devices com tag role=admin."""
    payload: Dict[str, Any] = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"pt": title, "en": title},
        "contents": {"pt": message, "en": message},
        "filters": [{"field": "tag", "key": "role", "relation": "=", "value": "admin"}],
    }
    if url:
        payload["url"] = url
    return _post_onesignal_payload(payload)


def notify_all(
    title: str, message: str, url: Optional[str] = None
) -> Tuple[bool, int, Dict[str, Any]]:
    """Diagnóstico: envia para todos os inscritos (ignora tags)."""
    payload: Dict[str, Any] = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"pt": title, "en": title},
        "contents": {"pt": message, "en": message},
        "included_segments": ["Subscribed Users"],
    }
    if url:
        payload["url"] = url
    return _post_onesignal_payload(payload)


def notify_admins_async(title: str, message: str, url: Optional[str] = None) -> None:
    threading.Thread(target=notify_admins, args=(title, message, url), daemon=True).start()


# -------------------------------------------------
# Rotas de páginas
# -------------------------------------------------
@app.get("/")
def home():
    return redirect(url_for("admin"))


@app.get("/admin")
def admin():
    return send_from_directory(TEMPLATES_DIR, "admin.html")


@app.get("/catalogo")
def catalogo():
    # dispara aviso ao abrir o catálogo (para role=admin)
    notify_admins_async("Catálogo acessado", "Alguém acabou de abrir o catálogo.")
    return send_from_directory(TEMPLATES_DIR, "catalogo.html")


# -------------------------------------------------
# Rotas de teste/diagnóstico
# -------------------------------------------------
@app.get("/test-notify")
def test_notify():
    ok, status, body = notify_admins("Teste (admins)", "Push de teste via tag role=admin")
    return jsonify({"ok": ok, "status": status, "onesignal": body})


@app.get("/test-notify-all")
def test_notify_all():
    ok, status, body = notify_all("Teste (todos)", "Push de teste para todos os inscritos")
    return jsonify({"ok": ok, "status": status, "onesignal": body})


@app.get("/debug/onesignal")
def debug_onesignal():
    """Mostra configuração (sem expor a chave por completo)."""
    return jsonify(
        {
            "app_id_set": bool(ONESIGNAL_APP_ID),
            "api_key_prefix": ONESIGNAL_API_KEY[:10] if ONESIGNAL_API_KEY else "",
            "api_key_masked": _mask_key(ONESIGNAL_API_KEY),
            "uses_v2_header": ONESIGNAL_API_KEY.startswith("os_v2_"),
            "api_url": ONESIGNAL_API_URL,
        }
    )


# -------------------------------------------------
# Service Workers / Manifest / Ícones
# -------------------------------------------------
@app.get("/OneSignalSDKWorker.js")
def onesignal_worker():
    return send_from_directory(STATIC_DIR, "OneSignalSDKWorker.js")


@app.get("/OneSignalSDKUpdaterWorker.js")
def onesignal_updater():
    return send_from_directory(STATIC_DIR, "OneSignalSDKUpdaterWorker.js")


@app.get("/manifest.json")
def manifest_root():
    return send_from_directory(STATIC_DIR, "manifest.json")


@app.get("/favicon.ico")
def favicon():
    icon_192 = os.path.join(STATIC_DIR, "icon-192.png")
    if os.path.exists(icon_192):
        return send_from_directory(STATIC_DIR, "icon-192.png")
    return ("", 204)


@app.get("/apple-touch-icon.png")
def apple_touch_icon():
    p = os.path.join(STATIC_DIR, "icon-512.png")
    if os.path.exists(p):
        return send_from_directory(STATIC_DIR, "icon-512.png")
    return ("", 204)


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


# -------------------------------------------------
# Dev local
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
