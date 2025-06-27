# main_final.py - VERSÃO COMPLETA FINAL COM TODAS AS FUNÇÕES

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtGui import QFont, QCursor, QColor
from PyQt5.QtCore import Qt
import fdb
import requests
from datetime import datetime, timedelta

# ==============================================================================
# INÍCIO DA CLASSE MercadoLivreBackend
# ==============================================================================
class MercadoLivreBackend:
    
    def __init__(self):
        self.base_url = "https://api.mercadolibre.com"
        self.config = {}
        self.session = requests.Session() 
        self.session.proxies = {'http': None, 'https': None}
        self.DB_CONFIG = { # Definido como atributo de instância
            'dsn': r'localhost:C:\Users\Marco-Note\Desktop\PythonProject\Sistema\base\banco\MBDATA_NOVO.FDB',
            'user': 'SYSDBA',
            'password': 'masterkey'
        }
        self._load_config()

    def _load_config(self):
        print("Backend: Carregando config do DB...")
        try:
            con = fdb.connect(**self.DB_CONFIG)
            cur = con.cursor()
            cur.execute("SELECT APP_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN, USER_ID, TOKEN_EXPIRATION_TIME FROM MELI_CONFIG WHERE ID = 1")
            row = cur.fetchone()
            if row:
                self.config = {
                    'app_id': row[0], 'client_secret': row[1], 'access_token': row[2],
                    'refresh_token': row[3], 'user_id': row[4], 'expiration_time': row[5]
                }
                print("Backend: Config carregada com sucesso.")
            con.close()
        except Exception as e:
            print(f"Backend Erro ao carregar config: {e}")
            self.config = {}

    def _save_tokens_to_db(self, new_token_data):
        print("Backend: Salvando novos tokens no DB...")
        try:
            con = fdb.connect(**self.DB_CONFIG)
            cur = con.cursor()
            expires_in = new_token_data['expires_in']
            expiration_time = datetime.now() + timedelta(seconds=expires_in)
            sql = "UPDATE MELI_CONFIG SET ACCESS_TOKEN = ?, REFRESH_TOKEN = ?, TOKEN_EXPIRATION_TIME = ? WHERE ID = 1"
            params = (new_token_data['access_token'], new_token_data['refresh_token'], expiration_time)
            cur.execute(sql, params)
            con.commit()
            con.close()
            print("Backend: Tokens salvos com sucesso.")
            return True
        except Exception as e:
            print(f"Backend Erro ao salvar tokens: {e}")
            return False

    def _refresh_token(self):
        print("Backend: Renovando token...")
        url = f"{self.base_url}/oauth/token"
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.config.get('app_id'),
            'client_secret': self.config.get('client_secret'),
            'refresh_token': self.config.get('refresh_token')
        }
        try:
            response = self.session.post(url, data=payload, timeout=15)
            response.raise_for_status()
            new_token_data = response.json()
            self.config['access_token'] = new_token_data['access_token']
            self.config['refresh_token'] = new_token_data['refresh_token']
            self._save_tokens_to_db(new_token_data)
            return True
        except requests.exceptions.RequestException as e:
            print(f"Backend Erro ao renovar token: {e}")
            if hasattr(e, 'response') and e.response: print(f"Resposta do servidor: {e.response.text}")
            return False

    def _is_token_expired(self):
        expiration_time = self.config.get('expiration_time')
        if not expiration_time: return True
        return datetime.now() >= (expiration_time - timedelta(minutes=5))

    def _make_request(self, method, url, **kwargs):
        print(f"Backend: Fazendo request para {url}")
        if self._is_token_expired():
            if not self._refresh_token():
                raise Exception("Nao foi possivel renovar o token de acesso.")
        
        self.session.headers.update({'Authorization': f'Bearer {self.config.get("access_token")}'})
        
        try:
            kwargs.setdefault('timeout', 15)
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            print(f"Backend: Sucesso no request para {url}")
            return response.json()
        except Exception as e:
            print(f"Backend Erro no make_request para {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   -> Resposta do Servidor: {e.response.text}")
            raise e

    def is_configured(self):
        return 'access_token' in self.config and self.config['access_token']

    def get_seller_id(self):
        return self.config.get('user_id')

    def get_local_products(self):
        print("Backend: Buscando produtos locais no DB...")
        products = []
        try:
            con = fdb.connect(**self.DB_CONFIG)
            cur = con.cursor()
            cur.execute("SELECT ID, NOME, MELI_ID, QUANTIDADE_ESTOQUE FROM PRODUTOS ORDER BY NOME")
            for row in cur.fetchall():
                products.append({
                    'id_local': row[0], 'nome': row[1],
                    'meli_id': row[2], 'estoque': row[3]
                })
            con.close()
        except Exception as e:
            print(f"Backend Erro ao buscar produtos locais: {e}")
        return products

    def get_meli_active_listings(self):
        seller_id = self.get_seller_id()
        if not seller_id: return []
        
        url = f"{self.base_url}/users/{seller_id}/items/search?status=active"
        listings = []
        try:
            data = self._make_request('get', url)
            meli_ids = data.get('results', [])
            
            if not meli_ids: return []

            url_details = f"{self.base_url}/items?ids={','.join(meli_ids[:20])}"
            items_details = self._make_request('get', url_details)

            for item in items_details:
                body = item.get('body', {})
                if body.get('error'): continue
                
                listings.append({
                    'meli_id': body.get('id'), 'titulo': body.get('title'),
                    'estoque': body.get('available_quantity'), 'preco': body.get('price'),
                    'link': body.get('permalink')
                })
        except Exception as e:
            print(f"Backend Erro ao buscar anuncios do MELI: {e}")
        return listings

    def link_product(self, id_local, meli_id):
        print(f"Backend: Vinculando produto local {id_local} com MELI ID {meli_id}...")
        try:
            con = fdb.connect(**self.DB_CONFIG)
            cur = con.cursor()
            cur.execute("UPDATE PRODUTOS SET MELI_ID = ? WHERE ID = ?", (meli_id, id_local))
            con.commit()
            con.close()
            print("Backend: Vínculo salvo com sucesso!")
            return True
        except Exception as e:
            print(f"Backend Erro ao vincular produto: {e}")
            return False
            
    def atualizar_estoque_meli(self, meli_id, nova_quantidade):
        """
        Atualiza a quantidade de um anúncio, lidando com variações e limpando o payload.
        """
        print(f"Backend: Atualizando estoque do item {meli_id} para {nova_quantidade}...")
        
        url_item_details = f"{self.base_url}/items/{meli_id}"
        try:
            item_data = self._make_request('get', url_item_details)
        except Exception as e:
            print(f"❌ ERRO ao buscar detalhes do item {meli_id}: {e}")
            return None

        variations = item_data.get('variations', [])
        url_put = f"{self.base_url}/items/{meli_id}"
        
        if variations:
            print(f"Backend: Item {meli_id} tem variações. Montando payload de variação.")
            
            # --- A MUDANÇA CRUCIAL ESTÁ AQUI ---
            # Vamos criar um novo payload de variação limpo,
            # contendo apenas os campos que a API precisa.
            
            payload_variations = []
            for var in variations:
                # Removemos o campo problemático e outros que não são necessários para a atualização
                var.pop('catalog_product_id', None) 
                var.pop('attributes', None) # Também é bom remover este
                
                payload_variations.append(var)
                
            # Atualizamos o estoque da primeira variação (como antes)
            payload_variations[0]['available_quantity'] = int(nova_quantidade)
            
            payload = {"variations": payload_variations}
        else:
            print(f"Backend: Item {meli_id} não tem variações. Atualizando estoque geral.")
            payload = {"available_quantity": int(nova_quantidade)}

        try:
            response_data = self._make_request('put', url_put, json=payload)
            print("✅ SUCESSO! Estoque atualizado no Mercado Livre.")
            return response_data
        except Exception as e:
            print(f"❌ ERRO ao atualizar estoque: {e}")
            return None

    # <<< MÉTODOS DE LEITURA REINSERIDOS AQUI >>>
    def get_vendas_hoje(self):
        try:
            hoje = datetime.now()
            date_from = hoje.strftime('%Y-%m-%dT00:00:00.000-03:00')
            date_to = hoje.strftime('%Y-%m-%dT23:59:59.999-03:00')
            url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&order.date_created.from={date_from}&order.date_created.to={date_to}"
            pedidos = self._make_request('get', url).get('results', [])
            return sum(p['total_amount'] for p in pedidos if p['status'] in ['paid', 'shipped', 'delivered'])
        except Exception: return 0.0

    def get_vendas_mes(self):
        try:
            hoje = datetime.now()
            primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0)
            date_from = primeiro_dia_mes.strftime('%Y-%m-%dT%H:%M:%S.000-03:00')
            date_to = hoje.strftime('%Y-%m-%dT%H:%M:%S.999-03:00')
            url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&order.date_created.from={date_from}&order.date_created.to={date_to}"
            pedidos = self._make_request('get', url).get('results', [])
            return sum(p['total_amount'] for p in pedidos if p['status'] in ['paid', 'shipped', 'delivered'])
        except Exception: return 0.0
    
    def get_pedidos_pendentes(self):
        try:
            url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&order.status=paid"
            data = self._make_request('get', url)
            return data.get('paging', {}).get('total', 0)
        except Exception: return 0

    def get_produtos_online(self):
        try:
            url = f"{self.base_url}/users/{self.get_seller_id()}/items/search?status=active"
            data = self._make_request('get', url)
            return data.get('paging', {}).get('total', 0)
        except Exception: return 0

    def get_ultimas_vendas(self, limit=50):
        try:
            url = f"{self.base_url}/orders/search?seller={self.get_seller_id()}&sort=date_desc&limit={limit}"
            pedidos = self._make_request('get', url).get('results', [])
            vendas_formatadas = []
            for pedido in pedidos:
                if not pedido['order_items']: continue
                primeiro_item = pedido['order_items'][0]['item']
                venda = {
                    'data': datetime.fromisoformat(pedido['date_created']).strftime('%d/%m/%Y %H:%M'),
                    'plataforma': 'Mercado Livre', 'produto': primeiro_item['title'],
                    'cliente': pedido['buyer']['nickname'], 'valor': f"R$ {pedido['total_amount']:.2f}".replace('.',','),
                    'status': pedido.get('shipping', {}).get('status', pedido.get('status', 'N/A')).replace('_', ' ').title()
                }
                vendas_formatadas.append(venda)
            return vendas_formatadas
        except Exception: return []

