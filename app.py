# app.py - Nosso Servidor em Python

from flask import Flask, render_template, request, jsonify
import os

# Inicializa o Flask
app = Flask(__name__, template_folder='templates')

# --- NOSSO BANCO DE DADOS EM MEMÓRIA ---
db = {
    "products": [
        {
            "id": "1",
            "nome": "Produto de Exemplo (do Python!)",
            "descricao": "Este produto foi carregado diretamente do servidor Python.",
            "valor": 199.99,
            "imagemUrl": "https://source.unsplash.com/random/400x300?tech,product",
            "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    ]
}
# ----------------------------------------

# --- ROTAS PARA SERVIR AS PÁGINAS HTML ---

@app.route('/')
def catalogo_page():
    """ Rota principal que mostra o catálogo para o cliente. """
    return render_template('catalogo.html')

@app.route('/admin')
def admin_page():
    """ Rota que mostra o painel de administração. """
    return render_template('admin.html')

# --- API: AS URLS QUE O JAVASCRIPT VAI USAR ---

@app.route('/api/products', methods=['GET'])
def get_products():
    """ API para obter a lista de todos os produtos. """
    return jsonify(db['products'])

@app.route('/api/products', methods=['POST'])
def add_product():
    """ API para adicionar um novo produto. """
    novo_produto = request.json
    novo_produto['id'] = str(os.urandom(8).hex()) # Gera um ID aleatório
    db['products'].append(novo_produto)
    return jsonify(novo_produto), 201 # 201 = Created

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """ API para excluir um produto pelo ID. """
    global db
    produto_encontrado = None
    for produto in db['products']:
        if produto['id'] == product_id:
            produto_encontrado = produto
            break
    
    if produto_encontrado:
        db['products'].remove(produto_encontrado)
        return jsonify({"message": "Produto excluído com sucesso"}), 200
    else:
        return jsonify({"error": "Produto não encontrado"}), 404

# --- INICIALIZAÇÃO DO SERVIDOR ---

if __name__ == '__main__':
    app.run(debug=True, port=5000)