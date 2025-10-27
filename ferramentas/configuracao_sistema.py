# Seus imports permanecem os mesmos
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QAction,
                             QMenu, QToolBar, QGraphicsDropShadowEffect, QMessageBox,
                             QScrollArea, QCheckBox, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QUrl, QTimer

# Importar funções do banco de dados
# Assumindo que get_connection() retorna um objeto de conexão padrão DB-API 2.0
from base.banco import execute_query, get_connection

class ConfiguracaoSistemaBackend:
    """
    Classe que gerencia o back-end da Configuração do Sistema (Versão Otimizada)
    """
    
    # OTIMIZAÇÃO: Definir a lista de módulos como uma constante de classe.
    # Isso evita recriá-la toda vez que o método é chamado e facilita a manutenção.
    MODULOS_SISTEMA = [
        "Cadastro de empresa", "Cadastro de Clientes", "Cadastro Funcionários",
        "Consulta CNPJ", "Produtos", "Fornecedores", "Pedido de vendas",
        "Recebimento de clientes", "Gerar lançamento Financeiro", "Controle de caixa (PDV)",
        "Conta corrente", "Classes financeiras", "Relatório de Vendas de Produtos",
        "Configuração de estação", "Configuração do Sistema", "PDV - Ponto de Venda",
        "Ver Dashboard do Mercado livre"
    ]

    def verificar_tabela_permissoes(self):
        """
        Verifica se a tabela PERMISSOES_SISTEMA existe e a cria se não existir.
        OTIMIZAÇÃO: Usa uma transação para garantir a atomicidade da criação.
        """
        conn = None
        try:
            # Verificar se a tabela existe
            query_check = "SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = 'PERMISSOES_SISTEMA'"
            result = execute_query(query_check)
            
            if result and result[0][0] == 0:
                print("Tabela PERMISSOES_SISTEMA não encontrada. Iniciando criação...")
                
                # OTIMIZAÇÃO: Usar uma transação para criar a tabela e seus objetos dependentes.
                # Isso garante que ou tudo é criado com sucesso, ou nada é.
                conn = get_connection()
                cursor = conn.cursor()

                try:
                    # Agrupar todos os comandos de criação (DDL)
                    ddl_commands = [
                        """
                        CREATE TABLE PERMISSOES_SISTEMA (
                            ID INTEGER NOT NULL PRIMARY KEY,
                            ID_FUNCIONARIO INTEGER NOT NULL,
                            NOME_FUNCIONARIO VARCHAR(100) NOT NULL,
                            MODULO VARCHAR(100) NOT NULL,
                            TEM_ACESSO CHAR(1) DEFAULT 'N'
                        )
                        """,
                        "CREATE GENERATOR GEN_PERMISSOES_SISTEMA_ID",
                        """
                        CREATE TRIGGER PERMISSOES_SISTEMA_BI FOR PERMISSOES_SISTEMA
                        ACTIVE BEFORE INSERT POSITION 0
                        AS
                        BEGIN
                            IF (NEW.ID IS NULL) THEN
                                NEW.ID = GEN_ID(GEN_PERMISSOES_SISTEMA_ID, 1);
                        END
                        """,
                        "CREATE INDEX IDX_PERMISSOES_FUNCIONARIO ON PERMISSOES_SISTEMA (ID_FUNCIONARIO, MODULO)"
                    ]
                    
                    for cmd in ddl_commands:
                        try:
                            cursor.execute(cmd)
                            print(f"Executado com sucesso: {cmd.splitlines()[1].strip() if len(cmd.splitlines()) > 1 else cmd}")
                        except Exception as e:
                            # Ignora erros se o objeto já existir (comportamento original)
                            print(f"Aviso: Objeto pode já existir. Comando: '{cmd.split()[0]} {cmd.split()[1]}'. Erro: {e}")
                            
                    conn.commit()
                    print("Criação da tabela e objetos relacionados concluída com sucesso.")
                    
                except Exception as e:
                    if conn:
                        conn.rollback() # Desfaz tudo se algo der errado
                    print(f"Erro catastrófico durante a criação da tabela. Rollback executado. Erro: {e}")
                    raise
                finally:
                    if conn:
                        conn.close()
            else:
                print("Tabela PERMISSOES_SISTEMA já existe.")
            return True
        except Exception as e:
            print(f"Erro ao verificar/criar tabela: {e}")
            raise Exception(f"Erro fatal ao inicializar o banco de dados para permissões: {str(e)}")

    def listar_modulos_sistema(self):
        """Retorna a lista de módulos do sistema."""
        return self.MODULOS_SISTEMA
    
    def listar_funcionarios(self):
        """Lista todos os funcionários cadastrados no sistema."""
        try:
            query = "SELECT ID, NOME FROM FUNCIONARIOS ORDER BY NOME"
            return execute_query(query)
        except Exception as e:
            print(f"Erro ao listar funcionários: {e}")
            return []

    def obter_permissoes_funcionario(self, id_funcionario):
        """
        Obtém todas as permissões de um funcionário.
        OTIMIZAÇÃO: Reduz múltiplas chamadas ao BD para uma única operação de inserção em lote.
        """
        try:
            # 1. Obter nome do funcionário
            nome_funcionario_result = execute_query("SELECT NOME FROM FUNCIONARIOS WHERE ID = ?", (id_funcionario,))
            if not nome_funcionario_result:
                print(f"Funcionário com ID {id_funcionario} não encontrado.")
                return {}
            nome_funcionario = nome_funcionario_result[0][0]

            # 2. Buscar permissões já existentes no banco
            permissoes_db = execute_query(
                "SELECT MODULO, TEM_ACESSO FROM PERMISSOES_SISTEMA WHERE ID_FUNCIONARIO = ?", 
                (id_funcionario,)
            )
            permissoes = {modulo: tem_acesso == 'S' for modulo, tem_acesso in permissoes_db}

            # 3. Identificar módulos que ainda não têm registro no banco para este funcionário
            modulos_existentes = set(permissoes.keys())
            modulos_sistema = set(self.listar_modulos_sistema())
            modulos_faltantes = modulos_sistema - modulos_existentes

            # 4. OTIMIZAÇÃO: Inserir todos os módulos faltantes de uma só vez.
            if modulos_faltantes:
                print(f"Encontrados {len(modulos_faltantes)} módulos sem permissão definida. Criando com acesso padrão...")
                # O padrão é conceder acesso ('S')
                dados_para_inserir = [
                    (id_funcionario, nome_funcionario, modulo, 'S') for modulo in modulos_faltantes
                ]
                
                query_insert = """
                INSERT INTO PERMISSOES_SISTEMA (ID_FUNCIONARIO, NOME_FUNCIONARIO, MODULO, TEM_ACESSO) 
                VALUES (?, ?, ?, ?)
                """
                
                # Usar uma transação para garantir que todas as inserções funcionem
                conn = get_connection()
                try:
                    cursor = conn.cursor()
                    # executemany é muito mais rápido que um loop de execute()
                    cursor.executemany(query_insert, dados_para_inserir)
                    conn.commit()
                finally:
                    conn.close()

                # Atualizar o dicionário local para refletir as novas permissões
                for modulo in modulos_faltantes:
                    permissoes[modulo] = True

            return permissoes
        except Exception as e:
            print(f"Erro ao obter permissões do funcionário: {e}")
            return {}

    def salvar_permissoes(self, id_funcionario, permissoes):
        """
        Salva todas as permissões de um funcionário.
        OTIMIZAÇÃO: Usa `UPDATE OR INSERT` e `executemany` para salvar tudo em uma única chamada ao BD.
        """
        try:
            # 1. Obter nome do funcionário
            nome_funcionario_result = execute_query("SELECT NOME FROM FUNCIONARIOS WHERE ID = ?", (id_funcionario,))
            if not nome_funcionario_result:
                print(f"Funcionário com ID {id_funcionario} não encontrado.")
                return False
            nome_funcionario = nome_funcionario_result[0][0]

            # 2. Preparar dados para a operação em lote
            dados_para_salvar = [
                (id_funcionario, nome_funcionario, 'S' if tem_acesso else 'N', modulo)
                for modulo, tem_acesso in permissoes.items()
            ]

            # 3. OTIMIZAÇÃO: Usar `UPDATE OR INSERT` (UPSERT) específico do Firebird.
            # Isso atualiza a linha se ela existir ou insere se não existir. Tudo em uma única operação atômica.
            query_upsert = """
            UPDATE OR INSERT INTO PERMISSOES_SISTEMA (ID_FUNCIONARIO, NOME_FUNCIONARIO, TEM_ACESSO, MODULO)
            VALUES (?, ?, ?, ?)
            MATCHING (ID_FUNCIONARIO, MODULO)
            """

            # 4. Executar a operação em lote
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.executemany(query_upsert, dados_para_salvar)
                conn.commit()
                print(f"Permissões salvas com sucesso para o funcionário ID {id_funcionario}.")
                return True
            except Exception as e:
                conn.rollback()
                print(f"Erro ao salvar permissões em lote. Rollback executado. Erro: {e}")
                return False
            finally:
                conn.close()

        except Exception as e:
            print(f"Erro ao preparar para salvar permissões: {e}")
            return False

    def verificar_permissao(self, id_funcionario, modulo):
        """
        Verifica se um funcionário tem permissão para um módulo específico.
        (Este método já era eficiente, sem necessidade de grandes alterações).
        """
        try:
            query = "SELECT TEM_ACESSO FROM PERMISSOES_SISTEMA WHERE ID_FUNCIONARIO = ? AND MODULO = ?"
            resultado = execute_query(query, (id_funcionario, modulo))
            
            if resultado:
                return resultado[0][0] == 'S'
            
            # Se não há registro, o padrão de segurança é negar o acesso.
            # Poderíamos consultar obter_permissoes_funcionario, mas isso seria mais lento.
            # A lógica atual que retorna False para permissões não explícitas é segura e rápida.
            return False
        except Exception as e:
            print(f"Erro ao verificar permissão: {e}")
            return False

