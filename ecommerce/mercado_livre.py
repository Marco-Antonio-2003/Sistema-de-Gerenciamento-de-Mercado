"""
Módulo Mercado Livre - E-commerce
Sistema de integração com Mercado Livre
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QMessageBox, QApplication)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt

# Adicionar o diretório base ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.banco import verificar_acesso_ecommerce


class MercadoLivreWindow(QWidget):
    """Janela principal do módulo Mercado Livre"""
    
    def __init__(self):
        super().__init__()
        self.usuario = None
        self.empresa = None
        self.id_funcionario = None
        self.init_ui()
        
    def set_credentials(self, usuario, empresa, id_funcionario):
        """Define as credenciais do usuário logado"""
        self.usuario = usuario
        self.empresa = empresa
        self.id_funcionario = id_funcionario
        
        # Verificar acesso ao e-commerce após definir credenciais
        self.verificar_acesso()
        
    def verificar_acesso(self):
        """Verifica se o usuário tem acesso ao módulo e-commerce"""
        if not self.usuario:
            return
            
        try:
            tem_acesso, motivo = verificar_acesso_ecommerce(self.usuario, self.empresa)
            
            if not tem_acesso:
                QMessageBox.critical(
                    self, 
                    "Acesso Negado", 
                    f"Acesso ao módulo Mercado Livre bloqueado.\n\n{motivo}\n\nEntre em contato com o administrador."
                )
                self.close()
                return
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao verificar permissões de acesso:\n{str(e)}"
            )
            self.close()
            return
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Mercado Livre - E-commerce")
        self.setGeometry(100, 100, 1000, 700)
        
        # Definir ícone da janela
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "ico-img", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFF100, stop:1 #3483FA);
                border-bottom: 2px solid #2D3561;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Título
        title_label = QLabel("Mercado Livre - E-commerce")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2D3561; background: transparent;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addWidget(header_frame)
        
        # Área de conteúdo principal
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(30)
        
        # Mensagem de boas-vindas
        welcome_label = QLabel("Bem-vindo ao módulo Mercado Livre")
        welcome_label.setFont(QFont("Arial", 18, QFont.Bold))
        welcome_label.setStyleSheet("color: #2D3561; margin-bottom: 20px;")
        welcome_label.setAlignment(Qt.AlignCenter)
        
        # Descrição
        desc_label = QLabel("Este módulo permite integração com o Mercado Livre\npara gerenciar produtos, pedidos e vendas.")
        desc_label.setFont(QFont("Arial", 14))
        desc_label.setStyleSheet("color: #666; margin-bottom: 30px;")
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Botões de ação principais
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Botão Produtos
        btn_produtos = QPushButton("Gerenciar Produtos")
        btn_produtos.setFixedSize(200, 60)
        btn_produtos.setFont(QFont("Arial", 12, QFont.Bold))
        btn_produtos.setStyleSheet("""
            QPushButton {
                background-color: #3483FA;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2968C8;
            }
            QPushButton:pressed {
                background-color: #1E4F96;
            }
        """)
        btn_produtos.clicked.connect(self.abrir_produtos)
        
        # Botão Pedidos
        btn_pedidos = QPushButton("Pedidos")
        btn_pedidos.setFixedSize(200, 60)
        btn_pedidos.setFont(QFont("Arial", 12, QFont.Bold))
        btn_pedidos.setStyleSheet("""
            QPushButton {
                background-color: #00A650;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00853E;
            }
            QPushButton:pressed {
                background-color: #00662C;
            }
        """)
        btn_pedidos.clicked.connect(self.abrir_pedidos)
        
        # Botão Configurações
        btn_config = QPushButton("Configurações")
        btn_config.setFixedSize(200, 60)
        btn_config.setFont(QFont("Arial", 12, QFont.Bold))
        btn_config.setStyleSheet("""
            QPushButton {
                background-color: #FF6900;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #E55A00;
            }
            QPushButton:pressed {
                background-color: #CC4C00;
            }
        """)
        btn_config.clicked.connect(self.abrir_configuracoes)
        
        buttons_layout.addWidget(btn_produtos)
        buttons_layout.addWidget(btn_pedidos)
        buttons_layout.addWidget(btn_config)
        
        # Adicionar elementos ao layout de conteúdo
        content_layout.addWidget(welcome_label)
        content_layout.addWidget(desc_label)
        content_layout.addLayout(buttons_layout)
        content_layout.addStretch()
        
        main_layout.addWidget(content_frame)
        
    def abrir_produtos(self):
        """Abre a tela de gerenciamento de produtos"""
        QMessageBox.information(
            self,
            "Em desenvolvimento",
            "O módulo de gerenciamento de produtos está em desenvolvimento."
        )
        
    def abrir_pedidos(self):
        """Abre a tela de pedidos"""
        QMessageBox.information(
            self,
            "Em desenvolvimento", 
            "O módulo de pedidos está em desenvolvimento."
        )
        
    def abrir_configuracoes(self):
        """Abre a tela de configurações"""
        QMessageBox.information(
            self,
            "Em desenvolvimento",
            "O módulo de configurações está em desenvolvimento."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MercadoLivreWindow()
    window.show()
    sys.exit(app.exec_())