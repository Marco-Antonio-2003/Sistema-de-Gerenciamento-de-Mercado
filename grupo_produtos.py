import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class GrupoProdutos(QWidget):
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
        titulo = QLabel("Grupo de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Layout para campos superiores
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(20)
        
        # Campo Código
        codigo_layout = QVBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        codigo_layout.addWidget(self.codigo_input)
        fields_layout.addLayout(codigo_layout)
        
        # Campo Nome
        nome_layout = QVBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        nome_layout.addWidget(self.nome_input)
        fields_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(fields_layout)
        
        # Layout para botões e grupo de produtos
        actions_layout = QHBoxLayout()
        
        # Layout para botões de ação
        buttons_layout = QVBoxLayout()
        
        # Botão Alterar
        btn_alterar = QPushButton("Alterar")
        # Adicionar ícone para o botão Alterar usando ícones do sistema
        try:
            btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        btn_alterar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6d9;
            }
        """)
        btn_alterar.clicked.connect(self.alterar)
        buttons_layout.addWidget(btn_alterar)
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        # Adicionar ícone para o botão Excluir usando ícones do sistema
        try:
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6d9;
            }
        """)
        btn_excluir.clicked.connect(self.excluir)
        buttons_layout.addWidget(btn_excluir)
        
        actions_layout.addLayout(buttons_layout)
        
        # Campo Grupo de Produtos (dropdown)
        grupo_layout = QVBoxLayout()
        grupo_label = QLabel("Grupo de Produtos:")
        grupo_label.setStyleSheet("color: white; font-size: 14px;")
        grupo_layout.addWidget(grupo_label)
        
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet("""
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        # Adicionar itens ao ComboBox (você deve adaptar para seus dados reais)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Grupo 1")
        self.grupo_combo.addItem("Grupo 2")
        self.grupo_combo.addItem("Grupo 3")
        grupo_layout.addWidget(self.grupo_combo)
        
        actions_layout.addLayout(grupo_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(actions_layout)
        
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
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Grupo"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
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
        
        # Dados de exemplo (código, nome, grupo)
        dados = [
            ("001", "Produto A", "Grupo 1"),
            ("002", "Produto B", "Grupo 2"),
            ("003", "Produto C", "Grupo 1"),
            ("004", "Produto D", "Grupo 3")
        ]
        
        # Adicionar linhas
        for row, (codigo, nome, grupo) in enumerate(dados):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(grupo))
    
    def selecionar_item(self):
        """Preenche os campos quando uma linha é selecionada"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.codigo_input.setText(self.tabela.item(row, 0).text())
            self.nome_input.setText(self.tabela.item(row, 1).text())
            
            # Encontrar e selecionar o grupo correto
            grupo_text = self.tabela.item(row, 2).text()
            index = self.grupo_combo.findText(grupo_text)
            if index >= 0:
                self.grupo_combo.setCurrentIndex(index)
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual se estiver em uma janela separada
        if hasattr(self, 'parent_window') and self.parent_window:
            self.parent_window.close()
        # Alternativamente, você pode implementar a lógica para voltar para outra tela
        # Como por exemplo, mudar o widget central de um QMainWindow
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
        grupo = self.grupo_combo.currentText()
        
        if not codigo or not nome or grupo == "Selecione um grupo":
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!")
            return
        
        # Atualizar na tabela
        self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
        self.tabela.setItem(row, 1, QTableWidgetItem(nome))
        self.tabela.setItem(row, 2, QTableWidgetItem(grupo))
        
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
        self.grupo_combo.setCurrentIndex(0)
        
        self.mostrar_mensagem("Sucesso", "Produto excluído com sucesso!")
    
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
    window.setWindowTitle("Grupo de Produtos")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    grupo_produtos_widget = GrupoProdutos(window)
    window.setCentralWidget(grupo_produtos_widget)
    
    window.show()
    sys.exit(app.exec_())