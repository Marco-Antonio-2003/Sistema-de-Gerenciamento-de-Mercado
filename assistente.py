# assistente.py
import json
import requests
from datetime import datetime
import os
import sys # Adicionado para sys.frozen
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QLabel, QApplication,
                            QDockWidget, QMainWindow, QMessageBox, QFrame, 
                            QScrollArea, QSizePolicy, QGraphicsOpacityEffect # Importar QGraphicsOpacityEffect
                           )
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QTextCursor, QFont, QColor, QPalette, QTextDocument, QTextOption, QIcon # Adicionado QIcon

class AssistenteAPI(QThread):
    """Thread para fazer requisições à API sem bloquear a interface"""
    resposta_recebida = pyqtSignal(str)
    erro_ocorrido = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # ATENÇÃO: Mantenha sua chave de API segura
        self.api_key = "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"
        self.mensagem = ""
        self.historico_conversa = []
        
    def configurar_mensagem(self, mensagem, historico=[]):
        """Configura a mensagem e histórico para a próxima requisição"""
        self.mensagem = mensagem
        self.historico_conversa = historico
        
    def run(self):
        """Executa a requisição à API em thread separada"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Você é um assistente virtual do MB Sistema - Sistema de Gerenciamento. 
                    Você deve ajudar os usuários a navegar pelo sistema, explicando onde ficam as funcionalidades e como usá-las.
                    
                    O sistema possui os seguintes módulos principais:
                    
                    GERAL:
                    - Cadastro de empresa
                    - Cadastro de Clientes (PESSOAS)
                    - Cadastro Funcionários
                    - Consulta CNPJ
                    
                    PRODUTOS E SERVIÇOS:
                    - Produtos (cadastro, consulta, edição)
                    - Grupo de produtos
                    - Unidade de medida
                    
                    COMPRAS:
                    - Fornecedores
                    
                    VENDAS:
                    - Pedido de vendas
                    - Clientes
                    
                    FINANCEIRO:
                    - Recebimento de clientes
                    - Gerar lançamento Financeiro
                    - Controle de caixa (PDV)
                    - Conta corrente
                    - Classes financeiras
                    
                    RELATÓRIOS:
                    - Relatório de Vendas de Produtos
                    - Fiscal NF-e, SAT, NFC-e
                    
                    FERRAMENTAS:
                    - Configuração de estação (impressoras)
                    - Configuração do Sistema
                    
                    PDV:
                    - Acesso ao PDV (Ponto de Venda) - botão verde no canto superior esquerdo
                    
                    Sempre seja prestativo e explique passo a passo como acessar cada funcionalidade.
                    Use emojis para tornar a conversa mais amigável."""
                }
            ]
            
            historico_limitado = self.historico_conversa[-10:] if len(self.historico_conversa) > 10 else self.historico_conversa
            messages.extend(historico_limitado)
            messages.append({"role": "user", "content": self.mensagem})
            
            print(f"Enviando mensagem: {self.mensagem}")
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mbsistema.com.br",
                    "X-Title": "MB Sistema - Assistente Virtual",
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "stream": False
                }),
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            # print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0 and 'message' in data['choices'][0] and 'content' in data['choices'][0]['message']:
                    resposta = data['choices'][0]['message']['content']
                    print(f"Resposta recebida: {resposta[:100]}...")
                    self.resposta_recebida.emit(resposta)
                else:
                    print(f"Resposta inesperada da API: {data}")
                    self.erro_ocorrido.emit("Resposta inválida ou vazia da API.")
            else:
                error_msg = f"Erro na API: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data and 'message' in error_data['error']:
                        error_msg += f" - {error_data['error']['message']}"
                    else:
                         error_msg += f" - {response.text[:200]}"
                except json.JSONDecodeError:
                    error_msg += f" - {response.text[:200]}"
                except Exception as e:
                     error_msg += f" - Erro ao processar detalhes do erro: {str(e)}"
                self.erro_ocorrido.emit(error_msg)
                
        except requests.exceptions.Timeout:
            self.erro_ocorrido.emit("Tempo limite excedido ao conectar com a IA. Tente novamente.")
        except requests.exceptions.ConnectionError:
            self.erro_ocorrido.emit("Erro de conexão com a IA. Verifique sua internet.")
        except Exception as e:
            self.erro_ocorrido.emit(f"Erro inesperado na comunicação com a IA: {str(e)}")
            import traceback
            traceback.print_exc()


