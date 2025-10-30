import sys
import os
import firebird.driver as fdb  # <-- Changed from 'import fdb'
import importlib.util
import unicodedata
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame, QAction,
                             QMenu, QToolBar, QGraphicsDropShadowEffect, QMessageBox, QDialog,
                             QDockWidget, QInputDialog) # <<< IMPORTADO
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize,QRect, QPropertyAnimation, QEasingCurve, QUrl, QTimer, QRect, pyqtSignal, QTimer
from PyQt5.QtGui import QDesktopServices
from base.banco import execute_query
try:
    # Esta estrutura de importação funciona tanto em dev quanto no .exe
    from mercado_livre.main_final import MercadoLivreBackend
    ML_BACKEND_DISPONIVEL = True
except ImportError:
    print("AVISO: Módulo do Mercado Livre não encontrado. A funcionalidade será desativada.")
    ML_BACKEND_DISPONIVEL = False
    MercadoLivreBackend = None

from app_setup import get_app

app = get_app()

class ContatosWhatsAppDialog(QDialog):
    # ... (Seu código da classe ContatosWhatsAppDialog - sem alterações) ...
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
        info_widget.setFixedWidth(300) # Largura fixa para garantir espaço
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 5, 0, 5)
        info_layout.setSpacing(3)
       
        # Nome
        nome_label = QLabel(contato["nome"])
        nome_label.setFont(QFont("Arial", 14, QFont.Bold))
        nome_label.setStyleSheet("color: #2c3e50; background: transparent;")
        nome_label.setWordWrap(False) # Evitar quebra de linha
        nome_label.setMinimumWidth(200) # Garantir largura mínima
       
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
        card_layout.addStretch() # Adicionar espaço flexível
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
    """Botão de menu que abre automaticamente ao passar o mouse"""
    
    # Variável de classe para rastrear qual botão está com menu aberto
    _current_button = None
    
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
        
        # Cria o menu
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
        
        # Timer para abrir o menu
        self.open_timer = QTimer(self)
        self.open_timer.setSingleShot(True)
        self.open_timer.timeout.connect(self._open_menu)
        
        # Timer para verificar e fechar o menu
        self.check_timer = QTimer(self)
        self.check_timer.setInterval(100)  # Verifica a cada 100ms
        self.check_timer.timeout.connect(self._check_should_close)
        
        # Remove o comportamento padrão de clique
        self.setMenu(None)
        
        # Habilita rastreamento de mouse
        self.setMouseTracking(True)
        
        # Conecta o sinal de quando o menu é fechado
        self.menu.aboutToHide.connect(self._on_menu_hide)
    
    def enterEvent(self, event):
        """Quando o mouse entra no botão"""
        super().enterEvent(event)
        
        # Se outro botão tem menu aberto, abre este imediatamente
        if MenuButton._current_button and MenuButton._current_button != self:
            MenuButton._current_button._close_menu()
            self._open_menu()
        else:
            # Senão, abre após pequeno delay
            self.open_timer.start(150)
    
    def leaveEvent(self, event):
        """Quando o mouse sai do botão"""
        super().leaveEvent(event)
        
        # Cancela abertura se estava agendada
        self.open_timer.stop()
        
        # Inicia verificação para fechar
        if not self.check_timer.isActive():
            self.check_timer.start()
    
    def _open_menu(self):
        """Abre o menu"""
        if self.menu.isEmpty():
            return
        
        # Para o timer de verificação
        self.check_timer.stop()
        
        # Posiciona e mostra o menu
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.menu.popup(pos)
        
        # Atualiza o botão atual
        MenuButton._current_button = self
        
        # Inicia timer de verificação
        self.check_timer.start()
    
    def _close_menu(self):
        """Fecha o menu"""
        self.check_timer.stop()
        if self.menu.isVisible():
            self.menu.hide()
        if MenuButton._current_button == self:
            MenuButton._current_button = None
    
    def _check_should_close(self):
        """Verifica se deve fechar o menu"""
        # Só verifica se este botão tem o menu aberto
        if MenuButton._current_button != self:
            self.check_timer.stop()
            return

        if not self.menu.isVisible():
            self.check_timer.stop()
            return

        # Obtém a posição global do cursor
        cursor_pos = QCursor.pos()
        
        # Verifica se o mouse está sobre o botão atual
        button_rect = self.rect()
        button_global_rect = QRect(
            self.mapToGlobal(button_rect.topLeft()),
            self.mapToGlobal(button_rect.bottomRight())
        )
        
        # Verifica se o mouse está sobre o menu
        menu_rect = self.menu.rect()
        menu_global_rect = QRect(
            self.menu.mapToGlobal(menu_rect.topLeft()),
            self.menu.mapToGlobal(menu_rect.bottomRight())
        )
        
        # Se o mouse está sobre o botão ou o menu, não fecha
        if button_global_rect.contains(cursor_pos) or menu_global_rect.contains(cursor_pos):
            return
        
        # Verifica se o mouse está sobre outro botão MenuButton
        for widget in self.parent().findChildren(MenuButton):
            if widget != self:
                other_rect = widget.rect()
                button_global_rect = QRect(
                    widget.mapToGlobal(other_rect.topLeft()),
                    widget.mapToGlobal(other_rect.bottomRight())
                )
                if button_global_rect.contains(cursor_pos):
                    # Mouse está sobre outro botão, fecha este e abre o outro
                    self._close_menu()
                    widget._open_menu()
                    return

        # Mouse não está em nenhum lugar relevante, fecha o menu
        self._close_menu()
    
    def _on_menu_hide(self):
        """Chamado quando o menu é fechado"""
        if MenuButton._current_button == self:
            MenuButton._current_button = None
        self.check_timer.stop()
    
    def mousePressEvent(self, event):
        """Desabilita o clique para abrir o menu"""
        # Permite clique apenas para fechar se já estiver aberto
        if self.menu.isVisible() and MenuButton._current_button == self:
            self._close_menu()
        # Não faz nada para evitar o comportamento padrão
        pass
    
