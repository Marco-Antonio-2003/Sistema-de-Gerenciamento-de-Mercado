# mercado_livre/gerar_tokens.py (VERSÃO CORRETA E AUTOMÁTICA)

import requests
import webbrowser
import fdb
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import datetime
import threading
import time

# IMPORTAMOS A BIBLIOTECA MÁGICA
from pyngrok import ngrok

# --- CONFIGURAÇÕES ---
APP_ID = '2308426983986199' # Coloque seu App ID aqui
CLIENT_SECRET = '95PBzqciPcfsD6IFUYpt5BxxQv1Aaj1O' # Sua nova chave secreta

# Configurações do servidor local
HOST_NAME = 'localhost'
PORT_NUMBER = 8080 # A porta em que nosso servidor local vai rodar

# URL da API do MELI para obter o token
TOKEN_URL = 'https://api.mercadolibre.com/oauth/token'

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
# Adapte para as credenciais do seu banco de dados
DB_CONFIG = {
    'dsn': r'localhost:C:\Users\Marco-Note\Desktop\PythonProject\Sistema\base\banco\MBDATA_NOVO.FDB',
    'user': 'SYSDBA',
    'password': 'masterkey'
}

# Variáveis globais para comunicação entre threads
auth_code = None
httpd_server = None

class CallbackHandler(BaseHTTPRequestHandler):
    """Mini-servidor para capturar o callback."""
    def do_GET(self):
        global auth_code, httpd_server
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"<h1>Sucesso!</h1><p>Autorizacao recebida. Voce ja pode fechar esta janela.</p>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Erro: Codigo de autorizacao nao encontrado.")
        
        # Sinaliza para o servidor parar após tratar a requisição
        threading.Thread(target=httpd_server.shutdown).start()

def get_tokens_from_code(code, redirect_uri):
    """Troca o código de autorização pelos tokens."""
    payload = {
        'grant_type': 'authorization_code',
        'client_id': APP_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri # A URI usada na autorização
    }
    response = requests.post(TOKEN_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()

def save_tokens_to_db(token_data):
    """Salva os tokens no banco de dados."""
    # (Esta função permanece exatamente igual à anterior)
    try:
        con = fdb.connect(**DB_CONFIG)
        cur = con.cursor()
        expires_in = token_data['expires_in']
        expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        sql = """
            UPDATE MELI_CONFIG SET
                APP_ID = ?, CLIENT_SECRET = ?, ACCESS_TOKEN = ?,
                REFRESH_TOKEN = ?, USER_ID = ?, TOKEN_EXPIRATION_TIME = ?
            WHERE ID = 1
        """
        params = (APP_ID, CLIENT_SECRET, token_data['access_token'],
                  token_data['refresh_token'], token_data['user_id'], expiration_time)
        cur.execute(sql, params)
        con.commit()
        print("\n[SUCESSO] Tokens salvos no banco de dados com sucesso!")
    except Exception as e:
        print(f"\n[ERRO] Falha ao salvar tokens no banco de dados: {e}")
    finally:
        if 'con' in locals() and con:
            con.close()

def main():
    global httpd_server
    print("--- Assistente de Configuracao Mercado Livre ---")
    
    # 1. Inicia o túnel ngrok e obtém a URL pública HTTPS
    print("1. Criando tunel seguro com ngrok...")
    try:
        # ngrok.set_auth_token("SEU_AUTHTOKEN_DO_NGROK") # Opcional, mas recomendado
        ngrok_tunnel = ngrok.connect(PORT_NUMBER, "http")
        public_url = ngrok_tunnel.public_url

        # Agora a variável public_url contém apenas a string "https://..."
        redirect_uri_https = f"{public_url}/callback"

        print(f"   -> Tunel criado: {redirect_uri_https}")
    except Exception as e:
        print(f"[ERRO] Nao foi possivel iniciar o ngrok. Verifique sua conexao ou instalacao. Erro: {e}")
        return

    # IMPORTANTE: Informa ao usuário para atualizar a URI no portal do MELI
    print("\n" + "="*60)
    print("ACAO MANUAL NECESSARIA:")
    print("1. Copie a URL abaixo:")
    print(f"   {redirect_uri_https}")
    print("2. Va para o portal de desenvolvedores do Mercado Livre.")
    print("3. Edite sua aplicacao e cole essa URL no campo 'URI de Redirect'.")
    print("4. Salve as alteracoes no portal do Mercado Livre.")
    print("="*60 + "\n")
    
    input("Pressione ENTER apos ter atualizado a URI no portal do Mercado Livre...")
    
    # 2. Monta a URL de autorização com a URI correta (HTTPS)
    auth_url_final = f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={APP_ID}&redirect_uri={redirect_uri_https}"

    # 3. Abre o navegador na página de autorização
    webbrowser.open(auth_url_final)
    print("\n2. Seu navegador foi aberto. Faca login e autorize a aplicacao.")
    
    # 4. Inicia o servidor local para aguardar o callback
    httpd_server = HTTPServer((HOST_NAME, PORT_NUMBER), CallbackHandler)
    print(f"3. Aguardando autorizacao...")
    httpd_server.serve_forever() # O servidor vai parar sozinho quando o callback for recebido

    # 5. Se o código foi recebido, continua o processo
    if auth_code:
        print("4. Codigo de autorizacao recebido! Trocando por tokens...")
        try:
            token_data = get_tokens_from_code(auth_code, redirect_uri_https)
            print("5. Tokens de acesso gerados com sucesso!")
            save_tokens_to_db(token_data)
        except Exception as e:
            print(f"\n[ERRO] Falha ao obter os tokens: {e}")
    else:
        print("\n[ERRO] O processo foi interrompido ou falhou. Nenhum codigo de autorizacao foi recebido.")
    
    # 6. Desconecta e fecha o túnel ngrok
    ngrok.disconnect(ngrok_tunnel.public_url)
    print("6. Tunel ngrok encerrado.")
    print("\nConfiguracao concluida.")

if __name__ == '__main__':
    main()