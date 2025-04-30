#principal.py
import sys
import os
import importlib.util
import unicodedata
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QAction,
                             QMenu, QToolBar, QGraphicsDropShadowEffect, QMessageBox)
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QUrl, QTimer
from PyQt5.QtGui import QDesktopServices


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
        self.contadores_labels = {}  # Armazenar referências aos labels de contagem
        self.initUI()
        
        # Configurar timer para atualizar contadores a cada 30 segundos
        self.timer_atualizacao = QTimer(self)
        self.timer_atualizacao.timeout.connect(self.atualizar_contadores)
        self.timer_atualizacao.start(30000)  # 30 segundos
        
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
        btn_ferramentas = MenuButton("FERRAMENTAS")
        
        btn_geral.add_menu_actions([
            "Cadastro de empresa",
            "Cadastro de Clientes",
            "Cadastro Funcionários",
            "Consulta CNPJ"
        ], self)
        
        btn_produtos.add_menu_actions([
            "Produtos",
        ], self)
        
        btn_compras.add_menu_actions(["Fornecedores"], self)
        btn_vendas.add_menu_actions([ "Pedido de vendas"], self)
        btn_financeiro.add_menu_actions([
            "Recebimento de clientes",
            "Gerar lançamento Financeiro",
            "Controle de caixa (PDV)",
            "Conta corrente",
            "Classes financeiras"
        ], self)
        btn_relatorios.add_menu_actions(["Fiscal NF-e, SAT, NFC-e",  "Relatório de Vendas de Produtos"], self)
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

        # Container das caixas de informação
        info_frame = QFrame()
        info_frame.setMaximumHeight(180)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(30)
        info_layout.setContentsMargins(50, 20, 50, 20)

        # Criar caixas de informação com ícones específicos
        self.criar_caixa_info(info_layout, "Clientes", "user.png", self.obter_contagem_pessoas())
        self.criar_caixa_info(info_layout, "Produtos", "product.png", self.obter_contagem_produtos())
        self.criar_caixa_info(info_layout, "Vendas", "sales.png", self.obter_contagem_vendas())

        home_layout.addWidget(info_frame)

        # Informações do usuário
        user_info = QLabel(f"Usuário: {self.usuario} | Empresa: {self.empresa}")
        user_info.setFont(QFont("Arial", 14))
        user_info.setStyleSheet("color: white; margin-top: 10px;")
        user_info.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(user_info)

        # finalmente adiciona a tela home ao layout principal
        main_layout.addWidget(home_screen, 1)
        
        # Botão de WhatsApp - versão corrigida
        self.botao_whatsapp = QPushButton(self)
        whatsapp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "whatsapp2.png")
        
        if os.path.exists(whatsapp_path):
            self.botao_whatsapp.setIcon(QIcon(whatsapp_path))
            self.botao_whatsapp.setIconSize(QSize(60, 60))
        else:
            print(f"AVISO: Ícone do WhatsApp não encontrado em: {whatsapp_path}")
            self.botao_whatsapp.setText("WhatsApp")
            self.botao_whatsapp.setStyleSheet("color: white; font-weight: bold;")
        
        # Estilo do botão
        self.botao_whatsapp.setFixedSize(80, 80)
        self.botao_whatsapp.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                border-radius: 40px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)
        
        # Adicionar sombra
        sombra = QGraphicsDropShadowEffect(self.botao_whatsapp)
        sombra.setBlurRadius(15)
        sombra.setColor(Qt.black)
        sombra.setOffset(0, 0)
        self.botao_whatsapp.setGraphicsEffect(sombra)
        
        # Configurar cursor e tooltip
        self.botao_whatsapp.setCursor(QCursor(Qt.PointingHandCursor))
        self.botao_whatsapp.setToolTip("Contato: +55 15 996125218")
        
        # Conectar ao evento de clique
        self.botao_whatsapp.clicked.connect(lambda: self.abrir_whatsapp("+5515996125218"))
        
        # Posicionar o botão no canto inferior direito
        self.botao_whatsapp.move(
            self.width() - self.botao_whatsapp.width() - 30,
            self.height() - self.botao_whatsapp.height() - 30
        )
        
        # Método para reposicionar o botão quando a janela for redimensionada
        def novo_resize_event(event):
            # Salvar o comportamento original de redimensionamento
            if hasattr(self, '_resize_original'):
                self._resize_original(event)
            else:
                super(MainWindow, self).resizeEvent(event)
            
            # Reposicionar o botão WhatsApp
            self.botao_whatsapp.move(
                self.width() - self.botao_whatsapp.width() - 30,
                self.height() - self.botao_whatsapp.height() - 30
            )
        
        # Salvar o método de redimensionamento original e substituí-lo
        self._resize_original = self.resizeEvent
        self.resizeEvent = novo_resize_event
        
        # Adicionar efeito de aumento ao passar o mouse
        def on_enter(event):
            self.animar_botao(self.botao_whatsapp, 1.2)
        
        def on_leave(event):
            self.animar_botao(self.botao_whatsapp, 1.0)
            
        self.botao_whatsapp.enterEvent = on_enter
        self.botao_whatsapp.leaveEvent = on_leave
        
        # Garantir que o botão fique por cima de outros widgets
        self.botao_whatsapp.raise_()
        
        # mapeamentos
        self.action_to_py_file = {
            "Cadastro de empresa": os.path.join("geral", "cadastro_empresa.py"),
            "Cadastro de Clientes": os.path.join("geral", "cadastro_pessoa.py"),
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
            "Relatório de Vendas de Produtos": os.path.join("relatorios", "relatorio_vendas_produtos.py"),  
            "Configuração de estação": os.path.join("ferramentas", "configuracao_impressora.py")
        }
        # casos especiais de nome de classe
        self.action_to_class = {
            # GERAL
            "Cadastro de empresa":          "CadastroEmpresaWindow",
            "Cadastro de Clientes":  "CadastroPessoaWindow",
            "Cadastro Funcionários":        "CadastroFuncionariosWindow",
            "Consulta CNPJ":                "ConsultaCNPJWindow",
            # PRODUTOS E SERVIÇOS
            "Produtos":                     "ProdutosWindow",
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
            "Relatório de Vendas de Produtos":                      "RelatorioVendasWindow",
            # FERRAMENTAS
            "Configuração de estação":      "ConfiguracaoImpressoraWindow"
        }

    def criar_caixa_info(self, layout_pai, titulo, nome_icone, contagem):
        """Cria uma caixa de informação com título, ícone e contagem"""
        box_frame = QFrame()
        box_frame.setMinimumSize(180, 150)
        box_frame.setStyleSheet("""
            QFrame {
                background-color: #00283d;
                border-radius: 15px;
            }
        """)
        
        # Adicionar efeito de sombra
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setColor(Qt.black)
        sombra.setOffset(0, 0)
        box_frame.setGraphicsEffect(sombra)
        
        box_layout = QVBoxLayout(box_frame)
        box_layout.setSpacing(10)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        label_titulo.setStyleSheet("color: white;")
        label_titulo.setAlignment(Qt.AlignCenter)
        
        # Ícone específico para cada categoria
        label_icone = QLabel()
        
        # Mapear ícones personalizados de acordo com o título
        icone_caminho = ""
        if nome_icone == "user.png":
            # Ícone para Clientes (pessoas)
            icone_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "user.png")
            emoji_fallback = "👥"  # Emoji de pessoas caso o ícone não seja encontrado
        elif nome_icone == "product.png":
            # Ícone para Produtos (caixa/pacote)
            icone_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "product.png")
            emoji_fallback = "📦"  # Emoji de caixa/pacote caso o ícone não seja encontrado
        elif nome_icone == "sales.png":
            # Ícone para Vendas (dinheiro/gráfico)
            icone_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "sales.png")
            emoji_fallback = "💰"  # Emoji de dinheiro caso o ícone não seja encontrado
        
        # Verificar se o ícone existe ou usar emoji como alternativa
        if os.path.exists(icone_caminho):
            pixmap_icone = QPixmap(icone_caminho)
            label_icone.setPixmap(pixmap_icone.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Usar emoji como fallback
            label_icone.setText(emoji_fallback)
            label_icone.setFont(QFont("Arial", 36, QFont.Bold))
            label_icone.setStyleSheet("color: white;")
        
        label_icone.setAlignment(Qt.AlignCenter)
        
        # Contagem
        label_contagem = QLabel(str(contagem))
        label_contagem.setFont(QFont("Arial", 24, QFont.Bold))
        label_contagem.setStyleSheet("color: white;")
        label_contagem.setAlignment(Qt.AlignCenter)
        
        # Adicionar ao layout
        box_layout.addWidget(label_titulo)
        box_layout.addWidget(label_icone)
        box_layout.addWidget(label_contagem)
        
        layout_pai.addWidget(box_frame)
        
        # Armazenar referência ao label para atualização posterior
        self.contadores_labels[titulo] = label_contagem
        
        return label_contagem

    def forcar_atualizacao_contadores(self):
        """Força a atualização imediata dos contadores na tela principal"""
        # Chamar a função de atualização de contadores
        self.atualizar_contadores()

    def atualizar_contadores(self):
        """Atualiza os contadores de todas as caixas de informação"""
        try:
            # Atualizar contador de clientes
            if "Clientes" in self.contadores_labels:
                novo_valor = self.obter_contagem_pessoas()
                self.atualizar_contador_com_animacao(self.contadores_labels["Clientes"], novo_valor)
                
            # Atualizar contador de produtos
            if "Produtos" in self.contadores_labels:
                novo_valor = self.obter_contagem_produtos()
                self.atualizar_contador_com_animacao(self.contadores_labels["Produtos"], novo_valor)
                
            # Atualizar contador de vendas
            if "Vendas" in self.contadores_labels:
                novo_valor = self.obter_contagem_vendas()
                self.atualizar_contador_com_animacao(self.contadores_labels["Vendas"], novo_valor)
                
            print("Contadores atualizados com sucesso!")
        except Exception as e:
            print(f"Erro ao atualizar contadores: {e}")

    def atualizar_contador_com_animacao(self, label, novo_valor):
        """Atualiza um contador com uma animação de destaque"""
        # Verificar se o valor mudou
        valor_atual = int(label.text()) if label.text().isdigit() else 0
        
        if valor_atual != novo_valor:
            # Salvar o estilo original
            estilo_original = label.styleSheet()
            
            # Aplicar estilo de destaque
            label.setStyleSheet("color: #00E676; font-weight: bold;")
            
            # Atualizar o valor
            label.setText(str(novo_valor))
            
            # Criar timer para restaurar o estilo original após 1 segundo
            QTimer.singleShot(1000, lambda: label.setStyleSheet(estilo_original))

    def animar_botao(self, botao, fator_escala):
        """Anima o botão para aumentar/diminuir de tamanho"""
        # Criar animação para largura
        anim_largura = QPropertyAnimation(botao, b"minimumWidth")
        anim_largura.setDuration(150)
        anim_largura.setStartValue(botao.width())
        anim_largura.setEndValue(int(80 * fator_escala))
        anim_largura.setEasingCurve(QEasingCurve.OutCubic)
        
        # Criar animação para altura
        anim_altura = QPropertyAnimation(botao, b"minimumHeight")
        anim_altura.setDuration(150)
        anim_altura.setStartValue(botao.height())
        anim_altura.setEndValue(int(80 * fator_escala))
        anim_altura.setEasingCurve(QEasingCurve.OutCubic)
        
        # Iniciar animações
        anim_largura.start()
        anim_altura.start()
        
        # Também animar o tamanho do ícone
        botao.setIconSize(QSize(int(60 * fator_escala), int(60 * fator_escala)))

    def abrir_whatsapp(self, numero_telefone):
        """Abre o WhatsApp com o número de telefone especificado"""
        try:
            # Verificar se o número de telefone está no formato correto
            numero_limpo = ''.join(filter(str.isdigit, numero_telefone))
            url = QUrl(f"https://wa.me/{numero_limpo}")
            
            # Imprimir para debug
            print(f"Abrindo URL: {url.toString()}")
            
            # Abrir URL
            resultado = QDesktopServices.openUrl(url)
            
            # Verificar se a URL foi aberta com sucesso
            if resultado:
                print("URL aberta com sucesso!")
            else:
                print("Falha ao abrir a URL.")
                # Alternativa: tentar abrir com o método tradicional
                import webbrowser
                webbrowser.open(f"https://wa.me/{numero_limpo}")
                
        except Exception as e:
            print(f"Erro ao abrir WhatsApp: {e}")
            # Mostrar mensagem de erro para o usuário
            QMessageBox.warning(self, "Erro", f"Erro ao abrir WhatsApp: {str(e)}")

    def obter_contagem_pessoas(self):
        """Obtém a contagem de PESSOAS do banco de dados"""
        try:
            from base.banco import execute_query
            result = execute_query("SELECT COUNT(*) FROM PESSOAS")
            return result[0][0] if result and result[0][0] else 0
        except Exception as e:
            print(f"Erro ao contar pessoas: {e}")
            return 0

    def obter_contagem_produtos(self):
        """Obtém a contagem de PRODUTOS do banco de dados"""
        try:
            from base.banco import execute_query
            result = execute_query("SELECT COUNT(*) FROM PRODUTOS")
            return result[0][0] if result and result[0][0] else 0
        except Exception as e:
            print(f"Erro ao contar produtos: {e}")
            return 0

    def obter_contagem_vendas(self):
        """Obtém a contagem de VENDAS do dia de hoje do banco de dados"""
        try:
            from base.banco import execute_query
            from datetime import datetime
            
            hoje = datetime.now().strftime("%Y-%m-%d")
            result = execute_query("SELECT COUNT(*) FROM PEDIDOS_VENDA WHERE DATA_PEDIDO = ?", (hoje,))
            return result[0][0] if result and result[0][0] else 0
        except Exception as e:
            print(f"Erro ao contar vendas: {e}")
            return 0

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
        special_modules = ["Fiscal NF-e, SAT, NFC-e", "Configuração de estação", "Relatório de Vendas de Produtos"]
        
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
                    
                elif action_title == "Relatório de Vendas de Produtos":
                    # Importação direta para o módulo de relatório de vendas
                    rel_path = self.action_to_py_file[action_title]
                    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
                    
                    # Carregamento do módulo
                    spec = importlib.util.spec_from_file_location("relatorio_vendas_produtos", abs_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    WindowClass = getattr(module, "RelatorioVendasWindow")
                    
                    # Criar e exibir a janela
                    win = WindowClass()
                    # Adicionar referência à janela principal
                    if hasattr(win, 'set_janela_principal'):
                        win.set_janela_principal(self)
                    win.setWindowTitle(action_title)
                    win.resize(900, 600)  # Definir tamanho da janela
                    win.show()
                    
                    # Conectar o sinal closeEvent para atualizar contadores quando a janela for fechada
                    original_close_event = win.closeEvent
                    
                    def novo_close_event(event):
                        # Chamar o closeEvent original
                        if original_close_event:
                            original_close_event(event)
                        # Atualizar contadores
                        self.atualizar_contadores()
                    
                    win.closeEvent = novo_close_event
                    
                    self.opened_windows.append(win)
                    return
                
                # Criar e exibir a janela
                win = WindowClass()
                # Adicionar referência à janela principal
                if hasattr(win, 'set_janela_principal'):
                    win.set_janela_principal(self)
                win.setWindowTitle(action_title)
                win.show()
                
                # Conectar o sinal closeEvent para atualizar contadores quando a janela for fechada
                original_close_event = win.closeEvent
                
                def novo_close_event(event):
                    # Chamar o closeEvent original
                    if original_close_event:
                        original_close_event(event)
                    # Atualizar contadores
                    self.atualizar_contadores()
                
                win.closeEvent = novo_close_event
                
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
            # Adicionar referência à janela principal
            if hasattr(win, 'set_janela_principal'):
                win.set_janela_principal(self)
            win.setWindowTitle(action_title)
            win.show()
            
            # Conectar o sinal closeEvent para atualizar contadores quando a janela for fechada
            original_close_event = win.closeEvent
            
            def novo_close_event(event):
                # Chamar o closeEvent original
                if original_close_event:
                    original_close_event(event)
                # Atualizar contadores
                self.atualizar_contadores()
            
            win.closeEvent = novo_close_event
            
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