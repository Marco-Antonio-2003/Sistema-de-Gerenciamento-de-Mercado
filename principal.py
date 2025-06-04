#principal.py
import sys
import os
import importlib.util
import unicodedata
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QAction,
                             QMenu, QToolBar, QGraphicsDropShadowEffect, QMessageBox, QDialog)
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QUrl, QTimer, QRect
from PyQt5.QtGui import QDesktopServices
from assistente import adicionar_assistente_ao_sistema


class ContatosWhatsAppDialog(QDialog):
    """Janela de contatos do WhatsApp com design melhorado"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contatos = [
            {
                "nome": "Marcos Barros",
                "funcao": "Suporte",
                "telefone": "15 99102-3337",
                "numero_limpo": "5515991023337"
            },
            {
                "nome": "Marco Antônio",
                "funcao": "Programador",
                "telefone": "15 99612-5218",
                "numero_limpo": "5515996125218"
            }
        ]
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface da janela de contatos"""
        self.setWindowTitle("Contatos - WhatsApp")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "whatsapp2.png")))
        # Aumentar largura para acomodar conteúdo
        self.setFixedSize(600, 350)
        
        # Remover botões de minimizar/maximizar e '?' do título
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Estilo geral da janela
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header com gradiente
        header_widget = QWidget()
        header_widget.setFixedHeight(70)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #25D366, stop:1 #128C7E);
                border-bottom: 2px solid #0d6e5a;
            }
        """)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Ícone do WhatsApp no header
        icon_label = QLabel()
        whatsapp_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "whatsapp2.png")
        if os.path.exists(whatsapp_icon_path):
            pixmap = QPixmap(whatsapp_icon_path)
            icon_label.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText("💬")
            icon_label.setFont(QFont("Arial", 28))
        icon_label.setStyleSheet("background: transparent;")
        
        # Título no header
        titulo = QLabel("Contatos WhatsApp")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("""
            color: white;
            background: transparent;
            padding-left: 10px;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        
        layout.addWidget(header_widget)
        
        # Container principal com padding
        main_container = QWidget()
        main_container.setStyleSheet("background-color: #f5f5f5;")
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Criar cards para cada contato
        for contato in self.contatos:
            self.criar_card_contato(main_layout, contato)
        
        # Espaçador
        main_layout.addStretch()
        
        # Adicionar o container principal ao layout
        layout.addWidget(main_container)
    
    def criar_card_contato(self, layout, contato):
        """Cria um card estilizado para um contato"""
        # Card principal
        card = QFrame()
        card.setMinimumHeight(95)
        card.setMaximumHeight(95)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
            QFrame:hover {
                border: 2px solid #25D366;
                background-color: #f0fff4;
            }
        """)
        
        # Adicionar sombra ao card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        # Layout do card
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(15)
        
        # Avatar/Inicial do contato
        avatar = QLabel()
        avatar.setFixedSize(50, 50)
        inicial = contato["nome"].split()[0][0].upper()
        avatar.setText(inicial)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                background-color: #25D366;
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        # Informações do contato
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")
        info_widget.setFixedWidth(300)  # Largura fixa para garantir espaço
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 5, 0, 5)
        info_layout.setSpacing(3)
        
        # Nome
        nome_label = QLabel(contato["nome"])
        nome_label.setFont(QFont("Arial", 14, QFont.Bold))
        nome_label.setStyleSheet("color: #2c3e50; background: transparent;")
        nome_label.setWordWrap(False)  # Evitar quebra de linha
        nome_label.setMinimumWidth(200)  # Garantir largura mínima
        
        # Função
        funcao_label = QLabel(contato["funcao"])
        funcao_label.setFont(QFont("Arial", 11))
        funcao_label.setStyleSheet("color: #7f8c8d; background: transparent;")
        funcao_label.setWordWrap(False)
        
        # Telefone com ícone
        telefone_label = QLabel(f"📱 {contato['telefone']}")
        telefone_label.setFont(QFont("Arial", 10))
        telefone_label.setStyleSheet("color: #34495e; background: transparent;")
        telefone_label.setWordWrap(False)
        
        info_layout.addWidget(nome_label)
        info_layout.addWidget(funcao_label)
        info_layout.addWidget(telefone_label)
        
        # Botão WhatsApp
        btn_whatsapp = QPushButton("WhatsApp")
        btn_whatsapp.setFixedSize(120, 40)
        btn_whatsapp.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
            QPushButton:pressed {
                background-color: #0d6e5a;
            }
        """)
        btn_whatsapp.setCursor(QCursor(Qt.PointingHandCursor))
        btn_whatsapp.clicked.connect(lambda: self.abrir_whatsapp(contato["numero_limpo"]))
        
        # Adicionar ícone ao botão
        whatsapp_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "whatsapp2.png")
        if os.path.exists(whatsapp_icon_path):
            btn_whatsapp.setIcon(QIcon(whatsapp_icon_path))
            btn_whatsapp.setIconSize(QSize(18, 18))
        
        # Montar o layout do card
        card_layout.addWidget(avatar)
        card_layout.addWidget(info_widget)
        card_layout.addStretch()  # Adicionar espaço flexível
        card_layout.addWidget(btn_whatsapp)
        
        # Tornar o card clicável
        card.mousePressEvent = lambda event: self.abrir_whatsapp(contato["numero_limpo"])
        card.setCursor(QCursor(Qt.PointingHandCursor))
        
        layout.addWidget(card)
    
    def abrir_whatsapp(self, numero):
        """Abre o WhatsApp com o número especificado"""
        try:
            url = QUrl(f"https://wa.me/{numero}")
            
            # Abrir URL
            resultado = QDesktopServices.openUrl(url)
            
            if resultado:
                print(f"WhatsApp aberto para o número: {numero}")
                self.close()
            else:
                print("Falha ao abrir a URL do WhatsApp.")
                import webbrowser
                webbrowser.open(f"https://wa.me/{numero}")
                self.close()
                
        except Exception as e:
            print(f"Erro ao abrir WhatsApp: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao abrir WhatsApp: {str(e)}")


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


