# main_final.py - VERSÃO COM ATUALIZAÇÃO AUTOMÁTICA EM TEMPO REAL

import sys
import webbrowser
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QProgressDialog,
                             QDialog, QCheckBox, QLineEdit)
from PyQt5.QtGui import QFont, QCursor, QColor
from PyQt5.QtCore import Qt, QTimer # <<< NOVIDADE: QTimer importado

import fdb
import requests
from datetime import datetime, timedelta

# ==============================================================================
# CLASSE MercadoLivreBackend (SEM ALTERAÇÕES)
# ==============================================================================
class MercadoLivreBackend:
    # (O código do backend continua o mesmo, sem alterações)
    def __init__(self):
        self.base_url = "https://api.mercadolibre.com"; self.redirect_uri = "https://callbackmbsistema.netlify.app/"; self.config = {}; self.session = requests.Session(); self.session.proxies = {'http': None, 'https': None}
        if getattr(sys, 'frozen', False): application_path = os.path.dirname(sys.executable)
        else: application_path = os.path.dirname(os.path.abspath(__file__))
        db_full_path = os.path.join(application_path, 'base', 'banco', 'MBDATA_NOVO.FDB')
        self.DB_CONFIG = {'dsn': f'localhost:{db_full_path}', 'user': 'SYSDBA', 'password': 'masterkey'}; self._load_config()
    def logout(self):
        try:
            con = fdb.connect(**self.DB_CONFIG); cur = con.cursor()
            sql = "UPDATE MELI_CONFIG SET ACCESS_TOKEN = NULL, REFRESH_TOKEN = NULL, USER_ID = NULL, TOKEN_EXPIRATION_TIME = NULL WHERE ID = 1"
            cur.execute(sql); con.commit(); con.close(); self._load_config(); return True, "Conta desconectada com sucesso."
        except Exception as e: return False, f"Ocorreu um erro ao tentar desconectar: {e}"
    def get_authorization_url(self):
        if not self.config.get('app_id'): return None, "APP_ID não encontrado no banco de dados.\n\nVerifique se as credenciais estão preenchidas na tabela MELI_CONFIG."
        app_id = self.config['app_id']; url = (f"https://auth.mercadolibre.com/authorization?response_type=code&client_id={app_id}&redirect_uri={self.redirect_uri}"); return url, None
    def exchange_code_for_token(self, code):
        url = f"{self.base_url}/oauth/token"
        payload = {'grant_type': 'authorization_code', 'client_id': self.config.get('app_id'), 'client_secret': self.config.get('client_secret'), 'code': code, 'redirect_uri': self.redirect_uri}
        try:
            response = self.session.post(url, data=payload, timeout=15); response.raise_for_status(); token_data = response.json()
            if self._save_tokens_to_db(token_data): self._load_config(); return True, "Autenticação realizada com sucesso!"
            else: return False, "Erro ao salvar os tokens no banco de dados."
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na comunicação com o Mercado Livre: {e}"
            if hasattr(e, 'response') and e.response:
                try: error_data = e.response.json(); error_msg = error_data.get('message', 'Erro desconhecido. Verifique se o código não expirou.')
                except ValueError: error_msg = f"Resposta inesperada do servidor: {e.response.text}"
            return False, error_msg
    def _load_config(self):
        try:
            con = fdb.connect(**self.DB_CONFIG); cur = con.cursor()
            cur.execute("SELECT APP_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN, USER_ID, TOKEN_EXPIRATION_TIME FROM MELI_CONFIG WHERE ID = 1"); row = cur.fetchone()
            if row and row[2]: self.config = {'app_id': row[0], 'client_secret': row[1], 'access_token': row[2], 'refresh_token': row[3], 'user_id': row[4], 'expiration_time': row[5]}
            else:
                cur.execute("SELECT APP_ID, CLIENT_SECRET FROM MELI_CONFIG WHERE ID = 1"); row_secrets = cur.fetchone()
                if row_secrets: self.config = {'app_id': row_secrets[0], 'client_secret': row_secrets[1]}
                else: self.config = {}
            con.close()
        except Exception as e:
            QMessageBox.critical(None, "Erro Crítico de Banco de Dados", f"Não foi possível conectar ou ler a configuração do banco.\n\nVerifique se:\n1. O servidor Firebird está instalado e rodando.\n2. O arquivo do banco de dados está na pasta 'base/banco/' junto ao executável.\n\nErro técnico: {e}"); self.config = {}; sys.exit(1)
    def _save_tokens_to_db(self, new_token_data):
        try:
            con = fdb.connect(**self.DB_CONFIG); cur = con.cursor(); expires_in = new_token_data['expires_in']; expiration_time = datetime.now() + timedelta(seconds=expires_in)
            sql = "UPDATE MELI_CONFIG SET ACCESS_TOKEN = ?, REFRESH_TOKEN = ?, TOKEN_EXPIRATION_TIME = ?, USER_ID = ? WHERE ID = 1"
            params = (new_token_data['access_token'], new_token_data['refresh_token'], expiration_time, str(new_token_data['user_id']))
            cur.execute(sql, params); con.commit(); con.close(); return True
        except Exception: return False
    def _refresh_token(self):
        url = f"{self.base_url}/oauth/token"; payload = {'grant_type': 'refresh_token', 'client_id': self.config.get('app_id'), 'client_secret': self.config.get('client_secret'), 'refresh_token': self.config.get('refresh_token')}
        try:
            response = self.session.post(url, data=payload, timeout=15); response.raise_for_status(); new_token_data = response.json()
            self.config['access_token'] = new_token_data['access_token']; self.config['refresh_token'] = new_token_data['refresh_token']
            self._save_tokens_to_db(new_token_data); return True
        except requests.exceptions.RequestException: return False
    def _is_token_expired(self):
        expiration_time = self.config.get('expiration_time');
        if not expiration_time: return True
        return datetime.now() >= (expiration_time - timedelta(minutes=5))
    def _make_request(self, method, url, **kwargs):
        if self._is_token_expired():
            if not self._refresh_token(): raise ConnectionError("Falha ao renovar o token de acesso. Sua sessão expirou.")
        self.session.headers.update({'Authorization': f'Bearer {self.config.get("access_token")}'})
        try:
            kwargs.setdefault('timeout', 15); response = self.session.request(method, url, **kwargs); response.raise_for_status(); return response.json()
        except Exception as e: raise e
    def is_configured(self): return 'access_token' in self.config and self.config['access_token']
    def get_seller_id(self): return self.config.get('user_id')
    def get_local_products(self):
        products = [];
        try:
            con = fdb.connect(**self.DB_CONFIG); cur = con.cursor(); cur.execute("SELECT ID, NOME, MELI_ID, QUANTIDADE_ESTOQUE FROM PRODUTOS ORDER BY NOME")
            for row in cur.fetchall(): products.append({'id_local': row[0], 'nome': row[1], 'meli_id': row[2], 'estoque': row[3]})
            con.close()
        except Exception: pass
        return products
    def get_linked_products(self):
        products = [];
        try:
            con = fdb.connect(**self.DB_CONFIG); cur = con.cursor(); cur.execute("SELECT ID, NOME, MELI_ID, QUANTIDADE_ESTOQUE FROM PRODUTOS WHERE MELI_ID IS NOT NULL ORDER BY NOME")
            for row in cur.fetchall(): products.append({'id_local': row[0], 'nome': row[1], 'meli_id': row[2], 'estoque': row[3]})
            con.close()
        except Exception: pass
        return products
    def get_meli_active_listings(self):
        seller_id = self.get_seller_id();
        if not seller_id: return []
        url = f"{self.base_url}/users/{seller_id}/items/search?status=active"; listings = []
        try:
            data = self._make_request('get', url); meli_ids = data.get('results', [])
            if not meli_ids: return []
            url_details = f"{self.base_url}/items?ids={','.join(meli_ids[:50])}"; items_details = self._make_request('get', url_details)
            for item in items_details:
                body = item.get('body', {});
                if body.get('error'): continue
                listings.append({'meli_id': body.get('id'), 'titulo': body.get('title'), 'estoque': body.get('available_quantity'), 'preco': body.get('price'), 'link': body.get('permalink')})
        except Exception: pass
        return listings
    def link_product(self, id_local, meli_id):
        try:
            con = fdb.connect(**self.DB_CONFIG); cur = con.cursor(); cur.execute("UPDATE PRODUTOS SET MELI_ID = ? WHERE ID = ?", (meli_id, id_local)); con.commit(); con.close(); return True
        except Exception: return False
    def atualizar_estoque_meli(self, meli_id, nova_quantidade):
        url_item_details = f"{self.base_url}/items/{meli_id}"
        try: item_data = self._make_request('get', url_item_details)
        except Exception: return None
        variations = item_data.get('variations', []); url_put = f"{self.base_url}/items/{meli_id}"
        if variations:
            payload_variations = []
            for var in variations: var.pop('catalog_product_id', None); var.pop('attributes', None); payload_variations.append(var)
            payload_variations[0]['available_quantity'] = int(nova_quantidade); payload = {"variations": payload_variations}
        else: payload = {"available_quantity": int(nova_quantidade)}
        try: return self._make_request('put', url_put, json=payload)
        except Exception: return None
    def get_vendas_hoje(self):
        try:
            hoje = datetime.now(); date_from = hoje.strftime('%Y-%m-%dT00:00:00.000-03:00'); date_to = hoje.strftime('%Y-%m-%dT23:59:59.999-03:00'); url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&order.date_created.from={date_from}&order.date_created.to={date_to}"; pedidos = self._make_request('get', url).get('results', []); return sum(p['total_amount'] for p in pedidos if p['status'] in ['paid', 'shipped', 'delivered'])
        except Exception: return 0.0
    def get_vendas_mes(self):
        try:
            hoje = datetime.now(); primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0); date_from = primeiro_dia_mes.strftime('%Y-%m-%dT%H:%M:%S.000-03:00'); date_to = hoje.strftime('%Y-%m-%dT%H:%M:%S.999-03:00'); url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&order.date_created.from={date_from}&order.date_created.to={date_to}"; pedidos = self._make_request('get', url).get('results', []); return sum(p['total_amount'] for p in pedidos if p['status'] in ['paid', 'shipped', 'delivered'])
        except Exception: return 0.0
    def get_pedidos_pendentes(self):
        try:
            url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&order.status=paid"; data = self._make_request('get', url); return data.get('paging', {}).get('total', 0)
        except Exception: return 0
    def get_produtos_online(self):
        try:
            url = f"{self.base_url}/users/{self.get_seller_id()}/items/search?status=active"; data = self._make_request('get', url); return data.get('paging', {}).get('total', 0)
        except Exception: return 0
    def get_ultimas_vendas(self, limit=50):
        try:
            url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&sort=date_desc&limit={limit}"; pedidos = self._make_request('get', url).get('results', []); vendas_formatadas = []
            for pedido in pedidos:
                if not pedido['order_items']: continue
                primeiro_item = pedido['order_items'][0]['item']
                venda = {'data': datetime.fromisoformat(pedido['date_created']).strftime('%d/%m/%Y %H:%M'), 'plataforma': 'Mercado Livre', 'produto': primeiro_item['title'], 'cliente': pedido['buyer']['nickname'], 'valor': f"R$ {pedido['total_amount']:.2f}".replace('.',','), 'status': pedido.get('shipping', {}).get('status', pedido.get('status', 'N/A')).replace('_', ' ').title()}
                vendas_formatadas.append(venda)
            return vendas_formatadas
        except Exception: return []

