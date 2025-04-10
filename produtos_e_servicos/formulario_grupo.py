
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FormularioGrupo(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Cadastro de Grupo de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; }"
        
        # Estilo para os inputs
        input_style = """
            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 30px;
            }
        """
        
        # Campo Código
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        form_layout.addRow(self.codigo_label, self.codigo_input)
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setStyleSheet(label_style)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(input_style)
        form_layout.addRow(self.nome_label, self.nome_input)
        
        # Campo Grupo
        self.grupo_label = QLabel("Grupo:")
        self.grupo_label.setStyleSheet(label_style)
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(input_style)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Grupo 1")
        self.grupo_combo.addItem("Grupo 2")
        self.grupo_combo.addItem("Grupo 3")
        form_layout.addRow(self.grupo_label, self.grupo_combo)
        
        main_layout.addLayout(form_layout)
        
        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(15)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """
        
        # Botão Voltar
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setStyleSheet(btn_style)
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet(btn_style)
        self.btn_salvar.clicked.connect(self.salvar)
        
        botoes_layout.addWidget(self.btn_voltar)
        botoes_layout.addWidget(self.btn_salvar)
        
        botoes_container = QHBoxLayout()
        botoes_container.addStretch()
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch()
        
        main_layout.addLayout(botoes_container)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
    def voltar(self):
        """Fecha a janela e volta para a tela anterior"""
        if self.parent and hasattr(self.parent, 'form_window'):
            self.parent.form_window.close()
    
    def salvar(self):
        """Salva os dados do grupo de produtos"""
        # Validação básica
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        grupo = self.grupo_combo.currentText()
        
        if not codigo or not nome or grupo == "Selecione um grupo":
            QMessageBox.warning(self, "Campos obrigatórios", "Todos os campos são obrigatórios.")
            return
        
        # Verificar se o código já existe
        for produto in self.parent.grupos_data:
            if produto["codigo"] == codigo:
                QMessageBox.warning(self, "Código duplicado", "Já existe um grupo com este código.")
                return
        
        # Adicionar novo grupo à lista
        novo_grupo = {
            "codigo": codigo,
            "nome": nome,
            "grupo": grupo
        }
        
        # Adicionar à lista de dados
        self.parent.grupos_data.append(novo_grupo)
        
        # Atualizar a tabela
        self.parent.carregar_dados()
        
        # Mostrar mensagem de sucesso
        QMessageBox.information(self, "Sucesso", "Grupo de produtos cadastrado com sucesso!")
        
        # Fechar o formulário
        if self.parent and hasattr(self.parent, 'form_window'):
            self.parent.form_window.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormularioGrupo()
    window.show()
    sys.exit(app.exec_())
