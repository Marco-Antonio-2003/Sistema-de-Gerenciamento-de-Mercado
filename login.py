import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                          QHBoxLayout, QPushButton, QLabel, QLineEdit,
                          QMessageBox, QFrame)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QSettings, QSize
from principal import MainWindow
from base.banco import validar_login, verificar_tabela_usuarios

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MB Sistema - Login")
        self.setFixedSize(700, 500)
        
        # Centralizar a janela na tela
        self.center_on_screen()
        
        # Configurações para salvar dados de usuário
        self.settings = QSettings("MBSistema", "Login")
        
        # Configurar a interface
        self.initUI()
        
        # Inicializar banco de dados
        self.inicializar_bd()
        
        # Carregar o usuário e empresa salvos, se existirem
        self.carregar_dados_salvos()
    
    def inicializar_bd(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        try:
            verificar_tabela_usuarios()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao inicializar banco de dados: {e}")
    
    def center_on_screen(self):
        """Centraliza a janela na tela"""
        screen_geometry = QApplication.desktop().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def paintEvent(self, event):
        """Desenha o fundo e o painel de login semitransparente"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Definir o fundo (azul escuro como fallback)
        painter.fillRect(self.rect(), QColor("#003366"))
        
        try:
            # Carregar a imagem de fundo da pasta ico-img
            background_path = resource_path(os.path.join("ico-img", "fundo_login.jpeg"))
            background = QPixmap(background_path)
            if not background.isNull():
                painter.drawPixmap(self.rect(), background)
            else:
                print(f"Erro ao carregar imagem: {background_path} não encontrado")
        except Exception as e:
            print(f"Erro ao carregar imagem de fundo: {e}")
            
        # ==== AQUI É ONDE O QUADRADO TRANSPARENTE É DESENHADO ====
            
        # Desenhar o painel de login com gradiente semitransparente
        panel_color = QColor("#6b809b")
        panel_color.setAlpha(200)  # Ajustar transparência (0-255)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        
        # Criar variações da cor base com diferentes níveis de transparência
        top_color = QColor("#6b809b")
        top_color.setAlpha(210)
        
        bottom_color = QColor("#6b809b")
        bottom_color.setAlpha(190)
        
        gradient.setColorAt(0, top_color)
        gradient.setColorAt(1, bottom_color)
        
        # Determinar tamanho e posição do painel
        panel_width = 400  # Largura do quadrado
        panel_height = 350  # Altura do quadrado
        panel_x = (self.width() - panel_width) // 2  # Centralização horizontal
        panel_y = (self.height() - panel_height) // 2 + 30  # Posição vertical (+ empurra para baixo)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(panel_x, panel_y, panel_width, panel_height, 10, 10)  # Último parâmetro: raio dos cantos arredondados
    
    def initUI(self):
        # Widget central transparente
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        
        # Layout principal - reduzindo a margem superior para subir os elementos
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 25, 0, 0)  # Diminuindo a margem superior
        
        # Container para centralizar o form
        form_container = QWidget()
        form_container.setAttribute(Qt.WA_TranslucentBackground)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 15, 30, 30)  # Reduzindo a margem superior
        form_layout.setSpacing(10)  # Reduzindo o espaçamento entre elementos
        
        # Título do sistema - com menos espaço abaixo
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignHCenter)
        title_layout.setContentsMargins(0, 0, 0, 5)  # Reduzindo o espaço abaixo dos títulos
        
        # Ajustando cores conforme especificado
        mb_label = QLabel("MB SISTEMA")
        mb_label.setFont(QFont("Arial", 22, QFont.Bold))
        mb_label.setStyleSheet("color: #a6a6a6;")
        mb_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(mb_label)
        
        subtitle_label = QLabel("SISTEMA DE GERENCIAMENTO")
        subtitle_label.setFont(QFont("Arial", 18, QFont.Bold))
        subtitle_label.setStyleSheet("color: #f7f8f9;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle_label)
        
        # Adicionar títulos diretamente ao layout principal para ficarem fora do painel
        # Usando um stretch pequeno (0 em vez de 1) para abaixar os títulos
        main_layout.addStretch(0)
        main_layout.addLayout(title_layout)
        
        form_layout.addSpacing(10)  # Reduzindo o espaçamento
        
        # Estilo para os rótulos
        label_style = "color: white; font-size: 14px; font-weight: bold;"
        
        # Campo Usuário
        usuario_label = QLabel("USUÁRIO")
        usuario_label.setStyleSheet(label_style)
        form_layout.addWidget(usuario_label)
        
        self.usuario_input = QLineEdit()
        self.usuario_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.usuario_input)
        
        # Campo Senha
        senha_label = QLabel("SENHA")
        senha_label.setStyleSheet(label_style)
        form_layout.addWidget(senha_label)
        
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.senha_input)
        
        # Campo Empresa
        empresa_label = QLabel("EMPRESA")
        empresa_label.setStyleSheet(label_style)
        form_layout.addWidget(empresa_label)
        
        self.empresa_input = QLineEdit()
        self.empresa_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.empresa_input)
        
        form_layout.addSpacing(5)  # Reduzindo ainda mais o espaçamento antes do botão
        
        # Botão Login
        self.login_button = QPushButton("LOGIN")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #39c0ed;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;  /* Reduzindo o espaço acima do botão */
            }
            QPushButton:hover {
                background-color: #2fbce9;
            }
            QPushButton:pressed {
                background-color: #25a7d3;
            }
        """)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)
        
        # Centralizar o formulário na janela
        container_layout = QHBoxLayout()
        container_layout.addStretch(1)
        container_layout.addWidget(form_container)
        container_layout.addStretch(1)
        main_layout.addLayout(container_layout)
        
        # Adicionar rótulo de versão no canto inferior direito
        versao_layout = QHBoxLayout()
        versao_label = QLabel("Versão: v0.1.0")
        versao_label.setStyleSheet("color: #f7f8f9; font-size: 11px;")
        versao_label.setAlignment(Qt.AlignRight)
        versao_layout.addStretch(1)  # Adiciona espaço à esquerda para empurrar para a direita
        versao_layout.addWidget(versao_label)
        versao_layout.setContentsMargins(0, 0, 10, 10)  # Margem direita e inferior
        
        main_layout.addLayout(versao_layout)
        main_layout.addStretch(1)  # Menos espaço na parte inferior
        
        # Conectar evento Enter para campos
        self.usuario_input.returnPressed.connect(self.avancar_para_senha)
        self.senha_input.returnPressed.connect(self.avancar_para_empresa)
        self.empresa_input.returnPressed.connect(self.login)
    
    def avancar_para_senha(self):
        """Avança para o campo de senha quando Enter é pressionado no campo de usuário"""
        self.senha_input.setFocus()
    
    def avancar_para_empresa(self):
        """Avança para o campo de empresa quando Enter é pressionado no campo de senha"""
        self.empresa_input.setFocus()
    
    def carregar_dados_salvos(self):
        """Carrega o usuário e empresa salvos anteriormente, se existirem"""
        usuario_salvo = self.settings.value("ultimo_usuario", "")
        empresa_salva = self.settings.value("ultima_empresa", "")
        
        if usuario_salvo:
            self.usuario_input.setText(usuario_salvo)
            
        if empresa_salva:
            self.empresa_input.setText(empresa_salva)
        
        # Se tiver usuário salvo, põe o foco na senha
        if usuario_salvo:
            self.senha_input.setFocus()
        else:
            self.usuario_input.setFocus()
    
    def salvar_dados(self, usuario, empresa):
        """Salva o usuário e empresa para uso futuro"""
        self.settings.setValue("ultimo_usuario", usuario)
        self.settings.setValue("ultima_empresa", empresa)
        self.settings.sync()
    
    def login(self):
        usuario = self.usuario_input.text().strip()
        senha = self.senha_input.text().strip()
        empresa = self.empresa_input.text().strip()
        
        # validações de campo
        if not usuario or not senha or not empresa:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!")
            return
        
        # salva usuário e empresa para próxima vez
        self.salvar_dados(usuario, empresa)
        
        try:
            # Validação no banco Firebird
            from base.banco import validar_login, autenticar_por_funcionario
            
            # Tentar autenticar e obter informações do funcionário
            info_funcionario = None
            id_funcionario = None
            
            # Verificar se é um usuário padrão
            ok = validar_login(usuario, senha, empresa)
            
            # Se for um funcionário com credenciais próprias
            if not ok:
                info_funcionario = autenticar_por_funcionario(usuario, senha)
                if info_funcionario:
                    ok = True
                    id_funcionario = info_funcionario.get("id_funcionario")
                    # Usar as informações do funcionário para login
                    empresa = info_funcionario.get("empresa", empresa)
            else:
                # Para usuários padrão, temos que buscar se está vinculado a algum funcionário
                from base.banco import buscar_funcionario_por_usuario
                func_info = buscar_funcionario_por_usuario(usuario)
                if func_info:
                    id_funcionario = func_info[0]  # Assumindo que retorna ID na primeira posição
            
            if not ok:
                self.mostrar_mensagem("Erro", "Usuário ou senha inválidos!")
                return
            
            # sucesso!
            self.mostrar_mensagem("Sucesso", "Login realizado com sucesso!")
            
            # Abrir a janela principal passando também o ID do funcionário
            self.main_window = MainWindow(
                usuario=usuario, 
                empresa=empresa, 
                id_funcionario=id_funcionario
            )
            self.main_window.show()
            self.close()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao acessar o banco: {e}")
            return
    
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
                background-color: #003366;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 2px;
            }
        """)
        msg_box.exec_()


# Para ajudar com o carregamento da imagem de fundo
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso """
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Erro ao obter caminho do recurso: {e}")
        return relative_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())