from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QAction,
                             QMenu, QToolBar, QGraphicsDropShadowEffect, QMessageBox,
                             QScrollArea, QCheckBox, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QUrl, QTimer

# Importar funções do banco de dados
from base.banco import execute_query, get_connection

class ConfiguracaoSistemaBackend:
    """Classe que gerencia o back-end da Configuração do Sistema"""
    
    def verificar_tabela_permissoes(self):
        """
        Verifica se a tabela PERMISSOES_SISTEMA existe e a cria se não existir
        
        Returns:
            bool: True se a tabela existe ou foi criada com sucesso
        """
        try:
            # Verificar se a tabela existe
            query_check = """
            SELECT COUNT(*) FROM RDB$RELATIONS 
            WHERE RDB$RELATION_NAME = 'PERMISSOES_SISTEMA'
            """
            result = execute_query(query_check)
            
            # Se a tabela não existe, cria
            if result[0][0] == 0:
                print("Tabela PERMISSOES_SISTEMA não encontrada. Criando...")
                query_create = """
                CREATE TABLE PERMISSOES_SISTEMA (
                    ID INTEGER NOT NULL PRIMARY KEY,
                    ID_FUNCIONARIO INTEGER NOT NULL,
                    NOME_FUNCIONARIO VARCHAR(100) NOT NULL,
                    MODULO VARCHAR(100) NOT NULL,
                    TEM_ACESSO CHAR(1) DEFAULT 'N'
                )
                """
                execute_query(query_create)
                print("Tabela PERMISSOES_SISTEMA criada com sucesso.")
                
                # Criar o gerador de IDs (sequence)
                try:
                    query_generator = """
                    CREATE GENERATOR GEN_PERMISSOES_SISTEMA_ID
                    """
                    execute_query(query_generator)
                    print("Gerador de IDs criado com sucesso.")
                except Exception as e:
                    print(f"Aviso: Gerador pode já existir: {e}")
                
                # Criar o trigger para autoincrementar o ID
                try:
                    query_trigger = """
                    CREATE TRIGGER PERMISSOES_SISTEMA_BI FOR PERMISSOES_SISTEMA
                    ACTIVE BEFORE INSERT POSITION 0
                    AS
                    BEGIN
                        IF (NEW.ID IS NULL) THEN
                            NEW.ID = GEN_ID(GEN_PERMISSOES_SISTEMA_ID, 1);
                    END
                    """
                    execute_query(query_trigger)
                    print("Trigger criado com sucesso.")
                except Exception as e:
                    print(f"Aviso: Trigger pode já existir: {e}")
                
                # Criar um índice para melhorar a performance das consultas
                try:
                    query_index = """
                    CREATE INDEX IDX_PERMISSOES_FUNCIONARIO ON PERMISSOES_SISTEMA (ID_FUNCIONARIO)
                    """
                    execute_query(query_index)
                    print("Índice criado com sucesso.")
                except Exception as e:
                    print(f"Aviso: Índice pode já existir: {e}")
                
                return True
            else:
                print("Tabela PERMISSOES_SISTEMA já existe.")
            
            return True
        except Exception as e:
            print(f"Erro ao verificar/criar tabela: {e}")
            raise Exception(f"Erro ao verificar/criar tabela de permissões: {str(e)}")
    
    def listar_modulos_sistema(self):
        """
        Lista todos os módulos/recursos do sistema que podem ter permissões configuradas
        
        Returns:
            list: Lista de nomes dos módulos disponíveis
        """
        # Lista atualizada com os módulos específicos solicitados pelo usuário
        modulos = [
            "Cadastro de empresa",
            "Cadastro de Clientes",
            "Cadastro Funcionários",
            "Consulta CNPJ",
            "Produtos",
            "Fornecedores",
            "Pedido de vendas",
            "Recebimento de clientes",
            "Gerar lançamento Financeiro",
            "Controle de caixa (PDV)",
            "Conta corrente",
            "Classes financeiras",
            "Relatório de Vendas de Produtos",
            "Configuração de estação",
            "Configuração do Sistema",
            "PDV - Ponto de Venda",
            "Ver Dashboard do Mercado livre"
        ]
        return modulos
    
    def listar_funcionarios(self):
        """
        Lista todos os funcionários cadastrados no sistema
        
        Returns:
            list: Lista de tuplas com ID e Nome dos funcionários
        """
        try:
            query = """
            SELECT ID, NOME FROM FUNCIONARIOS
            ORDER BY NOME
            """
            resultado = execute_query(query)
            return resultado
        except Exception as e:
            print(f"Erro ao listar funcionários: {e}")
            return []
    
    def obter_permissoes_funcionario(self, id_funcionario):
        """
        Obtém todas as permissões de um funcionário
        
        Args:
            id_funcionario (int): ID do funcionário
            
        Returns:
            dict: Dicionário com módulos como chaves e True/False como valores
        """
        try:
            # Verificar se o funcionário existe
            query_check = """
            SELECT NOME FROM FUNCIONARIOS
            WHERE ID = ?
            """
            resultado_check = execute_query(query_check, (id_funcionario,))
            
            if not resultado_check or len(resultado_check) == 0:
                print(f"Funcionário com ID {id_funcionario} não encontrado")
                return {}
            
            nome_funcionario = resultado_check[0][0]
            
            # Buscar permissões existentes
            query = """
            SELECT MODULO, TEM_ACESSO
            FROM PERMISSOES_SISTEMA
            WHERE ID_FUNCIONARIO = ?
            """
            resultado = execute_query(query, (id_funcionario,))
            
            # Converter para dicionário
            permissoes = {}
            for modulo, tem_acesso in resultado:
                permissoes[modulo] = (tem_acesso == 'S')
            
            # Adicionar módulos que não estão no banco ainda, com acesso CONCEDIDO por padrão
            modulos_disponiveis = self.listar_modulos_sistema()
            for modulo in modulos_disponiveis:
                if modulo not in permissoes:
                    # ### A MUDANÇA ESTÁ AQUI ###
                    # Criar permissão padrão no banco de dados com acesso VERDADEIRO
                    self.definir_permissao(id_funcionario, nome_funcionario, modulo, True) # <-- Mudado de False para True
                    permissoes[modulo] = True # <-- Mudado de False para True
            
            return permissoes
        except Exception as e:
            print(f"Erro ao obter permissões do funcionário: {e}")
            return {}
    
    def definir_permissao(self, id_funcionario, nome_funcionario, modulo, tem_acesso):
        """
        Define uma permissão específica para um funcionário
        
        Args:
            id_funcionario (int): ID do funcionário
            nome_funcionario (str): Nome do funcionário
            modulo (str): Nome do módulo
            tem_acesso (bool): Se o funcionário tem acesso ao módulo
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            # Verificar se a permissão já existe
            query_check = """
            SELECT ID FROM PERMISSOES_SISTEMA
            WHERE ID_FUNCIONARIO = ? AND MODULO = ?
            """
            resultado = execute_query(query_check, (id_funcionario, modulo))
            
            tem_acesso_str = 'S' if tem_acesso else 'N'
            
            if resultado and len(resultado) > 0:
                # Atualizar permissão existente
                id_permissao = resultado[0][0]
                query_update = """
                UPDATE PERMISSOES_SISTEMA
                SET TEM_ACESSO = ?
                WHERE ID = ?
                """
                execute_query(query_update, (tem_acesso_str, id_permissao))
            else:
                # Inserir nova permissão
                query_insert = """
                INSERT INTO PERMISSOES_SISTEMA (
                    ID_FUNCIONARIO, NOME_FUNCIONARIO, MODULO, TEM_ACESSO
                ) VALUES (?, ?, ?, ?)
                """
                execute_query(query_insert, (id_funcionario, nome_funcionario, modulo, tem_acesso_str))
            
            return True
        except Exception as e:
            print(f"Erro ao definir permissão: {e}")
            return False
    
    def salvar_permissoes(self, id_funcionario, permissoes):
        """
        Salva todas as permissões de um funcionário
        
        Args:
            id_funcionario (int): ID do funcionário
            permissoes (dict): Dicionário com módulos como chaves e True/False como valores
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            # Obter nome do funcionário
            query_nome = """
            SELECT NOME FROM FUNCIONARIOS
            WHERE ID = ?
            """
            resultado = execute_query(query_nome, (id_funcionario,))
            
            if not resultado or len(resultado) == 0:
                print(f"Funcionário com ID {id_funcionario} não encontrado")
                return False
            
            nome_funcionario = resultado[0][0]
            
            # Salvar cada permissão
            for modulo, tem_acesso in permissoes.items():
                self.definir_permissao(id_funcionario, nome_funcionario, modulo, tem_acesso)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar permissões: {e}")
            return False
    
    def verificar_permissao(self, id_funcionario, modulo):
        """
        Verifica se um funcionário tem permissão para um módulo específico
        
        Args:
            id_funcionario (int): ID do funcionário
            modulo (str): Nome do módulo
            
        Returns:
            bool: True se o funcionário tem acesso, False caso contrário
        """
        try:
            query = """
            SELECT TEM_ACESSO
            FROM PERMISSOES_SISTEMA
            WHERE ID_FUNCIONARIO = ? AND MODULO = ?
            """
            resultado = execute_query(query, (id_funcionario, modulo))
            
            if resultado and len(resultado) > 0:
                return resultado[0][0] == 'S'
            
            # Se não existe registro, o acesso é negado por padrão
            return False
        except Exception as e:
            print(f"Erro ao verificar permissão: {e}")
            # Em caso de erro, negar acesso por segurança
            return False


