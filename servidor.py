# servidor.py - VERSÃO FINAL COM CHAT + CÓDIGO ORIGINAL INTACTO E AJUSTADO

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth, messaging
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid

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
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='')


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


# --- Notificações ---
@app.route("/api/notify_visit", methods=["POST"])
def notify_visit():
    try:
        data = request.json
        owner_id = data.get("ownerId")
        session_id = data.get("sessionId") or str(uuid.uuid4())

        db.collection("sessions").document(session_id).set({
            "owner_uid": owner_id,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_message": "Novo visitante entrou no catálogo",
            "updated_at": firestore.SERVER_TIMESTAMP
        }, merge=True)

        db.collection("visits").add({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "owner_uid": owner_id or "unknown",
            "session_id": session_id
        })

        return jsonify({"success": True, "session_id": session_id}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --- CHAT ---
@app.route("/api/sessions", methods=["GET"])
@check_token
def get_sessions(user_uid):
    try:
        sessions_ref = db.collection("sessions").where(
            filter=FieldFilter("owner_uid", "==", user_uid)
        ).stream()
        sessions = [s.to_dict() | {"id": s.id} for s in sessions_ref]
        return jsonify(sessions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_messages/<session_id>", methods=["GET"])
@check_token
def get_messages(user_uid, session_id):
    try:
        msgs_ref = db.collection("sessions").document(session_id).collection("messages")\
            .order_by("timestamp", direction=firestore.Query.ASCENDING).stream()
        messages = [m.to_dict() | {"id": m.id} for m in msgs_ref]
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_messages", methods=["GET"])
def get_messages_public():
    try:
        session_id = request.args.get("sessionId")
        if not session_id:
            return jsonify({"error": "sessionId obrigatório"}), 400
        msgs_ref = db.collection("sessions").document(session_id).collection("messages")\
            .order_by("timestamp", direction=firestore.Query.ASCENDING).stream()
        messages = [m.to_dict() | {"id": m.id} for m in msgs_ref]
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/send_message", methods=["POST"])
def send_message():
    try:
        data = request.json
        session_id = data.get("session_id") or data.get("sessionId")
        sender = data.get("sender") or data.get("from", "user")
        text = data.get("text")

        if not session_id or not text:
            return jsonify({"error": "Dados incompletos"}), 400

        db.collection("sessions").document(session_id).collection("messages").add({
            "sender": sender,
            "text": text,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        db.collection("sessions").document(session_id).update({
            "last_message": text,
            "updated_at": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- ROTAS DE STATIC ---
@app.route('/manifest.json')
def manifest():
    return send_from_directory("static", "manifest.json")

@app.route("/icon-192.png")
def icon_192():
    return send_from_directory("static", "icon-192.png")

@app.route("/icon-512.png")
def icon_512():
    return send_from_directory("static", "icon-512.png")

@app.route("/firebase-messaging-sw.js")
def sw():
    return send_from_directory("static", "firebase-messaging-sw.js", mimetype="application/javascript")


# --- Inicialização ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[DEBUG] Flask rodando na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=True)