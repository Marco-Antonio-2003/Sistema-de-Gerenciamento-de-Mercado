import sys
import os
import subprocess
import unicodedata
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
    def __init__(self, usuario=None, empresa=None):
        super().__init__()
        self.usuario = usuario if usuario else "Usuário"
        self.empresa = empresa if empresa else "Empresa"
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
            "Recebimento de clientes",
            "Gerar lançamento Financeiro",
            "Controle de caixa (PDV)",
            "Conta corrente",
            "Classes financeiras"
        ], self)
        
        btn_relatorios.add_menu_actions([
            "Fiscal NF-e, SAT, NFC-e",
            "Estoque",
        ], self)
        
        btn_notas.add_menu_actions([
            "Manutenção de notas"
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
        
        # Logo
        logo_label = QLabel()
        # Caminho absoluto para o logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(400, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Se o logo não for encontrado, cria um texto alternativo
            logo_label = QLabel("MB SISTEMA\nSOLUÇÕES TECNOLÓGICAS")
            logo_label.setFont(QFont("Arial", 24, QFont.Bold))
            logo_label.setStyleSheet("color: #00E676; text-align: center;")
            logo_label.setAlignment(Qt.AlignCenter)
            print(f"Logo não encontrado em {logo_path}. Usando texto alternativo.")
        
        logo_label.setStyleSheet("margin-top: 30px; margin-bottom: 30px;")
        logo_label.setAlignment(Qt.AlignCenter)
        
        system_title = QLabel("MB Sistema")
        system_title.setFont(QFont("Arial", 36, QFont.Bold))
        system_title.setStyleSheet("color: white; margin-top: 20px;")
        system_title.setAlignment(Qt.AlignCenter)
        
        system_subtitle = QLabel("Sistema de gerenciamento")
        system_subtitle.setFont(QFont("Arial", 26))
        system_subtitle.setStyleSheet("color: white;")
        system_subtitle.setAlignment(Qt.AlignCenter)
        
        # Informações do usuário
        user_info = QLabel(f"Usuário: {self.usuario} | Empresa: {self.empresa}")
        user_info.setFont(QFont("Arial", 14))
        user_info.setStyleSheet("color: white; margin-top: 40px;")
        user_info.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(logo_label)
        title_layout.addWidget(system_title)
        title_layout.addWidget(system_subtitle)
        title_layout.addWidget(user_info)
        home_layout.addLayout(title_layout)
        
        # Adicionar tela inicial ao layout principal
        main_layout.addWidget(home_screen, 1)
        
        # Dicionário para mapear os títulos de ações para os arquivos .py correspondentes
        self.action_to_py_file = {
            # Módulos de GERAL
            "Cadastro de empresa": os.path.join("geral", "cadastro_empresa.py"),
            "Cadastro Pessoas (clientes)": os.path.join("geral", "cadastro_pessoa.py"),
            "Cadastro Funcionários": os.path.join("geral", "cadastro_funcionarios.py"),
            "Consulta CNPJ": os.path.join("geral", "consulta_cnpj.py"),
            "Cadastro de Email": os.path.join("geral", "cadastro_email.py"),
            
            # Módulos de PRODUTOS E SERVIÇOS
            "Grupo de produtos": os.path.join("produtos_e_servicos", "grupo_produtos.py"),
            "Un - unidade de medida": os.path.join("produtos_e_servicos", "unidade_medida.py"),
            "Produtos": os.path.join("produtos_e_servicos", "produtos.py"),
            
            # Módulos de COMPRAS
            "Fornecedores": os.path.join("compras", "fornecedores.py"),
            
            # Módulos de VENDAS
            "Clientes": os.path.join("vendas", "clientes.py"),
            "Pedido de vendas": os.path.join("vendas", "pedido_vendas.py"),
            
            # Módulos de FINANCEIRO
            "Recebimento de clientes": os.path.join("financeiro", "recebimento_clientes.py"),
            "Gerar lançamento Financeiro": os.path.join("financeiro", "lancamento_financeiro.py"),
            "Controle de caixa (PDV)": os.path.join("financeiro", "controle_caixa.py"),
            "Conta corrente": os.path.join("financeiro", "conta_corrente.py"),
            "Classes financeiras": os.path.join("financeiro", "classes_financeiras.py"),
            
            # Módulos de RELATÓRIOS
            "Fiscal NF-e, SAT, NFC-e": os.path.join("relatorios", "relatorio_fiscal.py"),
            "Estoque": os.path.join("relatorios", "estoque.py"),
            
            # Módulos de NOTAS FISCAIS
            "Manutenção de notas": os.path.join("notas_fiscais", "manutencao_notas.py"),
            
            # Módulos de FERRAMENTAS
            "Configuração de estação": os.path.join("ferramentas", "configuracao_impressora.py")
        }
        
    def normalize_text(self, text):
        """
        Normaliza texto removendo acentos e caracteres especiais.
        """
        # Primeiro normaliza para separar caracteres de base e combinados
        normalized = unicodedata.normalize('NFD', text)
        # Remove diacríticos (acentos)
        normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])
        return normalized
        
    def menu_action_triggered(self, action_title):
        print(f"Menu action triggered: {action_title}")
        
        # Verificar se existe um arquivo .py correspondente à ação
        if action_title in self.action_to_py_file:
            py_file = self.action_to_py_file[action_title]
            try:
                # Obter caminho absoluto para o arquivo
                script_dir = os.path.dirname(os.path.abspath(__file__))
                py_file_path = os.path.join(script_dir, py_file)
                
                # Verificar se o arquivo existe
                if os.path.exists(py_file_path):
                    # Executar o arquivo Python correspondente como um processo separado
                    print(f"Executando arquivo: {py_file_path}")
                    subprocess.Popen([sys.executable, py_file_path])
                else:
                    print(f"Arquivo não encontrado: {py_file_path}")
                    # Verificar se o diretório existe e criar o arquivo se necessário
                    directory = os.path.dirname(py_file_path)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                        print(f"Diretório criado: {directory}")
                    
                    # Criar um nome de classe a partir do título da ação - removendo acentos e caracteres especiais
                    class_name = self.normalize_text(action_title)
                    # Remover todos os espaços, hífens, parênteses e vírgulas
                    class_name = ''.join(c for c in class_name if c.isalnum())
                    
                    # Criar um arquivo Python básico
                    with open(py_file_path, 'w', encoding='utf-8') as f:
                        f.write(f"""import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class {class_name}Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("{action_title}")
        self.setGeometry(200, 200, 800, 600)
        self.initUI()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        title = QLabel("{action_title}")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        info = QLabel("Esta funcionalidade ainda está em desenvolvimento.")
        info.setFont(QFont("Arial", 14))
        info.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(info)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = {class_name}Window()
    window.show()
    sys.exit(app.exec_())
""")
                    print(f"Arquivo criado: {py_file_path}")
                    # Executar o arquivo recém-criado
                    subprocess.Popen([sys.executable, py_file_path])
            except Exception as e:
                print(f"Erro ao manipular o arquivo {py_file}: {str(e)}")
        else:
            print(f"Nenhum arquivo .py encontrado para a ação: {action_title}")

# Se este arquivo for executado diretamente, abra a janela principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())