class MensagemWidget(QFrame):
    """Widget customizado para cada mensagem do chat"""
    def __init__(self, texto, is_user=False, hora=None):
        super().__init__()
        self.is_user = is_user
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(2)
        container_layout.setContentsMargins(0,0,0,0)
        
        self.bolha = QLabel(texto)
        self.bolha.setWordWrap(True)
        self.bolha.setTextFormat(Qt.RichText)
        self.bolha.setOpenExternalLinks(True)
        self.bolha.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if is_user:
            self.bolha.setStyleSheet("""
                QLabel {
                    background-color: #005079;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            """)
        else:
            self.bolha.setStyleSheet("""
                QLabel {
                    background-color: #2C3E50;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            """)
        # Definir largura máxima da bolha para evitar que ocupe toda a largura
        self.bolha.setMaximumWidth(400) 
        container_layout.addWidget(self.bolha)
        
        if hora is None:
            hora = datetime.now().strftime("%H:%M")
        hora_label = QLabel(hora)
        hora_label.setStyleSheet("QLabel { color: #888; font-size: 11px; padding: 0 5px; background-color: transparent; }")
        
        if is_user:
            hora_label.setAlignment(Qt.AlignRight)
        else:
            hora_label.setAlignment(Qt.AlignLeft)
        container_layout.addWidget(hora_label)
        
        if is_user:
            layout.addStretch(1)
            layout.addWidget(container)
        else:
            layout.addWidget(container)
            layout.addStretch(1)
            
        self.setLayout(layout)
        # **AJUSTE KeyboardInterrupt**: Simplificar setStyleSheet aqui pode ajudar
        # self.setStyleSheet("QFrame { background-color: transparent; border: none; }") 
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)