# ==============================================================================
# FIM DA CLASSE MercadoLivreBackend
# ==============================================================================


# ==============================================================================
# INÍCIO DA JANELA DE VINCULAÇÃO
# ==============================================================================
class VincularProdutosWindow(QMainWindow):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Vincular Produtos com Mercado Livre")
        screen_geometry = QApplication.desktop().availableGeometry()
        self.setGeometry(
            int(screen_geometry.x() + screen_geometry.width() * 0.05),
            int(screen_geometry.y() + screen_geometry.height() * 0.05),
            int(screen_geometry.width() * 0.9),
            int(screen_geometry.height() * 0.9)
        )
        self.init_ui()
        self.carregar_listas()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        local_panel = QFrame()
        local_layout = QVBoxLayout(local_panel)
        local_label = QLabel("Produtos do seu Sistema")
        local_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.tabela_local = QTableWidget()
        self.tabela_local.setColumnCount(4)
        self.tabela_local.setHorizontalHeaderLabels(["ID Local", "Produto", "Estoque", "Vinculado a"])
        self.tabela_local.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_local.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela_local.setEditTriggers(QTableWidget.NoEditTriggers)
        local_layout.addWidget(local_label)
        local_layout.addWidget(self.tabela_local)
        
        link_panel = QFrame()
        link_layout = QVBoxLayout(link_panel)
        link_layout.addStretch()
        self.btn_vincular = QPushButton("➡️\nVincular\n➡️")
        self.btn_vincular.setMinimumHeight(100)
        self.btn_vincular.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_vincular.clicked.connect(self.vincular_selecionados)
        link_layout.addWidget(self.btn_vincular)
        link_layout.addStretch()
        
        meli_panel = QFrame()
        meli_layout = QVBoxLayout(meli_panel)
        meli_label = QLabel("Anúncios do Mercado Livre (Ativos)")
        meli_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.tabela_meli = QTableWidget()
        self.tabela_meli.setColumnCount(3)
        self.tabela_meli.setHorizontalHeaderLabels(["Anúncio", "Estoque", "Preço"])
        self.tabela_meli.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_meli.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela_meli.setEditTriggers(QTableWidget.NoEditTriggers)
        meli_layout.addWidget(meli_label)
        meli_layout.addWidget(self.tabela_meli)

        main_layout.addWidget(local_panel, 2)
        main_layout.addWidget(link_panel, 1)
        main_layout.addWidget(meli_panel, 3)

    def carregar_listas(self):
        produtos_locais = self.backend.get_local_products()
        self.tabela_local.setRowCount(len(produtos_locais))
        for row, prod in enumerate(produtos_locais):
            self.tabela_local.setItem(row, 0, QTableWidgetItem(str(prod['id_local'])))
            self.tabela_local.setItem(row, 1, QTableWidgetItem(prod['nome']))
            self.tabela_local.setItem(row, 2, QTableWidgetItem(str(prod['estoque'])))
            vinculo_item = QTableWidgetItem(prod['meli_id'] or "---")
            if prod['meli_id']:
                vinculo_item.setBackground(QColor("#d4edda"))
            self.tabela_local.setItem(row, 3, vinculo_item)

        anuncios_meli = self.backend.get_meli_active_listings()
        self.tabela_meli.setRowCount(len(anuncios_meli))
        for row, anuncio in enumerate(anuncios_meli):
            item_titulo = QTableWidgetItem(anuncio['titulo'])
            item_titulo.setData(Qt.UserRole, anuncio['meli_id'])
            self.tabela_meli.setItem(row, 0, item_titulo)
            self.tabela_meli.setItem(row, 1, QTableWidgetItem(str(anuncio['estoque'])))
            self.tabela_meli.setItem(row, 2, QTableWidgetItem(f"R$ {anuncio['preco']:.2f}"))
            
        self.tabela_local.resizeColumnsToContents()
        self.tabela_meli.resizeColumnsToContents()
        self.tabela_meli.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def vincular_selecionados(self):
        linha_local = self.tabela_local.currentRow()
        linha_meli = self.tabela_meli.currentRow()

        if linha_local == -1 or linha_meli == -1:
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione uma linha em cada tabela para vincular.")
            return
    
        id_local_str = self.tabela_local.item(linha_local, 0).text()
        id_local = int(id_local_str)
        nome_local = self.tabela_local.item(linha_local, 1).text()
        
        item_meli = self.tabela_meli.item(linha_meli, 0)
        meli_id = item_meli.data(Qt.UserRole)
        titulo_meli = item_meli.text()

        reply = QMessageBox.question(self, "Confirmar Vínculo", 
            f"Você tem certeza que deseja vincular:\n\n"
            f"Produto Local: (ID {id_local}) {nome_local}\n"
            f"COM\n"
            f"Anúncio MELI: {titulo_meli}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.backend.link_product(id_local, meli_id):
                QMessageBox.information(self, "Sucesso", "Produto vinculado com sucesso!")
                self.carregar_listas()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar o vínculo no banco de dados.")

# ==============================================================================
# INÍCIO DA JANELA PRINCIPAL DO PAINEL
# ==============================================================================
class MercadoLivreWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.janela_vincular = None
        print("Janela: __init__")
        self.backend = MercadoLivreBackend()
        self.init_ui()
        self.carregar_dados_reais()
    
    def init_ui(self):
        print("Janela: init_ui")
        self.setWindowTitle("Painel Mercado Livre")
        self.setStyleSheet("background-color: #f8f9fa;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        self.criar_header(main_layout)
        self.criar_resumo(main_layout)
        self.criar_tabela_vendas(main_layout)
    
    def criar_header(self, layout_pai):
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2); border-radius: 15px; }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        titulo = QLabel("💰 Painel Mercado Livre")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white; background: transparent;")
        
        info = QLabel("Todas as suas vendas do Mercado Livre em um só lugar")
        info.setFont(QFont("Arial", 12))
        info.setStyleSheet("color: white; background: transparent;")
        info.setAlignment(Qt.AlignRight)
        
        btn_vincular_produtos = QPushButton("🔗 Vincular Produtos")
        btn_vincular_produtos.setFont(QFont("Arial", 12, QFont.Bold))
        btn_vincular_produtos.setStyleSheet("""
            QPushButton { background-color: #ffffff; color: #333; padding: 10px 15px; border-radius: 5px; border: 1px solid #ccc; }
            QPushButton:hover { background-color: #f0f0f0; }
        """)
        btn_vincular_produtos.setCursor(QCursor(Qt.PointingHandCursor))
        btn_vincular_produtos.clicked.connect(self.abrir_janela_vincular)
        
        btn_simular_venda = QPushButton("💸 Simular Sincronização")
        btn_simular_venda.setStyleSheet("background-color: #dc3545; color: white; padding: 10px;")
        btn_simular_venda.setFont(QFont("Arial", 10, QFont.Bold))
        btn_simular_venda.clicked.connect(self.simular_venda_local_e_sincronizar)

        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(btn_simular_venda)
        header_layout.addWidget(btn_vincular_produtos)
        header_layout.addWidget(info)
        layout_pai.addWidget(header_frame)
    
    def criar_resumo(self, layout_pai):
        resumo_frame = QFrame()
        resumo_frame.setStyleSheet("background: transparent;")
        resumo_layout = QHBoxLayout(resumo_frame)
        resumo_layout.setSpacing(20)
        card1, self.lbl_vendas_hoje = self.criar_card_resumo("Vendas Hoje", "R$ 0,00", "#28a745")
        card2, self.lbl_vendas_mes = self.criar_card_resumo("Vendas do Mês", "R$ 0,00", "#17a2b8")
        card3, self.lbl_pedidos_pendentes = self.criar_card_resumo("Pedidos Pendentes", "0", "#ffc107")
        card4, self.lbl_produtos_online = self.criar_card_resumo("Produtos Online", "0", "#6f42c1")
        resumo_layout.addWidget(card1)
        resumo_layout.addWidget(card2)
        resumo_layout.addWidget(card3)
        resumo_layout.addWidget(card4)
        layout_pai.addWidget(resumo_frame)
    
    def criar_card_resumo(self, titulo, valor, cor):
        card = QFrame()
        card.setFixedSize(250, 100)
        card.setStyleSheet(f"""QFrame {{ background-color: white; border-radius: 10px; border-left: 5px solid {cor}; }}""")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Arial", 12))
        lbl_titulo.setStyleSheet("color: #6c757d;")
        lbl_valor = QLabel(valor)
        lbl_valor.setFont(QFont("Arial", 20, QFont.Bold))
        lbl_valor.setStyleSheet(f"color: {cor};")
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.addStretch()
        return card, lbl_valor
    
    def criar_tabela_vendas(self, layout_pai):
        table_frame = QFrame()
        table_frame.setStyleSheet("""QFrame { background-color: white; border-radius: 10px; border: 1px solid #dee2e6; }""")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        titulo_table = QLabel("📋 Últimas Vendas")
        titulo_table.setFont(QFont("Arial", 16, QFont.Bold))
        titulo_table.setStyleSheet("color: #495057; margin-bottom: 10px;")
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["Data", "Plataforma", "Produto", "Cliente", "Valor", "Status", "Ações"])
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setStyleSheet("""
            QTableWidget { gridline-color: #dee2e6; border: none; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #e9ecef; }
            QHeaderView::section { background-color: #f8f9fa; padding: 12px; border: none; border-bottom: 2px solid #dee2e6; font-weight: bold; color: #495057; }
        """)
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        table_layout.addWidget(titulo_table)
        table_layout.addWidget(self.tabela)
        layout_pai.addWidget(table_frame)
    
    def carregar_dados_reais(self):
        print("Janela: Carregando dados reais...")
        if not self.backend.is_configured():
            QMessageBox.warning(self, "Integração Não Configurada", "Execute o script 'gerar_tokens.py' primeiro.")
            return

        try:
            self.lbl_vendas_hoje.setText(f"R$ {self.backend.get_vendas_hoje():.2f}".replace('.',','))
            self.lbl_vendas_mes.setText(f"R$ {self.backend.get_vendas_mes():.2f}".replace('.',','))
            self.lbl_pedidos_pendentes.setText(str(self.backend.get_pedidos_pendentes()))
            self.lbl_produtos_online.setText(str(self.backend.get_produtos_online()))

            ultimas_vendas = self.backend.get_ultimas_vendas()
            self.tabela.setRowCount(len(ultimas_vendas))
            
            for row, venda in enumerate(ultimas_vendas):
                self.tabela.setItem(row, 0, QTableWidgetItem(venda['data']))
                plataforma_item = QTableWidgetItem(venda['plataforma'])
                plataforma_item.setForeground(QColor("#000000"))
                plataforma_item.setBackground(QColor("#FFF159"))
                plataforma_item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(row, 1, plataforma_item)
                self.tabela.setItem(row, 2, QTableWidgetItem(venda['produto']))
                self.tabela.setItem(row, 3, QTableWidgetItem(venda['cliente']))
                self.tabela.setItem(row, 4, QTableWidgetItem(venda['valor']))
                self.tabela.setItem(row, 5, QTableWidgetItem(venda['status']))
                
                btn_detalhes = QPushButton("👁️ Ver Detalhes")
                btn_detalhes.setStyleSheet("QPushButton { background-color: #6c757d; color: white; border: none; padding: 5px 10px; border-radius: 3px; } QPushButton:hover { background-color: #5a6268; }")
                btn_detalhes.setCursor(QCursor(Qt.PointingHandCursor))
                btn_detalhes.clicked.connect(lambda checked, r=row: self.ver_detalhes(r))
                self.tabela.setCellWidget(row, 6, btn_detalhes)
        except Exception as e:
            print(f"Janela: Erro ao carregar dados na UI: {e}")
            QMessageBox.critical(self, "Erro ao carregar dados", f"Ocorreu um erro: {e}")

    def ver_detalhes(self, row):
        produto = self.tabela.item(row, 2).text()
        cliente = self.tabela.item(row, 3).text()
        QMessageBox.information(self, "Detalhes da Venda", f"Exibindo detalhes para o produto:\n\n{produto}\n\nVendido para: {cliente}")

    def abrir_janela_vincular(self):
        if self.janela_vincular is None or not self.janela_vincular.isVisible():
            self.janela_vincular = VincularProdutosWindow(self.backend)
            self.janela_vincular.show()

    def simular_venda_local_e_sincronizar(self):
        # --- DADOS PARA O NOSSO TESTE ---
        # Substitua pelos IDs do produto que você vinculou
        id_produto_local = 12 
        meli_id_vinculado = "MLB4105289483" # Coloque o ID do anúncio com variações aqui
        # --- FIM DOS DADOS DE TESTE ---

        print(f"--- SIMULANDO SINCRONIZAÇÃO PARA O PRODUTO ID: {id_produto_local} ---")

        # 1. Obter o estoque atual do seu sistema
        estoque_atual_sistema = 0
        try:
            con = fdb.connect(**self.backend.DB_CONFIG)
            cur = con.cursor()
            cur.execute("SELECT QUANTIDADE_ESTOQUE FROM PRODUTOS WHERE ID = ?", (id_produto_local,))
            resultado = cur.fetchone()
            if resultado:
                estoque_atual_sistema = resultado[0]
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro DB", f"Não foi possível ler o estoque local: {e}")
            return
        
        print(f"Estoque ATUAL no sistema é: {estoque_atual_sistema}")
        
        # A simulação agora apenas TENTA enviar o estoque atual para o MELI.
        novo_estoque_para_enviar = estoque_atual_sistema

        reply = QMessageBox.question(self, "Confirmar Sincronização",
            f"Isso tentará sincronizar o estoque do anúncio {meli_id_vinculado} "
            f"para o valor atual do seu sistema, que é {novo_estoque_para_enviar}. Continuar?",
            QMessageBox.Yes | QMessageBox.No)

        if reply != QMessageBox.Yes:
            return

        # 2. CHAMAR A API PARA SINCRONIZAR COM O MERCADO LIVRE
        print(f"Iniciando sincronização com o Mercado Livre para o item {meli_id_vinculado}...")
        resultado_api = self.backend.atualizar_estoque_meli(meli_id_vinculado, novo_estoque_para_enviar)

        if resultado_api:
            QMessageBox.information(self, "Sincronização OK", f"Estoque do anúncio {meli_id_vinculado} atualizado com sucesso no Mercado Livre para {novo_estoque_para_enviar}!")
        else:
            QMessageBox.critical(self, "Falha na Sincronização", "Ocorreu um erro ao tentar atualizar o estoque no Mercado Livre. Verifique o terminal.")

        # Recarrega a tela de vinculação se ela estiver aberta, para vermos as mudanças
        if self.janela_vincular and self.janela_vincular.isVisible():
            self.janela_vincular.carregar_listas()
        
        self.carregar_dados_reais() # Recarrega também o painel principal

# ==============================================================================
# FIM DA JANELA PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MercadoLivreWindow()
    window.showMaximized() 
    sys.exit(app.exec_())