import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QDateEdit, 
    QComboBox, QDialog, QMessageBox, QLineEdit
)
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QDate, QDateTime

try:
    from base.banco import execute_query
except ImportError as e:
    print(f"AVISO: Erro ao importar módulo banco: {e}")
    # Definimos função fictícia para evitar erros
    def execute_query(query, params=None):
        print(f"Query fictícia: {query}")
        print(f"Params: {params}")
        return []

class ListaVendasDialog(QDialog):
    """Janela para exibir a lista de vendas dos últimos 30 dias"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Histórico de Vendas")
        self.setMinimumSize(900, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Configurar o layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Cabeçalho com filtros
        self.criar_cabecalho()
        
        # Tabela de vendas
        self.criar_tabela_vendas()
        
        # Carregar as vendas
        self.carregar_vendas()
    
    def criar_cabecalho(self):
        """Cria o cabeçalho com os filtros de vendas"""
        cabecalho_frame = QFrame()
        cabecalho_frame.setFrameShape(QFrame.StyledPanel)
        cabecalho_layout = QHBoxLayout(cabecalho_frame)
        
        # Filtros por data
        filtro_data_layout = QHBoxLayout()
        lbl_data_inicio = QLabel("Data inicial:")
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate().addDays(-30))  # 30 dias atrás
        
        lbl_data_fim = QLabel("Data final:")
        self.date_fim = QDateEdit()
        self.date_fim.setCalendarPopup(True)
        self.date_fim.setDate(QDate.currentDate())  # Hoje
        
        filtro_data_layout.addWidget(lbl_data_inicio)
        filtro_data_layout.addWidget(self.date_inicio)
        filtro_data_layout.addWidget(lbl_data_fim)
        filtro_data_layout.addWidget(self.date_fim)
        
        # Filtro por forma de pagamento
        lbl_forma_pagamento = QLabel("Forma de Pagamento:")
        self.combo_forma_pagamento = QComboBox()
        self.combo_forma_pagamento.addItem("Todas")
        self.combo_forma_pagamento.addItem("Dinheiro")
        self.combo_forma_pagamento.addItem("Cartão Débito")
        self.combo_forma_pagamento.addItem("Cartão Crédito")
        
        # Botão de busca
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setFixedWidth(100)
        self.btn_buscar.clicked.connect(self.carregar_vendas)
        
        # Campo de busca por número de venda
        lbl_num_venda = QLabel("Nº Venda:")
        self.entry_num_venda = QLineEdit()
        self.entry_num_venda.setFixedWidth(80)
        self.entry_num_venda.returnPressed.connect(self.carregar_vendas)
        
        # Adicionar todos os filtros ao layout do cabeçalho
        cabecalho_layout.addLayout(filtro_data_layout)
        cabecalho_layout.addWidget(lbl_forma_pagamento)
        cabecalho_layout.addWidget(self.combo_forma_pagamento)
        cabecalho_layout.addWidget(lbl_num_venda)
        cabecalho_layout.addWidget(self.entry_num_venda)
        cabecalho_layout.addStretch(1)
        cabecalho_layout.addWidget(self.btn_buscar)
        
        self.main_layout.addWidget(cabecalho_frame)
    
    def criar_tabela_vendas(self):
        """Cria a tabela onde serão exibidas as vendas"""
        self.table_vendas = QTableWidget()
        self.table_vendas.setColumnCount(7)
        self.table_vendas.setHorizontalHeaderLabels([
            "ID", "DATA", "HORA", "CLIENTE", "VENDEDOR", "VALOR TOTAL", "FORMA PAGAMENTO"
        ])
        
        # Configurar a tabela
        self.table_vendas.setAlternatingRowColors(True)
        self.table_vendas.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_vendas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_vendas.verticalHeader().setVisible(False)
        
        # Ajustar os tamanhos das colunas
        header = self.table_vendas.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # DATA
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # HORA
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # CLIENTE
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # VENDEDOR
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # VALOR TOTAL
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # FORMA PAGAMENTO
        
        # Conectar eventos
        self.table_vendas.doubleClicked.connect(self.visualizar_detalhes_venda)
        
        # Adicionar tabela ao layout principal
        self.main_layout.addWidget(self.table_vendas)
        
        # Botões de ação - MODIFICADO: Removidos botões Visualizar e Imprimir
        botoes_layout = QHBoxLayout()
        
        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.clicked.connect(self.close)
        
        botoes_layout.addStretch(1)
        botoes_layout.addWidget(self.btn_fechar)
        
        self.main_layout.addLayout(botoes_layout)

    
    def carregar_vendas(self):
        """Carrega as vendas de acordo com os filtros selecionados"""
        try:
            # Limpar a tabela
            self.table_vendas.setRowCount(0)
            
            # Obter os filtros
            data_inicio = self.date_inicio.date().toString("yyyy-MM-dd")
            data_fim = self.date_fim.date().toString("yyyy-MM-dd")
            forma_pagamento = self.combo_forma_pagamento.currentText()
            num_venda = self.entry_num_venda.text().strip()
            
            # Construir a query
            query = """
            SELECT ID_VENDA, DATA_VENDA, HORA_VENDA, ID_CLIENTE, ID_VENDEDOR, 
                   VALOR_FINAL, FORMA_PAGAMENTO, STATUS
            FROM VENDAS
            WHERE 1=1
            """
            
            params = []
            
            # Adicionar filtros à query
            if num_venda:
                query += " AND ID_VENDA = ?"
                params.append(int(num_venda) if num_venda.isdigit() else 0)
            else:
                # Filtros de data só se aplicam se não estiver buscando por número específico
                query += " AND DATA_VENDA BETWEEN ? AND ?"
                params.append(data_inicio)
                params.append(data_fim)
                
                # Filtro de forma de pagamento
                if forma_pagamento != "Todas":
                    query += " AND FORMA_PAGAMENTO LIKE ?"
                    params.append(f"%{forma_pagamento}%")
            
            # Ordenar por data e hora (mais recentes primeiro)
            query += " ORDER BY DATA_VENDA DESC, HORA_VENDA DESC"
            
            # Executar a query
            vendas = execute_query(query, tuple(params) if params else None)
            
            # Preencher a tabela
            for row, venda in enumerate(vendas):
                self.table_vendas.insertRow(row)
                
                # ID
                self.table_vendas.setItem(row, 0, QTableWidgetItem(str(venda[0])))
                
                # DATA (converter de YYYY-MM-DD para DD/MM/YYYY)
                data_str = venda[1]
                try:
                    # Tentar formatar a data se for um objeto date
                    if hasattr(data_str, 'strftime'):
                        data_str = data_str.strftime("%d/%m/%Y")
                    # Se for string no formato YYYY-MM-DD
                    elif isinstance(data_str, str) and len(data_str) == 10:
                        data_str = f"{data_str[8:10]}/{data_str[5:7]}/{data_str[0:4]}"
                except Exception as e:
                    print(f"Erro ao formatar data: {e}")
                
                self.table_vendas.setItem(row, 1, QTableWidgetItem(data_str))
                
                # HORA
                self.table_vendas.setItem(row, 2, QTableWidgetItem(str(venda[2])))
                
                # CLIENTE - Buscar o nome do cliente pelo ID
                id_cliente = venda[3]
                nome_cliente = self.buscar_nome_cliente(id_cliente) or f"Cliente {id_cliente}"
                self.table_vendas.setItem(row, 3, QTableWidgetItem(nome_cliente))
                
                # VENDEDOR - Buscar o nome do vendedor pelo ID
                id_vendedor = venda[4]
                nome_vendedor = self.buscar_nome_vendedor(id_vendedor) or f"Vendedor {id_vendedor}"
                self.table_vendas.setItem(row, 4, QTableWidgetItem(nome_vendedor))
                
                # VALOR TOTAL (formatar como moeda)
                valor = float(venda[5])
                valor_formatado = f"R$ {valor:.2f}".replace('.', ',')
                valor_item = QTableWidgetItem(valor_formatado)
                valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_vendas.setItem(row, 5, valor_item)
                
                # FORMA PAGAMENTO
                self.table_vendas.setItem(row, 6, QTableWidgetItem(str(venda[6])))
                
                # Definir cores com base no status
                status = venda[7]
                if status == "Cancelada":
                    # Aplicar cor vermelha para vendas canceladas
                    for col in range(self.table_vendas.columnCount()):
                        item = self.table_vendas.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 200, 200))
            
            # Exibir mensagem se nenhuma venda for encontrada
            if self.table_vendas.rowCount() == 0:
                QMessageBox.information(self, "Aviso", "Nenhuma venda encontrada para os filtros selecionados.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar vendas: {str(e)}")
    
    def buscar_nome_cliente(self, id_cliente):
        """Busca o nome do cliente pelo ID"""
        if not id_cliente or id_cliente == 0:
            return "Cliente não identificado"
            
        try:
            # Buscar na tabela PESSOAS onde TIPO_PESSOA é cliente
            query = """
            SELECT NOME FROM PESSOAS
            WHERE ID = ? AND (TIPO_PESSOA = 'Física' OR TIPO_PESSOA = 'Jurídica')
            """
            result = execute_query(query, (id_cliente,))
            
            if result and len(result) > 0:
                return result[0][0]
                
            return None
        except Exception as e:
            print(f"Erro ao buscar nome do cliente: {e}")
            return None
    
    def buscar_nome_vendedor(self, id_vendedor):
        """Busca o nome do vendedor pelo ID"""
        if not id_vendedor or id_vendedor == 0:
            return "Vendedor não identificado"
            
        try:
            # Buscar na tabela FUNCIONARIOS onde TIPO_VENDEDOR é vendedor
            query = """
            SELECT NOME FROM FUNCIONARIOS
            WHERE ID = ?
            """
            result = execute_query(query, (id_vendedor,))
            
            if result and len(result) > 0:
                return result[0][0]
                
            return None
        except Exception as e:
            print(f"Erro ao buscar nome do vendedor: {e}")
            return None
    
    def visualizar_detalhes_venda(self):
        """Abre uma janela com os detalhes da venda selecionada"""
        # Obter a linha selecionada
        selected_rows = self.table_vendas.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma venda para visualizar.")
            return
        
        # Obter o ID da venda
        row = selected_rows[0].row()
        id_venda = int(self.table_vendas.item(row, 0).text())
        
        # Abrir a janela de detalhes
        detalhes_dialog = DetalhesVendaDialog(id_venda, self)
        detalhes_dialog.exec_()
    
    def imprimir_venda(self):
        """Imprime a venda selecionada (comprovante)"""
        # Obter a linha selecionada
        selected_rows = self.table_vendas.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma venda para imprimir.")
            return
        
        # Obter o ID da venda
        row = selected_rows[0].row()
        id_venda = int(self.table_vendas.item(row, 0).text())
        
        try:
            # Aqui você pode implementar a lógica para imprimir o comprovante de venda
            # Por enquanto, exibimos apenas uma mensagem
            QMessageBox.information(self, "Impressão", 
                                   f"Enviando venda {id_venda} para impressão...\n"
                                   f"(Funcionalidade a ser implementada)")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao imprimir venda: {str(e)}")

class DetalhesVendaDialog(QDialog):
    """Janela para exibir os detalhes de uma venda"""
    
    def __init__(self, id_venda, parent=None):
        super().__init__(parent)
        
        self.id_venda = id_venda
        self.setWindowTitle(f"Detalhes da Venda #{id_venda}")
        self.setMinimumSize(700, 500)
        
        # Configurar o layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Criar o cabeçalho com informações da venda
        self.criar_cabecalho_venda()
        
        # Criar a tabela de itens
        self.criar_tabela_itens()
        
        # Carregar os dados da venda
        self.carregar_dados_venda()
        
        # Botão para fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(btn_fechar, alignment=Qt.AlignRight)
    
    def criar_cabecalho_venda(self):
        """Cria o cabeçalho com as informações gerais da venda"""
        # Frame para informações da venda
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        
        # Título
        lbl_titulo = QLabel(f"VENDA #{self.id_venda}")
        lbl_titulo.setStyleSheet("font-size: 16pt; font-weight: bold;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(lbl_titulo)
        
        # Grid para os dados principais
        dados_layout = QHBoxLayout()
        
        # Coluna 1 - Data, Hora, Cliente
        col1_layout = QVBoxLayout()
        self.lbl_data = QLabel("Data: --/--/----")
        self.lbl_hora = QLabel("Hora: --:--:--")
        self.lbl_cliente = QLabel("Cliente: ------")
        
        col1_layout.addWidget(self.lbl_data)
        col1_layout.addWidget(self.lbl_hora)
        col1_layout.addWidget(self.lbl_cliente)
        
        # Coluna 2 - Vendedor, Forma Pagamento, Status
        col2_layout = QVBoxLayout()
        self.lbl_vendedor = QLabel("Vendedor: ------")
        self.lbl_forma_pagamento = QLabel("Forma de Pagamento: ------")
        self.lbl_status = QLabel("Status: ------")
        
        col2_layout.addWidget(self.lbl_vendedor)
        col2_layout.addWidget(self.lbl_forma_pagamento)
        col2_layout.addWidget(self.lbl_status)
        
        # Coluna 3 - Valores
        col3_layout = QVBoxLayout()
        self.lbl_subtotal = QLabel("Subtotal: R$ 0,00")
        self.lbl_desconto = QLabel("Desconto: R$ 0,00")
        self.lbl_total = QLabel("Total: R$ 0,00")
        self.lbl_total.setStyleSheet("font-size: 14pt; font-weight: bold;")
        
        col3_layout.addWidget(self.lbl_subtotal)
        col3_layout.addWidget(self.lbl_desconto)
        col3_layout.addWidget(self.lbl_total)
        
        # Adicionar as colunas ao layout de dados
        dados_layout.addLayout(col1_layout)
        dados_layout.addLayout(col2_layout)
        dados_layout.addLayout(col3_layout)
        
        info_layout.addLayout(dados_layout)
        
        self.main_layout.addWidget(info_frame)
    
    def criar_tabela_itens(self):
        """Cria a tabela para exibir os itens da venda"""
        # Label para a seção de itens
        lbl_itens = QLabel("ITENS DA VENDA")
        lbl_itens.setStyleSheet("font-size: 12pt; font-weight: bold;")
        self.main_layout.addWidget(lbl_itens)
        
        # Tabela de itens
        self.table_itens = QTableWidget()
        self.table_itens.setColumnCount(5)
        self.table_itens.setHorizontalHeaderLabels([
            "ITEM", "PRODUTO", "QUANTIDADE", "VALOR UNIT.", "VALOR TOTAL"
        ])
        
        # Configurar a tabela
        self.table_itens.setAlternatingRowColors(True)
        self.table_itens.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_itens.verticalHeader().setVisible(False)
        
        # Ajustar os tamanhos das colunas
        header = self.table_itens.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ITEM
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # PRODUTO
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # QUANTIDADE
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # VALOR UNIT.
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # VALOR TOTAL
        
        self.main_layout.addWidget(self.table_itens)
    
    def carregar_dados_venda(self):
        """Carrega os dados da venda selecionada"""
        try:
            # Buscar dados da venda
            query_venda = """
            SELECT DATA_VENDA, HORA_VENDA, ID_CLIENTE, ID_VENDEDOR,
                   VALOR_TOTAL, DESCONTO, VALOR_FINAL, FORMA_PAGAMENTO, STATUS
            FROM VENDAS
            WHERE ID_VENDA = ?
            """
            
            result_venda = execute_query(query_venda, (self.id_venda,))
            
            if not result_venda or len(result_venda) == 0:
                QMessageBox.warning(self, "Aviso", "Venda não encontrada.")
                self.close()
                return
            
            venda = result_venda[0]
            
            # Formatar data (YYYY-MM-DD para DD/MM/YYYY)
            data_str = venda[0]
            if hasattr(data_str, 'strftime'):
                data_str = data_str.strftime("%d/%m/%Y")
            elif isinstance(data_str, str) and len(data_str) == 10:
                data_str = f"{data_str[8:10]}/{data_str[5:7]}/{data_str[0:4]}"
            
            # Atualizar os labels com as informações da venda
            self.lbl_data.setText(f"Data: {data_str}")
            self.lbl_hora.setText(f"Hora: {venda[1]}")
            
            # Buscar nome do cliente
            id_cliente = venda[2]
            nome_cliente = self.buscar_nome_cliente(id_cliente) or f"Cliente {id_cliente}"
            self.lbl_cliente.setText(f"Cliente: {nome_cliente}")
            
            # Buscar nome do vendedor
            id_vendedor = venda[3]
            nome_vendedor = self.buscar_nome_vendedor(id_vendedor) or f"Vendedor {id_vendedor}"
            self.lbl_vendedor.setText(f"Vendedor: {nome_vendedor}")
            
            # Valores
            valor_total = float(venda[4])
            desconto = float(venda[5])
            valor_final = float(venda[6])
            
            self.lbl_subtotal.setText(f"Subtotal: R$ {valor_total:.2f}".replace('.', ','))
            self.lbl_desconto.setText(f"Desconto: R$ {desconto:.2f}".replace('.', ','))
            self.lbl_total.setText(f"Total: R$ {valor_final:.2f}".replace('.', ','))
            
            # Forma de pagamento e status
            self.lbl_forma_pagamento.setText(f"Forma de Pagamento: {venda[7]}")
            self.lbl_status.setText(f"Status: {venda[8]}")
            
            # Colorir status de acordo com o valor
            if venda[8] == "Cancelada":
                self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
            elif venda[8] == "Finalizada":
                self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
            
            # Buscar os itens da venda
            self.carregar_itens_venda()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados da venda: {str(e)}")
    
    def carregar_itens_venda(self):
        """Carrega os itens da venda na tabela"""
        try:
            # Buscar itens da venda
            query_itens = """
            SELECT VI.ID_PRODUTO, P.NOME, VI.QUANTIDADE, VI.VALOR_UNITARIO, VI.VALOR_TOTAL
            FROM VENDAS_ITENS VI
            LEFT JOIN PRODUTOS P ON VI.ID_PRODUTO = P.CODIGO
            WHERE VI.ID_VENDA = ?
            ORDER BY VI.ID_PRODUTO
            """
            
            result_itens = execute_query(query_itens, (self.id_venda,))
            
            # Limpar a tabela
            self.table_itens.setRowCount(0)
            
            # Preencher a tabela com os itens
            for idx, item in enumerate(result_itens):
                row = self.table_itens.rowCount()
                self.table_itens.insertRow(row)
                
                # ITEM (número sequencial)
                self.table_itens.setItem(row, 0, QTableWidgetItem(str(idx + 1)))
                
                # PRODUTO (código + nome)
                id_produto = item[0]
                nome_produto = item[1] or f"Produto {id_produto}"
                produto_str = f"{id_produto} - {nome_produto}"
                self.table_itens.setItem(row, 1, QTableWidgetItem(produto_str))
                
                # QUANTIDADE
                quantidade = int(item[2])
                self.table_itens.setItem(row, 2, QTableWidgetItem(str(quantidade)))
                
                # VALOR UNITÁRIO
                valor_unit = float(item[3])
                valor_unit_str = f"R$ {valor_unit:.2f}".replace('.', ',')
                valor_unit_item = QTableWidgetItem(valor_unit_str)
                valor_unit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_itens.setItem(row, 3, valor_unit_item)
                
                # VALOR TOTAL
                valor_total = float(item[4])
                valor_total_str = f"R$ {valor_total:.2f}".replace('.', ',')
                valor_total_item = QTableWidgetItem(valor_total_str)
                valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_itens.setItem(row, 4, valor_total_item)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar itens da venda: {str(e)}")
    
    def buscar_nome_cliente(self, id_cliente):
        """Busca o nome do cliente pelo ID"""
        if not id_cliente or id_cliente == 0:
            return "Cliente não identificado"
            
        try:
            # Buscar na tabela PESSOAS onde TIPO_PESSOA é cliente
            query = """
            SELECT NOME FROM PESSOAS
            WHERE ID = ? AND (TIPO_PESSOA = 'Física' OR TIPO_PESSOA = 'Jurídica')
            """
            result = execute_query(query, (id_cliente,))
            
            if result and len(result) > 0:
                return result[0][0]
                
            return None
        except Exception as e:
            print(f"Erro ao buscar nome do cliente: {e}")
            return None
    
    def buscar_nome_vendedor(self, id_vendedor):
        """Busca o nome do vendedor pelo ID"""
        if not id_vendedor or id_vendedor == 0:
            return "Vendedor não identificado"
            
        try:
            # Buscar na tabela FUNCIONARIOS onde TIPO_VENDEDOR é vendedor
            query = """
            SELECT NOME FROM FUNCIONARIOS
            WHERE ID = ?
            """
            result = execute_query(query, (id_vendedor,))
            
            if result and len(result) > 0:
                return result[0][0]
                
            return None
        except Exception as e:
            print(f"Erro ao buscar nome do vendedor: {e}")
            return None
    
def abrir_janela_vendas(parent=None):
    """Abre a janela de histórico de vendas"""
    dialog = ListaVendasDialog(parent)
    dialog.exec_()


if __name__ == "__main__":
    # Teste direto do módulo
    app = QApplication(sys.argv)
    dialog = ListaVendasDialog()
    dialog.show()
    sys.exit(app.exec_())