import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QMessageBox, QFrame)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSettings
from principal import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MB Sistema - Login")
        self.setFixedSize(450, 600)
        
        # Centralizar a janela na tela
        self.center_on_screen()
        
        # Configurações para salvar dados de usuário
        self.settings = QSettings("MBSistema", "Login")
        
        # Configurar a interface
        self.initUI()
        
        # Carregar o usuário salvo, se existir
        self.carregar_usuario_salvo()
    
    def center_on_screen(self):
        """Centraliza a janela na tela"""
        screen_geometry = QApplication.desktop().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def initUI(self):
        # Define o estilo de fundo
        self.setStyleSheet("background-color: #003b57;")
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_label = QLabel()
        # Caminho absoluto para o logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(400, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Se o logo não for encontrado, cria um texto alternativo
            logo_label = QLabel("MB SISTEMA\nSOLUÇÕES TECNOLÓGICAS")
            logo_label.setFont(QFont("Arial", 24, QFont.Bold))
            logo_label.setStyleSheet("color: #00E676; text-align: center;")
            logo_label.setAlignment(Qt.AlignCenter)
        
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        
        # Espaço após o logo
        main_layout.addSpacing(30)
        
        # Frame para os campos de login
        login_frame = QFrame()
        login_frame.setStyleSheet("background-color: #00304d; border-radius: 10px;")
        login_frame.setFrameShape(QFrame.Box)
        login_frame.setFrameShadow(QFrame.Plain)
        login_frame.setLineWidth(0)
        
        login_layout = QVBoxLayout(login_frame)
        login_layout.setContentsMargins(30, 40, 30, 40)
        login_layout.setSpacing(20)
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 12px;
                font-size: 15px;
                border-radius: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Campo Usuário
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.usuario_input.setStyleSheet(lineedit_style)
        login_layout.addWidget(self.usuario_input)
        
        # Campo Senha
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Senha")
        self.senha_input.setEchoMode(QLineEdit.Password)  # Oculta a senha digitada
        self.senha_input.setStyleSheet(lineedit_style)
        login_layout.addWidget(self.senha_input)
        
        # Campo Empresa
        self.empresa_input = QLineEdit()
        self.empresa_input.setPlaceholderText("Empresa")
        self.empresa_input.setStyleSheet(lineedit_style)
        login_layout.addWidget(self.empresa_input)
        
        # Botão Login
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                border: none;
                padding: 12px;
                font-size: 15px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        self.login_button.clicked.connect(self.login)
        login_layout.addWidget(self.login_button)
        
        main_layout.addWidget(login_frame)
        
        # Versão do programa
        versao_label = QLabel("V. 1.0.0")
        versao_label.setStyleSheet("color: white; font-size: 12px;")
        versao_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(versao_label)
        
        # Conectar evento Enter para entrar
        self.usuario_input.returnPressed.connect(self.avancar_para_senha)
        self.senha_input.returnPressed.connect(self.avancar_para_empresa)
        self.empresa_input.returnPressed.connect(self.login)
    
    def avancar_para_senha(self):
        """Avança para o campo de senha quando Enter é pressionado no campo de usuário"""
        self.senha_input.setFocus()
    
    def avancar_para_empresa(self):
        """Avança para o campo de empresa quando Enter é pressionado no campo de senha"""
        self.empresa_input.setFocus()
    
    def carregar_usuario_salvo(self):
        """Carrega o usuário salvo anteriormente, se existir"""
        usuario_salvo = self.settings.value("ultimo_usuario", "")
        if usuario_salvo:
            self.usuario_input.setText(usuario_salvo)
            self.senha_input.setFocus()  # Coloca o foco no campo de senha
    
    def salvar_usuario(self, usuario):
        """Salva o usuário para uso futuro"""
        self.settings.setValue("ultimo_usuario", usuario)
        self.settings.sync()  # Garante que as configurações sejam salvas imediatamente
    
    def login(self):
        """Processa o login quando o botão é clicado ou Enter é pressionado"""
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()
        empresa = self.empresa_input.text()
        
        # Validação dos campos
        if not usuario:
            self.mostrar_mensagem("Atenção", "Por favor, informe o usuário!")
            self.usuario_input.setFocus()
            return
        
        if not senha:
            self.mostrar_mensagem("Atenção", "Por favor, informe a senha!")
            self.senha_input.setFocus()
            return
        
        if not empresa:
            self.mostrar_mensagem("Atenção", "Por favor, informe a empresa!")
            self.empresa_input.setFocus()
            return
        
        # Salvar o usuário para próximos logins
        self.salvar_usuario(usuario)
        
        # Aqui você pode adicionar a lógica de validação de login real
        # Por enquanto, apenas vamos simular um login bem-sucedido
        
        # Para fins de teste, vamos considerar qualquer login válido
        self.mostrar_mensagem("Sucesso", "Login realizado com sucesso!")
        
        # Abrir a tela principal
        try:
            self.main_window = MainWindow(usuario=usuario, empresa=empresa)
            self.main_window.show()
            self.close()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao abrir o sistema: {str(e)}")
            print(f"Erro ao abrir a tela principal: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Sucesso" in titulo:
            msg_box.setIcon(QMessageBox.Information)
        elif "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
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
                background-color: #003b57;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 2px;
            }
        """)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())