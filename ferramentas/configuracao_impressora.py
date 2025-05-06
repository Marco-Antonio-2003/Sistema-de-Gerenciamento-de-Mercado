import sys
import socket
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinterInfo, QPrintDialog, QPrinter

# Importar funções do banco de dados
from base.banco import execute_query, get_usuario_logado


class ConfiguracaoImpressoraWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.carregar_dados_do_banco()  # Carregar dados do banco ao iniciar
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#043b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(30)
        
        # Fundo para todo o aplicativo
        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())
        
        # Título em uma barra azul escura
        titulo_container = QWidget()
        titulo_container.setStyleSheet("background-color: #043b57;")
        titulo_container_layout = QVBoxLayout(titulo_container)
        titulo_container_layout.setContentsMargins(10, 10, 10, 10)
        
        titulo = QLabel("Configuração de estação")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_container_layout.addWidget(titulo)
        
        main_layout.addWidget(titulo_container)
        
        # Botões de categoria
        categorias_layout = QHBoxLayout()
        categorias_layout.setSpacing(5)
        
        categoria_style = """
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 15px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover, QPushButton:checked {
                background-color: #003d5c;
            }
        """
        
        self.categorias = ["Padrão", "Orçamento", "Pedidos", "Pedidos de Venda"]
        self.categoria_buttons = []
        
        for categoria in self.categorias:
            btn = QPushButton(categoria)
            btn.setStyleSheet(categoria_style)
            btn.setCheckable(True)
            categorias_layout.addWidget(btn)
            self.categoria_buttons.append(btn)
            btn.clicked.connect(self.mudar_categoria)
        
        self.categoria_buttons[0].setChecked(True)  # Por padrão, selecionar o primeiro botão
        main_layout.addLayout(categorias_layout)
        
        # Área de seleção de impressora
        impressora_frame = QFrame()
        impressora_frame.setStyleSheet("background-color: #fffff0; border-radius: 4px;")
        impressora_layout = QHBoxLayout(impressora_frame)
        impressora_layout.setContentsMargins(20, 20, 20, 20)
        
        # Texto "Escolher Impressora"
        escolher_label = QLabel("Escolher\nImpressora")
        escolher_label.setFont(QFont("Arial", 16, QFont.Bold))
        escolher_label.setStyleSheet("color: black;")
        impressora_layout.addWidget(escolher_label)
        
        # Campo para mostrar a impressora selecionada
        self.impressora_input = QLineEdit()
        self.impressora_input.setStyleSheet("""
            QLineEdit {
                background-color: #e8f0ff;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                min-height: 25px;
                border-radius: 4px;
                color: black;
            }
        """)
        self.impressora_input.setReadOnly(True)  # Campo apenas para exibição
        self.impressora_input.mousePressEvent = self.selecionar_impressora  # Abrir diálogo ao clicar
        impressora_layout.addWidget(self.impressora_input, 1)  # 1 para expandir e ocupar espaço disponível
        
        # Botão com ícone de impressora
        self.btn_impressora = QPushButton()
        self.btn_impressora.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
        """)
        # Definir um ícone de impressora
        icon_path = "printer.png"  # Você pode precisar fornecer o caminho correto para um ícone de impressora
        try:
            self.btn_impressora.setIcon(QIcon.fromTheme("printer"))
        except:
            # Usar emoji como fallback
            self.btn_impressora.setText("🖨️")
            self.btn_impressora.setFont(QFont("Arial", 18))
        
        self.btn_impressora.clicked.connect(self.selecionar_impressora)
        impressora_layout.addWidget(self.btn_impressora)
        
        main_layout.addWidget(impressora_frame)
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                font-weight: bold;
                padding: 15px 0;
                font-size: 16px;
                border-radius: 25px;
                margin: 10px 50px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar_configuracao)
        main_layout.addWidget(self.btn_salvar)
        
        # Adicionar espaço no final
        main_layout.addStretch()
        
        # Definir cor de fundo para a aplicação inteira
        app = QApplication.instance()
        if app:
            app.setStyleSheet("QWidget { background-color: #043b57; color: white; }")
            
        # Aplicar estilo no widget atual
        self.setStyleSheet("""
            QWidget { background-color: #043b57; }
            QMessageBox { background-color: white; }
        """)
        
        # Armazenar as configurações de impressoras
        self.impressoras = {
            "Padrão": "",
            "Orçamento": "",
            "Pedidos": "",
            "Pedidos de Venda": ""
        }
        
        # Categoria atual
        self.categoria_atual = "Padrão"
    
    def carregar_dados_do_banco(self):
        """Carrega as configurações de impressoras do banco de dados"""
        try:
            # Para cada categoria, buscar a impressora configurada
            for categoria in self.categorias:
                query = """
                SELECT IMPRESSORA FROM CONFIGURACAO_IMPRESSORAS
                WHERE CATEGORIA = ?
                """
                result = execute_query(query, (categoria,))
                
                if result and len(result) > 0:
                    self.impressoras[categoria] = result[0][0]
            
            # Atualizar o campo com a impressora da categoria atual
            self.impressora_input.setText(self.impressoras[self.categoria_atual])
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao carregar dados do banco: {str(e)}")
    
    def mudar_categoria(self):
        """Muda a categoria selecionada e carrega a configuração correspondente"""
        sender = self.sender()
        if sender:
            # Desmarcar todos os botões
            for btn in self.categoria_buttons:
                if btn != sender:
                    btn.setChecked(False)
            
            # Marcar o botão clicado
            sender.setChecked(True)
            
            # Atualizar categoria atual
            self.categoria_atual = sender.text()
            
            # Carregar configuração da categoria
            self.carregar_configuracao()
    
    def carregar_configuracao(self):
        """Carrega a configuração da impressora para a categoria atual"""
        # Aqui você carregaria a configuração do banco de dados/arquivo
        # Por enquanto, vamos usar o dicionário local
        impressora = self.impressoras.get(self.categoria_atual, "")
        self.impressora_input.setText(impressora)
    
    def selecionar_impressora(self, event=None):
        """Abre o diálogo de seleção de impressora"""
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        dialog.setOption(QPrintDialog.PrintToFile, False)
        dialog.setOption(QPrintDialog.PrintSelection, False)
        dialog.setOption(QPrintDialog.PrintPageRange, False)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            impressora_nome = printer.printerName()
            self.impressora_input.setText(impressora_nome)
            self.impressoras[self.categoria_atual] = impressora_nome
    
    def salvar_configuracao(self):
        """Salva a configuração da impressora para a categoria atual"""
        if not self.impressora_input.text():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Atenção")
            msg_box.setText(f"Por favor, selecione uma impressora para {self.categoria_atual}.")
            msg_box.setStyleSheet("""
                QMessageBox { 
                    background-color: white;
                }
                QLabel { 
                    color: black;
                    background-color: white;
                }
                QPushButton {
                    background-color: #043b57;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 2px;
                }
            """)
            msg_box.exec_()
            return
        
        try:
            # Salvar no banco de dados
            impressora = self.impressora_input.text()
            estacao = self.obter_estacao_atual()
            
            self.salvar_configuracao_impressora(self.categoria_atual, impressora, estacao)
            
            # Exibir mensagem de sucesso
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Configuração Salva")
            msg_box.setText(f"Impressora para {self.categoria_atual} configurada com sucesso!")
            msg_box.setStyleSheet("""
                QMessageBox { 
                    background-color: white;
                }
                QLabel { 
                    color: black;
                    background-color: white;
                }
                QPushButton {
                    background-color: #043b57;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 2px;
                }
            """)
            msg_box.exec_()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao salvar configuração: {str(e)}")
    
    def salvar_configuracao_impressora(self, categoria, impressora, estacao=None):
        """Salva a configuração de impressora no banco de dados"""
        try:
            # Verificar se já existe uma configuração para esta categoria
            query_check = """
            SELECT ID FROM CONFIGURACAO_IMPRESSORAS 
            WHERE CATEGORIA = ?
            """
            result = execute_query(query_check, (categoria,))
            
            # Obter dados do usuário logado
            data_atual = datetime.now().date()
            id_usuario = None
            nome_usuario = None
            
            # Se houver um usuário logado, usar seus dados
            try:
                usuario_logado = get_usuario_logado()
                if usuario_logado and usuario_logado["id"]:
                    id_usuario = usuario_logado["id"]
                    nome_usuario = usuario_logado["nome"]
            except:
                pass
            
            # Se já existe, atualiza
            if result and len(result) > 0:
                id_config = result[0][0]
                
                query_update = """
                UPDATE CONFIGURACAO_IMPRESSORAS
                SET IMPRESSORA = ?, ESTACAO = ?, DATA_CONFIGURACAO = ?, ID_USUARIO = ?, USUARIO = ?
                WHERE ID = ?
                """
                
                execute_query(query_update, (
                    impressora, estacao, data_atual, id_usuario, nome_usuario, id_config
                ))
            else:
                # Gerar próximo ID manualmente
                query_nextid = """
                SELECT COALESCE(MAX(ID), 0) + 1 FROM CONFIGURACAO_IMPRESSORAS
                """
                next_id = execute_query(query_nextid)[0][0]
                
                # Se não existe, insere com ID explícito
                query_insert = """
                INSERT INTO CONFIGURACAO_IMPRESSORAS (
                    ID, CATEGORIA, IMPRESSORA, ESTACAO, DATA_CONFIGURACAO, ID_USUARIO, USUARIO
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                execute_query(query_insert, (
                    next_id, categoria, impressora, estacao, data_atual, id_usuario, nome_usuario
                ))
            
            # Atualizar o dicionário local
            self.impressoras[categoria] = impressora
            
            print(f"Configuração de impressora para {categoria} salva com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração de impressora: {e}")
            raise Exception(f"Erro ao salvar configuração de impressora: {str(e)}")
    
    def obter_estacao_atual(self):
        """Obtém o nome da estação atual (computador)"""
        try:
            return socket.gethostname()
        except Exception as e:
            print(f"Erro ao obter nome da estação: {e}")
            return "Estação Desconhecida"
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
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
                background-color: #043b57;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 2px;
            }
        """)
        msg_box.exec_()


# Função para verificar e criar a tabela no banco de dados
def verificar_tabela_configuracao_impressoras():
    """Verifica se a tabela CONFIGURACAO_IMPRESSORAS existe e a cria se não existir"""
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'CONFIGURACAO_IMPRESSORAS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela CONFIGURACAO_IMPRESSORAS não encontrada. Criando...")
            query_create = """
            CREATE TABLE CONFIGURACAO_IMPRESSORAS (
                ID INTEGER NOT NULL PRIMARY KEY,
                CATEGORIA VARCHAR(50) NOT NULL,
                IMPRESSORA VARCHAR(100) NOT NULL,
                ESTACAO VARCHAR(50),
                DATA_CONFIGURACAO DATE,
                ID_USUARIO INTEGER,
                USUARIO VARCHAR(50)
            )
            """
            execute_query(query_create)
            print("Tabela CONFIGURACAO_IMPRESSORAS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_CONFIG_IMPRESSORAS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
            
            # Não vamos criar o trigger, vamos gerar o ID manualmente no código
            
            return True
        else:
            print("Tabela CONFIGURACAO_IMPRESSORAS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de configuração de impressoras: {str(e)}")


# Para testar a aplicação
if __name__ == "__main__":
    try:
        # Verificar e criar a tabela de impressoras se necessário
        verificar_tabela_configuracao_impressoras()
        
        app = QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("Configuração de Impressoras")
        window.setGeometry(100, 100, 800, 500)
        window.setStyleSheet("background-color: #043b57;")
        
        configuracao_widget = ConfiguracaoImpressoraWindow()
        window.setCentralWidget(configuracao_widget)
        
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        
        # Mostrar mensagem de erro em uma caixa de diálogo
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Erro ao iniciar aplicação: {str(e)}")
        msg.setWindowTitle("Erro")
        msg.exec_()
        
        sys.exit(1)