class ChatWidget(QWidget):
    """Widget principal do chat"""
    navegar_para = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.historico_conversa = []
        self.api_thread = AssistenteAPI()
        self.api_thread.resposta_recebida.connect(self.processar_resposta_api)
        self.api_thread.erro_ocorrido.connect(self.processar_erro_api)
        self.mensagens_widgets = []
        self.digitando_widget = None
        
        self.inicializar_ui()
        # **AJUSTE KeyboardInterrupt**: Chamar carregamento com delay para UI renderizar
        QTimer.singleShot(100, self.carregar_historico) 
        
    def inicializar_ui(self):
        """Configurar a interface do chat"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { background-color: #1a1a1a; border: none; }
            QScrollBar:vertical { background-color: #2a2a2a; width: 8px; border-radius: 4px; margin: 0; }
            QScrollBar::handle:vertical { background-color: #555; border-radius: 4px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background-color: #666; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; border: none; background: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.mensagens_container = QWidget()
        self.mensagens_container.setStyleSheet("background-color: #1a1a1a;")
        self.mensagens_layout = QVBoxLayout(self.mensagens_container)
        self.mensagens_layout.setSpacing(10)
        self.mensagens_layout.setContentsMargins(10, 10, 10, 10)
        self.mensagens_layout.addStretch(1)
        
        self.scroll_area.setWidget(self.mensagens_container)
        layout.addWidget(self.scroll_area, 1)
        
        input_container = QFrame()
        input_container.setStyleSheet("QFrame { background-color: #272525; padding: 10px; border-top: 1px solid #333; min-height: 70px; max-height: 150px; }")
        input_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(10)
        
        self.entrada_texto = QLineEdit()
        self.entrada_texto.setPlaceholderText("Digite sua mensagem...")
        self.entrada_texto.setStyleSheet("""
            QLineEdit { padding: 12px 20px; border: 2px solid #444; border-radius: 25px; font-size: 14px; background-color: #1a1a1a; color: white; font-family: 'Segoe UI', Arial, sans-serif; }
            QLineEdit:focus { border-color: #005079; outline: none; }
        """)
        self.entrada_texto.returnPressed.connect(self.processar_mensagem)
        self.entrada_texto.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.btn_enviar = QPushButton("➤")
        self.btn_enviar.setFixedSize(50, 50)
        self.btn_enviar.setStyleSheet("""
            QPushButton { background-color: #005079; color: white; border: none; border-radius: 25px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background-color: #0066a0; }
            QPushButton:disabled { background-color: #003d5c; color: #888; }
        """)
        self.btn_enviar.clicked.connect(self.processar_mensagem)
        
        input_layout.addWidget(self.entrada_texto)
        input_layout.addWidget(self.btn_enviar)
        layout.addWidget(input_container)
        
        sugestoes_frame = QFrame()
        sugestoes_frame.setStyleSheet("QFrame { background-color: #1a1a1a; padding: 8px; border-top: 1px solid #333; max-height: 50px; }")
        sugestoes_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sugestoes_layout = QHBoxLayout(sugestoes_frame)
        sugestoes_layout.setSpacing(8)
        sugestoes_layout.setContentsMargins(5, 0, 5, 0)
        
        sugestoes = ["📋 Cadastrar cliente", "🛒 Acessar PDV", "📊 Relatórios"]
        for sugestao in sugestoes:
            btn = QPushButton(sugestao)
            btn.setStyleSheet("""
                QPushButton { background-color: #2C3E50; color: white; border: none; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-family: 'Segoe UI', Arial, sans-serif; }
                QPushButton:hover { background-color: #34495E; }
            """)
            btn.clicked.connect(lambda checked, s=sugestao: self.usar_sugestao(s.split(' ', 1)[1]))
            sugestoes_layout.addWidget(btn)
        sugestoes_layout.addStretch()
        layout.addWidget(sugestoes_frame)

    def _adicionar_widget_mensagem(self, widget):
        """Adiciona um widget de mensagem ao layout, antes do stretch."""
        self.mensagens_layout.insertWidget(self.mensagens_layout.count() - 1, widget)
        self.mensagens_widgets.append(widget)

    def adicionar_mensagem_bot(self, texto):
        """Adicionar mensagem do bot ao chat"""
        texto_html = texto.replace('\n', '<br>')
        mensagem_widget = MensagemWidget(texto_html, is_user=False)
        self._adicionar_widget_mensagem(mensagem_widget)
        self.animar_mensagem(mensagem_widget)
        QTimer.singleShot(50, self.rolar_para_fim) 
        
    def adicionar_mensagem_usuario(self, texto):
        """Adicionar mensagem do usuário ao chat"""
        mensagem_widget = MensagemWidget(texto, is_user=True)
        self._adicionar_widget_mensagem(mensagem_widget)
        self.historico_conversa.append({"role": "user", "content": texto})
        self.animar_mensagem(mensagem_widget)
        QTimer.singleShot(50, self.rolar_para_fim)
        
    def animar_mensagem(self, widget):
        """Animar a entrada de uma nova mensagem"""
        try:
            if widget.graphicsEffect():
                widget.setGraphicsEffect(None)
        except RuntimeError: 
            return
            
        widget.show()
        opacity_effect = QGraphicsOpacityEffect(widget) 
        widget.setGraphicsEffect(opacity_effect)
        animation = QPropertyAnimation(opacity_effect, b"opacity", widget) 
        animation.setDuration(300)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.finished.connect(animation.deleteLater) 
        animation.start(QPropertyAnimation.DeleteWhenStopped)
        
    def mostrar_digitando(self):
        """Mostra indicador de digitação"""
        if self.digitando_widget is None:
            self.digitando_widget = MensagemWidget("<i>Digitando...</i> ✍️", is_user=False)
            self._adicionar_widget_mensagem(self.digitando_widget)
            self.animar_mensagem(self.digitando_widget)
            QTimer.singleShot(50, self.rolar_para_fim)
        
    def remover_digitando(self):
        """Remove o indicador de digitação"""
        if self.digitando_widget:
            self.mensagens_layout.removeWidget(self.digitando_widget)
            if self.digitando_widget in self.mensagens_widgets:
                 self.mensagens_widgets.remove(self.digitando_widget)
            self.digitando_widget.deleteLater()
            self.digitando_widget = None
    
    def rolar_para_fim(self):
        """Rolar o chat para o fim"""
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()))
        
    def usar_sugestao(self, texto):
        """Usar uma sugestão rápida"""
        self.entrada_texto.setText(texto)
        self.processar_mensagem()
        
    def processar_mensagem(self):
        """Processar a mensagem do usuário"""
        mensagem = self.entrada_texto.text().strip()
        if not mensagem or self.api_thread.isRunning(): 
            return
            
        self.adicionar_mensagem_usuario(mensagem)
        self.entrada_texto.clear()
        self.btn_enviar.setEnabled(False)
        self.entrada_texto.setEnabled(False)
        self.mostrar_digitando()
        self.api_thread.configurar_mensagem(mensagem, self.historico_conversa)
        self.api_thread.start()
        
    @pyqtSlot(str)
    def processar_resposta_api(self, resposta):
        """Processa a resposta recebida da API"""
        self.remover_digitando()
        self.adicionar_mensagem_bot(resposta)
        self.historico_conversa.append({"role": "assistant", "content": resposta})
        self.salvar_historico()
        self.btn_enviar.setEnabled(True)
        self.entrada_texto.setEnabled(True)
        self.entrada_texto.setFocus()
        self.processar_comandos_navegacao(resposta)
        
    @pyqtSlot(str)
    def processar_erro_api(self, erro):
        """Processa erros da API"""
        self.remover_digitando()
        self.adicionar_mensagem_bot(f"😔 Desculpe, ocorreu um erro:\n\n{erro}\n\nPor favor, tente novamente mais tarde ou verifique sua conexão.")
        self.btn_enviar.setEnabled(True)
        self.entrada_texto.setEnabled(True)
        self.entrada_texto.setFocus()
        
    def processar_comandos_navegacao(self, resposta):
        """Verifica se a resposta contém comandos para navegar no sistema"""
        navegacao = {
            "cadastro de cliente": ("geral", "cadastro_pessoa"),
            "cadastrar cliente": ("geral", "cadastro_pessoa"),
            "cadastro de produto": ("produtos", "produtos"),
            "cadastrar produto": ("produtos", "produtos"),
            "pdv": ("pdv", "pdv_principal"),
            "ponto de venda": ("pdv", "pdv_principal"),
            "recebimento": ("financeiro", "recebimento_clientes"),
            "relatório de vendas": ("relatorios", "relatorio_vendas"),
            "configuração": ("ferramentas", "configuracao_sistema"),
        }
        resposta_lower = resposta.lower()
        for palavra_chave, (modulo, acao) in navegacao.items():
            import re
            if re.search(r'\b' + re.escape(palavra_chave) + r'\b', resposta_lower):
                print(f"Comando de navegação detectado: {palavra_chave} -> {modulo}, {acao}")
                self.navegar_para.emit(modulo, acao)
                break 
        
    def limpar_historico(self):
        """Limpar o histórico da conversa"""
        resposta = QMessageBox.question(self, "Limpar Conversa", 
                                        "Deseja limpar todo o histórico da conversa? Esta ação não pode ser desfeita.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resposta == QMessageBox.Yes:
            while self.mensagens_layout.count() > 1:
                item = self.mensagens_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.mensagens_widgets.clear()
            self.historico_conversa = []
            self.salvar_historico()
            self.adicionar_mensagem_bot("Conversa limpa! 🔄\n\nComo posso ajudá-lo agora?")
            
    def get_historico_path(self):
        """Retorna o caminho do arquivo de histórico"""
        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_path, "assistente_historico.json")

    def salvar_historico(self):
        """Salvar histórico da conversa em arquivo JSON"""
        try:
            historico_path = self.get_historico_path()
            # Salvar apenas as últimas 50 mensagens
            historico_salvar = self.historico_conversa[-50:]
            with open(historico_path, 'w', encoding='utf-8') as f:
                json.dump({"ultima_atualizacao": datetime.now().isoformat(), "conversas": historico_salvar}, 
                          f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico do assistente: {e}")
            
    def carregar_historico(self):
        """Carregar histórico da conversa do arquivo JSON"""
        historico_carregado = False
        try:
            historico_path = self.get_historico_path()
            if os.path.exists(historico_path):
                with open(historico_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # **AJUSTE KeyboardInterrupt: Limitar mensagens carregadas inicialmente**
                    historico_completo = data.get("conversas", [])
                    self.historico_conversa = historico_completo # Manter histórico completo na memória
                    historico_para_exibir = historico_completo[-20:] # Carregar apenas as últimas 20
                
                # Limpar widgets existentes (exceto o stretch)
                while self.mensagens_layout.count() > 1: 
                    item = self.mensagens_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                self.mensagens_widgets.clear()
                        
                # Adicionar mensagens limitadas
                for i, msg in enumerate(historico_para_exibir):
                    texto = msg.get('content', '')
                    if msg.get('role') == 'user':
                        # Não animar mensagens do histórico
                        mensagem_widget = MensagemWidget(texto, is_user=True)
                        self._adicionar_widget_mensagem(mensagem_widget)
                    elif msg.get('role') == 'assistant':
                        texto_html = texto.replace('\n', '<br>')
                        mensagem_widget = MensagemWidget(texto_html, is_user=False)
                        self._adicionar_widget_mensagem(mensagem_widget)
                    
                    # **AJUSTE KeyboardInterrupt: Processar eventos periodicamente**
                    if i % 5 == 0: # Processar a cada 5 mensagens
                        QApplication.processEvents()
                
                if historico_para_exibir:
                    QTimer.singleShot(100, self.rolar_para_fim) # Rolar após carregar
                    historico_carregado = True
                        
        except FileNotFoundError:
            print("Arquivo de histórico não encontrado. Iniciando novo histórico.")
            self.historico_conversa = []
        except Exception as e:
            print(f"Erro ao carregar histórico do assistente: {e}")
            self.historico_conversa = []

        if not historico_carregado:
             # Adiciona mensagem de boas vindas se não houver histórico
             self.adicionar_mensagem_bot(
                "Olá! 👋 Bem-vindo ao MB Sistema!\n\n"
                "Sou seu assistente virtual e estou aqui para ajudá-lo a navegar pelo sistema.\n\n"
                "Como posso ajudá-lo hoje?"
             )


class ChatbotAssistente(QWidget):
    """Widget principal do assistente com cabeçalho"""
    navegar_para = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        
    def inicializar_ui(self):
        """Configurar a interface completa"""
        layout = QVBoxLayout(self) 
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background-color: #005079; padding: 0; border: none; min-height: 40px; max-height: 40px; }")
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 5, 10, 5) 
        
        header = QLabel("🤖 Assistente Virtual MB")
        header.setStyleSheet("QLabel { color: white; font-size: 16px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif; background-color: transparent; }")
        header_layout.addWidget(header, 1) 
        
        btn_limpar = QPushButton("🗑️")
        btn_limpar.setToolTip("Limpar conversa")
        btn_limpar.setFixedSize(30, 30)
        btn_limpar.setCursor(Qt.PointingHandCursor)
        btn_limpar.setStyleSheet("""
            QPushButton { background-color: transparent; color: white; border: none; font-size: 18px; padding: 0px; border-radius: 15px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
            QPushButton:pressed { background-color: rgba(255, 255, 255, 0.1); }
        """)
        header_layout.addWidget(btn_limpar)
        layout.addWidget(header_frame)
        
        self.chat_widget = ChatWidget()
        btn_limpar.clicked.connect(self.chat_widget.limpar_historico)
        self.chat_widget.navegar_para.connect(self.navegar_para) 
        layout.addWidget(self.chat_widget, 1) 


class ChatbotDockWidget(QDockWidget):
    """Widget dock para o chatbot"""
    navegar_para_main = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__("Assistente Virtual", parent)
        self.chatbot_widget_interno = ChatbotAssistente()
        self.setWidget(self.chatbot_widget_interno)
        self.chatbot_widget_interno.navegar_para.connect(self.navegar_para_main.emit)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setMinimumWidth(350)
        self.setMaximumWidth(600)
        self.setStyleSheet("""
            QDockWidget { border: 1px solid #005079; }
            QDockWidget::title { background-color: #005079; color: white; padding: 8px; text-align: left; font-weight: bold; }
            QDockWidget::close-button, QDockWidget::float-button { background-color: transparent; border: none; padding: 2px; border-radius: 4px; }
            QDockWidget::close-button:hover, QDockWidget::float-button:hover { background-color: rgba(255, 255, 255, 0.2); }
            QDockWidget::close-button:pressed, QDockWidget::float-button:pressed { background-color: rgba(255, 255, 255, 0.1); }
        """)


# Funções para integração com o sistema principal
def adicionar_assistente_ao_sistema(main_window):
    """Adiciona o assistente ao sistema principal (MainWindow)"""
    from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QCursor, QIcon, QColor
    
    if hasattr(main_window, 'chatbot_dock') and main_window.chatbot_dock is not None:
        print("Assistente já adicionado.")
        return

    main_window.btn_assistente = QPushButton("💬", main_window) 
    main_window.btn_assistente.setFixedSize(70, 70) 
    main_window.btn_assistente.setStyleSheet("""
        QPushButton { background-color: #005079; color: white; border: 2px solid white; border-radius: 35px; font-size: 28px; }
        QPushButton:hover { background-color: #0066a0; }
        QPushButton:pressed { background-color: #003d5c; }
    """)
    
    try:
        sombra = QGraphicsDropShadowEffect(main_window.btn_assistente)
        sombra.setBlurRadius(15)
        sombra.setColor(QColor(0, 0, 0, 100)) 
        sombra.setOffset(2, 2)
        main_window.btn_assistente.setGraphicsEffect(sombra)
    except Exception as e:
        print(f"Erro ao aplicar sombra no botão assistente: {e}")
    
    main_window.btn_assistente.setCursor(QCursor(Qt.PointingHandCursor))
    main_window.btn_assistente.setToolTip("Abrir/Fechar Assistente Virtual")
    
    main_window.chatbot_dock = ChatbotDockWidget(main_window) 
    main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.chatbot_dock)
    main_window.chatbot_dock.hide()  
    
    main_window.chatbot_dock.navegar_para_main.connect(lambda m, a: navegar_para_modulo(main_window, m, a))
    main_window.btn_assistente.clicked.connect(lambda: toggle_assistente(main_window))
    
    main_window._original_resizeEvent = getattr(main_window, 'resizeEvent', None)

    def novo_resize_event(event):
        if main_window._original_resizeEvent:
            main_window._original_resizeEvent(event)
        offset_y = 30
        if hasattr(main_window, 'botao_whatsapp') and main_window.botao_whatsapp.isVisible():
             offset_y += main_window.botao_whatsapp.height() + 15
        if hasattr(main_window, 'btn_assistente'): 
            main_window.btn_assistente.move(main_window.width() - main_window.btn_assistente.width() - 30, 
                                            main_window.height() - main_window.btn_assistente.height() - offset_y)
            main_window.btn_assistente.raise_()
    
    main_window.resizeEvent = novo_resize_event
    QTimer.singleShot(0, lambda: novo_resize_event(None)) 
    main_window.btn_assistente.raise_()
    main_window.btn_assistente.show() 

def toggle_assistente(main_window):
    """Mostrar/ocultar o assistente dock widget"""
    if not hasattr(main_window, 'chatbot_dock') or main_window.chatbot_dock is None:
        print("Erro: Dock do assistente não encontrado.")
        return
    if main_window.chatbot_dock.isVisible():
        main_window.chatbot_dock.hide()
    else:
        main_window.chatbot_dock.show()
        try:
            QTimer.singleShot(100, lambda: main_window.chatbot_dock.chatbot_widget_interno.chat_widget.entrada_texto.setFocus())
        except AttributeError:
            print("Aviso: Não foi possível focar no campo de entrada do chat.")

def navegar_para_modulo(main_window, modulo, acao):
    """Tenta navegar para um módulo/ação específico do sistema principal"""
    print(f"Tentando navegar para: Módulo='{modulo}', Ação='{acao}'")
    mapa_navegacao = {
        ("geral", "cadastro_pessoa"): "Cadastro de Clientes",
        ("geral", "cadastro_empresa"): "Cadastro de empresa",
        ("geral", "cadastro_funcionario"): "Cadastro Funcionários",
        ("geral", "consulta_cnpj"): "Consulta CNPJ",
        ("produtos", "produtos"): "Produtos",
        ("produtos", "grupo_produtos"): "Grupo de produtos", 
        ("produtos", "unidade_medida"): "Unidade de medida", 
        ("compras", "fornecedores"): "Fornecedores",
        ("vendas", "pedido_vendas"): "Pedido de vendas",
        ("vendas", "clientes"): "Cadastro de Clientes", 
        ("financeiro", "recebimento_clientes"): "Recebimento de clientes",
        ("financeiro", "gerar_lancamento_financeiro"): "Gerar lançamento Financeiro",
        ("financeiro", "controle_caixa_pdv"): "Controle de caixa (PDV)",
        ("financeiro", "conta_corrente"): "Conta corrente",
        ("financeiro", "classes_financeiras"): "Classes financeiras",
        ("relatorios", "relatorio_vendas"): "Relatório de Vendas de Produtos", 
        ("relatorios", "relatorio_vendas_produtos"): "Relatório de Vendas de Produtos",
        ("relatorios", "fiscal_nf_e_sat_nfc_e"): "Fiscal NF-e, SAT, NFC-e", 
        ("ferramentas", "configuracao_estacao"): "Configuração de estação", 
        ("ferramentas", "configuracao_sistema"): "Configuração do Sistema",
        ("pdv", "pdv_principal"): "PDV - Ponto de Venda", 
    }
    chave = (str(modulo).lower(), str(acao).lower())
    action_title = mapa_navegacao.get(chave)
    if action_title:
        if hasattr(main_window, 'menu_action_triggered') and callable(main_window.menu_action_triggered):
            print(f"Disparando ação do menu: '{action_title}'")
            main_window.menu_action_triggered(action_title)
        else:
            print(f"Erro: Método 'menu_action_triggered' não encontrado ou não chamável na MainWindow.")
            QMessageBox.warning(main_window, "Navegação Falhou", f"Não foi possível acionar a função '{action_title}'. Verifique a integração.")
    elif chave == ("pdv", "pdv_principal"):
         if hasattr(main_window, 'abrir_pdv') and callable(main_window.abrir_pdv):
             print("Acionando função específica para abrir PDV.")
             main_window.abrir_pdv()
         elif hasattr(main_window, 'pdv_button') and hasattr(main_window.pdv_button, 'click'):
             print("Simulando clique no botão PDV.")
             main_window.pdv_button.click()
         else:
             print("Erro: Não foi possível encontrar método ou botão para abrir o PDV.")
             QMessageBox.warning(main_window, "Navegação Falhou", "Não foi possível abrir o PDV automaticamente.")
    else:
        print(f"Aviso: Nenhuma ação de menu correspondente encontrada para {chave}. Mapa: {mapa_navegacao.keys()}")


