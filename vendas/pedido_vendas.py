import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QDateEdit, QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QDate


# Primeiro definimos a classe do formulário que antes estava em outro arquivo
class FormularioPedidoVendas(QWidget):
    def __init__(self, janela_parent=None, num_pedido=None, cliente=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.num_pedido = num_pedido
        self.cliente = cliente
        self.initUI()
        
        # Se estiver alterando um pedido existente, preencher os campos
        if self.num_pedido and self.cliente:
            self.preencher_campos()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#003b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
    
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Fundo para todo o aplicativo
        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())
        
        # Layout para o título centralizado (sem botão voltar)
        header_layout = QHBoxLayout()
        
        # Título centralizado
        titulo = QLabel("Cadastro de Pedido de vendas")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Estilo para DateEdit com ícone de calendário
        dateedit_style = """
            QDateEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QDateEdit:focus {
                border: 1px solid #0078d7;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit::down-arrow {
                width: 16px;
                height: 16px;
                image: url(ico-img/calendar-outline.svg);
            }
        """
        
        # Primeira linha - Número do Pedido e Cliente
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(10)
        
        # Campo Número do Pedido
        num_pedido_label = QLabel("Num. Pedido:")
        num_pedido_label.setStyleSheet("color: white; font-size: 16px;")
        linha1_layout.addWidget(num_pedido_label)
        
        self.num_pedido_input = QLineEdit()
        self.num_pedido_input.setStyleSheet(lineedit_style)
        self.num_pedido_input.setFixedWidth(150)
        if self.num_pedido:
            self.num_pedido_input.setText(self.num_pedido)
        linha1_layout.addWidget(self.num_pedido_input)
        
        # Campo Cliente
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        linha1_layout.addWidget(cliente_label)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setStyleSheet(lineedit_style)
        if self.cliente:
            self.cliente_input.setText(self.cliente)
        linha1_layout.addWidget(self.cliente_input, 1)
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha - Vendedor e Valor
        linha2_layout = QHBoxLayout()
        linha2_layout.setSpacing(10)
        
        # Campo Vendedor
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        linha2_layout.addWidget(vendedor_label)
        
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setStyleSheet(lineedit_style)
        linha2_layout.addWidget(self.vendedor_input, 1)
        
        # Campo Valor
        valor_label = QLabel("Valor:")
        valor_label.setStyleSheet("color: white; font-size: 16px;")
        linha2_layout.addWidget(valor_label)
        
        self.valor_input = QLineEdit()
        self.valor_input.setStyleSheet(lineedit_style)
        self.valor_input.setFixedWidth(150)
        linha2_layout.addWidget(self.valor_input)
        
        main_layout.addLayout(linha2_layout)
        
        # Terceira linha - Produto e Data
        linha3_layout = QHBoxLayout()
        linha3_layout.setSpacing(10)
        
        # Campo Produto
        produto_label = QLabel("Produto:")
        produto_label.setStyleSheet("color: white; font-size: 16px;")
        linha3_layout.addWidget(produto_label)
        
        self.produto_input = QLineEdit()
        self.produto_input.setStyleSheet(lineedit_style)
        linha3_layout.addWidget(self.produto_input, 1)
        
        # Campo Data
        data_label = QLabel("Data:")
        data_label.setStyleSheet("color: white; font-size: 16px;")
        linha3_layout.addWidget(data_label)
        
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setStyleSheet(dateedit_style)
        
        # Configurar calendário
        try:
            calendar = self.data_input.calendarWidget()
            calendar.setStyleSheet("""
                QCalendarWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    background-color: #003b57;
                    color: white;
                    selection-background-color: #005079;
                    selection-color: white;
                }
                QCalendarWidget QToolButton {
                    background-color: #003b57;
                    color: white;
                }
                QCalendarWidget QMenu {
                    background-color: #003b57;
                    color: white;
                }
            """)
        except:
            pass
            
        linha3_layout.addWidget(self.data_input)
        
        main_layout.addLayout(linha3_layout)
        
        # Botão Incluir
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 15px 0;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 20px 0;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
            QPushButton:pressed {
                background-color: #00cc7a;
            }
        """)
        self.btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(self.btn_incluir)
        
        # Adicionar espaço no final
        main_layout.addStretch()
    
    def preencher_campos(self):
        """Preenche os campos com os dados do pedido para alteração"""
        # Aqui você pode implementar a lógica para buscar os dados completos
        # do pedido e preencher todos os campos. Por agora, vamos simular alguns dados
        self.vendedor_input.setText("Carlos")
        self.valor_input.setText("R$ 2.450,00")
        self.produto_input.setText("Produto XYZ")
        
        # Mudando o texto do botão para indicar alteração
        self.btn_incluir.setText("Alterar")
    
    # Método voltar foi removido
    
    def incluir(self):
        """Inclui ou altera um pedido"""
        # Validar campos obrigatórios
        num_pedido = self.num_pedido_input.text()
        cliente = self.cliente_input.text()
        vendedor = self.vendedor_input.text()
        valor = self.valor_input.text()
        produto = self.produto_input.text()
        
        if not num_pedido or not cliente or not vendedor or not valor or not produto:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos obrigatórios!")
            return
        
        # Aqui você implementaria a lógica para salvar os dados
        # Por agora, vamos apenas mostrar uma mensagem de sucesso
        
        # Verificar se é inclusão ou alteração
        if self.num_pedido:
            mensagem = "Pedido alterado com sucesso!"
        else:
            mensagem = "Pedido incluído com sucesso!"
        
        self.mostrar_mensagem("Sucesso", mensagem)
        
        # Fechar a janela após a inclusão/alteração
        if self.janela_parent:
            self.janela_parent.close()
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #003b57;
            }
            QLabel { 
                color: white;
                background-color: #003b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        msg_box.exec_()


# Classe principal de Pedido de Vendas
class PedidoVendasWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.initUI()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#003b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
    
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Fundo para todo o aplicativo
        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())
        
        # Layout para o título centralizado (sem botão voltar)
        header_layout = QHBoxLayout()
        
        # Título centralizado
        titulo = QLabel("Pedido de vendas")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Estilo para DateEdit com ícone de calendário
        dateedit_style = """
            QDateEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QDateEdit:focus {
                border: 1px solid #0078d7;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit::down-arrow {
                width: 16px;
                height: 16px;
                image: url(ico-img/calendar-outline.svg);
            }
        """
        
        # Primeira linha de filtros
        filtro_layout1 = QHBoxLayout()
        filtro_layout1.setSpacing(10)
        
        # Campo Vendedor
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout1.addWidget(vendedor_label)
        
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setStyleSheet(lineedit_style)
        filtro_layout1.addWidget(self.vendedor_input, 1)
        
        main_layout.addLayout(filtro_layout1)
        
        # Segunda linha de filtros
        filtro_layout2 = QHBoxLayout()
        filtro_layout2.setSpacing(10)
        
        # Campo Cidade
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(cidade_label)
        
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(lineedit_style)
        filtro_layout2.addWidget(self.cidade_input, 1)
        
        # Campo Data de Entrada
        data_entrada_label = QLabel("Data de Entrada")
        data_entrada_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(data_entrada_label)
        
        self.data_entrada = QDateEdit()
        self.data_entrada.setCalendarPopup(True)
        self.data_entrada.setDate(QDate.currentDate())
        self.data_entrada.setStyleSheet(dateedit_style)
        
        # Configurar calendário para data de entrada
        try:
            calendar = self.data_entrada.calendarWidget()
            calendar.setStyleSheet("""
                QCalendarWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    background-color: #003b57;
                    color: white;
                    selection-background-color: #005079;
                    selection-color: white;
                }
                QCalendarWidget QToolButton {
                    background-color: #003b57;
                    color: white;
                }
                QCalendarWidget QMenu {
                    background-color: #003b57;
                    color: white;
                }
            """)
        except:
            pass
            
        filtro_layout2.addWidget(self.data_entrada)
        
        main_layout.addLayout(filtro_layout2)
        
        # Terceira linha de filtros
        filtro_layout3 = QHBoxLayout()
        # Zera margens internas (esquerda, topo, direita, base)
        filtro_layout3.setContentsMargins(0, 0, 0, 0)
        # Espaçamento mínimo entre widgets
        filtro_layout3.setSpacing(5)

        # Campo Data de Saída
        data_saida_label = QLabel("Data de Saída")
        data_saida_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout3.addWidget(data_saida_label)

        self.data_saida = QDateEdit()
        self.data_saida.setCalendarPopup(True)
        self.data_saida.setDate(QDate.currentDate())
        self.data_saida.setStyleSheet(dateedit_style)
        self.data_saida.setFixedWidth(120)  # ou ajuste pro tamanho que quiser
        filtro_layout3.addWidget(self.data_saida)

        # Depois do date edit, stretch para empurrar tudo à esquerda
        filtro_layout3.addStretch()

        main_layout.addLayout(filtro_layout3)


        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(15)
        
        # Espaço para alinhar os botões como na imagem
        acoes_layout.addStretch()
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
                border: 1px solid #0078d7;
            }
        """
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        try:
            # Ícone de adicionar
            self.btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        self.btn_cadastrar.setStyleSheet(btn_style)
        self.btn_cadastrar.clicked.connect(self.cadastrar)
        acoes_layout.addWidget(self.btn_cadastrar)
        
        # Botão Alterar
        self.btn_alterar = QPushButton("Alterar")
        try:
            # Ícone de editar
            self.btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        self.btn_alterar.setStyleSheet(btn_style)
        self.btn_alterar.clicked.connect(self.alterar)
        acoes_layout.addWidget(self.btn_alterar)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        try:
            # Ícone de lixeira
            self.btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        self.btn_excluir.setStyleSheet(btn_style)
        self.btn_excluir.clicked.connect(self.excluir)
        acoes_layout.addWidget(self.btn_excluir)
        
        main_layout.addLayout(acoes_layout)
        
        # Tabela de Pedidos
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                color: black;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Configurar tabela
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Num. Pedido", "Nome", "Valor", "Data", "Vendedor"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.itemSelectionChanged.connect(self.selecionar_item)
        
        # Adicionar alguns exemplos de dados
        self.carregar_dados_exemplo()
        
        main_layout.addWidget(self.tabela)
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Dados de exemplo (número do pedido, nome, valor, data, vendedor)
        dados = [
            ("00001", "Empresa ABC Ltda", "R$ 2.450,00", "01/04/2023", "Carlos"),
            ("00002", "João Silva", "R$ 890,50", "05/04/2023", "Maria"),
            ("00003", "Distribuidora XYZ", "R$ 5.780,00", "08/04/2023", "Pedro"),
            ("00004", "Ana Souza", "R$ 1.200,00", "12/04/2023", "Carlos"),
            ("00005", "Mercado Central", "R$ 3.450,00", "15/04/2023", "Maria")
        ]
        
        # Adicionar linhas
        for row, (num_pedido, nome, valor, data, vendedor) in enumerate(dados):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(num_pedido))
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(valor))
            self.tabela.setItem(row, 3, QTableWidgetItem(data))
            self.tabela.setItem(row, 4, QTableWidgetItem(vendedor))
    
    def selecionar_item(self):
        """Preenche os campos quando uma linha é selecionada"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            # Aqui você poderia preencher campos se necessário
    
    # Método voltar foi removido
    
    def alterar(self):
        """Altera os dados de um pedido"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um pedido para alterar!")
            return
        
        row = selected_rows[0].row()
        num_pedido = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        
        # Abrir o formulário para alteração
        self.abrir_formulario(num_pedido, nome)
    
    def excluir(self):
        """Exclui um pedido"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um pedido para excluir!")
            return
        
        row = selected_rows[0].row()
        
        # Criar uma caixa de diálogo de confirmação com estilo personalizado
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar Exclusão")
        msg_box.setText(f"Deseja realmente excluir o pedido {self.tabela.item(row, 0).text()}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #003b57;
            }
            QLabel { 
                color: white;
                background-color: #003b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.Yes:
            self.tabela.removeRow(row)
            self.mostrar_mensagem("Sucesso", "Pedido excluído com sucesso!")
    
    def cadastrar(self):
        """Abre a tela de cadastro de pedido"""
        self.abrir_formulario()
    
    def abrir_formulario(self, num_pedido=None, cliente=None):
        """Abre o formulário de pedido, para cadastro ou alteração"""
        try:
            # Como estamos usando a classe FormularioPedidoVendas definida no mesmo arquivo,
            # não precisamos importá-la
            
            # Criar uma instância do formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Cadastro de Pedido de vendas")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("background-color: #003b57;")
            
            # Configurar o widget central
            formulario_pedido_widget = FormularioPedidoVendas(
                janela_parent=self.form_window,
                num_pedido=num_pedido,
                cliente=cliente
            )
            self.form_window.setCentralWidget(formulario_pedido_widget)
            
            # Mostrar a janela de formulário
            self.form_window.show()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Não foi possível abrir o formulário: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #003b57;
            }
            QLabel { 
                color: white;
                background-color: #003b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Sistema - Pedido de Vendas")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    pedido_vendas_widget = PedidoVendasWindow(window)  # Passa a janela como parent
    window.setCentralWidget(pedido_vendas_widget)
    
    window.show()
    sys.exit(app.exec_())