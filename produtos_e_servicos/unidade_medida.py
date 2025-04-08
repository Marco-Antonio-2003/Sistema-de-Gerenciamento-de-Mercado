import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QComboBox, QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class UnidadeMedida(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        titulo = QLabel("Unidade de Medida")
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
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        codigo_layout.addWidget(self.codigo_input)
        fields_layout.addLayout(codigo_layout)
        
        # Campo Nome da Medida (dropdown)
        nome_layout = QVBoxLayout()
        nome_label = QLabel("Nome da Medida:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_combo = QComboBox()
        self.nome_combo.setStyleSheet("""
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
                selection-background-color: #e6e6e6;
            }
        """)
        # Adicionar itens ao ComboBox (apenas unidades comuns em supermercados)
        self.nome_combo.addItem("Selecione uma unidade")
        self.nome_combo.addItem("Quilograma (kg)")
        self.nome_combo.addItem("Grama (g)")
        self.nome_combo.addItem("Litro (L)")
        self.nome_combo.addItem("Mililitro (mL)")
        self.nome_combo.addItem("Unidade (un)")
        self.nome_combo.addItem("Pacote (pct)")
        self.nome_combo.addItem("Caixa (cx)")
        self.nome_combo.addItem("Bandeja (bdj)")
        self.nome_combo.addItem("Dúzia (dz)")
        self.nome_combo.addItem("Fardo (fd)")
        self.nome_combo.addItem("Garrafa (gf)")
        nome_layout.addWidget(self.nome_combo)
        fields_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(fields_layout)
        
        # Layout para botões de ação
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 20, 0, 20)
        
        # Espaçador à esquerda para centralizar os botões
        actions_layout.addStretch(1)
        
        # # Botão Alterar
        # btn_alterar = QPushButton("Alterar")
        # btn_alterar.setIcon(QIcon("editar.png"))  # Você precisará ter este ícone
        # btn_alterar.setStyleSheet("""
        #     QPushButton {
        #         background-color: #fffff0;
        #         color: black;
        #         border: 1px solid #cccccc;
        #         padding: 10px 20px;
        #         font-size: 14px;
        #         border-radius: 4px;
        #         text-align: center;
        #     }
        #     QPushButton:hover {
        #         background-color: #e6e6d9;
        #     }
        # """)
        # btn_alterar.clicked.connect(self.alterar)
        # actions_layout.addWidget(btn_alterar)
        
        # Espaço entre os botões
        spacer = QWidget()
        spacer.setFixedWidth(20)
        actions_layout.addWidget(spacer)
        
        # # Botão Excluir
        # btn_excluir = QPushButton("Excluir")
        # btn_excluir.setIcon(QIcon("lixeira.png"))  # Você precisará ter este ícone
        # btn_excluir.setStyleSheet("""
        #     QPushButton {
        #         background-color: #fffff0;
        #         color: black;
        #         border: 1px solid #cccccc;
        #         padding: 10px 20px;
        #         font-size: 14px;
        #         border-radius: 4px;
        #         text-align: center;
        #     }
        #     QPushButton:hover {
        #         background-color: #e6e6d9;
        #     }
        # """)
        # btn_excluir.clicked.connect(self.excluir)
        # actions_layout.addWidget(btn_excluir)
        
        # Espaçador à direita para centralizar os botões
        actions_layout.addStretch(1)
        
        main_layout.addLayout(actions_layout)
        
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
                margin: 0 100px;
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
        # Aqui você implementaria a navegação de volta
        print("Voltar para a tela anterior")
    
    def alterar(self):
        """Altera a unidade de medida selecionada"""
        codigo = self.codigo_input.text()
        nome = self.nome_combo.currentText()
        
        if not codigo or nome == "Selecione uma unidade":
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!")
            return
        
        self.mostrar_mensagem("Sucesso", "Unidade de medida alterada com sucesso!")
    
    def excluir(self):
        """Exclui a unidade de medida selecionada"""
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Atenção", "Selecione uma unidade de medida para excluir!")
            return
        
        # Limpar os campos
        self.codigo_input.clear()
        self.nome_combo.setCurrentIndex(0)
        
        self.mostrar_mensagem("Sucesso", "Unidade de medida excluída com sucesso!")
    
    def incluir(self):
        """Inclui uma nova unidade de medida"""
        codigo = self.codigo_input.text()
        nome = self.nome_combo.currentText()
        
        if not codigo or nome == "Selecione uma unidade":
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!")
            return
        
        # Limpar os campos após inclusão
        self.codigo_input.clear()
        self.nome_combo.setCurrentIndex(0)
        
        self.mostrar_mensagem("Sucesso", "Unidade de medida incluída com sucesso!")
    
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
    window.setWindowTitle("Unidade de Medida")
    window.setGeometry(100, 100, 800, 400)
    window.setStyleSheet("background-color: #043b57;")
    
    unidade_medida_widget = UnidadeMedida()
    window.setCentralWidget(unidade_medida_widget)
    
    window.show()
    sys.exit(app.exec_())