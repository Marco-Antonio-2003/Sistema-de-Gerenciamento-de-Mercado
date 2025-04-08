import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class Produtos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.initUI()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#043b57"))
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
        
        # Layout para o título e botão voltar
        header_layout = QHBoxLayout()
        
        # Botão Voltar
        btn_voltar = QPushButton("Voltar")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        btn_voltar.clicked.connect(self.voltar)
        header_layout.addWidget(btn_voltar)
        
        # Título
        titulo = QLabel("Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Primeira linha de campos
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(20)
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        codigo_layout.addWidget(self.codigo_input)
        linha1_layout.addLayout(codigo_layout)
        
        # Campo Nome
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        nome_layout.addWidget(self.nome_input)
        linha1_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha de campos
        linha2_layout = QHBoxLayout()
        linha2_layout.setSpacing(20)
        
        # Campo Código de Barras
        barras_layout = QHBoxLayout()
        barras_label = QLabel("Código de Barras:")
        barras_label.setStyleSheet("color: white; font-size: 14px;")
        barras_layout.addWidget(barras_label)
        
        self.barras_input = QLineEdit()
        self.barras_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        barras_layout.addWidget(self.barras_input)
        linha2_layout.addLayout(barras_layout, 1)  # 1 para expandir
        
        # Campo Grupo
        grupo_layout = QHBoxLayout()
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet("color: white; font-size: 14px;")
        grupo_layout.addWidget(grupo_label)
        
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Alimentos")
        self.grupo_combo.addItem("Bebidas")
        self.grupo_combo.addItem("Limpeza")
        self.grupo_combo.addItem("Higiene")
        self.grupo_combo.addItem("Hortifruti")
        grupo_layout.addWidget(self.grupo_combo)
        linha2_layout.addLayout(grupo_layout)
        
        main_layout.addLayout(linha2_layout)
        
        # Terceira linha de campos
        linha3_layout = QHBoxLayout()
        linha3_layout.setSpacing(20)
        
        # Campo Marca
        marca_layout = QHBoxLayout()
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet("color: white; font-size: 14px;")
        marca_layout.addWidget(marca_label)
        
        self.marca_input = QLineEdit()
        self.marca_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        marca_layout.addWidget(self.marca_input)
        linha3_layout.addLayout(marca_layout, 1)  # 1 para expandir
        
        # Botões de ação
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(10)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """
        
        # Botão Alterar
        btn_alterar = QPushButton("Alterar")
        try:
            btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        btn_alterar.setStyleSheet(btn_style)
        btn_alterar.clicked.connect(self.alterar)
        botoes_layout.addWidget(btn_alterar)
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        try:
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet(btn_style)
        btn_excluir.clicked.connect(self.excluir)
        botoes_layout.addWidget(btn_excluir)
        
        # Botão Cadastrar
        btn_cadastrar = QPushButton("Cadastrar")
        try:
            btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        btn_cadastrar.setStyleSheet(btn_style)
        btn_cadastrar.clicked.connect(self.cadastrar)
        botoes_layout.addWidget(btn_cadastrar)
        
        linha3_layout.addLayout(botoes_layout)
        
        main_layout.addLayout(linha3_layout)
        
        # Tabela de Produtos
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                color: black;
            }
            QHeaderView::section {
                background-color: #fffff0;
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
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Preço de Venda", "Quant. Estoque"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.itemSelectionChanged.connect(self.selecionar_item)
        
        # Adicionar alguns exemplos de dados
        self.carregar_dados_exemplo()
        
        main_layout.addWidget(self.tabela)
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Dados de exemplo (código, nome, preço de venda, quantidade em estoque)
        dados = [
            ("001", "Arroz Tipo 1 - 5kg", "R$ 23,90", "50"),
            ("002", "Feijão Carioca - 1kg", "R$ 8,50", "75"),
            ("003", "Leite Integral - 1L", "R$ 4,99", "120"),
            ("004", "Café Moído - 500g", "R$ 15,90", "65")
        ]
        
        # Adicionar linhas
        for row, (codigo, nome, preco, estoque) in enumerate(dados):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(preco))
            self.tabela.setItem(row, 3, QTableWidgetItem(estoque))
    
    def selecionar_item(self):
        """Preenche os campos quando uma linha é selecionada"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.codigo_input.setText(self.tabela.item(row, 0).text())
            self.nome_input.setText(self.tabela.item(row, 1).text())
            # Não temos dados para código de barras e marca na tabela
            # então vou apenas limpar esses campos
            self.barras_input.setText("")
            self.marca_input.setText("")
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual se estiver em uma janela separada
        if hasattr(self, 'parent_window') and self.parent_window:
            self.parent_window.close()
        # Alternativamente, você pode implementar a lógica para voltar para outra tela
        print("Voltando para a tela anterior")
    
    def alterar(self):
        """Altera os dados de um produto"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um produto para alterar!")
            return
        
        row = selected_rows[0].row()
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Preencha pelo menos o código e o nome!")
            return
        
        # Atualizar na tabela
        self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
        self.tabela.setItem(row, 1, QTableWidgetItem(nome))
        
        self.mostrar_mensagem("Sucesso", "Produto alterado com sucesso!")
    
    def excluir(self):
        """Exclui um produto"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um produto para excluir!")
            return
        
        row = selected_rows[0].row()
        self.tabela.removeRow(row)
        
        # Limpar os campos
        self.codigo_input.clear()
        self.nome_input.clear()
        self.barras_input.clear()
        self.marca_input.clear()
        self.grupo_combo.setCurrentIndex(0)
        
        self.mostrar_mensagem("Sucesso", "Produto excluído com sucesso!")
    
    def cadastrar(self):
        """Abre a tela de cadastro de produto"""
        # Importar o formulário de produtos
        from formulario_produtos import FormularioProdutos
        
        # Criar uma instância do formulário
        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Cadastro de Produtos")
        self.form_window.setGeometry(100, 100, 800, 600)
        self.form_window.setStyleSheet("background-color: #043b57;")
        
        # Configurar o widget central
        formulario_produtos_widget = FormularioProdutos(self)
        self.form_window.setCentralWidget(formulario_produtos_widget)
        
        # Mostrar a janela de formulário
        self.form_window.show()
    
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
                background-color: white;
            }
            QLabel { 
                color: black;
                background-color: white;
            }
            QPushButton {
                background-color: #043b57;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 2px;
            }
        """)
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Produtos")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    produtos_widget = Produtos(window)
    window.setCentralWidget(produtos_widget)
    
    window.show()
    sys.exit(app.exec_())