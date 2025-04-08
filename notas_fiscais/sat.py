import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                            QRadioButton, QCheckBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QTabWidget, QGridLayout, QDateEdit,
                            QComboBox, QGroupBox, QButtonGroup, QSpacerItem,
                            QSizePolicy, QToolButton)
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate

class SATWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manutenção de Notas Fiscais - CF-e SAT")
        self.setGeometry(100, 100, 800, 550)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #000000;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QDateEdit, QComboBox {
                height: 25px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 0 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
            QPushButton:pressed {
                background-color: #00283d;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                gridline-color: #dddddd;
                background-color: white;
                selection-background-color: #005079;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
            QRadioButton {
                spacing: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
        """)
        self.initUI()
        
    def initUI(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)
        
        # ===== ÁREA DE FILTROS =====
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QGridLayout(filter_frame)
        filter_layout.setVerticalSpacing(5)
        filter_layout.setHorizontalSpacing(10)
        
        # Data Nota de:
        filter_layout.addWidget(QLabel("Data Nota de:"), 0, 0, 1, 1)
        
        date_from_layout = QHBoxLayout()
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate())
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        date_from_layout.addWidget(self.date_from)
        
        date_from_layout.addWidget(QLabel(" a "))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        date_from_layout.addWidget(self.date_to)
        
        filter_layout.addLayout(date_from_layout, 0, 1, 1, 2)
        
        # Ordem
        filter_layout.addWidget(QLabel("Ordem"), 0, 3, 1, 1)
        self.ordem_combo = QComboBox()
        self.ordem_combo.addItems(["Código", "Data", "Cliente", "Valor"])
        filter_layout.addWidget(self.ordem_combo, 0, 4, 1, 1)
        
        # Situação (grupo de radio buttons)
        situacao_group = QGroupBox("Situação")
        situacao_layout = QVBoxLayout(situacao_group)
        self.radio_todos = QRadioButton("Todos")
        self.radio_todos.setChecked(True)
        self.radio_emitidas = QRadioButton("Emitidas")
        self.radio_nao_emitidas = QRadioButton("Não Emitidas")
        self.radio_canceladas = QRadioButton("Canceladas")
        
        situacao_layout.addWidget(self.radio_todos)
        situacao_layout.addWidget(self.radio_emitidas)
        situacao_layout.addWidget(self.radio_nao_emitidas)
        situacao_layout.addWidget(self.radio_canceladas)
        
        filter_layout.addWidget(situacao_group, 0, 5, 2, 1)
        
        # Tipo (grupo de radio buttons)
        tipo_group = QGroupBox("Tipo")
        tipo_layout = QVBoxLayout(tipo_group)
        self.radio_entrada = QRadioButton("Entrada")
        self.radio_saida = QRadioButton("Saída")
        self.radio_saida.setChecked(True)
        
        tipo_layout.addWidget(self.radio_entrada)
        tipo_layout.addWidget(self.radio_saida)
        tipo_layout.addStretch()
        
        filter_layout.addWidget(tipo_group, 0, 6, 2, 1)
        
        # Nome Contendo:
        filter_layout.addWidget(QLabel("Nome Contendo:"), 1, 0, 1, 1)
        self.nome_contendo = QLineEdit()
        filter_layout.addWidget(self.nome_contendo, 1, 1, 1, 2)
        
        # Nº Nota:
        filter_layout.addWidget(QLabel("Nº Nota:"), 2, 0, 1, 1)
        self.num_nota = QLineEdit()
        filter_layout.addWidget(self.num_nota, 2, 1, 1, 1)
        
        # Gerou Financeiro
        filter_layout.addWidget(QLabel("Gerou Financeiro"), 2, 2, 1, 1)
        self.gerou_financeiro = QComboBox()
        self.gerou_financeiro.addItems(["Todos", "Sim", "Não"])
        filter_layout.addWidget(self.gerou_financeiro, 2, 3, 1, 1)
        
        # Cód Nota:
        filter_layout.addWidget(QLabel("Cód Nota:"), 3, 0, 1, 1)
        self.cod_nota = QLineEdit()
        filter_layout.addWidget(self.cod_nota, 3, 1, 1, 1)
        
        # Gerou Estoque
        filter_layout.addWidget(QLabel("Gerou Estoque"), 3, 2, 1, 1)
        self.gerou_estoque = QComboBox()
        self.gerou_estoque.addItems(["Todos", "Sim", "Não"])
        filter_layout.addWidget(self.gerou_estoque, 3, 3, 1, 1)
        
        # Nº Pedido:
        filter_layout.addWidget(QLabel("Nº Pedido:"), 4, 0, 1, 1)
        self.num_pedido = QLineEdit()
        filter_layout.addWidget(self.num_pedido, 4, 1, 1, 1)
        
        # Empresa
        filter_layout.addWidget(QLabel("Empresa"), 4, 2, 1, 1)
        empresa_layout = QHBoxLayout()
        self.empresa_id = QLineEdit()
        self.empresa_id.setFixedWidth(30)
        self.empresa_id.setText("1")
        empresa_layout.addWidget(self.empresa_id)
        
        self.empresa_combo = QComboBox()
        self.empresa_combo.addItem("TSUNEHISSA ORITA 02126639843")
        empresa_layout.addWidget(self.empresa_combo, 1)
        
        filter_layout.addLayout(empresa_layout, 4, 3, 1, 3)
        
        # Botões de filtro
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.filtrar_btn = QPushButton("Filtrar")
        self.filtrar_btn.setIcon(QIcon(os.path.join("ico-img", "search.png")))
        self.filtrar_btn.clicked.connect(self.filtrar)
        
        self.limpar_btn = QPushButton("Limpar")
        self.limpar_btn.setIcon(QIcon(os.path.join("ico-img", "clear.png")))
        self.limpar_btn.clicked.connect(self.limpar_filtros)
        
        buttons_layout.addWidget(self.filtrar_btn)
        buttons_layout.addWidget(self.limpar_btn)
        buttons_layout.addStretch()
        
        filter_layout.addLayout(buttons_layout, 4, 6, 1, 1)
        
        main_layout.addWidget(filter_frame)
        
        # ===== TABELA DE NOTAS =====
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([" ", "Email", "Código", "Dt. Nota", "Nº Nota", "Cliente", "Valor Total", "Pedidos"])
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Cliente
        
        # Configurar a largura das colunas
        self.table.setColumnWidth(0, 30)  # Checkbox
        self.table.setColumnWidth(1, 30)  # Email
        self.table.setColumnWidth(2, 80)  # Código
        self.table.setColumnWidth(3, 80)  # Dt. Nota
        self.table.setColumnWidth(4, 80)  # Nº Nota
        self.table.setColumnWidth(6, 100)  # Valor Total
        self.table.setColumnWidth(7, 80)  # Pedidos
        
        # Adicionar linhas de exemplo para CF-e SAT
        self.table.setRowCount(2)
        
        # Primeira linha
        check1 = QTableWidgetItem()
        check1.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        check1.setCheckState(Qt.Unchecked)
        self.table.setItem(0, 0, check1)
        
        email1 = QTableWidgetItem()
        email1.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        email1.setCheckState(Qt.Unchecked)
        self.table.setItem(0, 1, email1)
        
        self.table.setItem(0, 2, QTableWidgetItem("0000096"))
        self.table.setItem(0, 3, QTableWidgetItem("01/04/25"))
        self.table.setItem(0, 4, QTableWidgetItem("0000412"))
        self.table.setItem(0, 5, QTableWidgetItem("SUPERMERCADO MODELO LTDA"))
        self.table.setItem(0, 6, QTableWidgetItem("135,25"))
        self.table.setItem(0, 7, QTableWidgetItem(""))
        
        # Segunda linha
        check2 = QTableWidgetItem()
        check2.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        check2.setCheckState(Qt.Unchecked)
        self.table.setItem(1, 0, check2)
        
        email2 = QTableWidgetItem()
        email2.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        email2.setCheckState(Qt.Unchecked)
        self.table.setItem(1, 1, email2)
        
        self.table.setItem(1, 2, QTableWidgetItem("0000097"))
        self.table.setItem(1, 3, QTableWidgetItem("01/04/25"))
        self.table.setItem(1, 4, QTableWidgetItem("0000413"))
        self.table.setItem(1, 5, QTableWidgetItem("FARMACIA POPULAR LTDA"))
        self.table.setItem(1, 6, QTableWidgetItem("87,50"))
        self.table.setItem(1, 7, QTableWidgetItem(""))
        
        # Conectar evento de duplo clique
        self.table.cellDoubleClicked.connect(self.abrir_detalhe_nota)
        
        main_layout.addWidget(self.table)
        
        # ===== ABAS DE INFORMAÇÕES =====
        self.tabs = QTabWidget()
        
        # Tab Informações CF-e SAT
        info_tab = QWidget()
        info_layout = QGridLayout(info_tab)
        
        # Chave de Acesso
        info_layout.addWidget(QLabel("Chave de Acesso:"), 0, 0)
        self.chave_acesso = QLineEdit("35250420080018000121550010000004131000000951")
        self.chave_acesso.setReadOnly(True)
        info_layout.addWidget(self.chave_acesso, 0, 1, 1, 3)
        
        # Data
        info_layout.addWidget(QLabel("Data:"), 0, 4)
        self.data_nfe = QLineEdit("01/04/2025 11:32:45")
        self.data_nfe.setReadOnly(True)
        info_layout.addWidget(self.data_nfe, 0, 5)
        
        # Nº Recibo
        info_layout.addWidget(QLabel("Nº Recibo:"), 1, 0)
        self.num_recibo = QLineEdit("351010808179777")
        self.num_recibo.setReadOnly(True)
        info_layout.addWidget(self.num_recibo, 1, 1)
        
        # Nº Prot. Envio
        info_layout.addWidget(QLabel("Nº Prot. Envio:"), 2, 0)
        self.num_prot_envio = QLineEdit("135250052641299")
        self.num_prot_envio.setReadOnly(True)
        info_layout.addWidget(self.num_prot_envio, 2, 1)
        
        # Situação
        info_layout.addWidget(QLabel("Situação:"), 2, 4)
        self.situacao_nfe = QLineEdit("AUTORIZADA")
        self.situacao_nfe.setReadOnly(True)
        info_layout.addWidget(self.situacao_nfe, 2, 5)
        
        self.tabs.addTab(info_tab, "Informações CF-e SAT")
        
        # Tab Mensagens
        mensagens_tab = QWidget()
        self.tabs.addTab(mensagens_tab, "Mensagens")
        
        main_layout.addWidget(self.tabs)
        
        # ===== BOTÕES DE AÇÃO =====
        actions_layout = QHBoxLayout()
        
        # Botão Incluir
        self.incluir_btn = QPushButton("Incluir")
        self.incluir_btn.setIcon(QIcon(os.path.join("ico-img", "add.png")))
        self.incluir_btn.clicked.connect(self.incluir)
        actions_layout.addWidget(self.incluir_btn)
        
        # Botão Alterar
        self.alterar_btn = QPushButton("Alterar")
        self.alterar_btn.setIcon(QIcon(os.path.join("ico-img", "edit.png")))
        self.alterar_btn.clicked.connect(self.alterar)
        actions_layout.addWidget(self.alterar_btn)
        
        # Botão Excluir
        self.excluir_btn = QPushButton("Excluir")
        self.excluir_btn.setIcon(QIcon(os.path.join("ico-img", "delete.png")))
        self.excluir_btn.clicked.connect(self.excluir)
        actions_layout.addWidget(self.excluir_btn)
        
        # Botão Consultar
        self.consultar_btn = QPushButton("Consultar")
        self.consultar_btn.setIcon(QIcon(os.path.join("ico-img", "search.png")))
        self.consultar_btn.clicked.connect(self.consultar)
        actions_layout.addWidget(self.consultar_btn)
        
        # Botão Opções
        self.opcoes_btn = QPushButton("Opções")
        self.opcoes_btn.setIcon(QIcon(os.path.join("ico-img", "options.png")))
        opcoes_menu = QComboBox()
        opcoes_menu.addItems(["Opção 1", "Opção 2", "Opção 3"])
        actions_layout.addWidget(self.opcoes_btn)
        
        # Botão Imprimir
        self.imprimir_btn = QPushButton("Imprimir")
        self.imprimir_btn.setIcon(QIcon(os.path.join("ico-img", "print.png")))
        self.imprimir_btn.clicked.connect(self.imprimir)
        actions_layout.addWidget(self.imprimir_btn)
        
        actions_layout.addStretch()
        
        main_layout.addLayout(actions_layout)
    
    def abrir_detalhe_nota(self, row, column):
        """Abre a tela de detalhes da nota fiscal quando o usuário clica duas vezes em uma linha da tabela."""
        try:
            from detalhe_nota_fiscal import DetalheNotaFiscalWindow
            nota_id = self.table.item(row, 2).text()  # Código da nota
            detalhes_window = DetalheNotaFiscalWindow(self, "CF-e SAT", nota_id)
            detalhes_window.show()
        except Exception as e:
            print(f"Erro ao abrir detalhe da nota: {str(e)}")
        
    def filtrar(self):
        print("Filtrando notas...")
        # Implementar lógica de filtro aqui
        
    def limpar_filtros(self):
        self.nome_contendo.clear()
        self.num_nota.clear()
        self.cod_nota.clear()
        self.num_pedido.clear()
        self.date_from.setDate(QDate.currentDate())
        self.date_to.setDate(QDate.currentDate())
        self.radio_todos.setChecked(True)
        self.radio_saida.setChecked(True)
        self.gerou_financeiro.setCurrentIndex(0)
        self.gerou_estoque.setCurrentIndex(0)
        self.ordem_combo.setCurrentIndex(0)
        
    def alterar(self):
        print("Alterando nota fiscal...")
        # Implementar lógica para alterar nota
        
    def excluir(self):
        print("Excluindo nota fiscal...")
        # Implementar lógica para excluir nota
        
    def consultar(self):
        print("Consultando nota fiscal...")
        # Implementar lógica para consultar nota
        
    def imprimir(self):
        print("Imprimindo nota fiscal...")
        # Implementar lógica para imprimir nota

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SATWindow()
    window.show()
    sys.exit(app.exec_())