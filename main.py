import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QAction,
                             QMenu, QToolBar)
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

class MenuButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("""
            QPushButton {
                background-color: #005079; 
                color: white; 
                border: none; 
                font-size: 14px; 
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
            QPushButton:pressed {
                background-color: #00283d;
            }
        """)
        
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                color: black;
                border: 1px solid #cccccc;
            }
            QMenu::item {
                padding: 8px 30px 8px 20px;
                min-width: 200px;
            }
            QMenu::item:selected {
                background-color: #e6e6e6;
            }
        """)
        
        self.setMenu(self.menu)

    def add_menu_actions(self, action_titles, window):
        for title in action_titles:
            action = QAction(title, self)
            action.triggered.connect(lambda checked, t=title: window.menu_action_triggered(t))
            self.menu.addAction(action)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("MB Sistema - Sistema de Gerenciamento")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #272525;")
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Barra de ferramentas para botões de menu
        menu_frame = QFrame()
        menu_frame.setStyleSheet("background-color: #272525;")
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setSpacing(5)
        
        # Botões do menu
        btn_geral = MenuButton("GERAL")
        btn_produtos = MenuButton("PRODUTOS E\nSERVIÇOS")
        btn_compras = MenuButton("COMPRAS")
        btn_vendas = MenuButton("VENDAS")
        btn_financeiro = MenuButton("FINANCEIRO")
        btn_relatorios = MenuButton("RELATÓRIOS")
        btn_notas = MenuButton("NOTAS FISCAIS")
        btn_ferramentas = MenuButton("FERRAMENTAS")
        
        # Adicionar ações aos botões de menu
        btn_geral.add_menu_actions([
            "Cadastro de empresa",
            "Cadastro Pessoas (clientes)",
            "Cadastro Funcionários",
            "Consulta CNPJ",
            "Cadastro de Email",
        ], self)
        
        btn_produtos.add_menu_actions([
            "Grupo de produtos",
            "Un - unidade de medida",
            "Produtos"
        ], self)
        
        btn_compras.add_menu_actions([
            "Fornecedores"
        ], self)
        
        btn_vendas.add_menu_actions([
            "Clientes",
            "Pedido de vendas"
        ], self)
        
        btn_financeiro.add_menu_actions([
            "Contas a receber",
            "Recebimento de clientes",
            "Contas a pagar",
            "Gerar lançamento Financeiro",
            "Controle de caixa (PDV)",
            "Conta corrente",
            "Classes financeiras"
        ], self)
        
        btn_relatorios.add_menu_actions([
            "Financeiro",
            "Estoque",
            "Fiscal"
        ], self)

        btn_ferramentas.add_menu_actions([
            "Configuração de estação"
        ], self)
        
        # Adicionar botões ao layout
        menu_layout.addWidget(btn_geral)
        menu_layout.addWidget(btn_produtos)
        menu_layout.addWidget(btn_compras)
        menu_layout.addWidget(btn_vendas)
        menu_layout.addWidget(btn_financeiro)
        menu_layout.addWidget(btn_relatorios)
        menu_layout.addWidget(btn_notas)
        menu_layout.addWidget(btn_ferramentas)
        
        # Adicionar barra de menu ao layout principal
        main_layout.addWidget(menu_frame)
        
        # Área de conteúdo com tela inicial
        home_screen = QWidget()
        home_screen.setStyleSheet("background-color: #005079;")
        home_layout = QVBoxLayout(home_screen)
        home_layout.setAlignment(Qt.AlignCenter)
        
        # Logo e título
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Placeholder para a logo (relógio com ícones)
        clock_label = QLabel()
        clock_label.setStyleSheet("margin-top: 30px; margin-bottom: 30px;")
        clock_label.setAlignment(Qt.AlignCenter)
        
        system_title = QLabel("MB Sistema")
        system_title.setFont(QFont("Arial", 36, QFont.Bold))
        system_title.setStyleSheet("color: white; margin-top: 20px;")
        system_title.setAlignment(Qt.AlignCenter)
        
        system_subtitle = QLabel("Sistema de gerenciamento")
        system_subtitle.setFont(QFont("Arial", 26))
        system_subtitle.setStyleSheet("color: white;")
        system_subtitle.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(clock_label)
        title_layout.addWidget(system_title)
        title_layout.addWidget(system_subtitle)
        home_layout.addLayout(title_layout)
        
        # Adicionar tela inicial ao layout principal
        main_layout.addWidget(home_screen, 1)
        
        # # Barra inferior para ferramentas do admin
        # admin_frame = QFrame()
        # admin_frame.setFixedHeight(40)
        # admin_frame.setStyleSheet("background-color: #1a1a1a;")
        # admin_layout = QHBoxLayout(admin_frame)
        
        # admin_label = QLabel("FERRAMENTAS DO ADMIN")
        # admin_label.setStyleSheet("color: white; font-weight: bold;")
        # admin_label.setAlignment(Qt.AlignCenter)
        # admin_layout.addWidget(admin_label)
        
        # main_layout.addWidget(admin_frame)
        
        # Dicionário para mapear os títulos de ações para os arquivos .py correspondentes
        self.action_to_py_file = {
            "Cadastro de empresa": "cadastro_empresa.py",
            "Cadastro Pessoas (clientes)": "cadastro_pessoa.py",
            "Cadastro Funcionários": "cadastro_funcionarios.py",
            "Consulta CNPJ": "consulta_cnpj.py",
            "Cadastro de Email": "cadastro_email.py",
            "Configuração de estação": "configuracao_impressora.py",
            "Grupo de produtos": "grupo_produtos.py",
            "Un - unidade de medida": "unidade_medida.py",
            "Produtos": "produtos.py",
            "Fornecedores": "fornecedores.py",
            "Clientes": "clientes.py",
            "Pedido de vendas": "pedido_vendas.py",
            #"Contas a receber": "contas_receber.py",
            "Recebimento de clientes": "recebimento_clientes.py",
            #"Contas a pagar": "contas_pagar.py",
            "Gerar lançamento Financeiro": "lancamento_financeiro.py",
            #"Controle de caixa (PDV)": "controle_caixa.py",
            #"Conta corrente": "conta_corrente.py",
            #"Classes financeiras": "classes_financeiras.py",
            #"Financeiro": "relatorio_financeiro.py",
            "Estoque": "relatorio_estoque.py",
            #"Fiscal": "relatorio_fiscal.py"
        }
        
        self.show()
            
    def menu_action_triggered(self, action_title):
        print(f"Menu action triggered: {action_title}")
        
        # Verificar se existe um arquivo .py correspondente à ação
        if action_title in self.action_to_py_file:
            py_file = self.action_to_py_file[action_title]
            try:
                # Executar o arquivo Python correspondente como um processo separado
                subprocess.Popen([sys.executable, py_file])
                print(f"Executando arquivo: {py_file}")
            except Exception as e:
                print(f"Erro ao abrir o arquivo {py_file}: {str(e)}")
        else:
            print(f"Nenhum arquivo .py encontrado para a ação: {action_title}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())