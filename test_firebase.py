# test_firebase.py

print("--- Iniciando teste de conexão Firebase ---")

import firebase_admin
from firebase_admin import credentials

try:
    print("Tentando carregar o arquivo 'credentials.json'...")
    cred = credentials.Certificate("credentials.json")
    print("Arquivo 'credentials.json' carregado com sucesso.")
    
    print("Tentando inicializar o app Firebase...")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    print(">>> SUCESSO! Conexão com o Firebase funcionando! <<<")

except Exception as e:
    print("\n>>> FALHA! Ocorreu um erro durante a conexão. <<<")
    print(f"Detalhes do erro: {e}")

print("\n--- Teste finalizado ---")