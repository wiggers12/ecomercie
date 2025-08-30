# servidor.py - VERSÃO DE DEPURAÇÃO FUNCIONAL

import os
from flask import Flask, render_template, request, jsonify
from functools import wraps
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth, messaging
from google.cloud.firestore_v1.base_query import FieldFilter

print(">>> [DEBUG] MÓDULO app.py SENDO CARREGADO <<<")

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("credentials.json") 
        firebase_admin.initialize_app(cred)
    print(">>> [DEBUG] Firebase conectado com sucesso!")
except Exception as e:
    print(f">>> !!! ERRO CRÍTICO: Não foi possível conectar ao Firebase. {e} !!! <<<")
    exit()

db = firestore.client()
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='')
print(">>> [DEBUG] Aplicação Flask inicializada <<<")

# --- DECORATOR DE AUTENTICAÇÃO ---
def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('Authorization'): return jsonify({'message': 'Nenhum token fornecido'}), 401
        try:
            id_token = request.headers['Authorization'].split('Bearer ')[1]
            decoded_token = auth.verify_id_token(id_token)
            kwargs['user_uid'] = decoded_token['uid']
        except Exception as e:
            print(f"!!! Erro de autenticação: {e} !!!")
            return jsonify({'message': 'Token inválido ou expirado'}), 401
        return f(*args, **kwargs)
    return wrap

# --- ROTAS HTML ---
@app.route('/')
def index_page():
    return "<h1>Servidor do Catálogo no Ar!</h1><p>Acesse /admin para gerenciar ou /catalogo/ID_DO_LOJISTA para ver um catálogo.</p>"

@app.route('/catalogo/<owner_id>')
def catalogo_page(owner_id): 
    return render_template('catalogo.html', owner_id=owner_id)

@app.route('/login')
def login_page(): return render_template('login.html')

@app.route('/admin')
def admin_page(): return render_template('admin.html')

# --- API ---
@app.route('/api/catalog_data/<owner_id>', methods=['GET'])
def get_catalog_data(owner_id):
    try:
        products_ref = db.collection('products').where(filter=FieldFilter('owner_uid', '==', owner_id)).stream()
        products_list = [p.to_dict() | {'id': p.id} for p in products_ref]
        return jsonify({"products": products_list})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/my_products', methods=['GET'])
@check_token
def get_my_products(user_uid):
    try:
        products_ref = db.collection('products').where(filter=FieldFilter('owner_uid', '==', user_uid)).stream()
        products_list = [p.to_dict() | {'id': p.id} for p in products_ref]
        return jsonify(products_list)
    except Exception as e: return jsonify({"error": str(e)}), 500

# <<< ROTA PROBLEMÁTICA AGORA COM ESPIÕES >>>
@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    print(f"\n--- [DEBUG] Rota GET /api/products/<id> foi chamada ---")
    print(f"    -> Tentando buscar produto com ID recebido: '{product_id}'")
    try:
        doc = db.collection('products').document(product_id).get()
        if doc.exists:
            print(f"    -> SUCESSO: Produto '{doc.to_dict().get('nome')}' encontrado no Firestore!")
            return jsonify(doc.to_dict() | {'id': doc.id})
        else:
            print(f"    -> FALHA: Produto com ID '{product_id}' NÃO foi encontrado no Firestore.")
            return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e: 
        print(f"    -> !!! ERRO em get_product: {e} !!!")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['POST'])
@check_token
def add_product(user_uid):
    try:
        novo_produto = request.json
        novo_produto['owner_uid'] = user_uid 
        _, document_ref = db.collection('products').add(novo_produto)
        novo_produto['id'] = document_ref.id
        return jsonify(novo_produto), 201
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/products/<product_id>', methods=['PUT'])
@check_token
def update_product(user_uid, product_id):
    try:
        doc_ref = db.collection('products').document(product_id)
        doc = doc_ref.get()
        if not doc.exists or doc.to_dict().get('owner_uid') != user_uid:
            return jsonify({"error": "Permissão negada"}), 403
        updates = request.json
        doc_ref.update(updates)
        updated_doc = doc_ref.get()
        return jsonify(updated_doc.to_dict() | {'id': updated_doc.id})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
@check_token
def delete_product(user_uid, product_id):
    try:
        doc_ref = db.collection('products').document(product_id)
        doc = doc_ref.get()
        if not doc.exists or doc.to_dict().get('owner_uid') != user_uid:
            return jsonify({"error": "Permissão negada"}), 403
        doc_ref.delete()
        return jsonify({"message": "Produto excluído"}), 200
    except Exception as e: return jsonify({"error": f"Erro: {e}"}), 404
        
@app.route('/api/notify_visit', methods=['POST'])
def notify_visit():
    try:
        data = request.json
        owner_id = data.get('ownerId')
        db.collection('visits').add({'timestamp': firestore.SERVER_TIMESTAMP,'owner_uid': owner_id or 'unknown'})
        return jsonify({"success": True}), 200
    except Exception as e: return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/save_fcm_token', methods=['POST'])
@check_token
def save_fcm_token(user_uid):
    try:
        token = request.json.get('token')
        if not token: return jsonify({"error": "Nenhum token"}), 400
        db.collection('users').document(user_uid).collection('tokens').document(token).set({})
        return jsonify({"success": True}), 200
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    print(f"--- [DEBUG] Iniciando servidor Flask na porta {port} ---")
    app.run(host='0.0.0.0', port=port, debug=True)