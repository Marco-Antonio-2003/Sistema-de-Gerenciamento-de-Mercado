#formulario_produtos.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QDateEdit, QComboBox, QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate

class FormularioProdutos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
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
        titulo = QLabel("Cadastro de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Estilo comum para QComboBox
        combobox_style = """
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
        """
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Primeira linha de campos
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(20)
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        codigo_layout.addWidget(self.codigo_input)
        linha1_layout.addLayout(codigo_layout)
        
        # Campo Nome
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
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
        self.barras_input.setStyleSheet(lineedit_style)
        barras_layout.addWidget(self.barras_input)
        linha2_layout.addLayout(barras_layout, 1)  # 1 para expandir
        
        # Campo Grupo
        grupo_layout = QHBoxLayout()
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet("color: white; font-size: 14px;")
        grupo_layout.addWidget(grupo_label)
        
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(combobox_style)
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
        
        self.marca_combo = QComboBox()
        self.marca_combo.setStyleSheet(combobox_style)
        # Adicione um botão de "+" na interface do ComboBox
        self.marca_combo.addItem("Selecione uma marca")
        self.marca_combo.addItem("Nestlé")
        self.marca_combo.addItem("Unilever")
        self.marca_combo.addItem("Procter & Gamble")
        self.marca_combo.addItem("Coca-Cola")
        self.marca_combo.addItem("Camil")
        marca_layout.addWidget(self.marca_combo)
        
        linha3_layout.addLayout(marca_layout, 1)  # 1 para expandir
        
        # Campo Preço de Venda
        preco_venda_layout = QHBoxLayout()
        preco_venda_label = QLabel("Preço de venda")
        preco_venda_label.setStyleSheet("color: white; font-size: 14px;")
        preco_venda_layout.addWidget(preco_venda_label)
        
        self.preco_venda_input = QLineEdit()
        self.preco_venda_input.setStyleSheet(lineedit_style)
        preco_venda_layout.addWidget(self.preco_venda_input)
        linha3_layout.addLayout(preco_venda_layout)
        
        # Campo Preço de Compra
        preco_compra_layout = QHBoxLayout()
        preco_compra_label = QLabel("Preço de Compra")
        preco_compra_label.setStyleSheet("color: white; font-size: 14px;")
        preco_compra_layout.addWidget(preco_compra_label)
        
        self.preco_compra_input = QLineEdit()
        self.preco_compra_input.setStyleSheet(lineedit_style)
        preco_compra_layout.addWidget(self.preco_compra_input)
        linha3_layout.addLayout(preco_compra_layout)
        
        main_layout.addLayout(linha3_layout)
        
        # Quarta linha de campos
        linha4_layout = QHBoxLayout()
        linha4_layout.setSpacing(20)
        
        # Campo Data de Cadastro
        data_layout = QHBoxLayout()
        data_label = QLabel("Data de Cadastro:")
        data_label.setStyleSheet("color: white; font-size: 14px;")
        data_layout.addWidget(data_label)
        
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit:hover {
                border: 1px solid #0078d7;
            }
        """)
        data_layout.addWidget(self.data_input)
        linha4_layout.addLayout(data_layout)
        
        # Campo Unidade
        unidade_layout = QHBoxLayout()
        unidade_label = QLabel("Unidade:")
        unidade_label.setStyleSheet("color: white; font-size: 14px;")
        unidade_layout.addWidget(unidade_label)
        
        self.unidade_combo = QComboBox()
        self.unidade_combo.setStyleSheet(combobox_style)
        self.unidade_combo.addItem("Selecione uma unidade")
        self.unidade_combo.addItem("Quilograma (kg)")
        self.unidade_combo.addItem("Grama (g)")
        self.unidade_combo.addItem("Litro (L)")
        self.unidade_combo.addItem("Mililitro (mL)")
        self.unidade_combo.addItem("Unidade (un)")
        self.unidade_combo.addItem("Pacote (pct)")
        self.unidade_combo.addItem("Caixa (cx)")
        self.unidade_combo.addItem("Bandeja (bdj)")
        self.unidade_combo.addItem("Dúzia (dz)")
        self.unidade_combo.addItem("Fardo (fd)")
        self.unidade_combo.addItem("Garrafa (gf)")
        unidade_layout.addWidget(self.unidade_combo)
        linha4_layout.addLayout(unidade_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(linha4_layout)
        
        # Botão Incluir
        btn_incluir = QPushButton("Incluir")
        btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 15px 0;
                font-size: 16px;
                border-radius: 4px;
                margin: 20px 100px 0;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(btn_incluir)
        
        # Adicionar espaço no final
        main_layout.addStretch()
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual
        if hasattr(self, 'parent_widget') and self.parent_widget and hasattr(self.parent_widget, 'form_window'):
            self.parent_widget.form_window.close()
        else:
            # Se não encontrar a janela pai, tenta fechar a janela atual
            parent_window = self.window()
            if parent_window and parent_window != self:
                parent_window.close()
            else:
                print("Voltar para a tela de produtos")
    
    def incluir(self):
        """Inclui um novo produto"""
        # Validar campos obrigatórios
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        grupo = self.grupo_combo.currentText()
        unidade = self.unidade_combo.currentText()
        preco_venda = self.preco_venda_input.text()
        
        if not codigo or not nome or grupo == "Selecione um grupo" or unidade == "Selecione uma unidade" or not preco_venda:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos obrigatórios (Código, Nome, Grupo, Unidade e Preço de Venda)!")
            return
        
        # Limpar os campos após inclusão
        self.codigo_input.clear()
        self.nome_input.clear()
        self.barras_input.clear()
        self.marca_combo.setCurrentIndex(0)
        self.preco_venda_input.clear()
        self.preco_compra_input.clear()
        self.data_input.setDate(QDate.currentDate())
        self.grupo_combo.setCurrentIndex(0)
        self.unidade_combo.setCurrentIndex(0)
        
        self.mostrar_mensagem("Sucesso", "Produto incluído com sucesso!")
    
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
    window.setWindowTitle("Cadastro de Produtos")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    formulario_produtos_widget = FormularioProdutos(window)
    window.setCentralWidget(formulario_produtos_widget)
    
    window.show()
    sys.exit(app.exec_())