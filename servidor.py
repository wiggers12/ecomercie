from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Cria app FastAPI
app = FastAPI()

# Garante que a pasta "static" existe
if not os.path.exists("static"):
    os.makedirs("static")

# Monta rota para servir arquivos estáticos (css, js, imagens)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota principal -> carrega index.html
@app.get("/")
async def serve_index():
    file_path = os.path.join("templates", "index.html")
    return FileResponse(file_path)

# Rota de saúde -> Render usa para checar se o servidor está ok
@app.get("/health")
async def health_check():
    return {"status": "ok"}
