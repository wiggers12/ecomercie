import os
import threading
import logging
from typing import Optional

import requests
from flask import Flask, jsonify, redirect, send_from_directory, url_for

# -------------------------------------------------
# Configuração básica
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder="static")

# Log mais verboso no Render
logging.basicConfig(level=logging.INFO)
logger = app.logger

# OneSignal (v2)
ONESIGNAL_APP_ID = os.getenv("2525d779-4ba0-490c-9ac7-b117167053f7").strip()
ONESIGNAL_API_KEY = os.getenv("os_v2_app_eus5o6klubeqzgwhwelrm4ct65566bcsffnuzqvqsbq3mutv6xslnbka2wxtt6znkniq3tqdmmopgvdalfhsytwltvp3hct7vf2hmiy", "").strip()

ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _post_onesignal(title: str, message: str, url: Optional[str] = None) -> requests.Response:
    """
    Envia push para devices com tag role=admin.
    Usa OneSignal API v2 (Authorization: Key <os_v2_...>).
    """
    if not ONESIGNAL_APP_ID or not ONESIGNAL_API_KEY:
        # Não quebre a requisição; apenas logue e devolva um "mock" de 500
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
        # Envia apenas para quem tiver a tag role=admin
        "filters": [{"field": "tag", "key": "role", "relation": "=", "value": "admin"}],
    }
    if url:
        payload["url"] = url

    headers = {
        # v2
        "Authorization": f"Key {ONESIGNAL_API_KEY}",
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        r = requests.post(ONESIGNAL_API_URL, headers=headers, json=payload, timeout=15)
        logger.info(f"OneSignal: {r.status_code} {r.text}")
        return r
    except Exception as exc:
        class _Mock:
            status_code = 500
            text = f"Exception: {exc}"
            ok = False
        logger.exception("Falha ao chamar OneSignal")
        return _Mock()  # type: ignore


def notify_admins_async(title: str, message: str, url: Optional[str] = None) -> None:
    """Dispara o push em background para não travar a resposta http."""
    threading.Thread(target=_post_onesignal, args=(title, message, url), daemon=True).start()


# -------------------------------------------------
# Rotas de páginas
# -------------------------------------------------
@app.get("/")
def home():
    # Atalho: entra direto no painel do admin
    return redirect(url_for("admin"))

@app.get("/admin")
def admin():
    return send_from_directory(TEMPLATES_DIR, "admin.html")

@app.get("/catalogo")
def catalogo():
    # Renderiza o catálogo e dispara aviso para admins
    notify_admins_async("Catálogo acessado", "Alguém acabou de abrir o catálogo.", url=None)
    return send_from_directory(TEMPLATES_DIR, "catalogo.html")


# -------------------------------------------------
# Teste de envio (servidor -> OneSignal)
# -------------------------------------------------
@app.get("/test-notify")
def test_notify():
    r = _post_onesignal("Teste do servidor", "Push de teste enviado pelo backend.")
    return jsonify({"sent": bool(getattr(r, "ok", False)), "status": getattr(r, "status_code", None)})


# -------------------------------------------------
# Service Workers do OneSignal na RAIZ
# (o SDK web procura exatamente nessas URLs)
# -------------------------------------------------
@app.get("/OneSignalSDKWorker.js")
def onesignal_worker():
    return send_from_directory(STATIC_DIR, "OneSignalSDKWorker.js")

@app.get("/OneSignalSDKUpdaterWorker.js")
def onesignal_updater():
    return send_from_directory(STATIC_DIR, "OneSignalSDKUpdaterWorker.js")


# -------------------------------------------------
# Manifest e favicon (evita 404 nos logs)
# -------------------------------------------------
@app.get("/manifest.json")
def manifest_root():
    # Se o teu HTML aponta para /static/manifest.json, esta rota é opcional.
    return send_from_directory(STATIC_DIR, "manifest.json")

@app.get("/favicon.ico")
def favicon():
    # Usa o ícone 192 como fallback
    icon_192 = os.path.join(STATIC_DIR, "icon-192.png")
    if os.path.exists(icon_192):
        return send_from_directory(STATIC_DIR, "icon-192.png")
    # Sem ícone? retorna 204 para não poluir logs
    return ("", 204)


# -------------------------------------------------
# Saúde / ping
# -------------------------------------------------
@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


# -------------------------------------------------
# Execução local
# -------------------------------------------------
if __name__ == "__main__":
    # Para desenvolvimento local
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)