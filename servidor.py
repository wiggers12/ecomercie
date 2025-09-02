# servidor.py - VERSÃO CORRIGIDA E LIMPA (OneSignal + Produtos + Sessions/Chat + Firebase SW)

import os
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1.base_query import FieldFilter

print(">>> [DEBUG] servidor.py carregando <<<")

# --- Inicialização do Firebase ---
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("credentials.json")
        firebase_admin.initialize_app(cred)
    print(">>> [DEBUG] Firebase conectado com sucesso! <<<")
except Exception as e:
    print(f">>> ERRO: Falha ao inicializar Firebase: {e}")
    exit()

db = firestore.client()
app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="")

# OneSignal config
ONESIGNAL_APP_ID = "2525d779-4ba0-490c-9ac7-b117167053f7"
ONESIGNAL_API_KEY = "ZGY2YmE2NjItMzEyZi00OTMwLTk4ZTUtMTkxNTdlMzI4ZjYx"  # REST API KEY do OneSignal


# --- Decorador de autenticação ---
def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get("Authorization"):
            return jsonify({"message": "Nenhum token fornecido"}), 401
        try:
            id_token = request.headers["Authorization"].split("Bearer ")[1]
            decoded_token = auth.verify_id_token(id_token)
            kwargs["user_uid"] = decoded_token["uid"]
        except Exception as e:
            print(f"[ERRO] Token inválido: {e}")
            return jsonify({"message": "Token inválido ou expirado"}), 401
        return f(*args, **kwargs)
    return wrap


# --- Rotas HTML ---
@app.route("/")
def index_page():
    return "<h1>Servidor do Catálogo no Ar!</h1><p>Acesse /admin para gerenciar ou /catalogo/ID_DO_LOJISTA para ver um catálogo.</p>"

@app.route("/catalogo/<owner_id>")
def catalogo_page(owner_id):
    return render_template("catalogo.html", owner_id=owner_id)

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")


# --- API Produtos ---
@app.route("/api/catalog_data/<owner_id>", methods=["GET"])
def get_catalog_data(owner_id):
    try:
        products_ref = db.collection("products").where(
            filter=FieldFilter("owner_uid", "==", owner_id)
        ).stream()
        products_list = [p.to_dict() | {"id": p.id} for p in products_ref]
        return jsonify({"products": products_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/my_products", methods=["GET"])
@check_token
def get_my_products(user_uid):
    try:
        products_ref = db.collection("products").where(
            filter=FieldFilter("owner_uid", "==", user_uid)
        ).stream()
        products_list = [p.to_dict() | {"id": p.id} for p in products_ref]
        return jsonify(products_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<product_id>", methods=["GET"])
def get_product(product_id):
    try:
        doc = db.collection("products").document(product_id).get()
        if doc.exists:
            return jsonify(doc.to_dict() | {"id": doc.id})
        return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products", methods=["POST"])
@check_token
def add_product(user_uid):
    try:
        novo_produto = request.json
        novo_produto["owner_uid"] = user_uid
        _, ref = db.collection("products").add(novo_produto)
        novo_produto["id"] = ref.id
        return jsonify(novo_produto), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<product_id>", methods=["PUT"])
@check_token
def update_product(user_uid, product_id):
    try:
        doc_ref = db.collection("products").document(product_id)
        doc = doc_ref.get()
        if not doc.exists or doc.to_dict().get("owner_uid") != user_uid:
            return jsonify({"error": "Permissão negada"}), 403
        updates = request.json
        doc_ref.update(updates)
        return jsonify(doc_ref.get().to_dict() | {"id": product_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<product_id>", methods=["DELETE"])
@check_token
def delete_product(user_uid, product_id):
    try:
        doc_ref = db.collection("products").document(product_id)
        doc = doc_ref.get()
        if not doc.exists or doc.to_dict().get("owner_uid") != user_uid:
            return jsonify({"error": "Permissão negada"}), 403
        doc_ref.delete()
        return jsonify({"message": "Produto excluído"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Salvar Token FCM ---
@app.route("/api/save_token", methods=["POST"])
@check_token
def save_token(user_uid):
    try:
        data = request.json
        token = data.get("token")
        if not token:
            return jsonify({"error": "Token inválido"}), 400

        # Salva ou atualiza o token no Firestore
        db.collection("fcm_tokens").document(user_uid).set(
            {"token": token}, merge=True
        )

        print(f"[DEBUG] Token salvo para {user_uid}: {token}")
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Notificações (OneSignal) ---
@app.route("/api/notify_visit", methods=["POST"])
def notify_visit():
    try:
        data = request.json
        owner_id = data.get("ownerId")

        # salva visita
        db.collection("visits").add(
            {"timestamp": firestore.SERVER_TIMESTAMP, "owner_uid": owner_id or "unknown"}
        )

        # envia notificação via OneSignal
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {ONESIGNAL_API_KEY}",
        }
        payload = {
            "app_id": ONESIGNAL_APP_ID,
            "included_segments": ["All"],
            "headings": {"en": "Nova visita 🚀"},
            "contents": {"en": "Alguém acabou de abrir seu catálogo!"},
        }

        r = requests.post(
            "https://onesignal.com/api/v1/notifications", headers=headers, json=payload
        )
        print("OneSignal response:", r.json())

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --- Static ---
@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")

@app.route("/icon-192.png")
def icon_192():
    return send_from_directory("static", "icon-192.png")

@app.route("/icon-512.png")
def icon_512():
    return send_from_directory("static", "icon-512.png")

# --- Firebase Messaging SW (para FCM funcionar) ---
@app.route("/firebase-messaging-sw.js")
def firebase_sw():
    return send_from_directory("static", "firebase-messaging-sw.js", mimetype="application/javascript")

# --- OneSignal Service Workers ---
@app.route("/OneSignalSDKWorker.js")
def onesignal_worker():
    return send_from_directory("static", "OneSignalSDKWorker.js")

@app.route("/OneSignalSDKUpdaterWorker.js")
def onesignal_updater():
    return send_from_directory("static", "OneSignalSDKUpdaterWorker.js")


# --- Inicialização ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"--- [DEBUG] Iniciando servidor Flask na porta {port} ---")
    app.run(host="0.0.0.0", port=port, debug=True)
