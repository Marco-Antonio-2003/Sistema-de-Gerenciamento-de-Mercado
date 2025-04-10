#principal.py
import sys
import os
import importlib.util
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
        self.opened_windows = []
        self.initUI()
        
        # Definir janela para maximizada (não tela cheia)
        self.showMaximized()
        
    def initUI(self):
        self.setWindowTitle("MB Sistema - Sistema de Gerenciamento")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #272525;")
        
        # central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # menu bar
        menu_frame = QFrame()
        menu_frame.setStyleSheet("background-color: #272525;")
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setSpacing(5)
        
        btn_geral = MenuButton("GERAL")
        btn_produtos = MenuButton("PRODUTOS E\nSERVIÇOS")
        btn_compras = MenuButton("COMPRAS")
        btn_vendas = MenuButton("VENDAS")
        btn_financeiro = MenuButton("FINANCEIRO")
        btn_relatorios = MenuButton("RELATÓRIOS")
        #btn_notas = MenuButton("NOTAS FISCAIS")
        btn_ferramentas = MenuButton("FERRAMENTAS")
        
        btn_geral.add_menu_actions([
            "Cadastro de empresa",
            "Cadastro Pessoas (clientes)",
            "Cadastro Funcionários",
            "Consulta CNPJ"
        ], self)
        
        btn_produtos.add_menu_actions([
            "Produtos",
            "Grupo de produtos",
            "Un - unidade de medida"
        ], self)
        
        btn_compras.add_menu_actions(["Fornecedores"], self)
        btn_vendas.add_menu_actions(["Clientes", "Pedido de vendas"], self)
        btn_financeiro.add_menu_actions([
            "Recebimento de clientes",
            "Gerar lançamento Financeiro",
            "Controle de caixa (PDV)",
            "Conta corrente",
            "Classes financeiras"
        ], self)
        btn_relatorios.add_menu_actions(["Fiscal NF-e, SAT, NFC-e", "Estoque"], self)
        #btn_notas.add_menu_actions(["Manutenção de notas"], self)
        btn_ferramentas.add_menu_actions(["Configuração de estação"], self)
        
        for btn in (btn_geral, btn_produtos, btn_compras, btn_vendas,
                    btn_financeiro, btn_relatorios, btn_ferramentas):
            menu_layout.addWidget(btn)
        main_layout.addWidget(menu_frame)
        
        # Área de conteúdo com tela inicial
        home_screen = QWidget()
        home_screen.setStyleSheet("background-color: #005079;")
        home_layout = QVBoxLayout(home_screen)
        home_layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(400, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("erro logo")
            logo_label.setFont(QFont("Arial", 24, QFont.Bold))
            logo_label.setStyleSheet("color: #00E676;")
            logo_label.setAlignment(Qt.AlignCenter)

        home_layout.addWidget(logo_label)

        # Título principal
        system_title = QLabel("MB Sistema")
        system_title.setFont(QFont("Arial", 36, QFont.Bold))
        system_title.setStyleSheet("color: white;")
        system_title.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(system_title)

        # Subtítulo
        system_subtitle = QLabel("Sistema de gerenciamento")
        system_subtitle.setFont(QFont("Arial", 26))
        system_subtitle.setStyleSheet("color: white;")
        system_subtitle.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(system_subtitle)

        # Informações do usuário
        user_info = QLabel(f"Usuário: {self.usuario} | Empresa: {self.empresa}")
        user_info.setFont(QFont("Arial", 14))
        user_info.setStyleSheet("color: white; margin-top: 40px;")
        user_info.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(user_info)

        # finalmente adiciona ao main_layout
        main_layout.addWidget(home_screen, 1)
        
        # mapeamentos
        self.action_to_py_file = {
            "Cadastro de empresa": os.path.join("geral", "cadastro_empresa.py"),
            "Cadastro Pessoas (clientes)": os.path.join("geral", "cadastro_pessoa.py"),
            "Cadastro Funcionários": os.path.join("geral", "cadastro_funcionarios.py"),
            "Consulta CNPJ": os.path.join("geral", "consulta_cnpj.py"),
            "Produtos": os.path.join("produtos_e_servicos", "produtos.py"),
            "Grupo de produtos": os.path.join("produtos_e_servicos", "grupo_produtos.py"),
            "Un - unidade de medida": os.path.join("produtos_e_servicos", "unidade_medida.py"),
            "Fornecedores": os.path.join("compras", "fornecedores.py"),
            "Clientes": os.path.join("vendas", "clientes.py"),
            "Pedido de vendas": os.path.join("vendas", "pedido_vendas.py"),
            "Recebimento de clientes": os.path.join("financeiro", "recebimento_clientes.py"),
            "Gerar lançamento Financeiro": os.path.join("financeiro", "lancamento_financeiro.py"),
            "Controle de caixa (PDV)": os.path.join("financeiro", "controle_caixa.py"),
            "Conta corrente": os.path.join("financeiro", "conta_corrente.py"),
            "Classes financeiras": os.path.join("financeiro", "classes_financeiras.py"),
            "Fiscal NF-e, SAT, NFC-e": os.path.join("relatorios", "relatorio_fiscal.py"),
            "Estoque": os.path.join("relatorios", "estoque.py"),
            #"Manutenção de notas": os.path.join("notas_fiscais", "manutencao_notas.py"),
            "Configuração de estação": os.path.join("ferramentas", "configuracao_impressora.py")
        }
        # casos especiais de nome de classe
        self.action_to_class = {
            # GERAL
            "Cadastro de empresa":          "CadastroEmpresaWindow",
            "Cadastro Pessoas (clientes)":  "CadastroPessoaWindow",
            "Cadastro Funcionários":        "CadastroFuncionariosWindow",
            "Consulta CNPJ":                "ConsultaCNPJWindow",
            # PRODUTOS E SERVIÇOS
            "Produtos":                     "ProdutosWindow",           # se você tiver um QMainWindow ProdutosWindow
            "Grupo de produtos":            "GrupoProdutosWindow",
            "Un - unidade de medida":       "UnidadeMedidaWindow",
            # COMPRAS
            "Fornecedores":                 "FornecedoresWindow",
            # VENDAS
            "Clientes":                     "ClientesWindow",
            "Pedido de vendas":             "PedidoVendasWindow",
            # FINANCEIRO
            "Recebimento de clientes":      "RecebimentoClientesWindow",
            "Gerar lançamento Financeiro":  "LancamentoFinanceiroWindow",
            "Controle de caixa (PDV)":      "ControleCaixaWindow",
            "Conta corrente":               "ContaCorrenteWindow",
            "Classes financeiras":          "ClassesFinanceirasWindow",
            # RELATÓRIOS
            "Fiscal NF-e, SAT, NFC-e":      "RelatorioFiscalWindow",
            "Estoque":                      "EstoqueWindow",
            # NOTAS FISCAIS
            "Manutenção de notas":          "ManutencaoNotasWindow",
            # FERRAMENTAS
            "Configuração de estação":      "ConfiguracaoImpressoraWindow"
        }

    def normalize_text(self, text):
        normalized = unicodedata.normalize('NFD', text)
        return ''.join(c for c in normalized if not unicodedata.combining(c))

    def load_module_dynamically(self, module_path, class_name):
        try:
            spec = importlib.util.spec_from_file_location("mod", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name, None)
        except Exception as e:
            print(f"Erro ao carregar dinamicamente {module_path}: {e}")
            return None

    def menu_action_triggered(self, action_title):
        print(f"Menu action triggered: {action_title}")
        
        # Tratamento especial para módulos conhecidos com problemas de importação
        special_modules = ["Fiscal NF-e, SAT, NFC-e", "Configuração de estação", "Estoque"]
        
        # Para todos os módulos, use uma abordagem mais direta
        # Primeiro, verifica se já há uma janela aberta
        self.opened_windows = [w for w in self.opened_windows if w.isVisible()]
        for w in self.opened_windows:
            if w.windowTitle() == action_title:
                w.setWindowState(w.windowState() & ~Qt.WindowMinimized)
                w.activateWindow()
                return
        
        # Se o módulo faz parte da lista especial, use importação direta com tratamento de erros
        if action_title in special_modules:
            try:
                if action_title == "Fiscal NF-e, SAT, NFC-e":
                    # Importação direta para o módulo de relatório fiscal
                    rel_path = self.action_to_py_file[action_title]
                    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
                    
                    # Importação explícita do módulo de impressão
                    from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
                    
                    # Carregamento do módulo
                    spec = importlib.util.spec_from_file_location("relatorio_fiscal", abs_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    WindowClass = getattr(module, "RelatorioFiscalWindow")
                    
                elif action_title == "Configuração de estação":
                    # Importação direta para configuração de impressora
                    rel_path = self.action_to_py_file[action_title]
                    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
                    
                    # Importação explícita do módulo de impressão
                    from PyQt5.QtPrintSupport import QPrinterInfo, QPrintDialog, QPrinter
                    
                    # Carregamento do módulo
                    spec = importlib.util.spec_from_file_location("configuracao_impressora", abs_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    WindowClass = getattr(module, "ConfiguracaoImpressoraWindow")
                    
                elif action_title == "Estoque":
                    # Importação direta para o módulo de estoque
                    rel_path = self.action_to_py_file[action_title]
                    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
                    
                    # Carregamento do módulo
                    spec = importlib.util.spec_from_file_location("estoque", abs_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    WindowClass = getattr(module, "EstoqueWindow")
                
                # Criar e exibir a janela
                win = WindowClass()
                win.setWindowTitle(action_title)
                win.show()
                self.opened_windows.append(win)
                return
                
            except Exception as e:
                print(f"Erro ao abrir {action_title}: {e}")
                import traceback
                traceback.print_exc()
        
        # Para os módulos não especiais, use o método original
        if action_title not in self.action_to_py_file:
            print("Ação não mapeada:", action_title)
            return
            
        rel = self.action_to_py_file[action_title]
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel)
        
        if not os.path.exists(path):
            print(f"ERRO: Arquivo não existe: {path}")
            return
            
        # Definir nome da classe
        if action_title in self.action_to_class:
            cls_name = self.action_to_class[action_title]
        else:
            base = ''.join(c for c in self.normalize_text(action_title) if c.isalnum())
            cls_name = base + "Window"
            
        # Tentar importação direta (abordagem modificada para ser mais robusta)
        try:
            # Determinando o caminho do módulo para importação
            rel_path = rel.replace(os.sep, '.')
            module_name = os.path.splitext(rel_path)[0]
            
            # Tentar importação direta como pacote primeiro
            try:
                module_parts = module_name.split('.')
                if len(module_parts) > 1:
                    package = module_parts[0]
                    module = __import__(module_name, fromlist=[cls_name])
                    WindowClass = getattr(module, cls_name, None)
                else:
                    # Fallback para importação com importlib
                    raise ImportError("Não é um pacote")
            except ImportError:
                # Importação com importlib como fallback
                spec = importlib.util.spec_from_file_location(module_name, path)
                if not spec:
                    raise ImportError(f"Não foi possível criar spec para {path}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                WindowClass = getattr(module, cls_name, None)
                
            if not WindowClass:
                raise ImportError(f"Classe {cls_name} não encontrada no módulo {module_name}")
                
            # Criar e exibir a janela
            win = WindowClass()
            win.setWindowTitle(action_title)
            win.show()
            self.opened_windows.append(win)
            
        except Exception as e:
            print(f"ERRO ao importar/iniciar o módulo {action_title}: {e}")
            import traceback
            traceback.print_exc()
            print("Não foi possível abrir a janela solicitada.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(usuario="Marco", empresa="MB Sistemas")
    window.show()
    sys.exit(app.exec_())