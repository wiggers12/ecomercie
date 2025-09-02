from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Rota principal -> serve o index.html
@app.get("/")
def serve_index():
    file_path = os.path.join("templates", "index.html")
    return FileResponse(file_path)

