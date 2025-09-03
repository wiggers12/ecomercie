import os
import threading
import logging
from typing import Optional

import requests
from flask import Flask, jsonify, redirect, send_from_directory, url_for

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder="static")

logging.basicConfig(level=logging.INFO)
logger = app.logger

# -------------------------------------------------
# OneSignal (v2)
# Use env vars, com fallback para as suas chaves
# -------------------------------------------------
ONESIGNAL_APP_ID = os.getenv(
    "ONESIGNAL_APP_ID",
    "2525d779-4ba0-490c-9ac7-b117167053f7"
).strip()

ONESIGNAL_API_KEY = os.getenv(
    "ONESIGNAL_API_KEY",
    "os_v2_app_eus5o6klubeqzgwhwelrm4ct65566bcsffnuzqvqsbq3mutv6xslnbka2wxtt6znkniq3tqdmmopgvdalfhsytwltvp3hct7vf2hmiy"
).strip()

ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"  # v2

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _post_onesignal(title: str, message: str, url: Optional[str] = None) -> requests.Response:
    """Envia push para quem tem a tag role=admin (OneSignal v2)."""
    if not ONESIGNAL_APP_ID or not ONESIGNAL_API_KEY:
        class _Mock:
            status_code = 500
            text = "ONESIGNAL_APP_ID/ONESIGNAL_API_KEY ausentes"
            ok = False
        logger.error("OneSignal: variáveis de ambiente ausentes")
        return _Mock()  # type: ignore

    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"pt": title, "en": title},
        "contents": {"pt": message, "en": message},
        "filters": [{"field": "tag", "key": "role", "relation": "=", "value": "admin"}],
    }
    if url:
        payload["url"] = url

    headers = {
        "Authorization": f"Key {ONESIGNAL_API_KEY}",  # v2 usa "Key"
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        r = requests.post(ONESIGNAL_API_URL, headers=headers, json=payload, timeout=15)
        logger.info(f"OneSignal: {r.status_code} {r.text}")
        return r
    except Exception as exc:
        logger.exception("Falha ao chamar OneSignal")
        class _Mock:
            status_code = 500
            text = f"Exception: {exc}"
            ok = False
        return _Mock()  # type: ignore


def notify_admins_async(title: str, message: str, url: Optional[str] = None) -> None:
    threading.Thread(target=_post_onesignal, args=(title, message, url), daemon=True).start()

# -------------------------------------------------
# Rotas
# -------------------------------------------------
@app.get("/")
def home():
    return redirect(url_for("admin"))

@app.get("/admin")
def admin():
    return send_from_directory(TEMPLATES_DIR, "admin.html")

@app.get("/catalogo")
def catalogo():
    # dispara aviso ao abrir o catálogo
    notify_admins_async("Catálogo acessado", "Alguém acabou de abrir o catálogo.")
    return send_from_directory(TEMPLATES_DIR, "catalogo.html")

@app.get("/test-notify")
def test_notify():
    r = _post_onesignal("Teste do servidor", "Push de teste enviado pelo backend.")
    return jsonify({"sent": bool(getattr(r, "ok", False)), "status": getattr(r, "status_code", None), "raw": getattr(r, "text", "")})

# Service Workers do OneSignal na raiz
@app.get("/OneSignalSDKWorker.js")
def onesignal_worker():
    return send_from_directory(STATIC_DIR, "OneSignalSDKWorker.js")

@app.get("/OneSignalSDKUpdaterWorker.js")
def onesignal_updater():
    return send_from_directory(STATIC_DIR, "OneSignalSDKUpdaterWorker.js")

# Manifest/ícones (evita 404)
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

# Dev local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
