from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Ecomercie", version="1.0.0")

# Garante que a pasta "static" existe
if not os.path.exists("static"):
    os.makedirs("static")

# Monta rota para arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# Rotas principais
# =========================

@app.get("/")
async def home():
    return FileResponse("templates/admin.html")



@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ecomercie", "version": "1.0.0"}

# =========================
# Rotas para OneSignal
# =========================

@app.get("/OneSignalSDKWorker.js")
async def onesignal_worker():
    return FileResponse("static/OneSignalSDKWorker.js")

@app.get("/OneSignalSDKUpdaterWorker.js")
async def onesignal_updater_worker():
    return FileResponse("static/OneSignalSDKUpdaterWorker.js")