class ConfiguracaoSistemaWindow(QMainWindow):
    """Implementação da tela de Configuração do Sistema com o back-end"""
    
    def __init__(self):
        super().__init__()
        self.backend = ConfiguracaoSistemaBackend()
        
        # Inicializar o banco de dados
        self.backend.verificar_tabela_permissoes()
        
        # Continuar com a inicialização da UI como já implementado anteriormente
        self.setWindowTitle("Configuração do Sistema")
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Configuração do Sistema")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Container principal com fundo azul
        content_container = QFrame()
        content_container.setStyleSheet("background-color: #0a3b59; border-radius: 10px;")
        content_container.setFrameShape(QFrame.StyledPanel)
        content_container.setFrameShadow(QFrame.Raised)
        
        # Efeito de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(5, 5)
        content_container.setGraphicsEffect(shadow)
        
        # Layout do conteúdo
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Layout das seções
        sections_layout = QHBoxLayout()
        sections_layout.setSpacing(20)
        
        # ===== SEÇÃO DE FUNCIONÁRIOS =====
        funcionarios_frame = QFrame()
        funcionarios_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        funcionarios_layout = QVBoxLayout(funcionarios_frame)
        
        funcionarios_label = QLabel("Funcionários")
        funcionarios_label.setFont(QFont("Arial", 14, QFont.Bold))
        funcionarios_layout.addWidget(funcionarios_label)
        
        # Lista de funcionários
        self.funcionarios_list = QListWidget()
        self.funcionarios_list.setStyleSheet("background-color: white; border: none;")
        self.funcionarios_list.itemClicked.connect(self.employee_selected)
        funcionarios_layout.addWidget(self.funcionarios_list)
        
        sections_layout.addWidget(funcionarios_frame, 1)
        
        # ===== SEÇÃO DE ACESSOS =====
        acessos_frame = QFrame()
        acessos_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        acessos_layout = QVBoxLayout(acessos_frame)
        
        acessos_label = QLabel("Acessos")
        acessos_label.setFont(QFont("Arial", 14, QFont.Bold))
        acessos_layout.addWidget(acessos_label)
        
        # Área de rolagem para os checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white; border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Checkboxes de acesso
        self.checkbox_widgets = {}
        modulos = self.backend.listar_modulos_sistema()
        
        for modulo in modulos:
            checkbox = QCheckBox(modulo)
            checkbox.setFont(QFont("Arial", 12))
            checkbox.setEnabled(False)  # Desabilitado inicialmente até selecionar um funcionário
            self.checkbox_widgets[modulo] = checkbox
            scroll_layout.addWidget(checkbox)
        
        scroll_area.setWidget(scroll_content)
        acessos_layout.addWidget(scroll_area)
        
        sections_layout.addWidget(acessos_frame, 1)
        
        content_layout.addLayout(sections_layout)
        
        # ===== BOTÃO SALVAR =====
        save_button = QPushButton("Salvar")
        save_button.setFont(QFont("Arial", 12, QFont.Bold))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
        """)
        save_button.setCursor(QCursor(Qt.PointingHandCursor))
        save_button.clicked.connect(self.save_configuration)
        
        content_layout.addWidget(save_button)
        
        main_layout.addWidget(content_container)
        
        # Cor de fundo da janela principal
        self.setStyleSheet("background-color: #0a3b59;")
        
        # Carregar funcionários na lista
        self.carregar_funcionarios()
    
    def carregar_funcionarios(self):
        """Carrega a lista de funcionários do banco de dados"""
        try:
            self.funcionarios_list.clear()
            funcionarios = self.backend.listar_funcionarios()
            
            for id_funcionario, nome_funcionario in funcionarios:
                # Armazenar o ID como dado do item
                item = QListWidgetItem(nome_funcionario)
                item.setData(Qt.UserRole, id_funcionario)
                self.funcionarios_list.addItem(item)
                
        except Exception as e:
            print(f"Erro ao carregar funcionários: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar lista de funcionários: {str(e)}")
    
    def employee_selected(self, item):
        """Função executada quando um funcionário é selecionado"""
        try:
            # Obter o ID do funcionário selecionado
            id_funcionario = item.data(Qt.UserRole)
            
            # Habilitar todos os checkboxes
            for checkbox in self.checkbox_widgets.values():
                checkbox.setEnabled(True)
                checkbox.setChecked(False)
            
            # Carregar as permissões do funcionário
            permissoes = self.backend.obter_permissoes_funcionario(id_funcionario)
            
            # Marcar as caixas de acordo com as permissões
            for modulo, tem_acesso in permissoes.items():
                if modulo in self.checkbox_widgets:
                    self.checkbox_widgets[modulo].setChecked(tem_acesso)
            
        except Exception as e:
            print(f"Erro ao selecionar funcionário: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar permissões: {str(e)}")
    
    def save_configuration(self):
        """Função executada quando o botão Salvar é clicado"""
        try:
            selected_items = self.funcionarios_list.selectedItems()
            
            if not selected_items:
                QMessageBox.warning(self, "Aviso", "Por favor, selecione um funcionário")
                return
            
            # Obter o ID do funcionário selecionado
            id_funcionario = selected_items[0].data(Qt.UserRole)
            
            # Coletar as permissões
            permissoes = {}
            for modulo, checkbox in self.checkbox_widgets.items():
                permissoes[modulo] = checkbox.isChecked()
            
            # Salvar as permissões
            if self.backend.salvar_permissoes(id_funcionario, permissoes):
                QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Erro ao salvar as configurações")
            
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao salvar configurações: {str(e)}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ConfiguracaoSistemaWindow()
    window.show()
    sys.exit(app.exec_())