class VincularProdutosWindow(QMainWindow):
    # (O código desta classe continua o mesmo, sem alterações)
    def __init__(self, backend):
        super().__init__(); self.backend = backend; self.setWindowTitle("Vincular Produtos com Mercado Livre")
        screen_geometry = QApplication.desktop().availableGeometry(); self.setGeometry(int(screen_geometry.x() + screen_geometry.width() * 0.05), int(screen_geometry.y() + screen_geometry.height() * 0.05), int(screen_geometry.width() * 0.9), int(screen_geometry.height() * 0.9)); self.init_ui(); self.carregar_listas()
    def init_ui(self):
        central_widget = QWidget(); self.setCentralWidget(central_widget); main_layout = QHBoxLayout(central_widget)
        local_panel = QFrame(); local_layout = QVBoxLayout(local_panel); local_label = QLabel("Produtos do seu Sistema"); local_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.tabela_local = QTableWidget(); self.tabela_local.setColumnCount(4); self.tabela_local.setHorizontalHeaderLabels(["ID Local", "Produto", "Estoque", "Vinculado a"]); self.tabela_local.setSelectionBehavior(QTableWidget.SelectRows); self.tabela_local.setSelectionMode(QTableWidget.SingleSelection); self.tabela_local.setEditTriggers(QTableWidget.NoEditTriggers)
        local_layout.addWidget(local_label); local_layout.addWidget(self.tabela_local)
        link_panel = QFrame(); link_layout = QVBoxLayout(link_panel); link_layout.addStretch()
        self.btn_vincular = QPushButton("➡️\nVincular\n➡️"); self.btn_vincular.setMinimumHeight(100); self.btn_vincular.setFont(QFont("Arial", 14, QFont.Bold)); self.btn_vincular.clicked.connect(self.vincular_selecionados)
        link_layout.addWidget(self.btn_vincular); link_layout.addStretch()
        meli_panel = QFrame(); meli_layout = QVBoxLayout(meli_panel); meli_label = QLabel("Anúncios do Mercado Livre (Ativos)"); meli_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.tabela_meli = QTableWidget(); self.tabela_meli.setColumnCount(3); self.tabela_meli.setHorizontalHeaderLabels(["Anúncio", "Estoque", "Preço"]); self.tabela_meli.setSelectionBehavior(QTableWidget.SelectRows); self.tabela_meli.setSelectionMode(QTableWidget.SingleSelection); self.tabela_meli.setEditTriggers(QTableWidget.NoEditTriggers)
        meli_layout.addWidget(meli_label); meli_layout.addWidget(self.tabela_meli)
        main_layout.addWidget(local_panel, 2); main_layout.addWidget(link_panel, 1); main_layout.addWidget(meli_panel, 3)
    def carregar_listas(self):
        self.setCursor(QCursor(Qt.WaitCursor))
        produtos_locais = self.backend.get_local_products(); self.tabela_local.setRowCount(len(produtos_locais))
        for row, prod in enumerate(produtos_locais):
            self.tabela_local.setItem(row, 0, QTableWidgetItem(str(prod['id_local']))); self.tabela_local.setItem(row, 1, QTableWidgetItem(prod['nome'])); self.tabela_local.setItem(row, 2, QTableWidgetItem(str(prod['estoque'])))
            vinculo_item = QTableWidgetItem(prod['meli_id'] or "---");
            if prod['meli_id']: vinculo_item.setBackground(QColor("#d4edda"))
            self.tabela_local.setItem(row, 3, vinculo_item)
        anuncios_meli = self.backend.get_meli_active_listings(); self.tabela_meli.setRowCount(len(anuncios_meli))
        for row, anuncio in enumerate(anuncios_meli):
            item_titulo = QTableWidgetItem(anuncio['titulo']); item_titulo.setData(Qt.UserRole, anuncio['meli_id'])
            self.tabela_meli.setItem(row, 0, item_titulo); self.tabela_meli.setItem(row, 1, QTableWidgetItem(str(anuncio['estoque']))); self.tabela_meli.setItem(row, 2, QTableWidgetItem(f"R$ {anuncio['preco']:.2f}"))
        self.tabela_local.resizeColumnsToContents(); self.tabela_meli.resizeColumnsToContents(); self.tabela_meli.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch); self.unsetCursor()
    def vincular_selecionados(self):
        linha_local = self.tabela_local.currentRow(); linha_meli = self.tabela_meli.currentRow()
        if linha_local == -1 or linha_meli == -1: QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione uma linha em cada tabela para vincular."); return
        id_local = int(self.tabela_local.item(linha_local, 0).text()); nome_local = self.tabela_local.item(linha_local, 1).text()
        item_meli = self.tabela_meli.item(linha_meli, 0); meli_id = item_meli.data(Qt.UserRole); titulo_meli = item_meli.text()
        reply = QMessageBox.question(self, "Confirmar Vínculo", f"Você tem certeza que deseja vincular:\n\nProduto Local: (ID {id_local}) {nome_local}\nCOM\nAnúncio MELI: {titulo_meli}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.backend.link_product(id_local, meli_id): QMessageBox.information(self, "Sucesso", "Produto vinculado com sucesso!"); self.carregar_listas()
            else: QMessageBox.critical(self, "Erro", "Não foi possível salvar o vínculo no banco de dados.")

class SelecaoSincronizacaoWindow(QDialog):
    # (O código desta classe continua o mesmo, sem alterações)
    def __init__(self, backend, parent=None):
        super().__init__(parent); self.backend = backend; self.produtos_selecionados = []
        self.setWindowTitle("Selecionar Produtos para Sincronizar"); self.setMinimumSize(800, 600)
        self.init_ui(); self.carregar_produtos_vinculados()
    def init_ui(self):
        layout = QVBoxLayout(self); label_titulo = QLabel("Marque os produtos que deseja sincronizar o estoque:"); label_titulo.setFont(QFont("Arial", 14, QFont.Bold)); layout.addWidget(label_titulo)
        botoes_layout = QHBoxLayout(); btn_marcar_todos = QPushButton("Marcar Todos"); btn_marcar_todos.clicked.connect(self.marcar_desmarcar_todos); btn_desmarcar_todos = QPushButton("Desmarcar Todos"); btn_desmarcar_todos.clicked.connect(lambda: self.marcar_desmarcar_todos(False))
        botoes_layout.addWidget(btn_marcar_todos); botoes_layout.addWidget(btn_desmarcar_todos); botoes_layout.addStretch(); layout.addLayout(botoes_layout)
        self.tabela = QTableWidget(); self.tabela.setColumnCount(4); self.tabela.setHorizontalHeaderLabels(["", "Produto no Sistema", "Estoque Local", "Anúncio Vinculado (ID)"]); self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch); self.tabela.setEditTriggers(QTableWidget.NoEditTriggers); self.tabela.setSelectionBehavior(QTableWidget.SelectRows); layout.addWidget(self.tabela)
        action_layout = QHBoxLayout(); action_layout.addStretch(); btn_cancelar = QPushButton("Cancelar"); btn_cancelar.clicked.connect(self.reject)
        btn_sincronizar = QPushButton("✅ Sincronizar Selecionados"); btn_sincronizar.setFont(QFont("Arial", 10, QFont.Bold)); btn_sincronizar.setStyleSheet("background-color: #28a745; color: white; padding: 8px;"); btn_sincronizar.clicked.connect(self.aceitar_selecao)
        action_layout.addWidget(btn_cancelar); action_layout.addWidget(btn_sincronizar); layout.addLayout(action_layout)
    def carregar_produtos_vinculados(self):
        produtos = self.backend.get_linked_products(); self.tabela.setRowCount(len(produtos))
        for row, prod in enumerate(produtos):
            chk_box_item = QCheckBox(); cell_widget = QWidget(); chk_layout = QHBoxLayout(cell_widget); chk_layout.addWidget(chk_box_item); chk_layout.setAlignment(Qt.AlignCenter); chk_layout.setContentsMargins(0,0,0,0); self.tabela.setCellWidget(row, 0, cell_widget)
            item_nome = QTableWidgetItem(prod['nome']); item_nome.setData(Qt.UserRole, prod); self.tabela.setItem(row, 1, item_nome)
            self.tabela.setItem(row, 2, QTableWidgetItem(str(prod['estoque']))); self.tabela.setItem(row, 3, QTableWidgetItem(prod['meli_id']))
        self.tabela.resizeColumnsToContents(); self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    def marcar_desmarcar_todos(self, checked=True):
        for row in range(self.tabela.rowCount()):
            chk_box = self.tabela.cellWidget(row, 0).findChild(QCheckBox); chk_box.setChecked(checked)
    def aceitar_selecao(self):
        self.produtos_selecionados.clear()
        for row in range(self.tabela.rowCount()):
            chk_box = self.tabela.cellWidget(row, 0).findChild(QCheckBox)
            if chk_box and chk_box.isChecked(): self.produtos_selecionados.append(self.tabela.item(row, 1).data(Qt.UserRole))
        if not self.produtos_selecionados: QMessageBox.warning(self, "Nenhum Produto Selecionado", "Por favor, marque pelo menos um produto para sincronizar."); return
        self.accept()
    def get_selecao(self): return self.produtos_selecionados

class MercadoLivreWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.janela_vincular = None; self.backend = MercadoLivreBackend(); self.init_ui(); self.check_auth_status(); self.showMaximized()
    
    def init_ui(self):
        self.setWindowTitle("Painel Mercado Livre"); self.setStyleSheet("background-color: #f8f9fa;")
        self.main_widget = QWidget(); self.setCentralWidget(self.main_widget); self.stacked_layout = QVBoxLayout(self.main_widget)
        self.connection_widget = self.create_connection_widget(); self.dashboard_widget = self.create_dashboard_widget()
        self.stacked_layout.addWidget(self.connection_widget); self.stacked_layout.addWidget(self.dashboard_widget)

        ### NOVIDADE: Criar e configurar o timer de atualização ###
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.carregar_dados_reais) # Conecta o timer à função de carregar dados
        # O timer será iniciado quando a janela ficar visível e parado quando ficar invisível

    def check_auth_status(self):
        if self.backend.is_configured():
            self.connection_widget.hide(); self.dashboard_widget.show(); self.carregar_dados_reais()
        else:
            self.dashboard_widget.hide(); self.connection_widget.show()

    def create_connection_widget(self):
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setAlignment(Qt.AlignCenter)
        label_titulo = QLabel("Integração com Mercado Livre"); label_titulo.setFont(QFont("Arial", 28, QFont.Bold)); label_titulo.setAlignment(Qt.AlignCenter)
        step1_label = QLabel("<b>Passo 1:</b> Clique no botão para autorizar o acesso no site do Mercado Livre."); step1_label.setFont(QFont("Arial", 12))
        btn_abrir_navegador = QPushButton("🔗 Abrir Página de Autorização"); btn_abrir_navegador.setFont(QFont("Arial", 14, QFont.Bold)); btn_abrir_navegador.setCursor(QCursor(Qt.PointingHandCursor)); btn_abrir_navegador.setFixedSize(450, 60); btn_abrir_navegador.setStyleSheet("background-color: #3483fa; color: white; border-radius: 8px; padding: 10px;"); btn_abrir_navegador.clicked.connect(self.abrir_navegador_autorizacao)
        step2_label = QLabel("<b>Passo 2:</b> Na página que abriu, copie o código e cole no campo abaixo."); step2_label.setFont(QFont("Arial", 12))
        self.code_input = QLineEdit(); self.code_input.setPlaceholderText("Cole o código de autorização aqui"); self.code_input.setFont(QFont("Arial", 14)); self.code_input.setFixedSize(450, 50)
        btn_confirmar = QPushButton("✅ Confirmar Código e Conectar"); btn_confirmar.setFont(QFont("Arial", 14, QFont.Bold)); btn_confirmar.setCursor(QCursor(Qt.PointingHandCursor)); btn_confirmar.setFixedSize(450, 60); btn_confirmar.setStyleSheet("background-color: #28a745; color: white; border-radius: 8px; padding: 10px;"); btn_confirmar.clicked.connect(self.confirmar_codigo_autorizacao)
        layout.addStretch(); layout.addWidget(label_titulo, 0, Qt.AlignCenter); layout.addSpacing(40); layout.addWidget(step1_label, 0, Qt.AlignCenter); layout.addWidget(btn_abrir_navegador, 0, Qt.AlignCenter); layout.addSpacing(30); layout.addWidget(step2_label, 0, Qt.AlignCenter); layout.addWidget(self.code_input, 0, Qt.AlignCenter); layout.addSpacing(10); layout.addWidget(btn_confirmar, 0, Qt.AlignCenter); layout.addStretch()
        return widget

    def abrir_navegador_autorizacao(self):
        auth_url, error = self.backend.get_authorization_url()
        if error: QMessageBox.critical(self, "Erro de Configuração", f"Não foi possível gerar a URL: {error}"); return
        webbrowser.open(auth_url)

    def confirmar_codigo_autorizacao(self):
        code = self.code_input.text().strip()
        if not code: QMessageBox.warning(self, "Código Ausente", "Por favor, cole o código de autorização no campo indicado."); return
        self.setCursor(QCursor(Qt.WaitCursor)); success, message = self.backend.exchange_code_for_token(code); self.unsetCursor()
        if success: QMessageBox.information(self, "Sucesso", message); self.code_input.clear(); self.check_auth_status() 
        else: QMessageBox.critical(self, "Erro na Autenticação", f"Falha ao validar o código:\n{message}")

    def create_dashboard_widget(self):
        widget = QWidget(); main_layout = QVBoxLayout(widget); main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(20)
        self.criar_header(main_layout); self.criar_resumo(main_layout); self.criar_tabela_vendas(main_layout)
        return widget
    
    def criar_header(self, layout_pai):
        header_frame = QFrame(); header_frame.setFixedHeight(80); header_frame.setStyleSheet("QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2); border-radius: 15px; }")
        header_layout = QHBoxLayout(header_frame); header_layout.setContentsMargins(20, 15, 20, 15)
        titulo = QLabel("💰 Painel Mercado Livre"); titulo.setFont(QFont("Arial", 24, QFont.Bold)); titulo.setStyleSheet("color: white; background: transparent;")
        btn_desconectar = QPushButton("🔌 Desconectar"); btn_desconectar.setFont(QFont("Arial", 12, QFont.Bold)); btn_desconectar.setStyleSheet("QPushButton { background-color: #dc3545; color: white; padding: 10px 15px; border-radius: 5px; border: 1px solid #c82333; } QPushButton:hover { background-color: #c82333; }"); btn_desconectar.setCursor(QCursor(Qt.PointingHandCursor)); btn_desconectar.clicked.connect(self.desconectar_conta)
        btn_sincronizar_estoque = QPushButton("🔄 Sincronizar Estoque"); btn_sincronizar_estoque.setFont(QFont("Arial", 12, QFont.Bold)); btn_sincronizar_estoque.setStyleSheet("QPushButton { background-color: #ffffff; color: #333; padding: 10px 15px; border-radius: 5px; border: 1px solid #ccc; } QPushButton:hover { background-color: #f0f0f0; }"); btn_sincronizar_estoque.setCursor(QCursor(Qt.PointingHandCursor)); btn_sincronizar_estoque.clicked.connect(self.abrir_dialogo_sincronizacao)
        btn_vincular_produtos = QPushButton("🔗 Vincular Produtos"); btn_vincular_produtos.setFont(QFont("Arial", 12, QFont.Bold)); btn_vincular_produtos.setStyleSheet("QPushButton { background-color: #ffffff; color: #333; padding: 10px 15px; border-radius: 5px; border: 1px solid #ccc; } QPushButton:hover { background-color: #f0f0f0; }"); btn_vincular_produtos.setCursor(QCursor(Qt.PointingHandCursor)); btn_vincular_produtos.clicked.connect(self.abrir_janela_vincular)
        header_layout.addWidget(titulo); header_layout.addStretch(); header_layout.addWidget(btn_desconectar); header_layout.addWidget(btn_sincronizar_estoque); header_layout.addWidget(btn_vincular_produtos); layout_pai.addWidget(header_frame)
    
    def desconectar_conta(self):
        reply = QMessageBox.question(self, "Confirmar Desconexão", "Você tem certeza que deseja desconectar sua conta do Mercado Livre?\n\nSerá necessário autorizar o acesso novamente para usar as funcionalidades.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = self.backend.logout()
            if success: QMessageBox.information(self, "Sucesso", message); self.check_auth_status()
            else: QMessageBox.critical(self, "Erro", message)

    def criar_resumo(self, layout_pai):
        resumo_frame = QFrame(); resumo_frame.setStyleSheet("background: transparent;"); resumo_layout = QHBoxLayout(resumo_frame); resumo_layout.setSpacing(20)
        card1, self.lbl_vendas_hoje = self.criar_card_resumo("Vendas Hoje", "R$ 0,00", "#28a745"); card2, self.lbl_vendas_mes = self.criar_card_resumo("Vendas do Mês", "R$ 0,00", "#17a2b8"); card3, self.lbl_pedidos_pendentes = self.criar_card_resumo("Pedidos Pendentes", "0", "#ffc107"); card4, self.lbl_produtos_online = self.criar_card_resumo("Produtos Online", "0", "#6f42c1")
        resumo_layout.addWidget(card1); resumo_layout.addWidget(card2); resumo_layout.addWidget(card3); resumo_layout.addWidget(card4); layout_pai.addWidget(resumo_frame)
    def criar_card_resumo(self, titulo, valor, cor):
        card = QFrame(); card.setFixedSize(250, 100); card.setStyleSheet(f"QFrame {{ background-color: white; border-radius: 10px; border-left: 5px solid {cor}; }}")
        layout = QVBoxLayout(card); layout.setContentsMargins(15, 10, 15, 10); lbl_titulo = QLabel(titulo); lbl_titulo.setFont(QFont("Arial", 12)); lbl_titulo.setStyleSheet("color: #6c757d;"); lbl_valor = QLabel(valor); lbl_valor.setFont(QFont("Arial", 20, QFont.Bold)); lbl_valor.setStyleSheet(f"color: {cor};")
        layout.addWidget(lbl_titulo); layout.addWidget(lbl_valor); layout.addStretch(); return card, lbl_valor
    
    def criar_tabela_vendas(self, layout_pai):
        table_frame = QFrame(); table_frame.setStyleSheet("QFrame { background-color: white; border-radius: 10px; border: 1px solid #dee2e6; }")
        table_layout = QVBoxLayout(table_frame); table_layout.setContentsMargins(15, 15, 15, 15); titulo_table = QLabel("📋 Últimas Vendas"); titulo_table.setFont(QFont("Arial", 16, QFont.Bold)); titulo_table.setStyleSheet("color: #495057; margin-bottom: 10px;")
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6); self.tabela.setHorizontalHeaderLabels(["Data", "Plataforma", "Produto", "Cliente", "Valor", "Status"])
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers); self.tabela.setSelectionMode(QTableWidget.NoSelection); self.tabela.setFocusPolicy(Qt.NoFocus)
        self.tabela.setStyleSheet(""" QTableWidget { gridline-color: #dee2e6; border: none; } QTableWidget::item { padding: 12px; border-bottom: 1px solid #e9ecef; } QHeaderView::section { background-color: #f8f9fa; padding: 12px; border: none; border-bottom: 2px solid #dee2e6; font-weight: bold; color: #495057; } """)
        header = self.tabela.horizontalHeader(); header.setSectionResizeMode(2, QHeaderView.Stretch); header.setSectionResizeMode(3, QHeaderView.Stretch)
        table_layout.addWidget(titulo_table); table_layout.addWidget(self.tabela); layout_pai.addWidget(table_frame)
    
    def carregar_dados_reais(self):
        print("Atualizando dados do Mercado Livre...") # Adicionado para debug
        self.setCursor(QCursor(Qt.WaitCursor))
        try:
            self.lbl_vendas_hoje.setText(f"R$ {self.backend.get_vendas_hoje():.2f}".replace('.',',')); self.lbl_vendas_mes.setText(f"R$ {self.backend.get_vendas_mes():.2f}".replace('.',',')); self.lbl_pedidos_pendentes.setText(str(self.backend.get_pedidos_pendentes())); self.lbl_produtos_online.setText(str(self.backend.get_produtos_online()))
            ultimas_vendas = self.backend.get_ultimas_vendas(); self.tabela.setRowCount(len(ultimas_vendas))
            item_font = QFont("Arial", 11)
            for row, venda in enumerate(ultimas_vendas):
                data_item = QTableWidgetItem(venda['data']); plataforma_item = QTableWidgetItem(venda['plataforma']); produto_item = QTableWidgetItem(venda['produto']); cliente_item = QTableWidgetItem(venda['cliente']); valor_item = QTableWidgetItem(venda['valor']); status_item = QTableWidgetItem(venda['status'])
                for item in [data_item, plataforma_item, produto_item, cliente_item, valor_item, status_item]: item.setFont(item_font)
                plataforma_item.setForeground(QColor("#000000")); plataforma_item.setBackground(QColor("#FFF159")); plataforma_item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(row, 0, data_item); self.tabela.setItem(row, 1, plataforma_item); self.tabela.setItem(row, 2, produto_item); self.tabela.setItem(row, 3, cliente_item); self.tabela.setItem(row, 4, valor_item); self.tabela.setItem(row, 5, status_item)
        except ConnectionError as e:
            QMessageBox.critical(self, "Erro de Conexão", f"{e}\nSua sessão expirou. Por favor, reconecte sua conta.")
            self.update_timer.stop() # Para o timer se a conexão falhar
            self.backend.config = {}; self.check_auth_status()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}") # Debug
        finally:
            self.unsetCursor()
    
    ### NOVIDADE: Métodos para controlar o timer com a visibilidade da janela ###
    def showEvent(self, event):
        """Chamado quando a janela é mostrada."""
        super().showEvent(event)
        print("Janela do ML visível, iniciando timer de atualização.")
        # Inicia o timer para rodar a cada 30 segundos (30000 ms)
        self.update_timer.start(30000)
    
    def hideEvent(self, event):
        """Chamado quando a janela é escondida ou fechada."""
        super().hideEvent(event)
        print("Janela do ML não visível, parando timer.")
        self.update_timer.stop()
        
    def abrir_janela_vincular(self):
        if self.janela_vincular is None or not self.janela_vincular.isVisible():
            self.janela_vincular = VincularProdutosWindow(self.backend); self.janela_vincular.show()
    def abrir_dialogo_sincronizacao(self):
        produtos_vinculados = self.backend.get_linked_products()
        if not produtos_vinculados: QMessageBox.information(self, "Nenhum Produto Vinculado", "Não há produtos vinculados para sincronizar. Vincule alguns produtos primeiro."); return
        msg_box = QMessageBox(self); msg_box.setWindowTitle("Modo de Sincronização"); msg_box.setText("Como você deseja sincronizar o estoque?"); msg_box.setIcon(QMessageBox.Question)
        btn_todos = msg_box.addButton("Sincronizar Todos", QMessageBox.AcceptRole); btn_selecionar = msg_box.addButton("Selecionar Produtos...", QMessageBox.ActionRole); msg_box.addButton("Cancelar", QMessageBox.RejectRole)
        msg_box.exec_()
        clicked_button = msg_box.clickedButton()
        if clicked_button == btn_todos: self.executar_sincronizacao(produtos_vinculados)
        elif clicked_button == btn_selecionar:
            dialog = SelecaoSincronizacaoWindow(self.backend, self)
            if dialog.exec_() == QDialog.Accepted:
                produtos_para_sincronizar = dialog.get_selecao()
                if produtos_para_sincronizar: self.executar_sincronizacao(produtos_para_sincronizar)
    def executar_sincronizacao(self, lista_de_produtos):
        if not lista_de_produtos: return
        total = len(lista_de_produtos)
        reply = QMessageBox.question(self, "Confirmar Sincronização", f"Você está prestes a sincronizar o estoque de {total} produto(s).\n\nDeseja continuar?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes: return
        
        progress = QProgressDialog("Sincronizando produtos...", "Cancelar", 0, total, self)
        progress.setWindowTitle("Progresso da Sincronização"); progress.setWindowModality(Qt.WindowModal); progress.show()
        sucessos = 0; falhas = 0
        for i, produto in enumerate(lista_de_produtos):
            progress.setValue(i); QApplication.processEvents()
            if progress.wasCanceled(): break
            nome_prod = produto['nome']; meli_id = produto['meli_id']; estoque_local = produto['estoque']
            progress.setLabelText(f"Sincronizando '{nome_prod}' ({i+1}/{total})...")
            resultado_api = self.backend.atualizar_estoque_meli(meli_id, estoque_local)
            if resultado_api: sucessos += 1
            else: falhas += 1
        progress.setValue(total)
        mensagem_final = f"Sincronização concluída!\n\n✅ Produtos atualizados com sucesso: {sucessos}\n❌ Falhas na atualização: {falhas}"
        QMessageBox.information(self, "Resultado da Sincronização", mensagem_final)
        if self.janela_vincular and self.janela_vincular.isVisible(): self.janela_vincular.carregar_listas()
        self.carregar_dados_reais()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MercadoLivreWindow()
    # A linha abaixo foi removida do __main__ porque o show() já é chamado pelo seu sistema principal
    # window.show()
    sys.exit(app.exec_())