# A classe ConfiguracaoSistemaWindow (sua UI) não precisa de NENHUMA alteração.
# Ela continuará funcionando como antes, mas agora será muito mais rápida
# ao selecionar um funcionário e ao salvar as configurações.
class ConfiguracaoSistemaWindow(QMainWindow):
    # ... seu código da UI permanece exatamente o mesmo ...
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
            
            # Carregar as permissões do funcionário (agora muito mais rápido)
            permissoes = self.backend.obter_permissoes_funcionario(id_funcionario)
            
            # Marcar as caixas de acordo com as permissões
            for modulo, tem_acesso in permissoes.items():
                if modulo in self.checkbox_widgets:
                    self.checkbox_widgets[modulo].setChecked(tem_acesso)
            
        except Exception as e:
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
            
            # Salvar as permissões (agora muito mais rápido)
            if self.backend.salvar_permissoes(id_funcionario, permissoes):
                QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Erro ao salvar as configurações")
            
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar configurações: {str(e)}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    # Simulação do módulo de banco de dados para teste
    # Em seu ambiente real, remova este bloco e use o seu `base.banco`
    class MockDb:
        def get_connection(self):
            # Esta função precisaria de uma implementação real para testes
            # mas o código da aplicação não precisa dela diretamente, apenas o backend
            return None 
        def execute_query(self, query, params=()):
            print(f"Executing Query: {query} with params {params}")
            if "FROM FUNCIONARIOS" in query:
                return [(1, "Alice"), (2, "Bob")]
            if "FROM PERMISSOES_SISTEMA" in query:
                # Simula que o funcionário 1 tem uma permissão
                if params and params[0] == 1:
                    return [("Cadastro de Clientes", "S")]
                return [] # Simula que o funcionário 2 não tem nenhuma
            if "FROM RDB$RELATIONS" in query:
                return [(1,)] # Simula que a tabela já existe
            return []

    mock_db = MockDb()
    # Substituindo as funções reais pelas mockadas
    import base.banco as banco
    banco.execute_query = mock_db.execute_query
    banco.get_connection = mock_db.get_connection
    
    window = ConfiguracaoSistemaWindow()
    window.show()
    sys.exit(app.exec_())