class MainWindow(QMainWindow):
    def __init__(self, usuario=None, empresa=None, id_funcionario=None):
        super().__init__()
        self.usuario = usuario if usuario else "Usuário"
        self.empresa = empresa if empresa else "Empresa"
        self.id_funcionario = id_funcionario
        self.permissoes = {}  # Dicionário para armazenar permissões
        self.opened_windows = []
        self.contadores_labels = {}  # Armazenar referências aos labels de contagem
        
        # Carregar permissões do funcionário (se aplicável)
        self.carregar_permissoes()
        
        self.initUI()
        
        # Atualizar visibilidade do botão PDV com base nas permissões
        self.atualizar_visibilidade_pdv()
        
        # Configurar timer para atualizar contadores a cada 30 segundos
        self.timer_atualizacao = QTimer(self)
        self.timer_atualizacao.timeout.connect(self.atualizar_contadores)
        self.timer_atualizacao.start(30000)  # 30 segundos
        
        # Configurar timer para verificar o Syncthing periodicamente
        self.timer_syncthing = QTimer(self)
        self.timer_syncthing.timeout.connect(self.verificar_syncthing)
        self.timer_syncthing.start(60000)  # Verificar a cada 60 segundos
        
        # Definir janela para maximizada (não tela cheia)
        self.showMaximized()
    
    def verificar_syncthing(self):
        """Verifica se o Syncthing está rodando e o reinicia se necessário"""
        try:
            from base.syncthing_manager import syncthing_manager
            if not syncthing_manager.verificar_syncthing_rodando():
                print("Syncthing não está rodando. Tentando reiniciar...")
                syncthing_manager.iniciar_syncthing()
        except Exception as e:
            print(f"Erro ao verificar status do Syncthing: {e}")

    def carregar_permissoes(self):
        """Carrega as permissões do funcionário logado"""
        if not self.id_funcionario:
            # Se não for um funcionário específico, conceder acesso total
            return
            
        try:
            # Instanciar a classe de backend da configuração do sistema
            from ferramentas.configuracao_sistema import ConfiguracaoSistemaBackend
            backend = ConfiguracaoSistemaBackend()
            
            # Carregar todas as permissões do funcionário
            self.permissoes = backend.obter_permissoes_funcionario(self.id_funcionario)
            
            # Atualizar a visibilidade dos elementos da interface com base nas permissões
            if hasattr(self, 'pdv_button'):
                self.atualizar_visibilidade_pdv()
                
            print(f"Permissões carregadas para o funcionário ID {self.id_funcionario}: {self.permissoes}")
        except Exception as e:
            print(f"Erro ao carregar permissões: {e}")
            # Em caso de erro, não aplica filtros
            self.permissoes = {}
    
    def verificar_permissao(self, modulo):
        """Verifica se o funcionário tem permissão para acessar um módulo"""
        # Se não for um funcionário específico, conceder acesso total
        if not self.id_funcionario:
            return True
            
        # Verificar permissão específica
        return self.permissoes.get(modulo, False)
    
    def add_menu_actions_with_permission(self, button, action_titles, window):
        """Adiciona ações ao menu com verificação de permissão"""
        for title in action_titles:
            # Verificar se o funcionário tem permissão
            if self.verificar_permissao(title) or not self.id_funcionario:
                action = QAction(title, button)
                action.triggered.connect(lambda checked, t=title: window.menu_action_triggered(t))
                button.menu.addAction(action)
    
    def atualizar_visibilidade_pdv(self):
        """Atualiza a visibilidade do botão PDV com base nas permissões"""
        # Verificar se tem permissão para o PDV
        tem_permissao_pdv = self.verificar_permissao("PDV - Ponto de Venda")
        
        # Exibir ou ocultar o botão PDV conforme permissão
        if hasattr(self, 'pdv_button'):
            if not tem_permissao_pdv and self.id_funcionario:
                # Esconder o botão se não tiver permissão
                self.pdv_button.hide()
            else:
                # Mostrar o botão se tiver permissão ou se não for funcionário específico
                self.pdv_button.show()
        
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
        
        # Uso do novo método para adicionar ações com verificação de permissão
        self.add_menu_actions_with_permission(btn_geral, [
            "Cadastro de empresa",
            "Cadastro de Clientes",
            "Cadastro Funcionários",
            "Consulta CNPJ"
        ], self)
        
        self.add_menu_actions_with_permission(btn_produtos, ["Produtos"], self)
        
        self.add_menu_actions_with_permission(btn_compras, ["Fornecedores"], self)
        
        self.add_menu_actions_with_permission(btn_vendas, ["Pedido de vendas"], self)
        
        self.add_menu_actions_with_permission(btn_financeiro, [
            "Recebimento de clientes",
            "Gerar lançamento Financeiro",
            "Controle de caixa (PDV)",
            "Conta corrente",
            "Classes financeiras"
        ], self)
        
        self.add_menu_actions_with_permission(btn_relatorios, [
            "Relatório de Vendas de Produtos",
            "Histórico de Cupons",
        ], self)
        
        self.add_menu_actions_with_permission(btn_ferramentas, [
            "Configuração de estação", 
            "Configuração do Sistema"
        ], self)
        
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

        # NOVO: Informações do desenvolvedor
        dev_info = QLabel("Desenvolvido e programado por Marco Antônio")
        dev_info.setFont(QFont("Arial", 12, -1, True))
        dev_info.setStyleSheet("color: #cccccc; margin-top: 5px;")
        dev_info.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(dev_info)

        # finalmente adiciona a tela home ao layout principal
        main_layout.addWidget(home_screen, 1)
        
        # Botão de WhatsApp - versão modificada para abrir janela de contatos
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
        self.botao_whatsapp.setToolTip("Clique para ver os contatos")
        
        # MODIFICADO: Conectar ao evento de abrir janela de contatos
        self.botao_whatsapp.clicked.connect(self.abrir_janela_contatos)
        
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
        
        # Importar e adicionar o assistente virtual
        try:
            from assistente import adicionar_assistente_ao_sistema
            adicionar_assistente_ao_sistema(self)
            print("Assistente Virtual carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar Assistente Virtual: {e}")

        # Criação do botão de acesso ao PDV no canto superior esquerdo
        self.pdv_button = QPushButton("Acesso ao\nPDV", self)
        self.pdv_button.setFixedSize(180, 80)  # Aumentado o tamanho do botão
        self.pdv_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                text-align: center;
                padding: 5px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1D6F42;
            }
            QPushButton:pressed {
                background-color: #125C30;
            }
        """)
        
        # Adicionar ícone correto ao botão (caixa.png)
        pdv_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "caixa.png")
        if os.path.exists(pdv_icon_path):
            self.pdv_button.setIcon(QIcon(pdv_icon_path))
            self.pdv_button.setIconSize(QSize(45, 45))  # Ícone maior para o botão maior
        else:
            # Caso o ícone não exista, cria um emoji como fallback
            print(f"AVISO: Ícone de caixa não encontrado em: {pdv_icon_path}")
            # Usar emoji de cashier/register como ícone alternativo no texto
            self.pdv_button.setText("🧾\nAcesso ao\nPDV")
            self.pdv_button.setFont(QFont("Arial", 10, QFont.Bold))
        
        # Adicionar sombra ao botão
        pdv_shadow = QGraphicsDropShadowEffect(self.pdv_button)
        pdv_shadow.setBlurRadius(15)
        pdv_shadow.setColor(Qt.black)
        pdv_shadow.setOffset(0, 0)
        self.pdv_button.setGraphicsEffect(pdv_shadow)
        
        # Conectar ao clique
        self.pdv_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.pdv_button.clicked.connect(self.abrir_pdv)
        
        # Posicionar o botão logo abaixo do menu "GERAL" (ajustado mais para baixo)
        self.pdv_button.move(30, 90)  # Mantida a mesma posição vertical
        self.pdv_button.raise_()
        
        # Método para reposicionar o botão PDV quando a janela for redimensionada
        def pdv_resize_event(event):
            # Chamar o método original de redimensionamento
            if hasattr(self, '_resize_original_pdv'):
                self._resize_original_pdv(event)
            else:
                novo_resize_event(event)
            
            # Manter o botão PDV na posição correta (abaixo do menu GERAL)
            self.pdv_button.move(30, 90)  # Ajustado para a nova posição
        
        # Salvar o método anterior e substituir
        self._resize_original_pdv = self.resizeEvent
        self.resizeEvent = pdv_resize_event
        
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
            #"Fiscal NF-e, SAT, NFC-e": os.path.join("relatorios", "relatorio_fiscal.py"),
            "Relatório de Vendas de Produtos": os.path.join("relatorios", "relatorio_vendas_produtos.py"), 
            "Histórico de Cupons": os.path.join("relatorios", "historico_cupom.py"), 
            "Configuração de estação": os.path.join("ferramentas", "configuracao_impressora.py"),
            "Configuração do Sistema": os.path.join("ferramentas", "configuracao_sistema.py"),
            "PDV - Ponto de Venda": os.path.join("PDV", "PDV_principal.py")
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
            "Histórico de Cupons":          "HistoricoCuponsWindow",
            # FERRAMENTAS
            "Configuração de estação":      "ConfiguracaoImpressoraWindow",
            "Configuração do Sistema": "ConfiguracaoSistemaWindow",
            # PDV
            "PDV - Ponto de Venda":         "PDVWindow"
        }

    def abrir_janela_contatos(self):
        """Abre a janela de contatos do WhatsApp"""
        try:
            # Criar e exibir a janela de contatos
            contatos_dialog = ContatosWhatsAppDialog(self)
            contatos_dialog.exec_()  # Usar exec_() para janela modal
        except Exception as e:
            print(f"Erro ao abrir janela de contatos: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao abrir janela de contatos: {str(e)}")

    def navegar_para_modulo(self, modulo, acao):
        """Navegar para um módulo específico do sistema"""
        print(f"Navegando para: {modulo} > {acao}")
        
        # Mapear para os action_titles corretos
        mapa_navegacao = {
            ("geral", "cadastro_pessoa"): "Cadastro de Clientes",
            ("geral", "cadastro_empresa"): "Cadastro de empresa",
            ("geral", "cadastro_funcionarios"): "Cadastro Funcionários",
            ("geral", "consulta_cnpj"): "Consulta CNPJ",
            ("produtos", "produtos"): "Produtos",
            ("pdv", "pdv_principal"): "PDV - Ponto de Venda",
            ("compras", "fornecedores"): "Fornecedores",
            ("vendas", "pedido_vendas"): "Pedido de vendas",
            ("financeiro", "recebimento_clientes"): "Recebimento de clientes",
            ("financeiro", "lancamento_financeiro"): "Gerar lançamento Financeiro",
            ("financeiro", "controle_caixa"): "Controle de caixa (PDV)",
            ("financeiro", "conta_corrente"): "Conta corrente",
            ("financeiro", "classes_financeiras"): "Classes financeiras",
            ("relatorios", "relatorio_vendas_produtos"): "Relatório de Vendas de Produtos",
            ("ferramentas", "configuracao_impressora"): "Configuração de estação",
            ("ferramentas", "configuracao_sistema"): "Configuração do Sistema"
        }
        
        chave = (modulo, acao)
        if chave in mapa_navegacao:
            self.menu_action_triggered(mapa_navegacao[chave])

    def abrir_pdv(self):
        """Abre o módulo do PDV"""
        # Verificar permissão
        if not self.verificar_permissao("PDV - Ponto de Venda") and self.id_funcionario:
            QMessageBox.warning(self, "Acesso Negado", 
                             "Você não tem permissão para acessar o PDV.")
            return

        try:
            pdv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PDV", "PDV_principal.py")
            
            if not os.path.exists(pdv_path):
                print(f"ERRO: Arquivo PDV não existe: {pdv_path}")
                QMessageBox.warning(self, "Erro", f"Módulo PDV não encontrado!")
                return
                
            # Verificar se já está aberto
            self.opened_windows = [w for w in self.opened_windows if w.isVisible()]
            for w in self.opened_windows:
                if w.windowTitle() == "PDV - Ponto de Venda":
                    w.setWindowState(w.windowState() & ~Qt.WindowMinimized)
                    w.activateWindow()
                    return
                    
            # Importar e abrir o módulo PDV
            spec = importlib.util.spec_from_file_location("PDV_principal", pdv_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Assumindo que a classe se chama PDVWindow
            WindowClass = getattr(module, "PDVWindow", None)
            
            if not WindowClass:
                print("Classe PDVWindow não encontrada no módulo PDV")
                QMessageBox.warning(self, "Erro", "Não foi possível iniciar o PDV!")
                return
                
            # Criar e exibir a janela
            win = WindowClass()
            # Adicionar referência à janela principal
            if hasattr(win, 'set_janela_principal'):
                win.set_janela_principal(self)
            # Passar credenciais do usuário e ID do funcionário se a janela aceitar
            if hasattr(win, 'set_credentials'):
                win.set_credentials(self.usuario, self.empresa, self.id_funcionario)
            win.setWindowTitle("PDV - Ponto de Venda")
            win.show()
            
            # Adicionar à lista de janelas abertas
            self.opened_windows.append(win)
            
        except Exception as e:
            print(f"ERRO ao abrir o PDV: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir o PDV: {str(e)}")

    
    def criar_caixa_info(self, layout_pai, titulo, nome_icone, contagem):
        """Cria uma caixa de informação com título, ícone e contagem - INTERATIVA"""
        # Container wrapper para manter espaço constante durante animação
        wrapper = QWidget()
        wrapper.setFixedSize(200, 170)
        wrapper.setStyleSheet("background-color: transparent;")
        
        box_frame = QFrame(wrapper)
        box_frame.setFixedSize(180, 150)
        box_frame.move(10, 10)  # Centralizar no wrapper
        box_frame.setStyleSheet("""
            QFrame {
                background-color: #00283d;
                border-radius: 15px;
                border: 2px solid transparent;
            }
        """)
        
        # Tornar o frame clicável
        box_frame.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Adicionar efeito de sombra
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setColor(QColor(0, 0, 0, 80))
        sombra.setOffset(0, 3)
        box_frame.setGraphicsEffect(sombra)
        
        # Guardar referência da sombra no frame
        box_frame.sombra = sombra
        
        box_layout = QVBoxLayout(box_frame)
        box_layout.setSpacing(10)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        label_titulo.setStyleSheet("color: white; background: transparent;")
        label_titulo.setAlignment(Qt.AlignCenter)
        
        # Ícone específico para cada categoria
        label_icone = QLabel()
        label_icone.setStyleSheet("background: transparent;")
        
        # Mapear ícones personalizados de acordo com o título
        icone_caminho = ""
        if nome_icone == "user.png":
            icone_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "user.png")
            emoji_fallback = "👥"
        elif nome_icone == "product.png":
            icone_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "product.png")
            emoji_fallback = "📦"
        elif nome_icone == "sales.png":
            icone_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "sales.png")
            emoji_fallback = "💰"
        
        # Verificar se o ícone existe ou usar emoji como alternativa
        if os.path.exists(icone_caminho):
            pixmap_icone = QPixmap(icone_caminho)
            label_icone.setPixmap(pixmap_icone.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            label_icone.setText(emoji_fallback)
            label_icone.setFont(QFont("Arial", 36, QFont.Bold))
            label_icone.setStyleSheet("color: white; background: transparent;")
        
        label_icone.setAlignment(Qt.AlignCenter)
        
        # Contagem (formatada como moeda se for Vendas)
        if titulo == "Vendas":
            try:
                valor_numerico = float(contagem)
                valor_formatado = f"R$ {valor_numerico:.2f}".replace('.', ',')
            except (ValueError, TypeError):
                valor_formatado = "R$ 0,00"
                
            label_contagem = QLabel(valor_formatado)
            label_contagem.setFont(QFont("Arial", 20, QFont.Bold))
        else:
            label_contagem = QLabel(str(contagem))
            label_contagem.setFont(QFont("Arial", 24, QFont.Bold))
        
        label_contagem.setStyleSheet("color: white; background: transparent;")
        label_contagem.setAlignment(Qt.AlignCenter)
        
        # Adicionar ao layout
        box_layout.addWidget(label_titulo)
        box_layout.addWidget(label_icone)
        box_layout.addWidget(label_contagem)
        
        # Adicionar evento de clique baseado no título
        def on_click(event):
            if titulo == "Clientes":
                self.menu_action_triggered("Cadastro de Clientes")
            elif titulo == "Produtos":
                self.menu_action_triggered("Produtos")
            elif titulo == "Vendas":
                self.menu_action_triggered("Relatório de Vendas de Produtos")
        
        box_frame.mousePressEvent = on_click
        
        # Adicionar animação de hover
        def on_enter(event):
            self.animar_caixa_info(box_frame, aumentar=True)
            
        def on_leave(event):
            self.animar_caixa_info(box_frame, aumentar=False)
            
        box_frame.enterEvent = on_enter
        box_frame.leaveEvent = on_leave
        
        # Adicionar o wrapper ao layout principal
        layout_pai.addWidget(wrapper)
        
        # Armazenar referência ao label para atualização posterior
        self.contadores_labels[titulo] = label_contagem
        
        # Armazenar referência ao frame para animações
        if not hasattr(self, 'info_frames'):
            self.info_frames = {}
        self.info_frames[titulo] = box_frame
        
        return label_contagem
    
        layout_pai.addWidget(wrapper)
    
    def animar_caixa_info(self, caixa, aumentar=True):
        """Anima a caixa de informação para aumentar/diminuir de tamanho"""
        # Criar grupo de animações para animar múltiplas propriedades
        if not hasattr(caixa, '_anim_group'):
            from PyQt5.QtCore import QParallelAnimationGroup
            caixa._anim_group = QParallelAnimationGroup()
            
            # Animação de geometria
            caixa._anim_geo = QPropertyAnimation(caixa, b"geometry")
            caixa._anim_geo.setDuration(200)
            caixa._anim_geo.setEasingCurve(QEasingCurve.OutCubic)
            caixa._anim_group.addAnimation(caixa._anim_geo)
        
        # Parar animações em andamento
        caixa._anim_group.stop()
        
        # Obter geometria atual
        geo_atual = caixa.geometry()
        
        if aumentar:
            # Calcular nova geometria (aumento de 10%)
            novo_width = int(180 * 1.1)
            novo_height = int(150 * 1.1)
            
            # Calcular posição para manter centralizado
            novo_x = geo_atual.x() - (novo_width - geo_atual.width()) // 2
            novo_y = geo_atual.y() - (novo_height - geo_atual.height()) // 2
            
            # Garantir que não saia dos limites do wrapper
            novo_x = max(0, min(novo_x, 200 - novo_width))
            novo_y = max(0, min(novo_y, 170 - novo_height))
            
            nova_geo = QRect(novo_x, novo_y, novo_width, novo_height)
            
            # Atualizar estilo (sem borda verde)
            caixa.setStyleSheet("""
                QFrame {
                    background-color: #003d5c;
                    border-radius: 15px;
                    border: none;
                }
            """)
            
            # Aumentar sombra
            if hasattr(caixa, 'sombra'):
                caixa.sombra.setBlurRadius(25)
                caixa.sombra.setOffset(0, 8)
                caixa.sombra.setColor(QColor(0, 0, 0, 120))
                
        else:
            # Voltar ao tamanho original
            nova_geo = QRect(10, 10, 180, 150)
            
            # Restaurar estilo original (sem borda)
            caixa.setStyleSheet("""
                QFrame {
                    background-color: #00283d;
                    border-radius: 15px;
                    border: none;
                }
            """)
            
            # Restaurar sombra original
            if hasattr(caixa, 'sombra'):
                caixa.sombra.setBlurRadius(15)
                caixa.sombra.setOffset(0, 3)
                caixa.sombra.setColor(QColor(0, 0, 0, 80))
        
        # Configurar e iniciar animação
        caixa._anim_geo.setStartValue(geo_atual)
        caixa._anim_geo.setEndValue(nova_geo)
        caixa._anim_group.start()


    # Alternativa: Método que remove o animar_caixa antigo e usa esta versão
    def animar_caixa(self, caixa, fator_escala):
        """Versão compatível com o código antigo"""
        aumentar = fator_escala > 1.0
        self.animar_caixa_info(caixa, aumentar)

    def atualizar_contadores(self):
        """Atualiza os contadores de todas as caixas de informação"""
        try:
            print("Iniciando atualização dos contadores...")
            
            # Atualizar contador de clientes (com animação)
            if "Clientes" in self.contadores_labels:
                novo_valor = self.obter_contagem_pessoas()
                self.atualizar_contador_com_animacao(self.contadores_labels["Clientes"], novo_valor)
                print(f"Contador de Clientes atualizado: {novo_valor}")
                    
            # Atualizar contador de produtos (com animação)
            if "Produtos" in self.contadores_labels:
                novo_valor = self.obter_contagem_produtos()
                self.atualizar_contador_com_animacao(self.contadores_labels["Produtos"], novo_valor)
                print(f"Contador de Produtos atualizado: {novo_valor}")
                    
            # Atualizar contador de vendas SEM animação de cor
            if "Vendas" in self.contadores_labels:
                novo_valor = self.obter_contagem_vendas()
                label = self.contadores_labels["Vendas"]
                
                # Apenas atualizar o texto sem mudar a cor
                valor_formatado = f"R$ {novo_valor:.2f}".replace('.', ',')
                label.setText(valor_formatado)
                print(f"Contador de Vendas atualizado: {valor_formatado}")
                    
            print("Contadores atualizados com sucesso!")
        except Exception as e:
            print(f"Erro ao atualizar contadores: {e}")
            import traceback
            traceback.print_exc()

    # Método para garantir que o PDV atualize a tela principal
    def forcar_atualizacao_contadores(self):
        """Força a atualização imediata dos contadores na tela principal"""
        print("Forçando atualização dos contadores a partir do PDV...")
        QTimer.singleShot(100, self.atualizar_contadores) 

    def atualizar_contador_com_animacao(self, label, novo_valor):
        """Atualiza um contador com uma animação de destaque"""
        # Verificar se é um valor monetário (texto começa com R$)
        texto_atual = label.text()
        if texto_atual.startswith("R$"):
            # Extrair o valor numérico atual
            try:
                valor_atual = float(texto_atual.replace("R$", "").replace(".", "").replace(",", ".").strip())
                
                # Verificar se o valor mudou
                if abs(valor_atual - novo_valor) > 0.01:  # Pequena margem para comparação de float
                    # Salvar o estilo original
                    estilo_original = label.styleSheet()
                    
                    # Aplicar estilo de destaque
                    label.setStyleSheet("color: #00E676; font-weight: bold;")
                    
                    # Atualizar o valor formatado como moeda
                    valor_formatado = f"R$ {novo_valor:.2f}".replace('.', ',')
                    label.setText(valor_formatado)
                    
                    # Criar timer para restaurar o estilo original após 1 segundo
                    QTimer.singleShot(1000, lambda: label.setStyleSheet(estilo_original))
            except ValueError:
                # Se houver erro ao converter, apenas atualiza o texto
                valor_formatado = f"R$ {novo_valor:.2f}".replace('.', ',')
                label.setText(valor_formatado)
        else:
            # Para valores não monetários (contadores simples)
            valor_atual = int(texto_atual) if texto_atual.isdigit() else 0
            
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
        """Obtém o valor total das vendas do dia atual"""
        try:
            # Importar datetime para obter a data atual
            from datetime import datetime, date
            
            # Obter a data atual
            data_atual = date.today()
            
            # Usar conexão direta
            from base.banco import get_connection
            
            # Obter conexão e criar cursor
            conn = get_connection()
            cursor = conn.cursor()
            
            # Verificar estrutura da tabela VENDAS para identificar a coluna de data
            cursor.execute("SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = 'VENDAS'")
            colunas = [col[0].strip() for col in cursor.fetchall()]
            print(f"Colunas na tabela VENDAS: {colunas}")
            
            # Possíveis nomes para a coluna de data
            possiveis_nomes_data = ['DATA_VENDA', 'DATA_EMISSAO', 'DATA', 'DT_VENDA', 'DT_EMISSAO', 'DATA_REGISTRO']
            
            # Encontrar a primeira coluna de data que existe na tabela
            coluna_data = None
            for nome in possiveis_nomes_data:
                if nome in colunas:
                    coluna_data = nome
                    print(f"Coluna de data encontrada: {coluna_data}")
                    break
            
            if not coluna_data:
                print("AVISO: Nenhuma coluna de data encontrada. Usando todas as vendas.")
                # Se não encontrar coluna de data, usar todas as vendas (comportamento atual)
                cursor.execute("SELECT VALOR_TOTAL FROM VENDAS")
            else:
                # Usar EXTRACT para comparar apenas a data no Firebird
                query = f"""
                SELECT VALOR_TOTAL FROM VENDAS 
                WHERE EXTRACT(YEAR FROM {coluna_data}) = ? 
                AND EXTRACT(MONTH FROM {coluna_data}) = ? 
                AND EXTRACT(DAY FROM {coluna_data}) = ?
                """
                params = (data_atual.year, data_atual.month, data_atual.day)
                print(f"Executando query: {query} com parâmetros {params}")
                cursor.execute(query, params)
            
            valores = cursor.fetchall()
            
            # Somar valores manualmente
            total = 0.0
            for valor in valores:
                if valor[0] is not None:
                    try:
                        total += float(valor[0])
                    except (ValueError, TypeError):
                        print(f"Aviso: Valor inválido encontrado: {valor[0]}")
            
            # Fechar cursor e conexão
            cursor.close()
            conn.close()
            
            if coluna_data:
                print(f"Valor total das vendas do dia {data_atual.strftime('%d/%m/%Y')}: {total}")
            else:
                print(f"Valor total de todas as vendas: {total}")
            
            return total
            
        except Exception as e:
            print(f"Erro ao obter total de vendas: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def diagnosticar_banco(self):
        """Executa diagnóstico completo do banco e valores"""
        try:
            # Executar verificações
            print("\n=== DIAGNÓSTICO DE BANCO DE DADOS ===")
            
            # Testar consulta via conexão direta
            from base.banco import get_connection
            
            # Obter conexão e criar cursor
            conn = get_connection()
            cursor = conn.cursor()
            
            # Verificar estrutura da tabela VENDAS
            cursor.execute("SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = 'VENDAS'")
            tabela_existe = cursor.fetchone()[0] > 0
            print(f"Tabela VENDAS existe: {tabela_existe}")
            
            if tabela_existe:
                # Verificar quantidade de registros
                cursor.execute("SELECT COUNT(*) FROM VENDAS")
                total_registros = cursor.fetchone()[0]
                print(f"Total de registros na tabela VENDAS: {total_registros}")
                
                # Verificar colunas da tabela
                cursor.execute("SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = 'VENDAS'")
                colunas = [col[0].strip() for col in cursor.fetchall()]
                print(f"Colunas na tabela VENDAS: {colunas}")
                
                # Verificar se a coluna VALOR_TOTAL existe
                if 'VALOR_TOTAL' in colunas:
                    print("Coluna VALOR_TOTAL encontrada!")
                else:
                    print("ERRO: Coluna VALOR_TOTAL não encontrada na tabela!")
                
                # Em vez de usar SUM, vamos pegar os valores individuais e somá-los no Python
                cursor.execute("SELECT VALOR_TOTAL FROM VENDAS")
                valores = cursor.fetchall()
                
                # Somar valores manualmente
                total = 0.0
                for valor in valores:
                    if valor[0] is not None:
                        try:
                            total += float(valor[0])
                        except (ValueError, TypeError):
                            print(f"Aviso: Valor inválido encontrado: {valor[0]}")
                
                print(f"Total calculado manualmente: {total}")
                
                # Atualizar o contador na interface
                if hasattr(self, 'contadores_labels') and "Vendas" in self.contadores_labels:
                    valor_formatado = f"R$ {total:.2f}".replace('.', ',')
                    self.contadores_labels["Vendas"].setText(valor_formatado)
                    print(f"Interface atualizada com: {valor_formatado}")
            
            # Fechar cursor e conexão
            cursor.close()
            conn.close()
            
            # Mostrar mensagem com o resultado
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Diagnóstico", 
                                f"Diagnóstico concluído! Total de vendas: R$ {total:.2f}")
            
        except Exception as e:
            print(f"Erro no diagnóstico: {e}")
            import traceback
            traceback.print_exc()
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Erro", f"Erro no diagnóstico: {str(e)}")

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
        
        # Verificar permissão antes de prosseguir
        if not self.verificar_permissao(action_title) and self.id_funcionario:
            QMessageBox.warning(self, "Acesso Negado", 
                               f"Você não tem permissão para acessar o módulo: {action_title}")
            return
        
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
                    # Passar credenciais do usuário e ID do funcionário se a janela aceitar
                    if hasattr(win, 'set_credentials'):
                        win.set_credentials(self.usuario, self.empresa, self.id_funcionario)
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
                # Passar credenciais do usuário e ID do funcionário se a janela aceitar
                if hasattr(win, 'set_credentials'):
                    win.set_credentials(self.usuario, self.empresa, self.id_funcionario)
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
            # Passar credenciais do usuário e ID do funcionário se a janela aceitar
            if hasattr(win, 'set_credentials'):
                win.set_credentials(self.usuario, self.empresa, self.id_funcionario)
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

    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela principal"""
        try:
            # Fechar todas as janelas abertas, EXCETO o PDV
            for window in self.opened_windows:
                try:
                    # Verificar se a janela ainda existe e está visível
                    if window and window.isVisible():
                        # Verificar se NÃO é o PDV (por título ou tipo)
                        if window.windowTitle() != "PDV - Ponto de Venda":
                            print(f"Fechando janela: {window.windowTitle()}")
                            window.close()
                        else:
                            print("Mantendo PDV aberto")
                except Exception as e:
                    print(f"Erro ao fechar janela: {e}")
            
            # Limpar a lista de janelas abertas, mantendo apenas o PDV
            self.opened_windows = [w for w in self.opened_windows 
                                if w and w.isVisible() and w.windowTitle() == "PDV - Ponto de Venda"]
            
            # Parar timers
            if hasattr(self, 'timer_atualizacao'):
                self.timer_atualizacao.stop()
            if hasattr(self, 'timer_syncthing'):
                self.timer_syncthing.stop()
            
            # Fechar Syncthing
            try:
                from base.banco import fechar_syncthing
                fechar_syncthing()
            except Exception as e:
                print(f"Erro ao encerrar Syncthing: {e}")
        
        except Exception as e:
            print(f"Erro no closeEvent: {e}")
            import traceback
            traceback.print_exc()
        
        # Aceitar o evento para fechar a janela principal
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(usuario="Marco", empresa="MB Sistemas")
    window.show()
    sys.exit(app.exec_())