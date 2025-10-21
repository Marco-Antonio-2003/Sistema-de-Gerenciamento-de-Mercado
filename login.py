import sys
import os
import time
import shutil  # Para operações de arquivo (backup)
import subprocess  # Para executar o script de atualização
import filecmp  # Para comparar arquivos

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                          QHBoxLayout, QPushButton, QLabel, QLineEdit, QDialog,
                          QMessageBox, QFrame, QProgressBar, QSplashScreen, QProgressDialog)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QLinearGradient, QMovie
from PyQt5.QtCore import Qt, QSettings, QSize, QTimer, QThread, pyqtSignal
from principal import MainWindow
from base.banco import iniciar_syncthing_se_necessario, validar_codigo_licenca, validar_login, verificar_tabela_usuarios, obter_id_usuario

Versao = "Versão: v0.1.5.3.3"

# --- INÍCIO DA SEÇÃO DE ATUALIZAÇÃO ---
def verificar_e_aplicar_atualizacao():
    """
    Verifica e aplica uma atualização de forma mais robusta.
    """
    try:
        app_dir = os.path.dirname(sys.executable)
        current_exe = sys.executable
        new_exe_path = os.path.join(app_dir, 'atualizacao', 'mbsistema.exe')

        # Verificar se existe atualização pendente
        if not os.path.exists(new_exe_path):
            return False

        # Verificar se o arquivo é diferente
        try:
            if os.path.getsize(current_exe) == os.path.getsize(new_exe_path):
                # Tamanho igual, verificar conteúdo
                import hashlib
                def file_hash(filepath):
                    hash_md5 = hashlib.md5()
                    with open(filepath, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    return hash_md5.hexdigest()
                
                if file_hash(current_exe) == file_hash(new_exe_path):
                    # Arquivos idênticos, limpar atualização
                    try:
                        os.remove(new_exe_path)
                        # Limpar pasta se estiver vazia
                        update_dir = os.path.dirname(new_exe_path)
                        if not os.listdir(update_dir):
                            os.rmdir(update_dir)
                    except:
                        pass
                    return False
        except Exception as e:
            print(f"Erro ao comparar arquivos: {e}")

        # Perguntar ao usuário
        confirm_reply = QMessageBox.question(
            None, 
            'Atualização Disponível',
            "Uma nova versão do sistema está pronta para ser instalada.\n\nDeseja instalar agora? O sistema será reiniciado.",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.Yes
        )

        if confirm_reply == QMessageBox.No:
            return False

        # Criar script de atualização
        from atualizador import criar_script_atualizacao
        script_path = criar_script_atualizacao(current_exe, new_exe_path)
        
        if script_path:
            # Executar script
            subprocess.Popen(f'"{script_path}"', shell=True, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return True
        else:
            QMessageBox.critical(None, "Erro", "Falha ao criar script de atualização.")
            return False

    except Exception as e:
        print(f"Erro na verificação de atualização: {e}")
        return False
    
# --- FIM DA SEÇÃO DE ATUALIZAÇÃO ---


class LoadingWorker(QThread):
    """Thread para executar tarefas de inicialização em background"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, task_type="startup"):
        super().__init__()
        self.task_type = task_type
    
    def run(self):
        """Executa as tarefas de inicialização reais em segundo plano."""
        try:
            # Tarefa 1: Iniciar o Syncthing
            self.status.emit("Iniciando serviços de sincronização...")
            # Importamos aqui dentro para manter a thread isolada
            from base.banco import iniciar_syncthing_se_necessario
            iniciar_syncthing_se_necessario()
            time.sleep(1) # Uma pequena pausa para garantir que o serviço subiu
            self.progress.emit(25)

            # Tarefa 2: Verificar o banco de dados
            self.status.emit("Verificando estrutura do banco de dados...")
            from base.banco import verificar_tabela_usuarios
            verificar_tabela_usuarios()
            self.progress.emit(50)

            # Tarefa 3: Limpar arquivos temporários/conflito
            self.status.emit("Realizando manutenção de arquivos...")
            from base.banco import limpar_arquivos_conflito
            limpar_arquivos_conflito()
            self.progress.emit(75)
            
            # Tarefa 4: Preparando para finalizar
            self.status.emit("Finalizando...")
            time.sleep(0.5) # Meio segundo para o usuário ver a última mensagem
            self.progress.emit(100)

            # CORREÇÃO: Linha incompleta corrigida
            self.finished.emit()

        except Exception as e:
            print(f"Erro durante a inicialização: {e}")
            # Se o erro foi apenas um aviso, pode emitir um status mais amigável:
            self.status.emit("Inicialização concluída com avisos.")
            self.progress.emit(100)
            time.sleep(2)
            self.finished.emit()
    
    def startup_tasks(self):
        """Tarefas de inicialização do programa"""
        # ### MUDANÇA: Reduzimos os tempos de espera (msleep) drasticamente ###
        tasks = [
            ("Carregando módulos...", 150),  # Era 1000
            ("Verificando banco de dados...", 200), # Era 1500
            ("Iniciando serviços...", 250), # Era 2000
            ("Preparando interface...", 150), # Era 1000
            ("Finalizando...", 50)     # Era 500
        ]
        
        progress_step = 100 // len(tasks)
        current_progress = 0
        
        for task_name, delay_ms in tasks:
            self.status.emit(task_name)
            self.msleep(delay_ms)  # Agora a simulação é muito mais rápida
            current_progress += progress_step
            self.progress.emit(min(current_progress, 100))
        
        self.progress.emit(100)
        self.finished.emit()

class AtualizacaoWorker(QThread):
    """Thread para executar atualização em background"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(str)  # Mensagem de resultado
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            # Importar aqui para evitar dependência circular
            from atualizador import executar_atualizacao
            
            def progress_callback(progresso):
                self.progress.emit(progresso)
                
            def status_callback(status):
                self.status.emit(status)
            
            resultado = executar_atualizacao(progress_callback, status_callback)
            self.finished.emit(resultado)
            
        except Exception as e:
            self.finished.emit(f"Erro na atualização: {str(e)}")

class SplashScreen(QWidget):
    """Tela de carregamento customizada"""
    def __init__(self, task_type="startup"):
        super().__init__()
        self.task_type = task_type
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 350)
        
        # Centralizar na tela
        self.center_on_screen()
        
        # Configurar UI
        self.setup_ui()
        
        # Worker thread para tarefas
        self.worker = LoadingWorker(task_type)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.on_loading_finished)
    
    def center_on_screen(self):
        """Centraliza a janela na tela"""
        screen_geometry = QApplication.desktop().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """Configura a interface da tela de carregamento"""
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo/Título
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Título principal
        main_title = "MB SISTEMA"
        subtitle = "Iniciando Sistema..."
        
        self.main_label = QLabel(main_title)
        self.main_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.main_label.setStyleSheet("color: #ffffff; background: transparent;")
        self.main_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.main_label)
        
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setFont(QFont("Arial", 12))
        self.subtitle_label.setStyleSheet("color: #e0e0e0; background: transparent;")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Status do carregamento
        self.status_label = QLabel("Inicializando...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #ffffff; background: transparent;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.1);
                height: 20px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #39c0ed, stop:1 #2fbce9);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Versão
        version_label = QLabel(Versao)
        version_label.setFont(QFont("Arial", 8))
        version_label.setStyleSheet("color: #a0a0a0; background: transparent;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        self.setLayout(layout)
    
    def paintEvent(self, event):
        """Desenha o fundo da splash screen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fundo com gradiente
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#1e3c72"))
        gradient.setColorAt(0.5, QColor("#2a5298"))
        gradient.setColorAt(1, QColor("#1e3c72"))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)
        
        # Borda sutil
        border_color = QColor("#ffffff")
        border_color.setAlpha(30)
        painter.setPen(border_color)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 15, 15)
    
    def start_loading(self):
        """Inicia o processo de carregamento"""
        self.worker.start()
    
    def update_progress(self, value):
        """Atualiza a barra de progresso"""
        self.progress_bar.setValue(value)
    
    def update_status(self, status):
        """Atualiza o texto de status"""
        self.status_label.setText(status)
    
    def on_loading_finished(self):
        """Chamado quando o carregamento termina"""
        QTimer.singleShot(500, self.close)  # Pequena pausa antes de fechar

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MB Sistema - Login")
        self.setFixedSize(700, 500)
        
        # Flag para controle de login bem-sucedido
        self.login_successful = False
        
        # Centralizar a janela na tela
        self.center_on_screen()
        
        # Configurações para salvar dados de usuário
        self.settings = QSettings("MBSistema", "Login")

        # Configurar a interface
        self.initUI()
        
        # Verificar e iniciar Syncthing (já foi chamado antes da janela de login na função main)
        # self.verificar_e_iniciar_syncthing()

        # Carregar o usuário e empresa salvos, se existirem
        self.carregar_dados_salvos()
    
    def verificar_e_iniciar_syncthing(self):
        """Verifica e tenta iniciar o Syncthing, com tentativas periódicas"""
        try:
            if self.tentativas_syncthing >= self.max_tentativas:
                print(f"Atingido número máximo de tentativas ({self.max_tentativas}) para iniciar o Syncthing")
                return
                
            self.tentativas_syncthing += 1
            print(f"Tentativa {self.tentativas_syncthing} de iniciar o Syncthing")
            
            from base.banco import iniciar_syncthing_se_necessario
            sucesso = iniciar_syncthing_se_necessario()
            
            if sucesso:
                self.syncthing_iniciado = True
                print("Syncthing iniciado com sucesso!")
            else:
                # Agendar nova tentativa após 3 segundos
                QTimer.singleShot(3000, self.verificar_e_iniciar_syncthing)
                print(f"Falha ao iniciar Syncthing. Tentando novamente em 3 segundos... ({self.tentativas_syncthing}/{self.max_tentativas})")
        except Exception as e:
            print(f"Erro ao verificar/iniciar Syncthing: {e}")
            # Mesmo com erro, tentar novamente
            QTimer.singleShot(3000, self.verificar_e_iniciar_syncthing)

    def inicializar_bd(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        try:
            verificar_tabela_usuarios()
            
            # Limpar arquivos de conflito ao iniciar
            try:
                from base.banco import limpar_arquivos_conflito
                limpar_arquivos_conflito()
            except Exception as e:
                print(f"Aviso: Erro ao limpar arquivos de conflito: {e}")
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
            
        # Desenhar o painel de login com gradiente semitransparente
        panel_color = QColor("#6b809b")
        panel_color.setAlpha(200)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        
        top_color = QColor("#6b809b")
        top_color.setAlpha(210)
        
        bottom_color = QColor("#6b809b")
        bottom_color.setAlpha(190)
        
        gradient.setColorAt(0, top_color)
        gradient.setColorAt(1, bottom_color)
        
        # Determinar tamanho e posição do painel
        panel_width = 400
        panel_height = 350
        panel_x = (self.width() - panel_width) // 2
        panel_y = (self.height() - panel_height) // 2 + 30
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(panel_x, panel_y, panel_width, panel_height, 10, 10)
    
    def initUI(self):
        # Widget central transparente
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 25, 0, 0)
        
        # Container para centralizar o form
        form_container = QWidget()
        form_container.setAttribute(Qt.WA_TranslucentBackground)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 15, 30, 30)
        form_layout.setSpacing(10)
        
        # Título do sistema
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignHCenter)
        title_layout.setContentsMargins(0, 0, 0, 5)
        
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
        
        main_layout.addStretch(0)
        main_layout.addLayout(title_layout)
        
        form_layout.addSpacing(10)
        
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
        
        form_layout.addSpacing(5)
        
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
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #2fbce9;
            }
            QPushButton:pressed {
                background-color: #25a7d3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)

        # Botão Verificar Atualização
        self.atualizar_button = QPushButton("VERIFICAR ATUALIZAÇÃO")
        self.atualizar_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.atualizar_button.setCursor(Qt.PointingHandCursor)
        self.atualizar_button.clicked.connect(self.verificar_atualizacao)
        form_layout.addWidget(self.atualizar_button)
        
        # Centralizar o formulário na janela
        container_layout = QHBoxLayout()
        container_layout.addStretch(1)
        container_layout.addWidget(form_container)
        container_layout.addStretch(1)
        main_layout.addLayout(container_layout)
        
        # Rótulo de versão no canto inferior direito
        versao_layout = QHBoxLayout()
        versao_label = QLabel(Versao)
        versao_label.setStyleSheet("color: #f7f8f9; font-size: 11px;")
        versao_label.setAlignment(Qt.AlignRight)
        versao_layout.addStretch(1)
        versao_layout.addWidget(versao_label)
        versao_layout.setContentsMargins(0, 0, 10, 10)
        
        main_layout.addLayout(versao_layout)
        main_layout.addStretch(1)
        
        # Conectar evento Enter para campos
        self.usuario_input.returnPressed.connect(self.avancar_para_senha)
        self.senha_input.returnPressed.connect(self.avancar_para_empresa)
        self.empresa_input.returnPressed.connect(self.login)
    
    def verificar_atualizacao(self):
        """Inicia o processo de verificação de atualização"""
        try:
            # Criar e configurar worker
            self.atualizacao_worker = AtualizacaoWorker()
            self.atualizacao_worker.progress.connect(self.atualizacao_progresso)
            self.atualizacao_worker.status.connect(self.atualizacao_status)
            self.atualizacao_worker.finished.connect(self.atualizacao_concluida)
            
            # Desabilitar botão durante atualização
            self.atualizar_button.setEnabled(False)
            self.atualizar_button.setText("VERIFICANDO...")
            
            # Diálogo de progresso
            self.progress_dialog = QProgressDialog("Verificando atualizações...", "Cancelar", 0, 100, self)
            self.progress_dialog.setWindowTitle("Atualização do Sistema")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.canceled.connect(self.cancelar_atualizacao)
            self.progress_dialog.show()
            
            # Iniciar worker
            self.atualizacao_worker.start()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao iniciar verificação de atualização: {str(e)}")
            self.restaurar_botao_atualizacao()

    def atualizacao_progresso(self, valor):
        """Atualiza a barra de progresso"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(valor)

    def atualizacao_status(self, status):
        """Atualiza o status da atualização"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setLabelText(status)

    def atualizacao_concluida(self, mensagem):
        """Chamado quando a atualização é concluída"""
        try:
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.close()
                
            self.mostrar_mensagem("Atualização", mensagem)
            
            # Se a atualização foi bem-sucedida e o sistema será reiniciado
            if "reiniciado" in mensagem.lower():
                QTimer.singleShot(1000, self.fechar_para_atualizacao)
            else:
                self.restaurar_botao_atualizacao()
                
        except Exception as e:
            print(f"Erro ao concluir atualização: {e}")
            self.restaurar_botao_atualizacao()

    def cancelar_atualizacao(self):
        """Cancela o processo de atualização"""
        try:
            if hasattr(self, 'atualizacao_worker') and self.atualizacao_worker.isRunning():
                self.atualizacao_worker.terminate()
                self.atualizacao_worker.wait(3000)  # Espera até 3 segundos
        except:
            pass
        finally:
            self.restaurar_botao_atualizacao()

    def restaurar_botao_atualizacao(self):
        """Restaura o botão de atualização ao estado normal"""
        self.atualizar_button.setEnabled(True)
        self.atualizar_button.setText("VERIFICAR ATUALIZAÇÃO")

    def fechar_para_atualizacao(self):
        """Fecha o sistema para permitir a atualização"""
        self.close()

    def solicitar_codigo_licenca(self, usuario_id):
        """Exibe diálogo solicitando código de licença"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Renovação de Licença")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Mensagem
        label = QLabel("Sua licença expirou ou precisa ser renovada. Por favor, insira o código de licença fornecido pelo suporte:")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Campo para código
        codigo_input = QLineEdit()
        codigo_input.setPlaceholderText("Insira o código de licença")
        layout.addWidget(codigo_input)
        
        # Botões
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Confirmar")
        cancel_button = QPushButton("Cancelar")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Variável para armazenar o resultado
        result = [None]
        
        # Funções para os botões
        def on_confirm():
            codigo = codigo_input.text().strip()
            if not codigo:
                QMessageBox.warning(dialog, "Código Inválido", "Por favor, insira um código de licença válido.")
                return
            
            # Validar o código
            if validar_codigo_licenca(codigo, usuario_id):
                result[0] = codigo
                dialog.accept()
            else:
                QMessageBox.critical(dialog, "Código Inválido", "O código de licença informado é inválido ou expirou.")
        
        # Conectar botões
        ok_button.clicked.connect(on_confirm)
        cancel_button.clicked.connect(lambda: dialog.reject())
        
        # Executar diálogo
        if dialog.exec_() == QDialog.Accepted:
            return result[0]
        
        return None

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
        
        # Validações de campo
        if not usuario or not senha or not empresa:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!")
            return
        
        # Desabilitar botão e mostrar carregamento
        self.login_button.setEnabled(False)
        self.login_button.setText("VERIFICANDO...")
        
        # Salva usuário e empresa para próxima vez
        self.salvar_dados(usuario, empresa)
        
        try:
            # Verificar se o usuário está bloqueado
            from base.banco import verificar_usuario_bloqueado
            bloqueado, motivo = verificar_usuario_bloqueado(usuario, empresa)
            if bloqueado:
                self.mostrar_mensagem("Acesso Bloqueado", motivo)
                self.restaurar_botao_login()
                return
                
            # Validação no banco Firebird
            from base.banco import validar_login, autenticar_por_funcionario, execute_query
            from base.banco import obter_id_usuario, verificar_necessidade_codigo_licenca, validar_codigo_licenca
            
            # Tentar autenticar e obter informações do funcionário
            info_funcionario = None
            id_funcionario = None
            usuario_id = None
            
            # Verificar se é um usuário padrão
            ok = validar_login(usuario, senha, empresa)
            
            # Se for um funcionário com credenciais próprias
            if not ok:
                info_funcionario = autenticar_por_funcionario(usuario, senha)
                if info_funcionario:
                    ok = True
                    id_funcionario = info_funcionario.get("id_funcionario")
                    empresa = info_funcionario.get("empresa", empresa)
            else:
                # Para usuários padrão, buscar se está vinculado a algum funcionário
                from base.banco import buscar_funcionario_por_usuario
                func_info = buscar_funcionario_por_usuario(usuario)
                if func_info:
                    id_funcionario = func_info[0]
                
                # Obter ID do usuário para verificação de licença
                usuario_id = obter_id_usuario(usuario, empresa)
            
            if not ok:
                self.mostrar_mensagem("Erro", "Usuário ou senha inválidos!")
                self.restaurar_botao_login()
                return
            
            # Se não temos o ID do usuário ainda, buscamos agora
            if not usuario_id:
                usuario_id = obter_id_usuario(usuario, empresa)
            
            # Verificar se precisa de código de licença
            if verificar_necessidade_codigo_licenca(usuario_id):
                self.restaurar_botao_login()
                codigo = self.solicitar_codigo_licenca(usuario_id)
                if not codigo:
                    return
                
                # Validar o código
                if not validar_codigo_licenca(codigo, usuario_id):
                    self.mostrar_mensagem("Erro", "Código de licença inválido ou expirado.")
                    return
                
                # Se chegou aqui, o código é válido
                from base.banco import atualizar_data_expiracao_por_codigo
                atualizar_data_expiracao_por_codigo(codigo, usuario_id)
                
                self.mostrar_mensagem("Sucesso", "Licença ativada com sucesso!")
            
            # Verificar mensalidade vencida (data de expiração)
            else:
                from datetime import datetime, date
                query = """
                SELECT DATA_EXPIRACAO, USUARIO_MASTER
                FROM USUARIOS
                WHERE USUARIO = ? AND EMPRESA = ?
                """
                result = execute_query(query, (usuario, empresa))
                
                if result and len(result) > 0:
                    data_expiracao, usuario_master = result[0]
                    
                    # Verificar data de expiração deste usuário
                    if data_expiracao and date.today() > data_expiracao:
                        self.mostrar_mensagem("Acesso Bloqueado", 
                                            "Mensalidade vencida. Por favor, entre em contato com o suporte.")
                        self.restaurar_botao_login()
                        return
                        
                    # Se for um usuário vinculado, verificar também o usuário master
                    if usuario_master:
                        query_master = """
                        SELECT DATA_EXPIRACAO, BLOQUEADO
                        FROM USUARIOS
                        WHERE ID = ?
                        """
                        result_master = execute_query(query_master, (usuario_master,))
                        
                        if result_master and len(result_master) > 0:
                            data_expiracao_master, bloqueado_master = result_master[0]
                            
                            if bloqueado_master and bloqueado_master.upper() == 'S':
                                self.mostrar_mensagem("Acesso Bloqueado", 
                                                "Conta principal bloqueada. Entre em contato com o suporte.")
                                self.restaurar_botao_login()
                                return
                                
                            if data_expiracao_master and date.today() > data_expiracao_master:
                                self.mostrar_mensagem("Acesso Bloqueado", 
                                                "Mensalidade da conta principal vencida. Entre em contato com o suporte.")
                                self.restaurar_botao_login()
                                return
                
            # --- LÓGICA PARA OBTER O ID CORRETO ---
            id_para_passar = None
            if id_funcionario:
                # Se logou como funcionário, o id que importa para permissões é o do funcionário
                id_para_passar = id_funcionario
            elif usuario_id:
                # Se logou como master, usamos o id do master
                id_para_passar = usuario_id
            
            # Login bem-sucedido! Abrir a janela principal diretamente
            self.open_main_window(usuario, empresa, id_para_passar, id_funcionario)

        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao acessar o sistema: {str(e)}")
            self.restaurar_botao_login()
            return
    
    def restaurar_botao_login(self):
        """Restaura o botão de login ao estado normal"""
        self.login_button.setEnabled(True)
        self.login_button.setText("LOGIN")
    
    def open_main_window(self, usuario, empresa, id_usuario, id_funcionario):
        """Abre a janela principal diretamente após login bem-sucedido"""
        try:
            self.login_successful = True
            
            try:
                from base.syncthing_manager import syncthing_manager
                syncthing_manager.iniciar_syncthing()
            except Exception as e:
                print(f"Aviso: Erro ao verificar Syncthing: {e}")
            
            self.main_window = MainWindow(
                usuario=usuario, 
                empresa=empresa,
                id_usuario=id_usuario,
                id_funcionario=id_funcionario
            )
            
            # CORREÇÃO: Conecta o sinal de logout ao método de reabertura
            self.main_window.logout_signal.connect(self.reabrir_tela_login)
            
            # CORREÇÃO: Mostra a janela principal primeiro
            self.main_window.show()
            
            # CORREÇÃO: Só esconde a janela de login após a principal estar visível
            self.hide()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao abrir janela principal: {str(e)}")
            self.restaurar_botao_login()

    def reabrir_tela_login(self):
        """Esta função é chamada quando o sinal de logout é emitido pela MainWindow."""
        print("Sinal de logout recebido. Reabrindo a tela de login.")
        
        try:
            # CORREÇÃO 1: Garante que a main_window seja fechada e limpa
            if hasattr(self, 'main_window') and self.main_window:
                try:
                    # Desconecta o sinal para evitar loops
                    self.main_window.logout_signal.disconnect(self.reabrir_tela_login)
                except:
                    pass  # Ignora se já estava desconectado
                
                # Força o fechamento se ainda estiver visível
                if self.main_window.isVisible():
                    self.main_window.close()
                
                # Limpa a referência
                self.main_window = None
            
            # CORREÇÃO 2: Reseta o estado de login
            self.login_successful = False
            
            # CORREÇÃO 3: Limpa os campos sensíveis
            self.senha_input.clear()
            
            # CORREÇÃO 4: Restaura o botão de login
            self.restaurar_botao_login()
            
            # CORREÇÃO 5: Força a janela de login para o primeiro plano
            self.show()
            self.raise_()  # Traz para frente
            self.activateWindow()  # Ativa a janela
            
            # CORREÇÃO 6: Foca no campo apropriado
            if self.usuario_input.text().strip():
                self.senha_input.setFocus()
            else:
                self.usuario_input.setFocus()
                
            print("Tela de login reaberta com sucesso.")
            
        except Exception as e:
            print(f"Erro ao reabrir tela de login: {e}")
            # Em caso de erro, força a reabertura básica
            self.show()
            self.raise_()
            self.activateWindow()
    
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela de login"""
        print("Fechando janela de login...")
        
        try:
            # CORREÇÃO: Fecha a janela principal se ainda estiver aberta
            if hasattr(self, 'main_window') and self.main_window:
                try:
                    print("Fechando main_window associada...")
                    # Desconecta sinais para evitar loops
                    try:
                        self.main_window.logout_signal.disconnect()
                    except:
                        pass
                    
                    # Fecha a janela principal
                    if self.main_window.isVisible():
                        self.main_window.close()
                    
                    # Limpa a referência
                    self.main_window = None
                    print("Main_window fechada com sucesso")
                    
                except Exception as e:
                    print(f"Erro ao fechar main_window: {e}")
            
            # Limpar arquivos de conflito
            try:
                from base.banco import limpar_arquivos_conflito
                limpar_arquivos_conflito()
                print("Arquivos de conflito limpos")
            except Exception as e:
                print(f"Erro ao limpar arquivos de conflito: {e}")
            
            # Fechar Syncthing apenas se o login não foi bem-sucedido
            # ou se a aplicação está sendo totalmente fechada
            if not hasattr(self, 'login_successful') or not self.login_successful:
                try:
                    from base.banco import fechar_syncthing
                    fechar_syncthing()
                    print("Syncthing fechado")
                except Exception as e:
                    print(f"Erro ao fechar Syncthing: {e}")
            
            print("Limpeza do closeEvent da LoginWindow concluída")
            
        except Exception as e:
            print(f"Erro geral no closeEvent da LoginWindow: {e}")
        
        # Aceita o evento para permitir o fechamento
        event.accept()

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



def resource_path(relative_path):
    """Obtém o caminho absoluto para o recurso"""
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Erro ao obter caminho do recurso: {e}")
        return relative_path

def main():
    """Função principal que inicia o aplicativo com splash screen e verificação de atualização."""
    app = QApplication(sys.argv)
    
    startup_splash = SplashScreen("startup")
    startup_splash.show()
    startup_splash.start_loading()
    
    # CORREÇÃO: Declarar login_window fora da função para manter referência
    login_window = None
    
    def proximo_passo():
        nonlocal login_window
        startup_splash.close()
        
        # Verifica atualização
        atualizacao_iniciada = verificar_e_aplicar_atualizacao()

        # Se não iniciou atualização, abre a tela de login
        if not atualizacao_iniciada:
            login_window = LoginWindow()
            login_window.show()
            
            # CORREÇÃO: Armazena a referência no app para evitar garbage collection
            app.login_window = login_window
    
    startup_splash.worker.finished.connect(proximo_passo)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()