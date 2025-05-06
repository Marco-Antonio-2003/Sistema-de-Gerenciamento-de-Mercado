#relatorio_fiscal.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QRadioButton, QDialog,
                             QButtonGroup, QSpacerItem, QSizePolicy,
                             QDateEdit, QGroupBox, QGridLayout)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog


class RelatorioFiscalWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho com título
        header_layout = QHBoxLayout()
        
        # # Botão Voltar
        # self.btn_voltar = QPushButton("Voltar")
        # self.btn_voltar.setStyleSheet("""
        #     QPushButton {
        #         background-color: #004465;
        #         color: white;
        #         padding: 6px 12px;
        #         border: none;
        #         border-radius: 4px;
        #         font-size: 12px;
        #     }
        #     QPushButton:hover {
        #         background-color: #00354f;
        #     }
        #     QPushButton:pressed {
        #         background-color: #0078d7;
        #     }
        # """)
        # self.btn_voltar.setMinimumWidth(70)
        # self.btn_voltar.clicked.connect(self.voltar)
        # header_layout.addWidget(self.btn_voltar)
        
        # Título
        title_label = QLabel("Relatório Fiscal")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-left: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label, 1)  # 1 = stretch factor
        
        # Adicionar espaço à direita para balancear o botão voltar
        spacer = QWidget()
        spacer.setMinimumWidth(70)
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Formulário para filtros
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(15)
        
        # Estilo para inputs
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
                min-height: 22px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Estilo para o DateEdit com ícone de calendário
        date_style = """
            QDateEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
                min-height: 22px;
                color: black;
            }
            QDateEdit::drop-down {
                border: 0px;
                image: url(ico-img/calendar-outline.svg);
                width: 20px;
                height: 20px;
                subcontrol-position: right center;
                subcontrol-origin: padding;
                margin-right: 5px;
            }
            QDateEdit::down-arrow {
                width: 0px;
                height: 0px;
            }
            QDateEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Estilo para calendário com fundo branco
        calendar_style = """
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QWidget {
                background-color: white;
                color: black;
            }
            QCalendarWidget QToolButton {
                background-color: white;
                color: black;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: black;
            }
            QCalendarWidget QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
            }
        """
        
        # Empresa
        empresa_label = QLabel("Empresa:")
        empresa_label.setFont(QFont("Arial", 11))
        empresa_label.setStyleSheet("color: white;")
        form_layout.addWidget(empresa_label, 0, 0)
        
        self.empresa_input = QLineEdit()
        self.empresa_input.setStyleSheet(input_style)
        form_layout.addWidget(self.empresa_input, 0, 1, 1, 3)  # span de 3 colunas
        
        # Cliente
        cliente_label = QLabel("Cliente:")
        cliente_label.setFont(QFont("Arial", 11))
        cliente_label.setStyleSheet("color: white;")
        form_layout.addWidget(cliente_label, 1, 0)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setStyleSheet(input_style)
        form_layout.addWidget(self.cliente_input, 1, 1)
        
        # Produto
        produto_label = QLabel("Produto:")
        produto_label.setFont(QFont("Arial", 11))
        produto_label.setStyleSheet("color: white;")
        form_layout.addWidget(produto_label, 1, 2)
        
        self.produto_input = QLineEdit()
        self.produto_input.setStyleSheet(input_style)
        form_layout.addWidget(self.produto_input, 1, 3)
        
        # Período de nota
        periodo_label = QLabel("Período de\nnota")
        periodo_label.setFont(QFont("Arial", 11))
        periodo_label.setStyleSheet("color: white;")
        form_layout.addWidget(periodo_label, 2, 0)
        
        # Date Edit com ícone de calendário incorporado
        self.data_inicial = QDateEdit(QDate.currentDate())
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setDisplayFormat("dd/MM/yyyy")
        self.data_inicial.setStyleSheet(date_style)
        form_layout.addWidget(self.data_inicial, 2, 1)
        
        # Até
        ate_label = QLabel("Até:")
        ate_label.setFont(QFont("Arial", 11))
        ate_label.setStyleSheet("color: white;")
        form_layout.addWidget(ate_label, 2, 2)
        
        # Date Edit com ícone de calendário incorporado
        self.data_final = QDateEdit(QDate.currentDate())
        self.data_final.setCalendarPopup(True)
        self.data_final.setDisplayFormat("dd/MM/yyyy")
        self.data_final.setStyleSheet(date_style)
        form_layout.addWidget(self.data_final, 2, 3)
        
        main_layout.addLayout(form_layout)
        
        # Layout para opções de filtro (dividido em 3 grupos)
        filtros_layout = QHBoxLayout()
        
        # Grupo Ordem
        self.ordem_group = QGroupBox("Ordem")
        self.ordem_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #00253e;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QRadioButton {
                color: white;
            }
        """)
        
        ordem_layout = QVBoxLayout(self.ordem_group)
        ordem_layout.setContentsMargins(10, 15, 10, 10)
        ordem_layout.setSpacing(5)
        
        # Radio buttons para Ordem
        self.ordem_button_group = QButtonGroup(self)
        
        self.radio_cliente = QRadioButton("Cliente")
        self.radio_cliente.setChecked(True)
        self.ordem_button_group.addButton(self.radio_cliente)
        ordem_layout.addWidget(self.radio_cliente)
        
        self.radio_data = QRadioButton("Data")
        self.ordem_button_group.addButton(self.radio_data)
        ordem_layout.addWidget(self.radio_data)
        
        self.radio_lancamento = QRadioButton("Lançamento")
        self.ordem_button_group.addButton(self.radio_lancamento)
        ordem_layout.addWidget(self.radio_lancamento)
        
        self.radio_numero = QRadioButton("Número")
        self.ordem_button_group.addButton(self.radio_numero)
        ordem_layout.addWidget(self.radio_numero)
        
        ordem_layout.addStretch(1)
        filtros_layout.addWidget(self.ordem_group)
        
        # Grupo Situação
        self.situacao_group = QGroupBox("Situação")
        self.situacao_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #00253e;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QRadioButton {
                color: white;
            }
        """)
        
        situacao_layout = QVBoxLayout(self.situacao_group)
        situacao_layout.setContentsMargins(10, 15, 10, 10)
        situacao_layout.setSpacing(5)
        
        # Radio buttons para Situação
        self.situacao_button_group = QButtonGroup(self)
        
        self.radio_autorizadas = QRadioButton("Autorizadas")
        self.radio_autorizadas.setChecked(True)
        self.situacao_button_group.addButton(self.radio_autorizadas)
        situacao_layout.addWidget(self.radio_autorizadas)
        
        self.radio_canceladas = QRadioButton("Canceladas")
        self.situacao_button_group.addButton(self.radio_canceladas)
        situacao_layout.addWidget(self.radio_canceladas)
        
        self.radio_nao_emitidas = QRadioButton("Não Emitidas")
        self.situacao_button_group.addButton(self.radio_nao_emitidas)
        situacao_layout.addWidget(self.radio_nao_emitidas)
        
        situacao_layout.addStretch(1)
        filtros_layout.addWidget(self.situacao_group)
        
        # Grupo Tipo de Nota / Tipo
        nota_tipo_layout = QVBoxLayout()
        
        # Subgrupo Tipo de Nota
        self.tipo_nota_group = QGroupBox("Tipo de Nota")
        self.tipo_nota_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #00253e;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QRadioButton {
                color: white;
            }
        """)
        
        tipo_nota_layout = QVBoxLayout(self.tipo_nota_group)
        tipo_nota_layout.setContentsMargins(10, 15, 10, 10)
        tipo_nota_layout.setSpacing(5)
        
        # Radio buttons para Tipo de Nota
        self.tipo_nota_button_group = QButtonGroup(self)
        
        self.radio_nfe = QRadioButton("NFe")
        self.radio_nfe.setChecked(True)
        self.tipo_nota_button_group.addButton(self.radio_nfe)
        tipo_nota_layout.addWidget(self.radio_nfe)
        
        self.radio_sat = QRadioButton("SAT")
        self.tipo_nota_button_group.addButton(self.radio_sat)
        tipo_nota_layout.addWidget(self.radio_sat)
        
        self.radio_nfce = QRadioButton("NFCe")
        self.tipo_nota_button_group.addButton(self.radio_nfce)
        tipo_nota_layout.addWidget(self.radio_nfce)
        
        nota_tipo_layout.addWidget(self.tipo_nota_group)
        
        # Subgrupo Tipo
        self.tipo_group = QGroupBox("Tipo")
        self.tipo_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #00253e;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QRadioButton {
                color: white;
            }
        """)
        
        tipo_layout = QVBoxLayout(self.tipo_group)
        tipo_layout.setContentsMargins(10, 15, 10, 10)
        tipo_layout.setSpacing(5)
        
        # Radio buttons para Tipo
        self.tipo_button_group = QButtonGroup(self)
        
        self.radio_entrada = QRadioButton("Entrada")
        self.radio_entrada.setChecked(True)
        self.tipo_button_group.addButton(self.radio_entrada)
        tipo_layout.addWidget(self.radio_entrada)
        
        self.radio_saida = QRadioButton("Saída")
        self.tipo_button_group.addButton(self.radio_saida)
        tipo_layout.addWidget(self.radio_saida)
        
        tipo_layout.addStretch(1)
        nota_tipo_layout.addWidget(self.tipo_group)
        
        filtros_layout.addLayout(nota_tipo_layout)
        
        main_layout.addLayout(filtros_layout)
        
        # Botão de Imprimir
        self.btn_imprimir = QPushButton("Imprimir")
        self.btn_imprimir.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: black;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00b248;
            }
        """)
        self.btn_imprimir.clicked.connect(self.mostrar_opcoes_impressao)
        
        # Layout do botão centralizado
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_imprimir)
        btn_layout.addStretch(1)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch(1)  # Adiciona espaço extra no final
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #003353; }" + calendar_style)
        
    def voltar(self):
        """Fecha a tela atual quando o botão voltar for clicado"""
        self.window().close()
    
    def mostrar_opcoes_impressao(self):
        """Abre um diálogo com opções para visualizar ou imprimir"""
        opcoes_dialog = OpcoesImpressaoDialog(self)
        opcoes_dialog.exec_()
    
    def visualizar_relatorio(self):
        """Abre a visualização prévia do relatório"""
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.imprimir_documento)
        preview.resize(1000, 700)  # Tamanho padrão da janela de visualização
        preview.exec_()
    
    def imprimir_documento(self, printer):
        """Função que realiza a impressão do documento"""
        # Aqui você implementaria o código para a renderização do documento
        # Por exemplo, usando QPainter para desenhar o conteúdo na impressora
        pass
    
    def enviar_para_impressora(self):
        """Envia o relatório diretamente para a impressora"""
        printer = QPrinter(QPrinter.HighResolution)
        # Aqui você configuraria a impressora com as definições salvas
        # printer.setPrinterName("Sua Impressora")
        
        # Opcionalmente, pode mostrar o diálogo de impressão
        # dialog = QPrintDialog(printer, self)
        # if dialog.exec_() == QPrintDialog.Accepted:
        #     self.imprimir_documento(printer)
        
        # Para envio direto sem diálogo:
        self.imprimir_documento(printer)
        
        # Mensagem de sucesso
        QMessageBox.information(self, "Impressão", "Relatório enviado para impressão com sucesso!")


class OpcoesImpressaoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        # Configuração da janela
        self.setWindowTitle("Opções de Impressão")
        self.setFixedWidth(300)
        self.setFixedHeight(150)
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Escolha uma opção:")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Botões de opção
        buttons_layout = QHBoxLayout()
        
        # Botão Visualizar
        self.btn_visualizar = QPushButton("Visualizar")
        self.btn_visualizar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #004c82;
            }
        """)
        self.btn_visualizar.clicked.connect(self.visualizar)
        buttons_layout.addWidget(self.btn_visualizar)
        
        # Botão Imprimir
        self.btn_imprimir = QPushButton("Imprimir")
        self.btn_imprimir.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: black;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00b248;
            }
        """)
        self.btn_imprimir.clicked.connect(self.imprimir)
        buttons_layout.addWidget(self.btn_imprimir)
        
        main_layout.addLayout(buttons_layout)
    
    def visualizar(self):
        """Chama a função de visualização e fecha o diálogo"""
        self.accept()
        self.parent.visualizar_relatorio()
    
    def imprimir(self):
        """Chama a função de impressão e fecha o diálogo"""
        self.accept()
        self.parent.enviar_para_impressora()


# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Relatório Fiscal")
    window.setGeometry(100, 100, 650, 500)
    window.setStyleSheet("QMainWindow { background-color: #003353; }")
    
    relatorio_fiscal = RelatorioFiscalWindow()
    window.setCentralWidget(relatorio_fiscal)
    
    window.show()
    sys.exit(app.exec_())