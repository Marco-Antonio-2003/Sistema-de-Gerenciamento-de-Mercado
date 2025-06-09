import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QCheckBox, QDialog,
                             QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

# Importar funções do banco.py para operações com o banco de dados
from base.banco import (execute_query, verificar_tabela_contas_correntes,
                       listar_contas_correntes, buscar_conta_corrente_por_id,
                       excluir_conta_corrente, filtrar_contas_correntes)

# Importar o FormularioContaCorrente
from financeiro.formulario_conta_corrente import FormularioContaCorrente

class ContaCorrenteWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Verificar e inicializar tabela no banco de dados
        self.inicializar_banco_dados()
        self.initUI()
        
    def inicializar_banco_dados(self):
        """Inicializa o banco de dados, criando tabelas se necessário"""
        try:
            verificar_tabela_contas_correntes()
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            self.mostrar_mensagem("Erro de Banco de Dados", 
                                 f"Ocorreu um erro ao inicializar o banco de dados: {str(e)}")
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho com título centralizado
        header_layout = QHBoxLayout()
        
        # Título centralizado
        title_label = QLabel("Contas Correntes")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addLayout(header_layout)
        
        # Formulário de filtros
        filtros_frame = QFrame()
        filtros_frame.setFrameShape(QFrame.StyledPanel)
        filtros_frame.setStyleSheet("""
            QFrame {
                background-color: #003353;
                border: 1px solid #00253e;
                border-radius: 5px;
            }
        """)
        
        filtros_layout = QVBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(15, 15, 15, 15)
        filtros_layout.setSpacing(10)
        
        # Linha superior com Código e Descrição
        filtro_superior = QHBoxLayout()
        
        # Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setFont(QFont("Arial", 12))
        codigo_label.setStyleSheet("color: white;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.codigo_input.setFixedWidth(100)
        codigo_layout.addWidget(self.codigo_input)
        filtro_superior.addLayout(codigo_layout)
        
        # Espaço entre código e descrição
        filtro_superior.addSpacing(20)
        
        # Descrição
        descricao_layout = QHBoxLayout()
        descricao_label = QLabel("Descrição:")
        descricao_label.setFont(QFont("Arial", 12))
        descricao_label.setStyleSheet("color: white;")
        descricao_layout.addWidget(descricao_label)
        
        self.descricao_input = QLineEdit()
        self.descricao_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.descricao_input.setMinimumWidth(300)
        descricao_layout.addWidget(self.descricao_input)
        filtro_superior.addLayout(descricao_layout)
        
        # Botões de filtro e limpar
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 5px 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_filtrar.clicked.connect(self.filtrar)
        filtro_superior.addWidget(self.btn_filtrar)
        
        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 5px 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_limpar.clicked.connect(self.limpar_filtros)
        filtro_superior.addWidget(self.btn_limpar)
        
        filtros_layout.addLayout(filtro_superior)
        main_layout.addWidget(filtros_frame)
        
        # Tabela de contas correntes
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Conta", "Descrição", "Banco", "Empresa", "Caixa PDV"])
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #cccccc;
            }
        """)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                alternate-background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Ajustar largura das colunas
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        self.table.itemClicked.connect(self.selecionar_linha)
        
        main_layout.addWidget(self.table)
        
        # Botões de controle
        btn_control_layout = QHBoxLayout()
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("+ Cadastrar")
        self.btn_cadastrar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 8px 15px;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_cadastrar.clicked.connect(self.cadastrar_conta)
        btn_control_layout.addWidget(self.btn_cadastrar)
        
        # Botão Alterar
        self.btn_alterar = QPushButton("✎ Alterar")
        self.btn_alterar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 8px 15px;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_alterar.clicked.connect(self.alterar_conta)
        btn_control_layout.addWidget(self.btn_alterar)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("✖ Excluir")
        self.btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 8px 15px;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir_conta)
        btn_control_layout.addWidget(self.btn_excluir)
        
        main_layout.addLayout(btn_control_layout)
        
        # Carregar dados do banco de dados
        self.carregar_dados_db()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")
    
    def carregar_dados_db(self):
        """Carrega os dados das contas correntes do banco de dados"""
        try:
            # Limpar a tabela
            self.table.setRowCount(0)
            
            # Buscar contas correntes no banco de dados
            contas = listar_contas_correntes()
            
            if contas:
                # Definir o número de linhas da tabela
                self.table.setRowCount(len(contas))
                
                # Preencher a tabela com os dados
                for row, conta in enumerate(contas):
                    # ID está no índice 0, mas não exibimos na tabela
                    self.table.setItem(row, 0, QTableWidgetItem(conta[1]))  # Código
                    self.table.setItem(row, 1, QTableWidgetItem(conta[2]))  # Descrição
                    self.table.setItem(row, 2, QTableWidgetItem(conta[3]))  # Banco
                    self.table.setItem(row, 3, QTableWidgetItem(conta[4]))  # Banco descrição
                    
                    # Para a coluna Caixa PDV, criar uma célula com um checkbox
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setCheckState(Qt.Checked if conta[5] == 'S' else Qt.Unchecked)
                    self.table.setItem(row, 4, checkbox_item)
            else:
                self.mostrar_mensagem("Informação", "Nenhuma conta corrente cadastrada.")
                
        except Exception as e:
            # Em caso de erro ao carregar os dados
            print(f"Erro ao carregar dados: {e}")
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao carregar os dados: {str(e)}")
    
    def selecionar_linha(self, item):
        # Implementar ações quando uma linha é selecionada
        row = item.row()
        conta = self.table.item(row, 0).text()
        descricao = self.table.item(row, 1).text()
        # Preencher os campos de filtro com os dados da linha selecionada
        self.codigo_input.setText(conta)
        self.descricao_input.setText(descricao)
    
    def filtrar(self):
        """Filtra os dados da tabela com base nos critérios de filtro"""
        try:
            codigo = self.codigo_input.text().strip()
            descricao = self.descricao_input.text().strip()
            
            # Buscar contas filtradas no banco de dados
            contas = filtrar_contas_correntes(codigo, descricao)
            
            # Limpar a tabela
            self.table.setRowCount(0)
            
            if contas:
                # Definir o número de linhas da tabela
                self.table.setRowCount(len(contas))
                
                # Preencher a tabela com os dados filtrados
                for row, conta in enumerate(contas):
                    self.table.setItem(row, 0, QTableWidgetItem(conta[1]))  # Código
                    self.table.setItem(row, 1, QTableWidgetItem(conta[2]))  # Descrição
                    self.table.setItem(row, 2, QTableWidgetItem(conta[3]))  # Banco
                    self.table.setItem(row, 3, QTableWidgetItem(conta[4]))  # Banco descrição
                    
                    # Para a coluna Caixa PDV, criar uma célula com um checkbox
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setCheckState(Qt.Checked if conta[5] == 'S' else Qt.Unchecked)
                    self.table.setItem(row, 4, checkbox_item)
            else:
                self.mostrar_mensagem("Informação", "Nenhuma conta corrente encontrada com os filtros informados.")
                
        except Exception as e:
            # Em caso de erro ao filtrar os dados
            print(f"Erro ao filtrar dados: {e}")
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao filtrar os dados: {str(e)}")
    
    def limpar_filtros(self):
        """Limpa os campos de filtro e recarrega todas as contas"""
        self.codigo_input.clear()
        self.descricao_input.clear()
        
        # Recarregar todos os dados
        self.carregar_dados_db()
    
    def cadastrar_conta(self):
        """Abre o formulário para cadastrar nova conta corrente"""
        try:
            # Criar uma janela do formulário
            dialog = FormularioContaCorrente(self)
            
            # Executar o diálogo
            if dialog.exec_() == QDialog.Accepted:
                # Recarregar os dados após o cadastro
                self.carregar_dados_db()
                
        except Exception as e:
            # Em caso de erro ao abrir o formulário
            print(f"Erro ao abrir formulário: {e}")
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao abrir o formulário: {str(e)}")
    
    def alterar_conta(self):
        """Abre o formulário para alterar conta selecionada"""
        row = self.table.currentRow()
        if row >= 0:
            try:
                # Obter o código da conta selecionada
                codigo = self.table.item(row, 0).text()
                
                # Buscar os dados completos da conta no banco de dados
                from base.banco import buscar_conta_corrente_por_codigo
                conta = buscar_conta_corrente_por_codigo(codigo)
                
                if conta:
                    # Criar a janela do formulário passando os dados da conta
                    dialog = FormularioContaCorrente(
                        self,
                        id_conta=conta[0],  # ID
                        codigo=conta[1],    # Código
                        descricao=conta[2], # Descrição
                        agencia=conta[6],   # Agência
                        numero_conta=conta[7], # Número da conta
                        empresa=conta[4],   # Descrição do banco
                        saldo=str(conta[8]) if conta[8] is not None else "0.00", # Saldo
                        caixa_pdv=conta[5] == 'S', # Caixa PDV
                        modo_edicao=True
                    )
                    
                    # Executar o diálogo
                    if dialog.exec_() == QDialog.Accepted:
                        # Recarregar os dados após a alteração
                        self.carregar_dados_db()
                else:
                    self.mostrar_mensagem("Erro", f"Não foi possível encontrar a conta {codigo}.")
            except Exception as e:
                # Em caso de erro ao abrir o formulário
                print(f"Erro ao abrir formulário de alteração: {e}")
                self.mostrar_mensagem("Erro", f"Ocorreu um erro ao abrir o formulário: {str(e)}")
        else:
            self.mostrar_mensagem("Seleção necessária", "Por favor, selecione uma conta para alterar.")
    
    def excluir_conta(self):
        """Exclui a conta selecionada após confirmação"""
        row = self.table.currentRow()
        if row >= 0:
            codigo = self.table.item(row, 0).text()
            descricao = self.table.item(row, 1).text()
            
            # Configurar caixa de mensagem de confirmação com estilo
            msg_box = QMessageBox(
                QMessageBox.Question,
                "Confirmar exclusão", 
                f"Deseja realmente excluir a conta {codigo} - {descricao}?",
                QMessageBox.Yes | QMessageBox.No,
                self
            )
            
            # Aplicar estilo com texto branco
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #003353;
                }
                QMessageBox QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
            
            # Estilizar botões
            yes_button = msg_box.button(QMessageBox.Yes)
            if yes_button:
                yes_button.setText("Sim")
                yes_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 80px;
                        min-height: 25px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            no_button = msg_box.button(QMessageBox.No)
            if no_button:
                no_button.setText("Não")
                no_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 80px;
                        min-height: 25px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            confirmacao = msg_box.exec_()
            
            if confirmacao == QMessageBox.Yes:
                try:
                    # Buscar o ID da conta no banco de dados
                    from base.banco import buscar_conta_corrente_por_codigo
                    conta = buscar_conta_corrente_por_codigo(codigo)
                    
                    if conta:
                        # Excluir a conta do banco de dados
                        excluir_conta_corrente(conta[0])
                        
                        # Remover a linha da tabela
                        self.table.removeRow(row)
                        
                        # Mensagem de sucesso
                        self.mostrar_mensagem("Exclusão concluída", f"A conta {codigo} foi excluída com sucesso.")
                    else:
                        self.mostrar_mensagem("Erro", f"Conta {codigo} não encontrada no banco de dados.")
                except Exception as e:
                    # Em caso de erro ao excluir a conta
                    print(f"Erro ao excluir conta: {e}")
                    self.mostrar_mensagem("Erro", f"Ocorreu um erro ao excluir a conta: {str(e)}")
        else:
            self.mostrar_mensagem("Seleção necessária", "Por favor, selecione uma conta para excluir.")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem estilizada"""
        msg_box = QMessageBox(
            QMessageBox.Information if "concluída" in titulo or "Informação" in titulo else QMessageBox.Warning,
            titulo, 
            texto,
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
            QMessageBox QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        # Obter o botão OK e aplicar estilo diretamente nele
        ok_button = msg_box.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #004465;
                    border: none;
                    border-radius: 3px;
                    min-width: 80px;
                    min-height: 25px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00354f;
                }
                QPushButton:pressed {
                    background-color: #0078d7;
                }
            """)
        
        msg_box.exec_()

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Contas Correntes")
    window.setGeometry(100, 100, 800, 500)
    window.setStyleSheet("QMainWindow { background-color: #043b57; }")
    
    contas_correntes = ContaCorrenteWindow()
    window.setCentralWidget(contas_correntes)
    window.show()
    sys.exit(app.exec_())