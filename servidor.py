# servidor.py
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import requests
import os

# =========================
# CONFIG
# =========================
ONESIGNAL_APP_ID  = "2525d779-4ba0-490c-9ac7-b117167053f7"  # seu App ID
ONESIGNAL_API_KEY = "ZGY2YmE2NjItMzEyZi00OTMwLTk4ZTUtMTkxNTdlMzI4ZjYx"  # sua REST API Key

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ecomercie")

app = FastAPI(title="Ecomercie", version="1.0.0")

# Garante pasta static
os.makedirs("static", exist_ok=True)

# Servir /static/*
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# PÁGINAS
# =========================
@app.get("/")
async def home():
    """
    Home -> abre admin por padrão (caso você ainda não tenha index.html)
    """
    index = "templates/index.html"
    return FileResponse(index) if os.path.exists(index) else FileResponse("templates/admin.html")

@app.get("/admin")
async def admin():
    return FileResponse("templates/admin.html")

@app.get("/catalogo")
async def catalogo():
    """
    Sempre que o catálogo for acessado, enviamos uma notificação ao ADMIN (tag role=admin).
    """
    send_admin_notification()
    return FileResponse("templates/catalogo.html")

# =========================
# ONESIGNAL SERVICE WORKERS NA RAIZ
# (o OneSignal busca esses caminhos diretamente na /)
# =========================
@app.get("/OneSignalSDKWorker.js")
async def onesignal_worker():
    return FileResponse("static/OneSignalSDKWorker.js")

@app.get("/OneSignalSDKUpdaterWorker.js")
async def onesignal_updater_worker():
    return FileResponse("static/OneSignalSDKUpdaterWorker.js")

# =========================
# HEALTH & TEST
# =========================
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ecomercie", "version": "1.0.0"}

@app.get("/test-notify")
def test_notify():
    ok = send_admin_notification()
    return JSONResponse({"sent": ok})

# =========================
# FUNÇÃO DE NOTIFICAÇÃO
# =========================
def send_admin_notification() -> bool:
    """
    Envia push para quem tiver a TAG role=admin no OneSignal.
    Retorna True se a API aceitou o envio.
    """
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        # Somente ADMIN:
        "filters": [
            {"field": "tag", "key": "role", "relation": "=", "value": "admin"}
        ],
        "headings": {"en": "Novo acesso ao catálogo"},
        "contents": {"en": "Alguém acabou de abrir o catálogo do Ecomercie."},
        # Ao clicar, abrir o admin
        "url": "https://ecomercie.onrender.com/admin",
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        log.info("OneSignal response %s: %s", r.status_code, r.text)
        return r.ok
    except Exception as e:
        log.exception("Erro ao enviar notificação OneSignal: %s", e)
        return False