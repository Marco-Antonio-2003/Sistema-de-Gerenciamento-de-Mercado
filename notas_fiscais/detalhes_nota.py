import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                            QRadioButton, QCheckBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QTabWidget, QGridLayout, QDateEdit,
                            QComboBox, QGroupBox, QButtonGroup, QToolButton,
                            QSpacerItem, QSizePolicy, QDialog, QFormLayout)
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate

class DetalheNotaFiscalWindow(QMainWindow):
    def __init__(self, parent=None, tipo_nota="NFE", nota_id=None):
        super().__init__(parent)
        self.tipo_nota = tipo_nota
        self.nota_id = nota_id
        self.setWindowTitle(f"Manutenção de Notas Fiscais - {self.tipo_nota}")
        self.setGeometry(100, 100, 800, 650)
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
                height: 20px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 0 5px;
                background-color: white;
            }
            QLineEdit:disabled {
                background-color: #f0f0f0;
                color: #808080;
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
                padding: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QToolButton {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #d0d0d0;
            }
            QCheckBox {
                spacing: 5px;
            }
        """)
        self.initUI()
        
    def initUI(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # Título "Consultando Registro"
        title_layout = QHBoxLayout()
        
        title_label = QLabel("Consultando Registro")
        title_label.setFont(QFont("Arial", 12, QFont.Bold | QFont.Italic))
        title_label.setStyleSheet("color: #5f5f5f;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Botões Gravar e Voltar
        gravar_btn = QPushButton("Gravar")
        gravar_btn.setIcon(QIcon(os.path.join("ico-img", "save.png")))
        gravar_btn.clicked.connect(self.gravar)
        title_layout.addWidget(gravar_btn)
        
        voltar_btn = QPushButton("Voltar")
        voltar_btn.setIcon(QIcon(os.path.join("ico-img", "back.png")))
        voltar_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e60000;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        voltar_btn.clicked.connect(self.close)
        title_layout.addWidget(voltar_btn)
        
        main_layout.addLayout(title_layout)
        
        # Linha 1: Lançamento, Data, Tipo de Operação, Série
        row1_layout = QHBoxLayout()
        
        # Lançamento
        row1_layout.addWidget(QLabel("Lançamento"))
        self.lancamento_edit = QLineEdit("94")
        self.lancamento_edit.setFixedWidth(60)
        self.lancamento_edit.setReadOnly(True)
        self.lancamento_edit.setStyleSheet("background-color: #d6f5d6;")
        row1_layout.addWidget(self.lancamento_edit)
        
        # Data
        row1_layout.addWidget(QLabel("Data"))
        self.data_edit = QDateEdit()
        self.data_edit.setCalendarPopup(True)
        self.data_edit.setDate(QDate.fromString("01/04/2025", "dd/MM/yyyy"))
        self.data_edit.setDisplayFormat("dd/MM/yyyy")
        self.data_edit.setFixedWidth(100)
        row1_layout.addWidget(self.data_edit)
        
        # Tipo de Operação
        row1_layout.addWidget(QLabel("Tipo de Operação"))
        operacao_layout = QHBoxLayout()
        self.operacao_code = QLineEdit("3")
        self.operacao_code.setFixedWidth(30)
        operacao_layout.addWidget(self.operacao_code)
        
        self.operacao_combo = QComboBox()
        self.operacao_combo.addItem("5102 - VENDA DE MERCADORIA (S)")
        operacao_layout.addWidget(self.operacao_combo)
        
        row1_layout.addLayout(operacao_layout)
        
        # Série
        row1_layout.addWidget(QLabel("Série"))
        self.serie_edit = QLineEdit("1")
        self.serie_edit.setFixedWidth(60)
        row1_layout.addWidget(self.serie_edit)
        
        main_layout.addLayout(row1_layout)
        
        # Linha 2: Natureza, Finalidade, campos de verificação
        row2_layout = QHBoxLayout()
        
        # Natureza
        row2_layout.addWidget(QLabel("Natureza"))
        self.natureza_combo = QComboBox()
        self.natureza_combo.addItem("VENDA DE MERCADORIA")
        self.natureza_combo.setFixedWidth(250)
        row2_layout.addWidget(self.natureza_combo)
        
        # Finalidade
        row2_layout.addWidget(QLabel("Finalidade"))
        finalidade_layout = QHBoxLayout()
        self.finalidade_code = QLineEdit("2")
        self.finalidade_code.setFixedWidth(30)
        finalidade_layout.addWidget(self.finalidade_code)
        
        self.finalidade_combo = QComboBox()
        self.finalidade_combo.addItem("Normal")
        finalidade_layout.addWidget(self.finalidade_combo)
        
        row2_layout.addLayout(finalidade_layout)
        
        # Estoque (Checkbox)
        estoque_layout = QVBoxLayout()
        estoque_layout.addWidget(QLabel("Estoque"))
        self.estoque_check = QCheckBox()
        self.estoque_check.setChecked(True)
        estoque_layout.addWidget(self.estoque_check)
        row2_layout.addLayout(estoque_layout)
        
        # Financeiro
        row2_layout.addWidget(QLabel("Financeiro"))
        self.financeiro_combo = QComboBox()
        self.financeiro_combo.addItem("Não")
        self.financeiro_combo.setFixedWidth(100)
        row2_layout.addWidget(self.financeiro_combo)
        
        main_layout.addLayout(row2_layout)
        
        # Abas
        self.tabs = QTabWidget()
        
        # Tab Dados
        dados_tab = QWidget()
        dados_layout = QVBoxLayout(dados_tab)
        
        # Seção Destinatário
        dest_group = QGroupBox("Destinatário")
        dest_layout = QGridLayout(dest_group)
        
        # Linha 1: Código, Nome, CNPJ/CPF, Inscrição Estadual, Consumidor Final
        dest_layout.addWidget(QLabel("Código"), 0, 0)
        dest_code_layout = QHBoxLayout()
        self.dest_code = QLineEdit("7")
        self.dest_code.setFixedWidth(40)
        dest_code_layout.addWidget(self.dest_code)
        
        dest_code_btn = QToolButton()
        dest_code_btn.setText("...")
        dest_code_btn.clicked.connect(self.buscar_cliente)
        dest_code_layout.addWidget(dest_code_btn)
        
        dest_layout.addLayout(dest_code_layout, 0, 1)
        
        dest_layout.addWidget(QLabel("Nome"), 0, 2)
        self.dest_nome = QLineEdit("SIND DOS EMPREGADOS RURAIS DE RIB BRANCO E GUAP")
        dest_layout.addWidget(self.dest_nome, 0, 3)
        
        dest_layout.addWidget(QLabel("CNPJ / CPF"), 0, 4)
        self.dest_cnpj = QLineEdit("50.825.355/0001-98")
        dest_layout.addWidget(self.dest_cnpj, 0, 5)
        
        dest_layout.addWidget(QLabel("Inscrição Estadual"), 0, 6)
        self.dest_ie = QLineEdit()
        dest_layout.addWidget(self.dest_ie, 0, 7)
        
        dest_layout.addWidget(QLabel("Consumidor Final"), 0, 8)
        self.dest_consumidor = QComboBox()
        self.dest_consumidor.addItems(["Sim", "Não"])
        dest_layout.addWidget(self.dest_consumidor, 0, 9)
        
        # Linha 2: Endereço, Bairro, CEP, Cidade
        dest_layout.addWidget(QLabel("Endereço"), 1, 0)
        self.dest_endereco = QLineEdit("RUA CUSTODIO GOMES, 913")
        dest_layout.addWidget(self.dest_endereco, 1, 1, 1, 2)
        
        dest_layout.addWidget(QLabel("Bairro"), 1, 3)
        self.dest_bairro = QLineEdit("CENTRO")
        dest_layout.addWidget(self.dest_bairro, 1, 4)
        
        dest_layout.addWidget(QLabel("CEP"), 1, 5)
        self.dest_cep = QLineEdit("18430000")
        dest_layout.addWidget(self.dest_cep, 1, 6)
        
        dest_layout.addWidget(QLabel("Cidade"), 1, 7)
        cidade_layout = QHBoxLayout()
        self.dest_cidade_code = QLineEdit("118")
        self.dest_cidade_code.setFixedWidth(30)
        cidade_layout.addWidget(self.dest_cidade_code)
        
        self.dest_cidade = QLineEdit("RIBEIRÃO BRANCO")
        cidade_layout.addWidget(self.dest_cidade)
        
        cidade_btn = QToolButton()
        cidade_btn.setText("...")
        cidade_btn.clicked.connect(lambda: self.buscar_cidade())
        cidade_layout.addWidget(cidade_btn)
        
        dest_layout.addLayout(cidade_layout, 1, 8, 1, 2)
        
        # Linha 3: Fone/Fax, Intermediários
        dest_layout.addWidget(QLabel("Fone / Fax"), 2, 0)
        self.dest_fone = QLineEdit()
        dest_layout.addWidget(self.dest_fone, 2, 1, 1, 2)
        
        dest_layout.addWidget(QLabel("Indicador IE Destinatário"), 2, 3)
        self.dest_ie_indicador = QComboBox()
        self.dest_ie_indicador.addItem("Não Contribuinte")
        dest_layout.addWidget(self.dest_ie_indicador, 2, 4)
        
        dest_layout.addWidget(QLabel("Indicador Dest. Operação"), 2, 5)
        self.dest_operacao = QComboBox()
        self.dest_operacao.addItem("0 - Automático")
        dest_layout.addWidget(self.dest_operacao, 2, 6)
        
        dest_layout.addWidget(QLabel("Indicador de Presença"), 2, 7)
        self.dest_presenca = QComboBox()
        self.dest_presenca.addItem("0-Não se aplica (NF Complementar/Ajuste)")
        dest_layout.addWidget(self.dest_presenca, 2, 8, 1, 2)
        
        # Linha 4: Intermediador
        dest_layout.addWidget(QLabel("Intermediador"), 3, 0)
        intermed_layout = QHBoxLayout()
        self.intermed_btn = QToolButton()
        self.intermed_btn.setText("...")
        intermed_layout.addWidget(self.intermed_btn)
        dest_layout.addLayout(intermed_layout, 3, 1, 1, 2)
        
        dest_layout.addWidget(QLabel("Empresa"), 3, 3)
        empresa_layout = QHBoxLayout()
        self.empresa_code = QLineEdit("1")
        self.empresa_code.setFixedWidth(30)
        empresa_layout.addWidget(self.empresa_code)
        
        self.empresa_nome = QLineEdit("TSUNEHISSA ORITA 02126639843")
        empresa_layout.addWidget(self.empresa_nome)
        
        empresa_btn = QToolButton()
        empresa_btn.setText("...")
        empresa_layout.addWidget(empresa_btn)
        
        dest_layout.addLayout(empresa_layout, 3, 4, 1, 4)
        
        dados_layout.addWidget(dest_group)
        
        # Seção Informações de Pagamento
        pagamento_group = QGroupBox("Informações de pagamento")
        pagamento_layout = QGridLayout(pagamento_group)
        
        pagamento_layout.addWidget(QLabel("Indicador Forma Pagto"), 0, 0)
        self.pagto_forma = QComboBox()
        self.pagto_forma.addItem("1 - À Prazo")
        pagamento_layout.addWidget(self.pagto_forma, 0, 1)
        
        pagamento_layout.addWidget(QLabel("Tipo Pagamento"), 0, 2)
        self.pagto_tipo = QComboBox()
        pagamento_layout.addWidget(self.pagto_tipo, 0, 3)
        
        pagamento_layout.addWidget(QLabel("Descrição"), 0, 4)
        self.pagto_descricao = QLineEdit()
        pagamento_layout.addWidget(self.pagto_descricao, 0, 5)
        
        dados_layout.addWidget(pagamento_group)
        
        # Seção Transportadora
        transp_group = QGroupBox("Transportadora")
        transp_layout = QGridLayout(transp_group)
        
        # Linha 1: Código, Transportadora, CNPJ/CPF, IE/RG
        transp_layout.addWidget(QLabel("Código"), 0, 0)
        transp_code_layout = QHBoxLayout()
        self.transp_code = QLineEdit()
        self.transp_code.setFixedWidth(40)
        transp_code_layout.addWidget(self.transp_code)
        
        transp_code_btn = QToolButton()
        transp_code_btn.setText("...")
        transp_code_layout.addWidget(transp_code_btn)
        
        transp_layout.addLayout(transp_code_layout, 0, 1)
        
        transp_layout.addWidget(QLabel("Transportadora"), 0, 2)
        self.transp_nome = QLineEdit()
        transp_layout.addWidget(self.transp_nome, 0, 3)
        
        transp_layout.addWidget(QLabel("CNPJ / CPF"), 0, 4)
        self.transp_cnpj = QLineEdit()
        transp_layout.addWidget(self.transp_cnpj, 0, 5)
        
        transp_layout.addWidget(QLabel("IE / RG"), 0, 6)
        self.transp_ie = QLineEdit()
        transp_layout.addWidget(self.transp_ie, 0, 7)
        
        # Linha 2: Endereço, Cidade, Placa, UF Placa
        transp_layout.addWidget(QLabel("Endereço"), 1, 0)
        self.transp_endereco = QLineEdit()
        transp_layout.addWidget(self.transp_endereco, 1, 1, 1, 3)
        
        transp_layout.addWidget(QLabel("Cidade"), 1, 4)
        cidade_transp_layout = QHBoxLayout()
        self.transp_cidade = QLineEdit()
        cidade_transp_layout.addWidget(self.transp_cidade)
        
        transp_cidade_btn = QToolButton()
        transp_cidade_btn.setText("...")
        cidade_transp_layout.addWidget(transp_cidade_btn)
        
        transp_layout.addLayout(cidade_transp_layout, 1, 5)
        
        transp_layout.addWidget(QLabel("Placa"), 1, 6)
        self.transp_placa = QLineEdit()
        transp_layout.addWidget(self.transp_placa, 1, 7)
        
        transp_layout.addWidget(QLabel("UF Placa"), 1, 8)
        self.transp_uf_placa = QLineEdit()
        transp_layout.addWidget(self.transp_uf_placa, 1, 9)
        
        # Linha 3: Tipo Frete, Redespacho
        transp_layout.addWidget(QLabel("Tipo Frete"), 2, 0)
        self.transp_tipo_frete = QComboBox()
        self.transp_tipo_frete.addItem("1 - Conta Destinatário (FOB)")
        transp_layout.addWidget(self.transp_tipo_frete, 2, 1, 1, 2)
        
        transp_layout.addWidget(QLabel("Redespacho"), 2, 3)
        redespacho_layout = QHBoxLayout()
        self.transp_redespacho = QLineEdit()
        redespacho_layout.addWidget(self.transp_redespacho)
        
        redespacho_btn = QToolButton()
        redespacho_btn.setText("...")
        redespacho_layout.addWidget(redespacho_btn)
        
        transp_layout.addLayout(redespacho_layout, 2, 4, 1, 6)
        
        dados_layout.addWidget(transp_group)
        
        # Duas seções finais lado a lado
        bottom_layout = QHBoxLayout()
        
        # Seção B2B - Informações de Compra
        b2b_group = QGroupBox("B2B - Informações de Compra")
        b2b_layout = QGridLayout(b2b_group)
        
        b2b_layout.addWidget(QLabel("Pedido Compra"), 0, 0)
        self.b2b_pedido = QLineEdit()
        b2b_layout.addWidget(self.b2b_pedido, 0, 1)
        
        b2b_layout.addWidget(QLabel("Nota Empenho"), 0, 2)
        self.b2b_nota_empenho = QLineEdit()
        b2b_layout.addWidget(self.b2b_nota_empenho, 0, 3)
        
        b2b_layout.addWidget(QLabel("Nº Contrato"), 1, 0)
        self.b2b_contrato = QLineEdit()
        b2b_layout.addWidget(self.b2b_contrato, 1, 1, 1, 3)
        
        bottom_layout.addWidget(b2b_group)
        
        # Seção Exportação
        export_group = QGroupBox("Exportação")
        export_layout = QGridLayout(export_group)
        
        export_layout.addWidget(QLabel("UF Embarque"), 0, 0)
        self.export_uf = QLineEdit()
        export_layout.addWidget(self.export_uf, 0, 1)
        
        export_layout.addWidget(QLabel("Local Embarque"), 0, 2)
        local_embarque_layout = QHBoxLayout()
        self.export_local = QLineEdit()
        local_embarque_layout.addWidget(self.export_local)
        
        local_btn = QToolButton()
        local_btn.setText("...")
        local_embarque_layout.addWidget(local_btn)
        
        export_layout.addLayout(local_embarque_layout, 0, 3)
        
        export_layout.addWidget(QLabel("Local Despacho"), 1, 0)
        self.export_despacho = QLineEdit()
        export_layout.addWidget(self.export_despacho, 1, 1, 1, 3)
        
        bottom_layout.addWidget(export_group)
        
        dados_layout.addLayout(bottom_layout)
        
        # Botão "Editar Itens" na direita
        edit_layout = QHBoxLayout()
        edit_layout.addStretch()
        self.edit_items_btn = QPushButton("Editar Itens")
        self.edit_items_btn.clicked.connect(self.editar_itens)
        edit_layout.addWidget(self.edit_items_btn)
        
        dados_layout.addLayout(edit_layout)
        
        # Adicionar a aba Dados
        self.tabs.addTab(dados_tab, "Dados")
        
        # Adicionar as outras abas (vazias por enquanto)
        self.tabs.addTab(QWidget(), "Produtos")
        self.tabs.addTab(QWidget(), "Serviços")
        self.tabs.addTab(QWidget(), "Totais da Nota")
        self.tabs.addTab(QWidget(), "Referências")
        
        main_layout.addWidget(self.tabs)
    
    def buscar_cliente(self):
        print("Buscando cliente...")
        # Aqui você pode implementar a lógica para abrir a tela de busca de clientes
        # E recuperar os dados para preencher os campos do destinatário
    
    def buscar_cidade(self):
        print("Buscando cidade...")
        # Implementar lógica para buscar cidade
    
    def editar_itens(self):
        print("Editando itens da nota...")
        # Implementar lógica para editar os itens da nota
    
    def gravar(self):
        print("Gravando nota fiscal...")
        # Implementar lógica para salvar os dados da nota fiscal

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DetalheNotaFiscalWindow()
    window.show()
    sys.exit(app.exec_())