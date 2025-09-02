from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import requests

app = FastAPI(title="Ecomercie", version="1.0.0")

# Monta rota para arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# Páginas
# =========================

@app.get("/admin")
async def admin():
    return FileResponse("templates/admin.html")

@app.get("/catalogo")
async def catalogo():
    # Dispara notificação sempre que o catálogo for acessado
    send_admin_notification()
    return FileResponse("templates/catalogo.html")

# =========================
# Notificação via OneSignal
# =========================
ONESIGNAL_APP_ID = "2525d779-4ba0-490c-9ac7-b117167053f7"
ONESIGNAL_API_KEY = "ZGY2YmE2NjItMzEyZi00OTMwLTk4ZTUtMTkxNTdlMzI4ZjYx"

def send_admin_notification():
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["Subscribed Users"],  # envia a todos os inscritos
        "headings": {"en": "Novo acesso ao catálogo"},
        "contents": {"en": "Um usuário acabou de abrir o catálogo 🚀"}
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        print("Resposta OneSignal:", r.status_code, r.json())
    except Exception as e:
        print("Erro ao enviar notificação:", e)

# =========================
# Healthcheck
# =========================
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ecomercie", "version": "1.0.0"}