class NotificationPopup(QDialog):
    """Uma janela de notificação pop-up não-intrusiva."""
    def __init__(self, title, message, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.layout = QVBoxLayout(self)
        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("bg_frame")
        self.layout.addWidget(self.bg_frame)
       
        self.bg_layout = QVBoxLayout(self.bg_frame)
        self.bg_layout.setContentsMargins(20, 15, 20, 15)
        self.bg_layout.setSpacing(5)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("title")
        self.message_label = QLabel(message)
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        self.bg_layout.addWidget(self.title_label)
        self.bg_layout.addWidget(self.message_label)
       
        self.setStyleSheet("""
            #bg_frame {
                background-color: rgba(30, 40, 50, 0.9);
                border-radius: 10px;
                border: 1px solid #00E676;
            }
            #title {
                color: #00E676; /* Verde Neon */
                font-size: 14px;
                font-weight: bold;
            }
            #message {
                color: white;
                font-size: 12px;
            }
        """)
        # Timer para fechar a notificação automaticamente
        self.timer_close = QTimer(self)
        self.timer_close.setSingleShot(True)
        self.timer_close.timeout.connect(self.close)
        self.timer_close.start(7000) # Fecha após 7 segundos
    def mousePressEvent(self, event):
        self.close()
    def show_notification(self):
        screen_geometry = QApplication.desktop().availableGeometry()
        self.adjustSize() # Ajusta o tamanho ao conteúdo
        self.move(
            screen_geometry.right() - self.width() - 15,
            screen_geometry.bottom() - self.height() - 15
        )
        self.show()
class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()
   
    def __init__(self, usuario=None, empresa=None, id_usuario=None, id_funcionario=None):
        super().__init__()
        self.usuario = usuario if usuario else "Usuário"
        self.empresa = empresa if empresa else "Empresa"
        self.id_usuario = id_usuario
        self.id_funcionario = id_funcionario
        self.id_ultima_venda_notificada = None
        self.btn_gerenciar_favoritos = None

        self.favorites = self.load_favorites()
        self.favorite_buttons = []
       
        self.permissoes = {}
        self.opened_windows = []
        self.contadores_labels = {}
        self.id_ultima_venda_notificada_ml = None
        self.ml_backend_para_notificacao = None
       
        # ### NOVIDADE: Inicializa o backend do ML se disponível ###
        self.ml_backend = None
        if ML_BACKEND_DISPONIVEL:
            try:
                # Cria uma instância separada do backend apenas para notificações
                self.ml_backend_para_notificacao = MercadoLivreBackend()
                if self.ml_backend_para_notificacao.is_configured():
                    self.vendas_timer_ml = QTimer(self)
                    self.vendas_timer_ml.timeout.connect(self.verificar_novas_vendas_ml)
                    self.vendas_timer_ml.start(60000) # Verifica a cada 60 segundos
                    QTimer.singleShot(5000, self.verificar_novas_vendas_ml)
            except Exception as e:
                print(f"Erro ao iniciar o monitor de vendas do ML: {e}")
        self.tem_acesso_ecommerce = False
        self.verificar_acesso_geral_modulos()
        self.carregar_permissoes()
       
        self.initUI()
       
        self.atualizar_visibilidade_pdv()
       
        # self.timer_atualizacao = QTimer(self)
        # self.timer_atualizacao.timeout.connect(self.atualizar_contadores)
        # self.timer_atualizacao.start(30000)
       
        self.timer_syncthing = QTimer(self)
        self.timer_syncthing.timeout.connect(self.verificar_syncthing)
        self.timer_syncthing.start(60000)
        if self.tem_acesso_ecommerce:
            self.vendas_timer = QTimer(self)
            self.vendas_timer.timeout.connect(self.verificar_novas_vendas_ml)
            # Verifica a cada 60 segundos (60000 milissegundos)
            self.vendas_timer.start(60000)
            # Faz uma verificação inicial após 5 segundos do início
            QTimer.singleShot(5000, self.verificar_novas_vendas_ml)
       
        self.showMaximized()

    def get_favorites_file(self):
        """Retorna o caminho gravável do arquivo de favoritos (ao lado do EXE em modo frozen)."""
        if getattr(sys, 'frozen', False):
            # Em EXE: diretório ao lado do executável (gravável)
            base_dir = os.path.dirname(sys.executable)
        else:
            # Em dev: diretório do script
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        config_dir = os.path.join(base_dir, "config")
        os.makedirs(config_dir, exist_ok=True)  # Cria a pasta 'config' se não existir
        return os.path.join(config_dir, "favorites.json")
    
    def create_favorite_button(self, action_name):
        """Cria um botão de favorito estilizado."""
        button = QPushButton(action_name)
        button.setMinimumSize(160, 45)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet("""
            QPushButton {
                background-color: #003d5c;
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #005079; }
            QPushButton:pressed { background-color: #00283d; }
        """)
        button.clicked.connect(lambda: self.menu_action_triggered(action_name))
        return button

    def update_favorites_display(self):
        """Limpa e recria os botões de favoritos na tela, filtrando por permissões."""
        # Limpa layout antigo
        while self.favorites_layout.count():
            child = self.favorites_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Adiciona um espaçador no início
        self.favorites_layout.addStretch()

        # --- MODIFICADO: Re-filtra os favoritos antes de exibir ---
        favoritos_filtrados = self.filtrar_favoritos_com_permissao(self.favorites)
        
        # Se houve mudanças na lista de favoritos (alguns foram removidos), salva a nova lista
        if len(favoritos_filtrados) != len(self.favorites):
            self.favorites = favoritos_filtrados
            self.save_favorites()

        # Cria botões para os favoritos filtrados
        for favorite in sorted(favoritos_filtrados):
            button = self.create_favorite_button(favorite)
            self.favorites_layout.addWidget(button)
        self.favorites_layout.addStretch()

    def abrir_seletor_favoritos(self):
        """Abre a janela para o usuário selecionar seus módulos favoritos."""
        try:
            # --- CORREÇÃO AQUI: Usando 'self.id_usuario' que é o nome correto ---
            # Verifica se a informação do usuário logado existe.
            if not hasattr(self, 'id_usuario') or self.id_usuario is None:
                QMessageBox.critical(self, "Erro de Autenticação", 
                                    "Não foi possível identificar o ID do usuário logado. Por favor, reinicie o sistema.")
                return

            # Importa a classe do arquivo 'favoritos.py'
            from ferramentas.favoritos import SeletorModulosEstilizado
            
            # Pega todos os módulos que podem ser abertos
            modulos_disponiveis = self.action_to_py_file.keys()
            
            # --- CORREÇÃO AQUI: Passando a variável correta para o seletor ---
            seletor = SeletorModulosEstilizado(
                modulos_disponiveis=modulos_disponiveis, 
                favoritos_atuais=self.favorites,
                usuario_id=self.id_usuario,  
                parent=self
            )
            
            if seletor.exec_() == QDialog.Accepted:
                self.favorites = seletor.get_selecao_final()
                self.save_favorites()
                self.update_favorites_display()
                
        except ImportError:
            QMessageBox.warning(self, "Erro de Importação", "O arquivo 'ferramentas/favoritos.py' não foi encontrado ou contém erros.")
        except Exception as e:
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro ao abrir o seletor de favoritos:\n{e}")


    def load_favorites(self):
        """Carrega a lista de favoritos do arquivo JSON gravável, copiando do bundado se necessário."""
        writable_path = self.get_favorites_file()
        bundled_path = self.resource_path("config/favorites.json")
        
        # Se o arquivo gravável não existe, tenta copiar do bundado
        if not os.path.exists(writable_path):
            if os.path.exists(bundled_path):
                try:
                    import shutil
                    shutil.copy2(bundled_path, writable_path)
                    print(f"Arquivo favorites.json copiado do bundado para: {writable_path}")
                except Exception as e:
                    print(f"Erro ao copiar favorites.json: {e}")
            else:
                # Arquivo não existe nem no bundado: cria vazio
                self.save_favorites()  # Salva lista vazia para inicializar
        
        if not os.path.exists(writable_path):
            return []  # Fallback: lista vazia
        
        try:
            with open(writable_path, 'r', encoding='utf-8') as f:
                favoritos_salvos = json.load(f)
            
            # Filtra os favoritos baseado nas permissões do usuário
            return self.filtrar_favoritos_com_permissao(favoritos_salvos)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Erro ao carregar favoritos: {e}")
            return []  # Retorna lista vazia em caso de erro
        
    def filtrar_favoritos_com_permissao(self, favoritos_lista):
        """
        Filtra uma lista de favoritos, removendo aqueles para os quais
        o usuário não tem permissão.
        """
        # --- NOVO: Lista de módulos que exigem permissão especial ---
        modulos_com_restricao = {
            "Ver Dashboard do Mercado livre": "ACESSO_ECOMMERCE",
            "Dashboard Mercado Livre": "ACESSO_ECOMMERCE"
        }
        
        favoritos_permitidos = []
        
        for modulo in favoritos_lista:
            # Se o módulo não tem restrição, permite
            if modulo not in modulos_com_restricao:
                favoritos_permitidos.append(modulo)
                continue
            
            # Se tem restrição, verifica a permissão
            campo_permissao = modulos_com_restricao[modulo]
            
            if self.verificar_permissao_especifica(campo_permissao):
                favoritos_permitidos.append(modulo)
            else:
                print(f"Módulo '{modulo}' removido dos favoritos: sem permissão de acesso.")
        
        return favoritos_permitidos
    
    def verificar_permissao_especifica(self, campo_permissao):
        """
        Verifica se o usuário tem uma permissão específica no banco de dados.
        
        Args:
            campo_permissao (str): Nome do campo de permissão no banco (ex: "ACESSO_ECOMMERCE")
        
        Returns:
            bool: True se tem permissão, False caso contrário
        """
        if not self.id_usuario:
            return False  # Se não houver ID de usuário, nega por segurança

        try:
            from base.banco import execute_query
            
            # 1. Descobrir se o usuário é master ou funcionário
            query_user_info = f"SELECT USUARIO_MASTER FROM USUARIOS WHERE ID = {self.id_usuario}"
            result = execute_query(query_user_info)
            
            if not result or not result[0]:
                print(f"Aviso: Usuário com ID {self.id_usuario} não encontrado no banco.")
                return False

            usuario_master_id = result[0][0]
            
            # Se o usuário não tem um mestre (é NULL), ele é o próprio mestre.
            id_para_verificar = usuario_master_id if usuario_master_id is not None else self.id_usuario

            # 2. Verificar a permissão específica do usuário mestre
            query_permissao = f"SELECT {campo_permissao} FROM USUARIOS WHERE ID = {id_para_verificar}"
            permissao_result = execute_query(query_permissao)

            if permissao_result and permissao_result[0] and permissao_result[0][0] == 'S':
                return True  # Acesso permitido
            else:
                return False  # Acesso negado

        except Exception as e:
            print(f"Erro ao verificar permissão {campo_permissao}: {e}")
            return False  # Em caso de erro, nega o acesso por segurança

    def save_favorites(self):
        """Salva a lista atual de favoritos no arquivo JSON."""
        try:
            with open(self.get_favorites_file(), 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar favoritos: {e}")  

    def get_db_connection(self):
        """Retorna uma conexão com o banco Firebird e erro se houver"""
        try:
            # Determina o diretório base da aplicação
            if getattr(sys, 'frozen', False):
                # Se for um executável compilado (.exe)
                base_dir = os.path.dirname(sys.executable)
            else:
                # Se for um script Python normal
                # O arquivo main.py está na raiz, então pegamos o diretório dele
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # O banco sempre estará em base/banco relativo ao diretório da aplicação
            db_path = os.path.join(base_dir, "base", "banco", "MBDATA_NOVO.FDB")
            
            # Verifica se o arquivo existe
            if not os.path.isfile(db_path):
                # Tenta um nível acima (caso o script esteja em uma subpasta)
                base_dir_alt = os.path.dirname(base_dir)
                db_path_alt = os.path.join(base_dir_alt, "base", "banco", "MBDATA_NOVO.FDB")
                
                if os.path.isfile(db_path_alt):
                    db_path = db_path_alt
                else:
                    print(f"ERRO: Banco não encontrado!")
                    print(f"  Tentativa 1: {db_path}")
                    print(f"  Tentativa 2: {db_path_alt}")
                    print(f"  Diretório atual: {os.getcwd()}")
                    return None, f"Banco de dados não encontrado"
            
            print(f"Conectando ao banco: {db_path}")
            
            conexao = fdb.connect(
                database=db_path,
                user='SYSDBA',
                password='masterkey',
                charset='UTF8'
            )
            return conexao, None
            
        except Exception as e:
            print(f"Erro ao conectar com banco: {e}")
            return None, str(e)
    
    def caixa_esta_aberto(self):
        """Verifica se existe caixa aberto para o usuário atual"""
        conexao, error = self.get_db_connection()
        if error:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Erro")
            msg_box.setText(f"Não foi possível conectar ao banco de dados!\nDetalhes: {error}")
            self.aplicar_estilo_aviso(msg_box) # Aplica o estilo
            msg_box.exec_()
            return False
           
        try:
            cursor = conexao.cursor()
           
            # Primeiro, verifica se a tabela CAIXA existe
            cursor.execute("""
                SELECT COUNT(*) FROM RDB$RELATIONS
                WHERE RDB$RELATION_NAME = 'CAIXA' AND RDB$SYSTEM_FLAG = 0
            """)
           
            if cursor.fetchone()[0] == 0:
                # Tabela não existe, considera como não tendo caixa aberto
                cursor.close()
                conexao.close()
                return False
           
            # Verifica caixas abertos (sem data de fechamento)
            cursor.execute("""
                SELECT COUNT(*) FROM CAIXA
                WHERE USUARIO = ? AND DATA_FECHAMENTO IS NULL
            """, [self.usuario])
           
            count = cursor.fetchone()[0]
            cursor.close()
            conexao.close()
            return count > 0
           
        except Exception as e:
            print(f"Erro ao verificar caixa: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao verificar caixa: {str(e)}")
            if conexao:
                conexao.close()
            return False
        
    def abrir_caixa(self, fundo_troco):
        """Abre um novo caixa para o usuário atual"""
        conexao, error = self.get_db_connection()
        if error:
            QMessageBox.warning(self, "Erro", f"Não foi possível conectar ao banco de dados!\nDetalhes: {error}")
            return False
        
        try:
            cursor = conexao.cursor()
        
            # Verifica se a tabela CAIXA existe, se não existir, cria
            cursor.execute("""
                SELECT COUNT(*) FROM RDB$RELATIONS
                WHERE RDB$RELATION_NAME = 'CAIXA' AND RDB$SYSTEM_FLAG = 0
            """)
        
            if cursor.fetchone()[0] == 0:
                # Cria a tabela CAIXA
                self.criar_estrutura_caixa(cursor)
        
            # Insere novo caixa
            cursor.execute("""
                INSERT INTO CAIXA (DATA_ABERTURA, HORA_ABERTURA, USUARIO, FUNDO_TROCO, STATUS)
                VALUES (CURRENT_DATE, CURRENT_TIME, ?, ?, 'ABERTO')
            """, [self.usuario, float(fundo_troco)])
        
            conexao.commit()
        
            # Pega o código do caixa criado com SELECT ao invés de CURRENT_VALUE
            cursor.execute("""
                SELECT CODIGO FROM CAIXA
                WHERE USUARIO = ? AND DATA_ABERTURA = CURRENT_DATE
                ORDER BY CODIGO DESC
                ROWS 1
            """, [self.usuario])
        
            resultado = cursor.fetchone()
            codigo = resultado[0] if resultado else "N/A"
        
            cursor.close()
            conexao.close()
        
            # MODIFICADO: Criar e estilizar o QMessageBox manualmente em vez de usar QMessageBox.information
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Caixa Aberto")
            msg_box.setText(f"Caixa #{codigo} aberto com sucesso!\nFundo de troco: R$ {fundo_troco:.2f}")
            # Remover o ícone!
            msg_box.setIcon(QMessageBox.NoIcon)  # Isso remove o ícone de exclamação
            self.aplicar_estilo_aviso(msg_box)
            msg_box.exec_()
            
            return True
        
        except Exception as e:
            print(f"Erro ao abrir caixa: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao abrir caixa: {str(e)}")
            if conexao:
                conexao.rollback()
                conexao.close()
            return False
    
    def fechar_caixa(self):
        """Fecha o caixa aberto do usuário atual"""
        conexao, error = self.get_db_connection()
        if error:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Erro")
            msg_box.setText(f"Não foi possível conectar ao banco de dados!\nDetalhes: {error}")
            self.aplicar_estilo_aviso(msg_box) # Aplica o estilo
            msg_box.exec_()
            return False
        
        try:
            cursor = conexao.cursor()
        
            # Verifica se existe caixa aberto
            cursor.execute("""
                SELECT CODIGO FROM CAIXA
                WHERE USUARIO = ? AND DATA_FECHAMENTO IS NULL
            """, [self.usuario])
        
            resultado = cursor.fetchone()
            if not resultado:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Aviso")
                msg_box.setText("Não há caixa aberto para fechar!")
                self.aplicar_estilo_aviso(msg_box) # Aplica o estilo
                msg_box.exec_()
                cursor.close()
                conexao.close()
                return False
        
            codigo_caixa = resultado[0]
        
            # Fecha o caixa
            cursor.execute("""
                UPDATE CAIXA
                SET DATA_FECHAMENTO = CURRENT_DATE,
                    HORA_FECHAMENTO = CURRENT_TIME,
                    STATUS = 'FECHADO'
                WHERE CODIGO = ?
            """, [codigo_caixa])
        
            conexao.commit()
            cursor.close()
            conexao.close()
        
            # Substitua o QMessageBox.information por uma instância explícita
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Caixa Fechado")
            msg_box.setText(f"Caixa #{codigo_caixa} fechado com sucesso!")
            self.aplicar_estilo_aviso(msg_box) # Aplica o estilo
            msg_box.exec_()
            return True
        
        except Exception as e:
            print(f"Erro ao fechar caixa: {e}")
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Erro")
            msg_box.setText(f"Erro ao fechar caixa: {str(e)}")
            self.aplicar_estilo_aviso(msg_box) # Aplica o estilo
            msg_box.exec_()
            if conexao:
                conexao.rollback()
                conexao.close()
            return False
        
    def criar_estrutura_caixa(self, cursor):
        """Cria a estrutura da tabela CAIXA se não existir"""
        try:
            # Cria a tabela
            cursor.execute("""
                CREATE TABLE CAIXA (
                    CODIGO INTEGER NOT NULL PRIMARY KEY,
                    DATA_ABERTURA DATE,
                    HORA_ABERTURA TIME,
                    DATA_FECHAMENTO DATE,
                    HORA_FECHAMENTO TIME,
                    USUARIO VARCHAR(50),
                    FUNDO_TROCO DECIMAL(10,2) DEFAULT 0.00,
                    STATUS VARCHAR(10) DEFAULT 'ABERTO'
                )
            """)
           
            # Cria sequence
            cursor.execute("CREATE SEQUENCE SEQ_CAIXA")
           
            # Cria trigger
            cursor.execute("""
                CREATE TRIGGER TRG_CAIXA_BI FOR CAIXA
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.CODIGO IS NULL) THEN
                        NEW.CODIGO = NEXT VALUE FOR SEQ_CAIXA;
                END
            """)
           
            print("Estrutura da tabela CAIXA criada com sucesso!")
           
        except Exception as e:
            print(f"Erro ao criar estrutura da tabela CAIXA: {e}")
            raise
    def verificar_novas_vendas_ml(self):
        # A verificação inicial se o backend existe é feita dentro do método obter_pedidos_pendentes_ml
        # Mas vamos manter uma verificação aqui para clareza e para evitar trabalho desnecessário.
        if not ML_BACKEND_DISPONIVEL:
            return
        print("Timer Global: Verificando novas vendas do Mercado Livre...")
        try:
            # CRIA UMA INSTÂNCIA NOVA E TEMPORÁRIA para garantir que use as credenciais mais recentes.
            backend_ml_temporario = MercadoLivreBackend()
            # Se a instância não estiver configurada (usuário deslogou), simplesmente para a execução.
            if not backend_ml_temporario.is_configured():
                print("Timer Global: Backend do ML não configurado. Pausando verificação.")
                return
            vendas = backend_ml_temporario.get_ultimas_vendas(limit=5)
            if not vendas:
                return
           
            id_mais_recente = vendas[0]['id_pedido']
            if self.id_ultima_venda_notificada_ml is None:
                self.id_ultima_venda_notificada_ml = id_mais_recente
                print(f"Monitor de vendas iniciado. Venda mais recente ID: {id_mais_recente}")
                return
            for venda in reversed(vendas):
                if venda['id_pedido'] > self.id_ultima_venda_notificada_ml:
                    print(f"NOVA VENDA DETECTADA! ID: {venda['id_pedido']}")
                    self.id_ultima_venda_notificada_ml = venda['id_pedido']
                   
                    mensagem = f"{venda['produto']}\nValor: {venda['valor']}"
                    self.mostrar_notificacao("📦 Nova Venda no Mercado Livre!", mensagem)
                   
                    # Passa a instância já criada para a função de baixa de estoque.
                    self.dar_baixa_estoque_ml(venda, backend_ml_temporario)
        except Exception as e:
            print(f"Erro no timer global de vendas: {e}")
    def mostrar_notificacao(self, titulo, mensagem):
        popup = NotificationPopup(titulo, mensagem, self)
        popup.show_notification()
        QApplication.alert(self) # Faz o ícone da barra de tarefas piscar
    def dar_baixa_estoque_ml(self, dados_venda, ml_backend_instance):
        """Dá baixa no estoque local com base em uma venda do Mercado Livre."""
        try:
            id_pedido = dados_venda.get('id_pedido')
            if not id_pedido: return
            from base.banco import execute_query
            conn = execute_query()
            cursor = conn.cursor()
            # Use a instância do backend que foi passada como argumento
            detalhes_pedido = ml_backend_instance._make_request('get', f"https://api.mercadolibre.com/orders/{id_pedido}")
           
            for item in detalhes_pedido.get('order_items', []):
                meli_id_produto = item['item']['id']
                quantidade_vendida = item['quantity']
               
                print(f"Dando baixa de {quantidade_vendida} unidade(s) para o produto MELI_ID {meli_id_produto}")
                cursor.execute("SELECT ID, QUANTIDADE_ESTOQUE FROM PRODUTOS WHERE MELI_ID = ?", (meli_id_produto,))
                produto_local = cursor.fetchone()
                if produto_local:
                    cursor.execute(
                        "UPDATE PRODUTOS SET QUANTIDADE_ESTOQUE = QUANTIDADE_ESTOQUE - ? WHERE MELI_ID = ?",
                        (quantidade_vendida, meli_id_produto)
                    )
                    print(f"Produto {meli_id_produto} encontrado. Estoque atualizado.")
                else:
                    print(f"AVISO: Produto com MELI_ID {meli_id_produto} não encontrado no banco de dados local. A baixa não foi realizada.")
           
            conn.commit()
            cursor.close()
            conn.close()
            print("Processo de baixa de estoque para o pedido concluído.")
            self.forcar_atualizacao_contadores()
        except Exception as e:
            print(f"Erro ao dar baixa no estoque local para venda do ML: {e}")
           
    def mostrar_notificacao_venda(self, mensagem):
        """Cria e exibe o pop-up e aciona o piscar do ícone."""
        # Cria a notificação
        popup = NotificationPopup("📦 Nova Venda no Mercado Livre!", mensagem, self)
        popup.show_notification()
       
        # Aciona o piscar da barra de tarefas
        QApplication.alert(self)
    # --- Métodos de Verificação e Permissão (sem alterações) ---
    def verificar_acesso_geral_modulos(self):
        if not self.id_usuario:
            print("Aviso: Nenhum ID de usuário fornecido. Acesso ao e-commerce negado.")
            return
        try:
            from base.banco import verificar_acesso_ecommerce
            self.tem_acesso_ecommerce = verificar_acesso_ecommerce(self.id_usuario)
            print(f"Verificação de acesso E-commerce para usuário ID {self.id_usuario}: {self.tem_acesso_ecommerce}")
        except Exception as e:
            print(f"Erro ao verificar acesso ao e-commerce: {e}")
            self.tem_acesso_ecommerce = False
   
    def verificar_syncthing(self):
        try:
            from base.syncthing_manager import syncthing_manager
            if not syncthing_manager.verificar_syncthing_rodando():
                print("Syncthing não está rodando. Tentando reiniciar...")
                syncthing_manager.iniciar_syncthing()
        except Exception as e:
            print(f"Erro ao verificar status do Syncthing: {e}")
    def carregar_permissoes(self):
        if not self.id_funcionario:
            return
           
        try:
            from ferramentas.configuracao_sistema import ConfiguracaoSistemaBackend
            backend = ConfiguracaoSistemaBackend()
            self.permissoes = backend.obter_permissoes_funcionario(self.id_funcionario)
            if hasattr(self, 'pdv_button'):
                self.atualizar_visibilidade_pdv()
            print(f"Permissões carregadas para o funcionário ID {self.id_funcionario}: {self.permissoes}")
        except Exception as e:
            print(f"Erro ao carregar permissões: {e}")
            self.permissoes = {}
   
    def verificar_permissao(self, modulo):
        if not self.id_funcionario:
            return True
        return self.permissoes.get(modulo, False)
   
    def add_menu_actions_with_permission(self, button, action_titles, window):
        for title in action_titles:
            if self.verificar_permissao(title) or not self.id_funcionario:
                action = QAction(title, button)
                action.triggered.connect(lambda checked, t=title: window.menu_action_triggered(t))
                button.menu.addAction(action)
   
    def atualizar_visibilidade_pdv(self):
        tem_permissao_pdv = self.verificar_permissao("PDV - Ponto de Venda")
        if hasattr(self, 'pdv_button'):
            if not tem_permissao_pdv and self.id_funcionario:
                self.pdv_button.hide()
            else:
                self.pdv_button.show()
   
    # --- Métodos de Gerenciamento do Assistente e Botões ---
    def toggle_assistente_dock(self):
        """Abre ou fecha o QDockWidget do assistente."""
        if hasattr(self, 'chatbot_dock'):
            if self.chatbot_dock.isVisible():
                self.chatbot_dock.hide()
            else:
                self.chatbot_dock.show()
    def on_assistente_visibilidade_mudou(self, visivel):
        """Gerencia a visibilidade dos botões flutuantes quando o dock muda."""
        if visivel:
            if hasattr(self, 'botao_whatsapp'): self.botao_whatsapp.hide()
            if hasattr(self, 'logout_button'): self.logout_button.hide()
            if hasattr(self, 'btn_assistente'): self.btn_assistente.hide()
        else:
            if hasattr(self, 'botao_whatsapp'): self.botao_whatsapp.show()
            if hasattr(self, 'logout_button'): self.logout_button.show()
            if hasattr(self, 'btn_assistente'): self.btn_assistente.show()
        # Após mudar a visibilidade, re-posiciona quem ficou visível
        self.posicionar_botoes_flutuantes()
    def posicionar_botoes_fixos(self):
        """Posiciona os botões fixos do canto superior (PDV e Logout)."""
        if hasattr(self, 'pdv_button'):
            self.pdv_button.move(30, 90)
            self.pdv_button.raise_()
        if hasattr(self, 'logout_button'):
            self.logout_button.move(self.width() - self.logout_button.width() - 30, 90)
            self.logout_button.raise_()
   
    def posicionar_botoes_flutuantes(self):
        """Calcula e aplica a posição de todos os botões flutuantes (canto inferior direito)."""
        margem_x = 30
        margem_y = 30
       
        if hasattr(self, 'botao_whatsapp') and self.botao_whatsapp.isVisible():
            self.botao_whatsapp.move(
                self.width() - self.botao_whatsapp.width() - margem_x,
                self.height() - self.botao_whatsapp.height() - margem_y
            )
            self.botao_whatsapp.raise_()
            margem_y += self.botao_whatsapp.height() + 15
        if hasattr(self, 'btn_assistente') and self.btn_assistente.isVisible():
            self.btn_assistente.move(
                self.width() - self.btn_assistente.width() - margem_x,
                self.height() - self.btn_assistente.height() - margem_y
            )
            self.btn_assistente.raise_()
    # --- Inicialização da UI ---
    def initUI(self):
        self.setWindowTitle("MB Sistema - Sistema de Gerenciamento")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("background-color: #272525;")
       
        central_widget = QWidget()
        central_widget.setMinimumWidth(800)
        self.setCentralWidget(central_widget)
       
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
       
        # --- 1. BARRA DE MENUS ---
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
        #btn_fiscal = MenuButton("Fiscal")
        self.btn_mercado_livre = MenuButton("MERCADO LIVRE")
       
        self.add_menu_actions_with_permission(btn_geral, ["Cadastro de empresa", "Cadastro de Clientes", "Cadastro Funcionários", "Consulta CNPJ"], self)
        self.add_menu_actions_with_permission(btn_produtos, ["Produtos"], self)
        self.add_menu_actions_with_permission(btn_compras, ["Fornecedores"], self)
        self.add_menu_actions_with_permission(btn_vendas, ["Pedido de vendas"], self)
        self.add_menu_actions_with_permission(btn_financeiro, ["Recebimento de clientes", "Gerar lançamento Financeiro", "Controle de caixa (PDV)", "Conta corrente", "Classes financeiras"], self)
        self.add_menu_actions_with_permission(btn_relatorios, ["Relatório de Vendas de Produtos"], self)
        self.add_menu_actions_with_permission(btn_ferramentas, ["Configuração de estação", "Configuração do Sistema", "Adicionar Favoritos"], self)
        #self.add_menu_actions_with_permission(btn_fiscal, ["Manutenção de Nota Fiscal"], self)
        self.add_menu_actions_with_permission(self.btn_mercado_livre, ["Ver Dashboard do Mercado livre"], self)
       
        for btn in (btn_geral, btn_produtos, btn_compras, btn_vendas, btn_financeiro, btn_relatorios, btn_ferramentas, self.btn_mercado_livre):
            menu_layout.addWidget(btn)
        main_layout.addWidget(menu_frame)
        self.atualizar_visibilidade_modulos()

        # --- 2. TELA PRINCIPAL (HOME SCREEN) ---
        home_screen = QWidget()
        home_screen.setStyleSheet("background-color: #005079;")
        # CRIA O LAYOUT DA HOME SCREEN AQUI
        home_layout = QVBoxLayout(home_screen)
        home_layout.setAlignment(Qt.AlignCenter)

        # --- 3. ÁREA DE FAVORITOS (AGORA ADICIONADA AO home_layout) ---
        self.favorites_container = QFrame()
        self.favorites_container.setMaximumWidth(1100)
        self.favorites_container.setStyleSheet("""
            QFrame {
                background-color: rgba(1, 47, 74, 0.7);
                border-radius: 25px;
            }
        """)
        self.favorites_container.setMinimumHeight(100)
        favorites_main_layout = QVBoxLayout(self.favorites_container)
        favorites_main_layout.setContentsMargins(15, 15, 15, 15)
        self.favorites_layout = QHBoxLayout()
        self.favorites_layout.setSpacing(15)
        self.favorites_layout.setAlignment(Qt.AlignCenter)
        favorites_main_layout.addLayout(self.favorites_layout)
        # Adiciona o container de favoritos ao layout da home
        home_layout.addWidget(self.favorites_container)

        # --- 4. LOGO ---
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(400, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("erro logo")
        home_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
       
        # --- 5. TÍTULO E BOTÃO DE ATUALIZAR ---
        title_section_widget = QWidget()
        title_section_layout = QHBoxLayout(title_section_widget)
        title_section_layout.setContentsMargins(0,0,0,0)
        title_section_layout.setSpacing(20)
        title_section_layout.setAlignment(Qt.AlignCenter)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
       
        system_title = QLabel("MB Sistema")
        system_title.setFont(QFont("Arial", 36, QFont.Bold))
        system_title.setStyleSheet("color: white;")
        system_title.setAlignment(Qt.AlignCenter)
        text_layout.addWidget(system_title)
       
        system_subtitle = QLabel("Sistema de gerenciamento")
        system_subtitle.setFont(QFont("Arial", 26))
        system_subtitle.setStyleSheet("color: white;")
        system_subtitle.setAlignment(Qt.AlignCenter)
        text_layout.addWidget(system_subtitle)
       
        title_section_layout.addLayout(text_layout)
        
        self.btn_atualizar = QPushButton(self)
        self.btn_atualizar.setFixedSize(40, 40)
        self.btn_atualizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_atualizar.setToolTip("Atualizar dados do painel")
        refresh_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "refresh.png")
        if os.path.exists(refresh_icon_path):
            self.btn_atualizar.setIcon(QIcon(refresh_icon_path))
            self.btn_atualizar.setIconSize(QSize(24, 24))
        else:
            self.btn_atualizar.setText("🔄"); self.btn_atualizar.setFont(QFont("Arial", 16))
        self.btn_atualizar.setStyleSheet("""
            QPushButton { background-color: transparent; border: 2px solid #FFFFFF; border-radius: 20px; color: white; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
            QPushButton:pressed { background-color: rgba(255, 255, 255, 0.2); }
        """)
        self.btn_atualizar.clicked.connect(self.atualizar_contadores)
        title_section_layout.addWidget(self.btn_atualizar)
        home_layout.addWidget(title_section_widget)
       
        # --- 6. CAIXAS DE INFORMAÇÃO ---
        info_frame = QFrame()
        info_frame.setMaximumHeight(180)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(30)
        info_layout.setContentsMargins(50, 20, 50, 20)
       
        self.criar_caixa_info(info_layout, "Clientes", "user.png", self.obter_contagem_pessoas())
        self.criar_caixa_info(info_layout, "Produtos", "product.png", self.obter_contagem_produtos())
        self.criar_caixa_info(info_layout, "Vendas", "sales.png", self.obter_contagem_vendas())
        if self.tem_acesso_ecommerce:
             self.criar_caixa_info(info_layout, "ML Envios", "mercado-livre.png", self.obter_pedidos_pendentes_ml())
        home_layout.addWidget(info_frame)
       
        # --- 7. INFORMAÇÕES DO USUÁRIO E DESENVOLVEDOR ---
        user_info = QLabel(f"Usuário: {self.usuario} | Empresa: {self.empresa}")
        user_info.setFont(QFont("Arial", 14))
        user_info.setStyleSheet("color: #cccccc; margin-top: 10px;")
        user_info.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(user_info)
       
        dev_info = QLabel("Desenvolvido e programado por Marco Antônio")
        dev_info.setFont(QFont("Arial", 12, -1, True))
        dev_info.setStyleSheet("color: #cccccc; margin-top: 5px;")
        dev_info.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(dev_info)
       
        # Adiciona a tela principal (com tudo dentro) ao layout geral
        main_layout.addWidget(home_screen, 1)
       
        # --- 8. BOTÕES FLUTUANTES E FIXOS ---
        self.botao_whatsapp = QPushButton(self)
        self.btn_assistente = QPushButton("💬", self)
        self.pdv_button = QPushButton("Acesso ao\nPDV", self)
        self.logout_button = QPushButton("Sair do Sistema", self)
       
        # Configuração do Botão WhatsApp
        whatsapp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "whatsapp2.png")
        if os.path.exists(whatsapp_path):
            self.botao_whatsapp.setIcon(QIcon(whatsapp_path))
            self.botao_whatsapp.setIconSize(QSize(60, 60))
        self.botao_whatsapp.setFixedSize(80, 80)
        self.botao_whatsapp.setStyleSheet("QPushButton { background-color: #25D366; border-radius: 40px; border: 2px solid white; } QPushButton:hover { background-color: #128C7E; }")
        sombra_wpp = QGraphicsDropShadowEffect(self.botao_whatsapp); sombra_wpp.setBlurRadius(15); sombra_wpp.setColor(Qt.black); self.botao_whatsapp.setGraphicsEffect(sombra_wpp)
        self.botao_whatsapp.setCursor(QCursor(Qt.PointingHandCursor)); self.botao_whatsapp.setToolTip("Clique para ver os contatos")
        self.botao_whatsapp.clicked.connect(self.abrir_janela_contatos)
       
        # Configuração do Botão Assistente
        self.btn_assistente.setFixedSize(60, 60)
        self.btn_assistente.setStyleSheet("QPushButton { background-color: #005079; color: white; border: 2px solid white; border-radius: 30px; font-size: 24px; } QPushButton:hover { background-color: #0066a0; }")
        self.btn_assistente.setToolTip("Assistente Virtual")
        self.btn_assistente.clicked.connect(self.toggle_assistente_dock)
        
        # Integração do DockWidget do Assistente
        try:
            from assistente import ChatbotDockWidget
            self.chatbot_dock = ChatbotDockWidget(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.chatbot_dock)
            self.chatbot_dock.hide()
            self.chatbot_dock.visibilityChanged.connect(self.on_assistente_visibilidade_mudou)
            self.chatbot_dock.navegar_para_main.connect(self.navegar_para_modulo)
        except Exception as e:
            print(f"Erro ao carregar Assistente: {e}")
            self.btn_assistente.hide()
            
        # Configuração do Botão PDV
        self.pdv_button.setFixedSize(180, 80)
        self.pdv_button.setStyleSheet("QPushButton { background-color: #2E8B57; color: white; border-radius: 10px; font-weight: bold; text-align: center; padding: 5px; font-size: 18px; } QPushButton:hover { background-color: #1D6F42; }")
        pdv_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "caixa.png")
        if os.path.exists(pdv_icon_path):
            self.pdv_button.setIcon(QIcon(pdv_icon_path)); self.pdv_button.setIconSize(QSize(45, 45))
        sombra_pdv = QGraphicsDropShadowEffect(self.pdv_button); sombra_pdv.setBlurRadius(15); sombra_pdv.setColor(Qt.black); self.pdv_button.setGraphicsEffect(sombra_pdv)
        self.pdv_button.setCursor(QCursor(Qt.PointingHandCursor)); self.pdv_button.clicked.connect(self.abrir_pdv)

        # Configuração do Botão Logout
        self.logout_button.setFixedSize(180, 80)
        self.logout_button.setStyleSheet("QPushButton { background-color: #c0392b; color: white; border-radius: 10px; font-weight: bold; text-align: center; padding: 5px; font-size: 18px; } QPushButton:hover { background-color: #a93226; }")
        logout_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", "logout.png")
        if os.path.exists(logout_icon_path):
            self.logout_button.setIcon(QIcon(logout_icon_path)); self.logout_button.setIconSize(QSize(30, 30))
        sombra_logout = QGraphicsDropShadowEffect(self.logout_button); sombra_logout.setBlurRadius(15); sombra_logout.setColor(Qt.black); self.logout_button.setGraphicsEffect(sombra_logout)
        self.logout_button.setCursor(QCursor(Qt.PointingHandCursor)); self.logout_button.clicked.connect(self.handle_logout)
        
        self.setDockNestingEnabled(True)
       
        self._original_resizeEvent = self.resizeEvent
        self.resizeEvent = self._novo_resizeEvent
        
        QTimer.singleShot(0, self.posicionar_botoes_fixos)
        QTimer.singleShot(0, self.posicionar_botoes_flutuantes)

        # Atualiza a exibição inicial dos favoritos
        self.update_favorites_display()
       
        # --- 9. MAPEAMENTOS DE MÓDULOS ---
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
            "Relatório de Vendas de Produtos": os.path.join("relatorios", "relatorio_vendas_produtos.py"),
            "Configuração de estação": os.path.join("ferramentas", "configuracao_impressora.py"),
            "Configuração do Sistema": os.path.join("ferramentas", "configuracao_sistema.py"),
            "Adicionar Favoritos": os.path.join("ferramentas", "favoritos.py"),
            "Manutenção de Nota Fiscal": os.path.join("Fiscal", "nota_fiscal_main.py"),
            "Ver Dashboard do Mercado livre": os.path.join("mercado_livre", "main_final.py"),
            "PDV - Ponto de Venda": os.path.join("PDV", "PDV_principal.py")
        }
        self.action_to_class = {
            "Cadastro de empresa": "CadastroEmpresaWindow", "Cadastro de Clientes": "CadastroPessoaWindow",
            "Cadastro Funcionários": "CadastroFuncionariosWindow", "Consulta CNPJ": "ConsultaCNPJWindow",
            "Produtos": "ProdutosWindow", "Grupo de produtos": "GrupoProdutosWindow",
            "Un - unidade de medida": "UnidadeMedidaWindow", "Fornecedores": "FornecedoresWindow",
            "Clientes": "ClientesWindow", "Pedido de vendas": "PedidoVendasWindow",
            "Recebimento de clientes": "RecebimentoClientesWindow", "Gerar lançamento Financeiro": "LancamentoFinanceiroWindow",
            "Controle de caixa (PDV)": "ControleCaixaWindow", "Conta corrente": "ContaCorrenteWindow",
            "Classes financeiras": "ClassesFinanceirasWindow", "Fiscal NF-e, SAT, NFC-e": "RelatorioFiscalWindow",
            "Relatório de Vendas de Produtos": "RelatorioVendasWindow", "Configuração de estação": "ConfiguracaoImpressoraWindow",
            "Configuração do Sistema": "ConfiguracaoSistemaWindow","Adicionar Favoritos": "SeletorModulosEstilizado","Manutenção de Nota Fiscal": "NotaFiscalMainWindow", "Ver Dashboard do Mercado livre": "MercadoLivreWindow",
            "PDV - Ponto de Venda": "PDVWindow"
        }

    def resource_path(self, relative_path):
        """Obtém caminho absoluto para recurso bundado, compatível com PyInstaller."""
        try:
            # Em modo frozen (EXE), usa o diretório temporário extraído
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def aplicar_estilo_aviso(self, widget):
        """Aplica o estilo de fundo branco e botões azuis a um QMessageBox ou QInputDialog."""
        style = """
            /* Estilo para a janela */
            QDialog, QMessageBox, QInputDialog {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #c0c0c0;
                border-radius: 8px;
            }

            /* Estilo para QLabel dentro */
            QDialog QLabel, QMessageBox QLabel {
                color: #000000;
                background-color: transparent;
            }
            
            /* Estilo específico para o texto da mensagem */
            QMessageBox QLabel#qt_msgbox_label {
                color: #000000;
            }

            /* Estilo para QLineEdit em QInputDialog */
            QInputDialog QLineEdit {
                background-color: #f0f8ff;
                color: #000000;
                border: 1px solid #c0d9ec;
                border-radius: 4px;
                padding: 2px;
            }

            /* Força o estilo para TODOS os botões */
            QPushButton {
                background-color: #004766 !important;
                color: white !important;
                border: 1px solid #003555 !important;
                border-radius: 6px !important;
                padding: 6px 12px !important;
                min-width: 80px !important;
                font-weight: normal !important;
            }
            QPushButton:hover {
                background-color: #005580 !important;
                border-color: #006699 !important;
            }
            QPushButton:pressed {
                background-color: #003344 !important;
            }
            QPushButton:focus {
                outline: none !important;
                border: 2px solid #0077aa !important;
            }
        """
        widget.setStyleSheet(style)
        
        # Traduzir os botões para português
        buttons = widget.findChildren(QPushButton)
        for button in buttons:
            if button.text() == "&Yes":
                button.setText("Sim")
            elif button.text() == "&No":
                button.setText("Não")
            elif button.text() == "Yes":
                button.setText("Sim")
            elif button.text() == "No":
                button.setText("Não")
            elif button.text() == "&OK":
                button.setText("OK")
            elif button.text() == "&Cancel":
                button.setText("Cancelar")

    # Adicione este novo método dentro da classe MainWindow
    def obter_pedidos_pendentes_ml(self):
        """
        Busca o número de pedidos pendentes usando uma instância ATUALIZADA do backend do ML.
        """
        # Só executa se o módulo do ML estiver disponível no sistema.
        if ML_BACKEND_DISPONIVEL:
            try:
                # Cria uma instância NOVA do backend toda vez que a função é chamada.
                # Isso garante que ele leia as credenciais mais recentes salvas no disco.
                backend_ml_temporario = MercadoLivreBackend()
               
                # Verifica se a nova instância está configurada (ou seja, se o login foi feito).
                if backend_ml_temporario.is_configured():
                    # Se estiver logado, busca os pedidos pendentes.
                    return backend_ml_temporario.get_pedidos_pendentes()
                else:
                    # Se não estiver logado, retorna 0.
                    print("ML não configurado para obter pedidos. O usuário precisa logar.")
                    return 0
            except Exception as e:
                print(f"Erro ao criar backend temporário ou buscar pedidos pendentes do ML: {e}")
                return 0
       
        # Se o módulo do ML nem existe, retorna 0.
        return 0
    # --- NOVO MÉTODO ÚNICO PARA resizeEvent ---
    def _novo_resizeEvent(self, event):
        """Novo método centralizado para lidar com o redimensionamento da janela."""
        # Chama o comportamento original do evento
        self._original_resizeEvent(event)
       
        # Chama as funções de posicionamento
        self.posicionar_botoes_fixos()
        self.posicionar_botoes_flutuantes()

    # --- Demais Métodos da Classe (sem alterações) ---
    def handle_logout(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Confirmação')
        msg_box.setText('Você tem certeza que deseja sair?')
        msg_box.setInformativeText('Isso fechará o sistema por completo!.')
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_sim = msg_box.button(QMessageBox.Yes); btn_sim.setText('Sim')
        btn_nao = msg_box.button(QMessageBox.No); btn_nao.setText('Não')
        msg_box.setDefaultButton(btn_nao)
        self.aplicar_estilo_aviso(msg_box)
        
        resposta = msg_box.exec_()
        if resposta == QMessageBox.Yes:
            # Primeiro, fechar todas as janelas abertas
            for window in self.opened_windows[:]:  # Cria uma cópia da lista para evitar problemas durante iteração
                if window and window.isVisible():
                    try:
                        print(f"Fechando janela: {window.windowTitle()}")
                        window.close()
                    except Exception as e:
                        print(f"Erro ao fechar janela: {e}")
            
            # Limpar a lista de janelas abertas
            self.opened_windows.clear()
            
            # Parar todos os timers ativos
            if hasattr(self, 'timer_atualizacao'): 
                self.timer_atualizacao.stop()
            if hasattr(self, 'timer_syncthing'): 
                self.timer_syncthing.stop()
            if hasattr(self, 'vendas_timer_ml'): 
                self.vendas_timer_ml.stop()
            if hasattr(self, 'vendas_timer'): 
                self.vendas_timer.stop()
                
            # Fechar o syncthing se necessário
            try:
                from base.banco import fechar_syncthing
                fechar_syncthing()
            except Exception as e:
                print(f"Erro ao encerrar Syncthing: {e}")
                
            # Agora que todas as janelas filhas foram fechadas, emitir o sinal e fechar a janela principal
            self.logout_signal.emit()
            self.close()
   
    def atualizar_visibilidade_modulos(self):
        if hasattr(self, 'btn_mercado_livre'):
            self.btn_mercado_livre.setVisible(self.tem_acesso_ecommerce)
        self.atualizar_visibilidade_pdv()
    def abrir_janela_contatos(self):
        try:
            contatos_dialog = ContatosWhatsAppDialog(self)
            contatos_dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao abrir janela de contatos: {str(e)}")
    def navegar_para_modulo(self, modulo, acao):
        mapa_navegacao = {
            ("geral", "cadastro_pessoa"): "Cadastro de Clientes", ("geral", "cadastro_empresa"): "Cadastro de empresa",
            ("geral", "cadastro_funcionarios"): "Cadastro Funcionários", ("geral", "consulta_cnpj"): "Consulta CNPJ",
            ("produtos", "produtos"): "Produtos", ("pdv", "pdv_principal"): "PDV - Ponto de Venda",
            ("compras", "fornecedores"): "Fornecedores", ("vendas", "pedido_vendas"): "Pedido de vendas",
            ("financeiro", "recebimento_clientes"): "Recebimento de clientes", ("financeiro", "lancamento_financeiro"): "Gerar lançamento Financeiro",
            ("financeiro", "controle_caixa"): "Controle de caixa (PDV)", ("financeiro", "conta_corrente"): "Conta corrente",
            ("financeiro", "classes_financeiras"): "Classes financeiras", ("relatorios", "relatorio_vendas_produtos"): "Relatório de Vendas de Produtos",
            ("ferramentas", "configuracao_impressora"): "Configuração de estação", ("ferramentas", "configuracao_sistema"): "Configuração do Sistema", ("ferramentas", "Adicionar Favoritos"): "Adicionar Favoritos"
        }
        chave = (modulo, acao)
        if chave in mapa_navegacao:
            self.menu_action_triggered(mapa_navegacao[chave])

    def aplicar_estilo_aviso(self, dialog):
        # Definir a cor de fundo do diálogo para branco
        dialog.setStyleSheet("""
            QMessageBox, QDialog, QInputDialog {
                background-color: white;
            }
            QLabel {
                color: black;
                background-color: transparent;
            }
            QPushButton {
                background-color: #004766;  /* Mudança aqui */
                color: white;                /* Mudança aqui */
                padding: 5px 15px;
                border: 1px solid #003555;   /* Borda mais escura */
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005580;   /* Tom mais claro no hover */
            }
            QPushButton:pressed {
                background-color: #003344;   /* Tom mais escuro ao clicar */
            }
        """)
        
        # Traduzir os botões para português
        buttons = dialog.findChildren(QPushButton)
        for button in buttons:
            if button.text() == "&Yes":
                button.setText("Sim")
            elif button.text() == "&No":
                button.setText("Não")

    def abrir_pdv(self):
        if not self.verificar_permissao("PDV - Ponto de Venda") and self.id_funcionario:
            QMessageBox.warning(self, "Acesso Negado", "Você não tem permissão para acessar o PDV.")
            return
        # Verificar se o caixa está aberto para este usuário/estação
        if not self.caixa_esta_aberto():
            msg_box = QMessageBox(self)
            # msg_box.setIcon(QMessageBox.Question)  # REMOVA ou comente esta linha
            msg_box.setWindowTitle("Abrir Caixa")
            msg_box.setText("O caixa não está aberto. Deseja abrir agora?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            self.aplicar_estilo_aviso(msg_box)
            resposta = msg_box.exec_()
            if resposta == QMessageBox.Yes:
                input_dialog = QInputDialog(self)
                input_dialog.setWindowTitle("Abertura de Caixa")
                input_dialog.setLabelText("Informe o fundo de troco inicial:")
                input_dialog.setDoubleValue(0.0)
                input_dialog.setDoubleMinimum(0.0)
                input_dialog.setDoubleMaximum(999999.99)
                input_dialog.setDoubleDecimals(2)
                self.aplicar_estilo_aviso(input_dialog) # Isso não é suficiente para os botões
                from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox, QLineEdit
                for spin in input_dialog.findChildren((QDoubleSpinBox, QSpinBox)):
                    spin.setStyleSheet("""
                        background-color: #ffffff !important;
                        color: #000000 !important;
                        border: 1px solid #c0d9ec !important;
                        border-radius: 4px !important;
                        padding: 2px !important;
                    """)
                    le = spin.findChild(QLineEdit)
                    if le:
                        le.setStyleSheet("""
                            background-color: #ffffff !important;
                            color: #000000 !important;
                            border: 1px solid #c0d9ec !important;
                            border-radius: 4px !important;
                            padding: 2px !important;
                        """)
                
                # Adicione esta parte para forçar o estilo nos botões:
                input_dialog.setStyleSheet(input_dialog.styleSheet() + """
                    QDialogButtonBox > QPushButton {
                        background-color: #004766 !important;
                        color: white !important;
                        border: 1px solid #003555 !important;
                        border-radius: 6px !important;
                        padding: 6px 12px !important;
                        min-width: 80px !important;
                    }
                    QDialogButtonBox > QPushButton:hover {
                        background-color: #005580 !important;
                    }
                    QDialogButtonBox > QPushButton:pressed {
                        background-color: #003344 !important;
                    }
                """)

                ok = input_dialog.exec_()
                fundo_troco = input_dialog.doubleValue() if ok else 0.0 # Obtém o valor apenas se 'OK' foi clicado
                if ok:
                    self.abrir_caixa(fundo_troco)
                else:
                    return # Não abre PDV se cancelar
            else:
                return # Não abre PDV se não abrir caixa
        try:
            pdv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PDV", "PDV_principal.py")
            if not os.path.exists(pdv_path):
                QMessageBox.warning(self, "Erro", f"Módulo PDV não encontrado!")
                return
            self.opened_windows = [w for w in self.opened_windows if w.isVisible()]
            for w in self.opened_windows:
                if w.windowTitle() == "PDV - Ponto de Venda":
                    w.setWindowState(w.windowState() & ~Qt.WindowMinimized)
                    w.activateWindow()
                    return
            spec = importlib.util.spec_from_file_location("PDV_principal", pdv_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            WindowClass = getattr(module, "PDVWindow", None)
            if not WindowClass:
                QMessageBox.warning(self, "Erro", "Não foi possível iniciar o PDV!")
                return
            win = WindowClass()
            if hasattr(win, 'set_janela_principal'):
                win.set_janela_principal(self)
            if hasattr(win, 'set_credentials'):
                win.set_credentials(self.usuario, self.empresa, self.id_funcionario)
            win.setWindowTitle("PDV - Ponto de Venda")
            win.show()
            self.opened_windows.append(win)
            # Conectar o fechamento do PDV ao fechamento do caixa
            original_close = win.closeEvent
            def new_close(event):
                if self.caixa_esta_aberto():
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Fechar Caixa")
                    msg_box.setText("Deseja fechar o caixa ao sair do PDV?")
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msg_box.setDefaultButton(QMessageBox.No)
                    self.aplicar_estilo_aviso(msg_box) # Aplica o estilo
                    resposta = msg_box.exec_()
                    if resposta == QMessageBox.Yes:
                        self.fechar_caixa()
                if original_close:
                    original_close(event)
            win.closeEvent = new_close
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir o PDV: {str(e)}")

    def criar_caixa_info(self, layout_pai, titulo, nome_icone, contagem):
        wrapper = QWidget()
        wrapper.setFixedSize(200, 170)
        wrapper.setStyleSheet("background-color: transparent;")
        box_frame = QFrame(wrapper)
        box_frame.setFixedSize(180, 150)
        box_frame.move(10, 10)
        box_frame.setStyleSheet("QFrame { background-color: #00283d; border-radius: 15px; border: 2px solid transparent; }")
        box_frame.setCursor(QCursor(Qt.PointingHandCursor))
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15); sombra.setColor(QColor(0, 0, 0, 80)); sombra.setOffset(0, 3)
        box_frame.setGraphicsEffect(sombra)
        box_frame.sombra = sombra
        box_layout = QVBoxLayout(box_frame)
        box_layout.setSpacing(10)
        label_titulo = QLabel(titulo)
        label_titulo.setFont(QFont("Arial", 16, QFont.Bold)); label_titulo.setStyleSheet("color: white; background: transparent;"); label_titulo.setAlignment(Qt.AlignCenter)
        label_icone = QLabel()
        label_icone.setStyleSheet("background: transparent;")
        icone_map = {"user.png": "👥", "product.png": "📦", "sales.png": "💰"}
        icone_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img", nome_icone)
        if os.path.exists(icone_caminho):
            pixmap_icone = QPixmap(icone_caminho)
            label_icone.setPixmap(pixmap_icone.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            label_icone.setText(icone_map.get(nome_icone, "?"))
            label_icone.setFont(QFont("Arial", 36, QFont.Bold)); label_icone.setStyleSheet("color: white; background: transparent;")
        label_icone.setAlignment(Qt.AlignCenter)
        if titulo == "Vendas":
            try: valor_numerico = float(contagem); valor_formatado = f"R$ {valor_numerico:.2f}".replace('.', ',')
            except (ValueError, TypeError): valor_formatado = "R$ 0,00"
            label_contagem = QLabel(valor_formatado); label_contagem.setFont(QFont("Arial", 20, QFont.Bold))
        else:
            label_contagem = QLabel(str(contagem)); label_contagem.setFont(QFont("Arial", 24, QFont.Bold))
        label_contagem.setStyleSheet("color: white; background: transparent;"); label_contagem.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(label_titulo); box_layout.addWidget(label_icone); box_layout.addWidget(label_contagem)
        def on_click(event):
            if titulo == "Clientes": self.menu_action_triggered("Cadastro de Clientes")
            elif titulo == "Produtos": self.menu_action_triggered("Produtos")
            elif titulo == "Vendas": self.menu_action_triggered("Relatório de Vendas de Produtos")
            elif titulo == "ML Envios": self.menu_action_triggered("Ver Dashboard do Mercado livre")
        box_frame.mousePressEvent = on_click
        def on_enter(event): self.animar_caixa_info(box_frame, aumentar=True)
        def on_leave(event): self.animar_caixa_info(box_frame, aumentar=False)
        box_frame.enterEvent = on_enter; box_frame.leaveEvent = on_leave
        layout_pai.addWidget(wrapper)
        self.contadores_labels[titulo] = label_contagem
        if not hasattr(self, 'info_frames'): self.info_frames = {}
        self.info_frames[titulo] = box_frame
        return label_contagem
    def animar_caixa_info(self, caixa, aumentar=True):
        if not hasattr(caixa, '_anim_group'):
            from PyQt5.QtCore import QParallelAnimationGroup
            caixa._anim_group = QParallelAnimationGroup()
            caixa._anim_geo = QPropertyAnimation(caixa, b"geometry"); caixa._anim_geo.setDuration(200); caixa._anim_geo.setEasingCurve(QEasingCurve.OutCubic)
            caixa._anim_group.addAnimation(caixa._anim_geo)
        caixa._anim_group.stop()
        geo_atual = caixa.geometry()
        if aumentar:
            novo_width = int(180 * 1.1); novo_height = int(150 * 1.1)
            novo_x = geo_atual.x() - (novo_width - geo_atual.width()) // 2
            novo_y = geo_atual.y() - (novo_height - geo_atual.height()) // 2
            novo_x = max(0, min(novo_x, 200 - novo_width)); novo_y = max(0, min(novo_y, 170 - novo_height))
            nova_geo = QRect(novo_x, novo_y, novo_width, novo_height)
            caixa.setStyleSheet("QFrame { background-color: #003d5c; border-radius: 15px; border: none; }")
            if hasattr(caixa, 'sombra'):
                caixa.sombra.setBlurRadius(25); caixa.sombra.setOffset(0, 8); caixa.sombra.setColor(QColor(0, 0, 0, 120))
        else:
            nova_geo = QRect(10, 10, 180, 150)
            caixa.setStyleSheet("QFrame { background-color: #00283d; border-radius: 15px; border: none; }")
            if hasattr(caixa, 'sombra'):
                caixa.sombra.setBlurRadius(15); caixa.sombra.setOffset(0, 3); caixa.sombra.setColor(QColor(0, 0, 0, 80))
        caixa._anim_geo.setStartValue(geo_atual); caixa._anim_geo.setEndValue(nova_geo)
        caixa._anim_group.start()
    def animar_caixa(self, caixa, fator_escala): self.animar_caixa_info(caixa, fator_escala > 1.0)
   
    def atualizar_contadores(self):
        print("Botão clicado: Atualizando todos os contadores...")
       
        # ### NOVIDADE: Desabilita o botão e muda o cursor para 'Aguarde' ###
        if hasattr(self, 'btn_atualizar'):
            self.btn_atualizar.setEnabled(False)
        self.setCursor(QCursor(Qt.WaitCursor))
       
        # O QTimer.singleShot força a interface a se redesenhar ANTES de começar o trabalho pesado.
        # Isso garante que o cursor de "aguarde" apareça imediatamente.
        QTimer.singleShot(50, self._executar_atualizacao)
    def _executar_atualizacao(self):
        """Função auxiliar que faz o trabalho pesado da atualização."""
        try:
            # Atualiza contadores locais
            if "Clientes" in self.contadores_labels:
                self.atualizar_contador_com_animacao(self.contadores_labels["Clientes"], self.obter_contagem_pessoas())
            if "Produtos" in self.contadores_labels:
                self.atualizar_contador_com_animacao(self.contadores_labels["Produtos"], self.obter_contagem_produtos())
            if "Vendas" in self.contadores_labels:
                novo_valor = self.obter_contagem_vendas()
                label = self.contadores_labels["Vendas"]
                valor_formatado = f"R$ {novo_valor:.2f}".replace('.', ',')
                label.setText(valor_formatado)
            # Atualiza o contador do Mercado Livre
            if "ML Envios" in self.contadores_labels:
                pedidos_pendentes = self.obter_pedidos_pendentes_ml()
                self.atualizar_contador_com_animacao(self.contadores_labels["ML Envios"], pedidos_pendentes)
        except Exception as e:
            print(f"Erro ao atualizar contadores: {e}")
        finally:
            # ### NOVIDADE: Reabilita o botão e restaura o cursor ao final ###
            if hasattr(self, 'btn_atualizar'):
                self.btn_atualizar.setEnabled(True)
            self.unsetCursor()
    def forcar_atualizacao_contadores(self): QTimer.singleShot(100, self.atualizar_contadores)
    def atualizar_contador_com_animacao(self, label, novo_valor):
        texto_atual = label.text()
        if texto_atual.startswith("R$"):
            try:
                valor_atual = float(texto_atual.replace("R$", "").replace(".", "").replace(",", ".").strip())
                if abs(valor_atual - novo_valor) > 0.01:
                    estilo_original = label.styleSheet(); label.setStyleSheet("color: #00E676; font-weight: bold;")
                    valor_formatado = f"R$ {novo_valor:.2f}".replace('.', ','); label.setText(valor_formatado)
                    QTimer.singleShot(1000, lambda: label.setStyleSheet(estilo_original))
            except ValueError: label.setText(f"R$ {novo_valor:.2f}".replace('.', ','))
        else:
            valor_atual = int(texto_atual) if texto_atual.isdigit() else 0
            if valor_atual != novo_valor:
                estilo_original = label.styleSheet(); label.setStyleSheet("color: #00E676; font-weight: bold;")
                label.setText(str(novo_valor)); QTimer.singleShot(1000, lambda: label.setStyleSheet(estilo_original))
    def animar_botao(self, botao, fator_escala):
        anim_largura = QPropertyAnimation(botao, b"minimumWidth"); anim_largura.setDuration(150); anim_largura.setStartValue(botao.width()); anim_largura.setEndValue(int(80 * fator_escala)); anim_largura.setEasingCurve(QEasingCurve.OutCubic)
        anim_altura = QPropertyAnimation(botao, b"minimumHeight"); anim_altura.setDuration(150); anim_altura.setStartValue(botao.height()); anim_altura.setEndValue(int(80 * fator_escala)); anim_altura.setEasingCurve(QEasingCurve.OutCubic)
        anim_largura.start(); anim_altura.start(); botao.setIconSize(QSize(int(60 * fator_escala), int(60 * fator_escala)))
    def abrir_whatsapp(self, numero_telefone):
        try:
            numero_limpo = ''.join(filter(str.isdigit, numero_telefone)); url = QUrl(f"https://wa.me/{numero_limpo}")
            if not QDesktopServices.openUrl(url):
                import webbrowser; webbrowser.open(f"https://wa.me/{numero_limpo}")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao abrir WhatsApp: {str(e)}")
    def obter_contagem_pessoas(self):
        try: from base.banco import execute_query; result = execute_query("SELECT COUNT(*) FROM PESSOAS"); return result[0][0] if result and result[0][0] else 0
        except Exception as e: print(f"Erro ao contar pessoas: {e}"); return 0
    def obter_contagem_produtos(self):
        try: from base.banco import execute_query; result = execute_query("SELECT COUNT(*) FROM PRODUTOS"); return result[0][0] if result and result[0][0] else 0
        except Exception as e: print(f"Erro ao contar produtos: {e}"); return 0
    def obter_contagem_vendas(self):
        try:
            from datetime import date; from base.banco import execute_query
            data_atual = date.today(); conn = execute_query(); cursor = conn.cursor()
            cursor.execute("SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = 'VENDAS'")
            colunas = [col[0].strip() for col in cursor.fetchall()]
            coluna_data = next((nome for nome in ['DATA_VENDA', 'DATA_EMISSAO', 'DATA', 'DT_VENDA', 'DT_EMISSAO', 'DATA_REGISTRO'] if nome in colunas), None)
            if not coluna_data:
                cursor.execute("SELECT VALOR_TOTAL FROM VENDAS")
            else:
                query = f"SELECT VALOR_TOTAL FROM VENDAS WHERE EXTRACT(YEAR FROM {coluna_data})=? AND EXTRACT(MONTH FROM {coluna_data})=? AND EXTRACT(DAY FROM {coluna_data})=?"
                cursor.execute(query, (data_atual.year, data_atual.month, data_atual.day))
            valores = cursor.fetchall(); cursor.close(); conn.close()
            return sum(float(v[0]) for v in valores if v[0] is not None)
        except Exception as e: print(f"Erro ao obter total de vendas: {e}"); return 0.0
   
    def diagnosticar_banco(self):
        # ... (seu código de diagnóstico, sem alterações) ...
        pass
    def normalize_text(self, text):
        normalized = unicodedata.normalize('NFD', text); return ''.join(c for c in normalized if not unicodedata.combining(c))
    def load_module_dynamically(self, module_path, class_name):
        try:
            spec = importlib.util.spec_from_file_location("mod", module_path); module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module); return getattr(module, class_name, None)
        except Exception as e: print(f"Erro ao carregar dinamicamente {module_path}: {e}"); return None

    def menu_action_triggered(self, action_title):
        # --- NOVO: Verificação adicional para módulos com restrição especial ---
        modulos_com_restricao = {
            "Ver Dashboard do Mercado livre": "ACESSO_ECOMMERCE",
            "Dashboard Mercado Livre": "ACESSO_ECOMMERCE"
        }
        
        # Verifica se é um módulo com restrição especial
        if action_title in modulos_com_restricao:
            campo_permissao = modulos_com_restricao[action_title]
            if not self.verificar_permissao_especifica(campo_permissao):
                QMessageBox.warning(self, "Acesso Bloqueado", 
                                f"Seu usuário não tem permissão para acessar: {action_title}.\n\n"
                                "Entre em contato com o administrador da sua empresa para liberar o acesso.")
                return    

        # --- NOVO: Verificação para o caso especial dos favoritos ---
        if action_title == "Adicionar Favoritos":
            self.abrir_seletor_favoritos()
            return

        # O resto do método continua como antes...
        if not self.verificar_permissao(action_title) and self.id_funcionario:
            QMessageBox.warning(self, "Acesso Negado", f"Você não tem permissão para acessar o módulo: {action_title}")
            return
    
        # MELHORIA: Limpar janelas inválidas da lista antes de verificar
        self.opened_windows = [w for w in self.opened_windows if w and w.isVisible()]
        
        # Verifica se a janela já está aberta
        for w in self.opened_windows:
            try:
                if hasattr(w, 'windowTitle') and w.windowTitle() == action_title:
                    w.setWindowState(w.windowState() & ~Qt.WindowMinimized)
                    w.activateWindow()
                    w.raise_()  # Traz para frente
                    return
            except Exception as e:
                print(f"Erro ao verificar janela: {e}")
    
        if action_title not in self.action_to_py_file:
            print(f"Ação '{action_title}' não encontrada no mapeamento")
            return
    
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.action_to_py_file[action_title])
        if not os.path.exists(path):
            QMessageBox.warning(self, "Erro", f"Arquivo não encontrado: {path}")
            return
        
        cls_name = self.action_to_class.get(action_title, ''.join(c for c in self.normalize_text(action_title) if c.isalnum()) + "Window")
        
        try:
            print(f"Tentando abrir: {action_title} -> {path} -> {cls_name}")
            
            spec = importlib.util.spec_from_file_location(cls_name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            WindowClass = getattr(module, cls_name, None)
            
            if not WindowClass:
                raise ImportError(f"Classe {cls_name} não encontrada no módulo")
            
            # Cria a instância da janela
            win = WindowClass()
            
            # Configura a janela
            if hasattr(win, 'set_janela_principal'):
                win.set_janela_principal(self)
            if hasattr(win, 'set_credentials'):
                win.set_credentials(self.usuario, self.empresa, self.id_funcionario)
            
            win.setWindowTitle(action_title)
            
            # MELHORIA: Conecta o evento de fechamento ANTES de mostrar a janela
            original_close_event = getattr(win, 'closeEvent', None)
            def novo_close_event(event):
                try:
                    # Remove da lista de janelas abertas ao fechar
                    if win in self.opened_windows:
                        self.opened_windows.remove(win)
                        print(f"Janela '{action_title}' removida da lista de janelas abertas")
                    
                    # Chama o evento original se existir
                    if original_close_event:
                        original_close_event(event)
                    
                    # Atualiza contadores após fechar
                    self.atualizar_contadores()
                    
                except Exception as e:
                    print(f"Erro no closeEvent personalizado: {e}")
                    if original_close_event:
                        original_close_event(event)
            
            win.closeEvent = novo_close_event
            
            # Adiciona à lista de janelas abertas ANTES de mostrar
            self.opened_windows.append(win)
            print(f"Janela '{action_title}' adicionada à lista. Total de janelas: {len(self.opened_windows)}")
            
            # Mostra a janela
            win.show()
            win.raise_()
            win.activateWindow()
            
        except Exception as e:
            error_msg = f"Não foi possível abrir a janela '{action_title}':\n{str(e)}"
            print(f"ERRO: {error_msg}")
            QMessageBox.warning(self, "Erro de Módulo", error_msg)

    def closeEvent(self, event):
        print("Iniciando processo de fechamento da aplicação...")
        
        try:
            # 1. FECHAR TODAS AS JANELAS FILHAS PRIMEIRO
            # Pega todas as janelas filhas da aplicação
            all_widgets = QApplication.allWidgets()
            janelas_para_fechar = []
            
            for widget in all_widgets:
                # Verifica se é uma janela (não é a principal) e está visível
                if (isinstance(widget, (QMainWindow, QDialog, QWidget)) and 
                    widget != self and 
                    widget.isWindow() and 
                    widget.isVisible() and
                    hasattr(widget, 'windowTitle')):
                    
                    janelas_para_fechar.append(widget)
                    print(f"Janela encontrada para fechar: {widget.windowTitle()}")
            
            # Fecha todas as janelas encontradas
            for janela in janelas_para_fechar:
                try:
                    print(f"Fechando janela: {janela.windowTitle()}")
                    janela.close()
                    QApplication.processEvents()  # Processa eventos pendentes
                except Exception as e:
                    print(f"Erro ao fechar janela {janela}: {e}")
            
            # 2. FECHAR JANELAS DA LISTA DE CONTROLE
            if hasattr(self, 'opened_windows'):
                print(f"Fechando {len(self.opened_windows)} janelas da lista de controle...")
                for window in self.opened_windows[:]:  # Cria uma cópia da lista
                    if window and hasattr(window, 'close'):
                        try:
                            if window.isVisible():
                                print(f"Fechando janela da lista: {getattr(window, 'windowTitle', lambda: 'Sem título')()}")
                                window.close()
                            QApplication.processEvents()
                        except Exception as e:
                            print(f"Erro ao fechar janela da lista: {e}")
                
                # Limpa a lista
                self.opened_windows.clear()
            
            # 3. PARAR TODOS OS TIMERS ATIVOS
            timers_para_parar = ['timer_atualizacao', 'timer_syncthing', 'vendas_timer_ml', 'vendas_timer']
            for timer_name in timers_para_parar:
                if hasattr(self, timer_name):
                    timer = getattr(self, timer_name)
                    if timer and hasattr(timer, 'stop'):
                        try:
                            timer.stop()
                            print(f"Timer {timer_name} parado")
                        except Exception as e:
                            print(f"Erro ao parar timer {timer_name}: {e}")
            
            # 4. FECHAR DOCK DO ASSISTENTE
            if hasattr(self, 'chatbot_dock'):
                try:
                    self.chatbot_dock.close()
                    print("Dock do assistente fechado")
                except Exception as e:
                    print(f"Erro ao fechar dock do assistente: {e}")
            
            # 5. FECHAR SYNCTHING
            try:
                from base.banco import fechar_syncthing
                fechar_syncthing()
                print("Syncthing encerrado")
            except Exception as e:
                print(f"Erro ao encerrar Syncthing: {e}")
            
            # 6. PROCESSAR EVENTOS FINAIS
            QApplication.processEvents()
            
            print("Processo de fechamento concluído com sucesso")
            
        except Exception as e:
            print(f"Erro no closeEvent: {e}")
        
        # Aceita o evento de fechamento
        event.accept()

if __name__ == "__main__":
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"mbsistema.unique.id.v1")
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMessageBox, QDialog, QInputDialog {
            background-color: #ffffff;
            color: #000000;
            border-radius: 8px;
        }
        QPushButton {
            background-color: #004766;
            color: white;
            border: 1px solid #003555;
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #005580;
        }
    """)
    window = MainWindow(usuario="Marco", empresa="MB Sistemas")
    window.show()
    sys.exit(app.exec_())