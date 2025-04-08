import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QFormLayout, QMessageBox, QTableWidgetItem)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class FormularioEmail(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela  # Referência para a tela de cadastro
        self.janela_parent = janela_parent  # Referência para a janela que contém este widget
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Layout para o botão de voltar e título
        header_layout = QHBoxLayout()
        
        # Botão de voltar
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setFixedWidth(80)
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Título
        titulo_layout = QVBoxLayout()
        titulo = QLabel("Cadastro de Email")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(titulo)
        
        # Adicionar botão de voltar e título ao header
        header_layout.addWidget(self.btn_voltar)
        header_layout.addLayout(titulo_layout)
        
        main_layout.addLayout(header_layout)
        
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
        
        # Campo Código
        codigo_layout = QFormLayout()
        codigo_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        codigo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        self.codigo_input.setFixedWidth(150)
        self.codigo_input.setReadOnly(True)  # Código é gerado automaticamente
        
        codigo_layout.addRow(self.codigo_label, self.codigo_input)
        main_layout.addLayout(codigo_layout)
        
        # Campo Email
        email_layout = QFormLayout()
        email_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        email_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet(label_style)
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(input_style)
        self.email_input.setPlaceholderText("exemplo@email.com")
        
        email_layout.addRow(self.email_label, self.email_input)
        main_layout.addLayout(email_layout)
        
        # Campo Nome
        nome_layout = QFormLayout()
        nome_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        nome_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.nome_label = QLabel("Nome:")
        self.nome_label.setStyleSheet(label_style)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(input_style)
        
        nome_layout.addRow(self.nome_label, self.nome_input)
        main_layout.addLayout(nome_layout)
        
        # Espaço entre os campos e botão
        main_layout.addSpacing(20)
        
        # Botão Incluir
        incluir_layout = QHBoxLayout()
        incluir_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                font-weight: bold;
                padding: 12px 40px;
                font-size: 16px;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir.clicked.connect(self.salvar_email)
        
        incluir_layout.addWidget(self.btn_incluir)
        main_layout.addLayout(incluir_layout)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
    
    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
    def validar_email(self, email):
        """Valida o formato do email"""
        import re
        # Validação simples de email
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(padrao, email):
            return True
        return False
    
    def salvar_email(self):
        """Salva os dados do email na tabela da tela de cadastro"""
        email = self.email_input.text()
        nome = self.nome_input.text()
        
        # Validação básica
        if not email:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Campo obrigatório")
            msg_box.setText("Por favor, informe o email.")
            msg_box.setStyleSheet("QMessageBox { background-color: white; }")
            msg_box.exec_()
            return
            
        if not nome:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Campo obrigatório")
            msg_box.setText("Por favor, informe o nome.")
            msg_box.setStyleSheet("QMessageBox { background-color: white; }")
            msg_box.exec_()
            return
        
        # Validar formato do email
        if not self.validar_email(email):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Email inválido")
            msg_box.setText("Por favor, informe um email válido.")
            msg_box.setStyleSheet("QMessageBox { background-color: white; }")
            msg_box.exec_()
            return
        
        # Verificar acesso à tabela
        if not self.cadastro_tela or not hasattr(self.cadastro_tela, 'table'):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Erro")
            msg_box.setText("Não foi possível acessar a tabela de emails.")
            msg_box.setStyleSheet("QMessageBox { background-color: white; }")
            msg_box.exec_()
            return
        
        # Verificar email duplicado
        for row in range(self.cadastro_tela.table.rowCount()):
            email_cell = self.cadastro_tela.table.item(row, 1)
            if email_cell and email_cell.text() == email:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Email duplicado")
                msg_box.setText("Este email já está cadastrado.")
                msg_box.setStyleSheet("QMessageBox { background-color: white; }")
                msg_box.exec_()
                return
        
        # Gerar código
        ultimo_codigo = 0
        if self.cadastro_tela.table.rowCount() > 0:
            ultimo_codigo = int(self.cadastro_tela.table.item(self.cadastro_tela.table.rowCount()-1, 0).text())
        
        novo_codigo = ultimo_codigo + 1
        
        # Adicionar à tabela
        row_position = self.cadastro_tela.table.rowCount()
        self.cadastro_tela.table.insertRow(row_position)
        self.cadastro_tela.table.setItem(row_position, 0, QTableWidgetItem(str(novo_codigo)))
        self.cadastro_tela.table.setItem(row_position, 1, QTableWidgetItem(email))
        
        # Mensagem de sucesso
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Sucesso")
        msg_box.setText(f"Email cadastrado com sucesso!\nEmail: {email}\nCódigo: {novo_codigo}")
        msg_box.setStyleSheet("QMessageBox { background-color: white; }")
        msg_box.exec_()
        
        # Fechar a janela
        if self.janela_parent:
            self.janela_parent.close()


# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Formulário de Cadastro de Email")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    from PyQt5.QtWidgets import QTableWidgetItem
    # Criar uma classe mock para teste
    class MockCadastroTela:
        def __init__(self):
            from PyQt5.QtWidgets import QTableWidget
            self.table = QTableWidget()
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["Código", "Email"])
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem("1"))
            self.table.setItem(0, 1, QTableWidgetItem("teste@email.com"))
    
    form_widget = FormularioEmail(cadastro_tela=MockCadastroTela())
    window.setCentralWidget(form_widget)
    
    window.show()
    sys.exit(app.exec_())