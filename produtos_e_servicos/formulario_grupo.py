#formulario de cadastro de grupo de produtos
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CustomMessageBox(QMessageBox):
    """Classe personalizada para QMessageBox com cores customizadas"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilo para os botões do MessageBox
        self.setStyleSheet("""
            QMessageBox {
                background-color: #043b57;
                color: white;
            }
            QLabel {
                color: white;
                background-color: #043b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: 1px solid #007ab3;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)

class FormularioGrupo(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.codigo_original = None  # Para armazenar o código original em caso de alteração
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
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 30px;
            }
        """
        
        # Estilo específico para ComboBox (fundo branco e seleção azul)
        combo_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #043b57;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #043b57;
                color: white;
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
        self.grupo_combo.setStyleSheet(combo_style)
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
        
        # # Botão Voltar
        # self.btn_voltar = QPushButton("Voltar")
        # self.btn_voltar.setStyleSheet(btn_style)
        # self.btn_voltar.clicked.connect(self.voltar)
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet(btn_style)
        self.btn_salvar.clicked.connect(self.salvar)
        
        #botoes_layout.addWidget(self.btn_voltar)
        botoes_layout.addWidget(self.btn_salvar)
        
        botoes_container = QHBoxLayout()
        botoes_container.addStretch()
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch()
        
        main_layout.addLayout(botoes_container)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem personalizada"""
        msg_box = CustomMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    # def voltar(self):
    #     """Fecha a janela e volta para a tela anterior"""
    #     if self.parent and hasattr(self.parent, 'form_window'):
    #         self.parent.form_window.close()
    
    def salvar(self):
        """Salva os dados do grupo de produtos"""
        # Validação básica
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        grupo = self.grupo_combo.currentText()
        
        if not codigo or not nome or grupo == "Selecione um grupo":
            self.mostrar_mensagem("Campos obrigatórios", "Todos os campos são obrigatórios.", QMessageBox.Warning)
            return
        
        # Verificar se é uma alteração
        if self.codigo_original is not None and self.btn_salvar.text() == "Salvar Alterações":
            # Modo de alteração
            for i, item in enumerate(self.parent.grupos_data):
                if item["codigo"] == self.codigo_original:
                    # Atualizar dados do grupo
                    self.parent.grupos_data[i]["codigo"] = codigo
                    self.parent.grupos_data[i]["nome"] = nome
                    self.parent.grupos_data[i]["grupo"] = grupo
                    
                    # Atualizar a tabela
                    self.parent.carregar_dados()
                    
                    # Mostrar mensagem de sucesso
                    self.mostrar_mensagem("Sucesso", "Grupo de produtos alterado com sucesso!")
                    
                    # Fechar o formulário
                    #self.voltar()
                    return
                    
            # Se chegou aqui, o grupo não foi encontrado
            self.mostrar_mensagem("Erro", "Grupo não encontrado para alteração.", QMessageBox.Warning)
            return
        else:
            # Modo de inclusão - verificar se o código já existe
            for produto in self.parent.grupos_data:
                if produto["codigo"] == codigo:
                    self.mostrar_mensagem("Código duplicado", "Já existe um grupo com este código.", QMessageBox.Warning)
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
            self.mostrar_mensagem("Sucesso", "Grupo de produtos cadastrado com sucesso!")
            
            # Fechar o formulário
            #self.voltar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormularioGrupo()
    window.show()
    sys.exit(app.exec_())