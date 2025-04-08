import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from formulario_email import FormularioEmail

class CadastroEmail(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = QLabel("Cadastro de Email")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; font-weight: bold; }"
        
        # Estilo para os inputs
        input_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
        """
        
        # Campo Email
        email_layout = QHBoxLayout()
        
        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet(label_style)
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(input_style)
        
        email_layout.addWidget(self.email_label)
        email_layout.addWidget(self.email_input)
        
        main_layout.addLayout(email_layout)
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        self.codigo_input.setFixedWidth(150)
        
        codigo_layout.addWidget(self.codigo_label)
        codigo_layout.addWidget(self.codigo_input)
        codigo_layout.addStretch()
        
        main_layout.addLayout(codigo_layout)
        
        # Layout para os botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setAlignment(Qt.AlignCenter)
        botoes_layout.setSpacing(10)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setStyleSheet(btn_style)
        try:
            self.btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        self.btn_cadastrar.clicked.connect(self.abrir_formulario_email)
        
        # Botão Alterar
        self.btn_alterar = QPushButton("Alterar")
        self.btn_alterar.setStyleSheet(btn_style)
        try:
            self.btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        self.btn_alterar.clicked.connect(self.alterar_email)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setStyleSheet(btn_style)
        try:
            self.btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        self.btn_excluir.clicked.connect(self.excluir_email)
        
        botoes_layout.addWidget(self.btn_cadastrar)
        botoes_layout.addWidget(self.btn_alterar)
        botoes_layout.addWidget(self.btn_excluir)
        
        main_layout.addLayout(botoes_layout)
        main_layout.addSpacing(15)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Código", "Email"])
        
        # Configurar cabeçalhos da tabela
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Estilo da tabela - Modificado para usar a cor #0078d7 na seleção
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #fffff0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        # Permitir seleção de linha completa
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        self.table.itemClicked.connect(self.selecionar_email)
        
        # Adicionar tabela ao layout principal
        main_layout.addWidget(self.table)
        
        # Estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
        # Dados iniciais para testes
        self.carregar_dados_teste()
    
    def carregar_dados_teste(self):
        """Carrega alguns dados de teste na tabela"""
        dados_teste = [
            ("1", "joao.silva@email.com"),
            ("2", "maria.oliveira@email.com"),
            ("3", "carlos.souza@email.com")
        ]
        
        self.table.setRowCount(len(dados_teste))
        
        for i, (codigo, email) in enumerate(dados_teste):
            self.table.setItem(i, 0, QTableWidgetItem(codigo))
            self.table.setItem(i, 1, QTableWidgetItem(email))
    
    def selecionar_email(self, item):
        """Seleciona um email na tabela e preenche os campos"""
        row = item.row()
        
        codigo = self.table.item(row, 0).text()
        email = self.table.item(row, 1).text()
        
        self.codigo_input.setText(codigo)
        self.email_input.setText(email)
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem para o usuário"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStyleSheet("QMessageBox { background-color: white; }")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def abrir_formulario_email(self):
        """Abre o formulário para cadastro de email"""
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Formulário de Cadastro de Email")
        self.janela_formulario.setGeometry(150, 150, 600, 400)
        self.janela_formulario.setStyleSheet("background-color: #043b57;")
        
        formulario = FormularioEmail(cadastro_tela=self, janela_parent=self.janela_formulario)
        self.janela_formulario.setCentralWidget(formulario)
        
        self.janela_formulario.show()
    
    def alterar_email(self):
        """Abre o formulário para alteração de email selecionado"""
        # Verificar se há uma linha selecionada
        if not self.codigo_input.text():
            self.mostrar_mensagem("Seleção necessária", 
                                "Selecione um email para alterar.", 
                                QMessageBox.Warning)
            return
        
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Alterar Cadastro de Email")
        self.janela_formulario.setGeometry(150, 150, 600, 400)
        self.janela_formulario.setStyleSheet("background-color: #043b57;")
        
        formulario = FormularioEmail(cadastro_tela=self, janela_parent=self.janela_formulario)
        
        # Preencher os dados do email selecionado no formulário
        codigo = self.codigo_input.text()
        email = self.email_input.text()
        
        formulario.codigo_input.setText(codigo)
        formulario.email_input.setText(email)
        
        # Em uma implementação real, você buscaria o nome do email no banco de dados
        # Para este exemplo, usaremos um nome genérico
        nome = "Nome do Contato"
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == codigo:
                # Se existir uma coluna para nome na tabela real, você usaria isso
                # nome = self.table.item(row, 2).text()
                break
                
        formulario.nome_input.setText(nome)
        
        self.janela_formulario.setCentralWidget(formulario)
        self.janela_formulario.show()
    
    def excluir_email(self):
        """Exclui o email selecionado na tabela"""
        # Verificar se há uma linha selecionada
        if not self.codigo_input.text():
            self.mostrar_mensagem("Seleção necessária", 
                                "Selecione um email para excluir.", 
                                QMessageBox.Warning)
            return
        
        # Confirmar exclusão
        codigo = self.codigo_input.text()
        email = self.email_input.text()
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir o email '{email}' (Código: {codigo})?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("QMessageBox { background-color: white; }")
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.Yes:
            # Busca a linha pelo código
            encontrado = False
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).text() == codigo:
                    self.table.removeRow(row)
                    
                    # Limpa os campos
                    self.codigo_input.clear()
                    self.email_input.clear()
                    
                    self.mostrar_mensagem("Sucesso", f"Email '{email}' excluído com sucesso!")
                    encontrado = True
                    break
            
            if not encontrado:
                self.mostrar_mensagem("Não encontrado", 
                                    f"Email com código {codigo} não encontrado.", 
                                    QMessageBox.Warning)


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Sistema de Cadastro de Emails")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    cadastro_widget = CadastroEmail()
    window.setCentralWidget(cadastro_widget)
    
    window.show()
    sys.exit(app.exec_())