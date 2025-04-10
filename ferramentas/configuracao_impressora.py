#configuração de impressora
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinterInfo, QPrintDialog, QPrinter


class ConfiguracaoImpressoraWindow(QWidget):
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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(30)
        
        # Fundo para todo o aplicativo
        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())
        
        # Título em uma barra azul escura
        titulo_container = QWidget()
        titulo_container.setStyleSheet("background-color: #043b57;")
        titulo_container_layout = QVBoxLayout(titulo_container)
        titulo_container_layout.setContentsMargins(10, 10, 10, 10)
        
        titulo = QLabel("Configuração de estação")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_container_layout.addWidget(titulo)
        
        main_layout.addWidget(titulo_container)
        
        # Botões de categoria
        categorias_layout = QHBoxLayout()
        categorias_layout.setSpacing(5)
        
        categoria_style = """
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 15px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover, QPushButton:checked {
                background-color: #003d5c;
            }
        """
        
        self.categorias = ["Padrão", "Orçamento", "Pedidos", "Pedidos de Venda"]
        self.categoria_buttons = []
        
        for categoria in self.categorias:
            btn = QPushButton(categoria)
            btn.setStyleSheet(categoria_style)
            btn.setCheckable(True)
            categorias_layout.addWidget(btn)
            self.categoria_buttons.append(btn)
            btn.clicked.connect(self.mudar_categoria)
        
        self.categoria_buttons[0].setChecked(True)  # Por padrão, selecionar o primeiro botão
        main_layout.addLayout(categorias_layout)
        
        # Área de seleção de impressora
        impressora_frame = QFrame()
        impressora_frame.setStyleSheet("background-color: #fffff0; border-radius: 4px;")
        impressora_layout = QHBoxLayout(impressora_frame)
        impressora_layout.setContentsMargins(20, 20, 20, 20)
        
        # Texto "Escolher Impressora"
        escolher_label = QLabel("Escolher\nImpressora")
        escolher_label.setFont(QFont("Arial", 16, QFont.Bold))
        escolher_label.setStyleSheet("color: black;")
        impressora_layout.addWidget(escolher_label)
        
        # Campo para mostrar a impressora selecionada
        self.impressora_input = QLineEdit()
        self.impressora_input.setStyleSheet("""
            QLineEdit {
                background-color: #e8f0ff;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                min-height: 25px;
                border-radius: 4px;
                color: black;
            }
        """)
        self.impressora_input.setReadOnly(True)  # Campo apenas para exibição
        self.impressora_input.mousePressEvent = self.selecionar_impressora  # Abrir diálogo ao clicar
        impressora_layout.addWidget(self.impressora_input, 1)  # 1 para expandir e ocupar espaço disponível
        
        # Botão com ícone de impressora
        self.btn_impressora = QPushButton()
        self.btn_impressora.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
        """)
        # Definir um ícone de impressora
        icon_path = "printer.png"  # Você pode precisar fornecer o caminho correto para um ícone de impressora
        try:
            self.btn_impressora.setIcon(QIcon.fromTheme("printer"))
        except:
            # Usar emoji como fallback
            self.btn_impressora.setText("🖨️")
            self.btn_impressora.setFont(QFont("Arial", 18))
        
        self.btn_impressora.clicked.connect(self.selecionar_impressora)
        impressora_layout.addWidget(self.btn_impressora)
        
        main_layout.addWidget(impressora_frame)
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                font-weight: bold;
                padding: 15px 0;
                font-size: 16px;
                border-radius: 25px;
                margin: 10px 50px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar_configuracao)
        main_layout.addWidget(self.btn_salvar)
        
        # Adicionar espaço no final
        main_layout.addStretch()
        
        # Definir cor de fundo para a aplicação inteira
        app = QApplication.instance()
        if app:
            app.setStyleSheet("QWidget { background-color: #043b57; color: white; }")
            
        # Aplicar estilo no widget atual
        self.setStyleSheet("""
            QWidget { background-color: #043b57; }
            QMessageBox { background-color: white; }
        """)
        
        # Armazenar as configurações de impressoras
        self.impressoras = {
            "Padrão": "",
            "Orçamento": "",
            "Pedidos": "",
            "Pedidos de Venda": ""
        }
        
        # Categoria atual
        self.categoria_atual = "Padrão"
    
    def mudar_categoria(self):
        """Muda a categoria selecionada e carrega a configuração correspondente"""
        sender = self.sender()
        if sender:
            # Desmarcar todos os botões
            for btn in self.categoria_buttons:
                if btn != sender:
                    btn.setChecked(False)
            
            # Marcar o botão clicado
            sender.setChecked(True)
            
            # Atualizar categoria atual
            self.categoria_atual = sender.text()
            
            # Carregar configuração da categoria
            self.carregar_configuracao()
    
    def carregar_configuracao(self):
        """Carrega a configuração da impressora para a categoria atual"""
        # Aqui você carregaria a configuração do banco de dados/arquivo
        # Por enquanto, vamos usar o dicionário local
        impressora = self.impressoras.get(self.categoria_atual, "")
        self.impressora_input.setText(impressora)
    
    def selecionar_impressora(self, event=None):
        """Abre o diálogo de seleção de impressora"""
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        dialog.setOption(QPrintDialog.PrintToFile, False)
        dialog.setOption(QPrintDialog.PrintSelection, False)
        dialog.setOption(QPrintDialog.PrintPageRange, False)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            impressora_nome = printer.printerName()
            self.impressora_input.setText(impressora_nome)
            self.impressoras[self.categoria_atual] = impressora_nome
    
    def salvar_configuracao(self):
        """Salva a configuração da impressora para a categoria atual"""
        if not self.impressora_input.text():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Atenção")
            msg_box.setText(f"Por favor, selecione uma impressora para {self.categoria_atual}.")
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
            return
            
        # Exibir mensagem de sucesso
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Configuração Salva")
        msg_box.setText(f"Impressora para {self.categoria_atual} configurada com sucesso!")
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
        
        # Aqui você salvaria a configuração no banco de dados/arquivo


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Configuração de Impressoras")
    window.setGeometry(100, 100, 800, 500)
    window.setStyleSheet("background-color: #043b57;")
    
    configuracao_widget = ConfiguracaoImpressoraWindow()
    window.setCentralWidget(configuracao_widget)
    
    window.show()
    sys.exit(app.exec_())