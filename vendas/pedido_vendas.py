import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QDateEdit, 
                           QMessageBox, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QDate

# Importar funções do banco de dados
from base.banco import (verificar_tabela_pedidos_venda, listar_pedidos_venda,
                       buscar_pedido_por_id, buscar_pedido_por_numero,
                       criar_pedido, atualizar_pedido, excluir_pedido,
                       buscar_pedidos_por_filtro, obter_vendedores_pedidos,
                       obter_clientes_pedidos, obter_cidades_pedidos,
                       listar_funcionarios, listar_pessoas, listar_produtos)

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Agora tente importar novamente
from formulario_pedido_vendas import FormularioPedidoVendas

JANELA_LARGURA = 800
JANELA_ALTURA = 600

# Classe para os ComboBox editáveis
class ComboBoxEditavel(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxEditavel, self).__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer().setCaseSensitivity(Qt.CaseInsensitive)
        
        # Definir como vazio ao inicializar
        self.clearEditText()  # Limpa o texto no editor
        
        # Estilo do ComboBox com seta para baixo
        self.setStyleSheet("""
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
                image: url(ico-img/down-arrow.png);
            }
            QComboBox QAbstractItemView {
                background-color: #fffff0;
                selection-background-color: #0078d7;
                selection-color: white;
                border: 1px solid #cccccc;
            }
        """)
        
    def showPopup(self):
        """Sobrescreve o método de mostrar popup para garantir que o texto atual não seja selecionado"""
        super().showPopup()
        
    def addItems(self, items):
        """Sobrescreve o método addItems para não selecionar o primeiro item"""
        super().addItems(items)
        self.setCurrentIndex(-1)  # Definir índice como -1 (nenhum selecionado)
        self.clearEditText()  # Limpar o texto do editor

# Classe principal para a tela de Pedido de Vendas
class PedidoVendasWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.form_window = None  # Para armazenar a referência da janela de formulário
        self.initUI()
        self.setMinimumSize(JANELA_LARGURA, JANELA_ALTURA)
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#003b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
    
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Fundo para todo o aplicativo
        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())
        
        # Layout para o título centralizado
        header_layout = QHBoxLayout()
        
        # Título centralizado
        titulo = QLabel("Pedido de vendas")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para DateEdit com ícone de calendário
        dateedit_style = """
            QDateEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QDateEdit:focus {
                border: 1px solid #0078d7;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QDateEdit::down-arrow {
                width: 14px;
                height: 14px;
                image: url(ico-img/calendar-outline.svg);
            }
        """
        
        # Primeira linha de filtros - Nome
        filtro_layout0 = QHBoxLayout()
        filtro_layout0.setSpacing(10)
        
        # Campo Nome (Cliente) - ComboBox Editável
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 16px;")
        nome_label.setFixedWidth(80)  # Fixar largura para alinhamento
        filtro_layout0.addWidget(nome_label)
        
        self.nome_input = ComboBoxEditavel()
        
        # Preencher com nomes de clientes existentes
        try:
            clientes = obter_clientes_pedidos()
            self.nome_input.addItems(clientes)
            # Também adicionar clientes da tabela PESSOAS
            pessoas = listar_pessoas()
            for pessoa in pessoas:
                nome = pessoa[1]  # Nome da pessoa
                if nome and nome not in clientes:
                    self.nome_input.addItem(nome)
            
            # Garantir que o ComboBox comece vazio
            self.nome_input.setCurrentIndex(-1)
            self.nome_input.clearEditText()
        except Exception as e:
            print(f"Erro ao carregar nomes de clientes: {e}")
        
        filtro_layout0.addWidget(self.nome_input, 1)
        
        main_layout.addLayout(filtro_layout0)
        
        # Segunda linha de filtros - Vendedor
        filtro_layout1 = QHBoxLayout()
        filtro_layout1.setSpacing(10)
        
        # Campo Vendedor - ComboBox Editável
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        vendedor_label.setFixedWidth(80)  # Fixar largura para alinhamento
        filtro_layout1.addWidget(vendedor_label)
        
        self.vendedor_input = ComboBoxEditavel()
        
        # Preencher com vendedores existentes
        try:
            # Obter vendedores de pedidos anteriores
            vendedores = obter_vendedores_pedidos()
            
            # Obter funcionários da tabela FUNCIONARIOS
            funcionarios = listar_funcionarios()
            
            # Combinar as listas, evitando duplicatas
            todos_vendedores = set(vendedores)
            for funcionario in funcionarios:
                todos_vendedores.add(funcionario[1])  # Nome do funcionário
            
            # Adicionar ao combobox
            self.vendedor_input.addItems(sorted(todos_vendedores))
            
            # Garantir que o ComboBox comece vazio
            self.vendedor_input.setCurrentIndex(-1)
            self.vendedor_input.clearEditText()
        except Exception as e:
            print(f"Erro ao carregar vendedores: {e}")
        
        filtro_layout1.addWidget(self.vendedor_input, 1)
        
        main_layout.addLayout(filtro_layout1)
        
        # Terceira linha de filtros - Cidade e Data Entrada
        filtro_layout2 = QHBoxLayout()
        filtro_layout2.setSpacing(10)
        
        # Campo Cidade - ComboBox Editável
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet("color: white; font-size: 16px;")
        cidade_label.setFixedWidth(80)  # Fixar largura para alinhamento
        filtro_layout2.addWidget(cidade_label)
        
        self.cidade_input = ComboBoxEditavel()
        
        # Preencher com cidades existentes
        try:
            # Obter cidades de pedidos anteriores
            cidades_pedidos = obter_cidades_pedidos()
            
            # Obter cidades das pessoas cadastradas
            pessoas = listar_pessoas()
            
            # Combinar as listas, evitando duplicatas
            todas_cidades = set(cidades_pedidos)
            for pessoa in pessoas:
                cidade = pessoa[9] if len(pessoa) > 9 else None  # Índice da cidade
                if cidade and cidade.strip():
                    todas_cidades.add(cidade)
            
            # Adicionar ao combobox
            self.cidade_input.addItems(sorted(todas_cidades))
            
            # Garantir que o ComboBox comece vazio
            self.cidade_input.setCurrentIndex(-1)
            self.cidade_input.clearEditText()
        except Exception as e:
            print(f"Erro ao carregar cidades: {e}")
        
        # Adicionar cidade ao layout com peso 1
        filtro_layout2.addWidget(self.cidade_input, 1)
        
        # Campo Data de Entrada
        data_entrada_label = QLabel("Data de Entrada")
        data_entrada_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(data_entrada_label)
        
        self.data_entrada = QDateEdit()
        self.data_entrada.setCalendarPopup(True)
        self.data_entrada.setDate(QDate.currentDate())
        self.data_entrada.setStyleSheet(dateedit_style)
        self.data_entrada.setFixedWidth(120)
        
        # Configurar calendário para data de entrada
        try:
            calendar = self.data_entrada.calendarWidget()
            calendar.setStyleSheet("""
                QCalendarWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    background-color: #003b57;
                    color: white;
                    selection-background-color: #005079;
                    selection-color: white;
                }
                QCalendarWidget QToolButton {
                    background-color: #003b57;
                    color: white;
                }
                QCalendarWidget QMenu {
                    background-color: #003b57;
                    color: white;
                }
            """)
        except:
            pass
            
        filtro_layout2.addWidget(self.data_entrada)
        
        main_layout.addLayout(filtro_layout2)
        
        # Quarta linha de filtros - Data de Saída e Botão Filtrar
        filtro_layout3 = QHBoxLayout()
        filtro_layout3.setSpacing(10)
        
        # Campo Data de Saída
        data_saida_label = QLabel("Data de Saída")
        data_saida_label.setStyleSheet("color: white; font-size: 16px;")
        data_saida_label.setFixedWidth(100)  # Fixar largura para alinhamento
        filtro_layout3.addWidget(data_saida_label)
        
        self.data_saida = QDateEdit()
        self.data_saida.setCalendarPopup(True)
        self.data_saida.setDate(QDate.currentDate())
        self.data_saida.setStyleSheet(dateedit_style)
        self.data_saida.setFixedWidth(120)
        
        # Configurar calendário para data de saída
        try:
            calendar = self.data_saida.calendarWidget()
            calendar.setStyleSheet("""
                QCalendarWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    background-color: #003b57;
                    color: white;
                    selection-background-color: #005079;
                    selection-color: white;
                }
                QCalendarWidget QToolButton {
                    background-color: #003b57;
                    color: white;
                }
                QCalendarWidget QMenu {
                    background-color: #003b57;
                    color: white;
                }
            """)
        except:
            pass
            
        filtro_layout3.addWidget(self.data_saida)
        
        # Adicionar espaço para empurrar o botão Filtrar para a direita
        filtro_layout3.addStretch(1)
        
        # Botão Filtrar
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
        """)
        self.btn_filtrar.clicked.connect(self.carregar_dados)
        self.btn_filtrar.setFixedWidth(100)
        filtro_layout3.addWidget(self.btn_filtrar)
        
        main_layout.addLayout(filtro_layout3)
        
        # Espaço vertical entre filtros e botões CRUD
        main_layout.addSpacing(10)
        
        # Botões de ação (CRUD)
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(15)
        
        # Espaço para alinhar os botões à direita
        acoes_layout.addStretch()
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
                border: 1px solid #0078d7;
            }
        """
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        try:
            # Ícone de adicionar
            self.btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        self.btn_cadastrar.setStyleSheet(btn_style)
        self.btn_cadastrar.clicked.connect(self.cadastrar)
        acoes_layout.addWidget(self.btn_cadastrar)
        
        # Botão Alterar
        self.btn_alterar = QPushButton("Alterar")
        try:
            # Ícone de editar
            self.btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        self.btn_alterar.setStyleSheet(btn_style)
        self.btn_alterar.clicked.connect(self.alterar)
        acoes_layout.addWidget(self.btn_alterar)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        try:
            # Ícone de lixeira
            self.btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        self.btn_excluir.setStyleSheet(btn_style)
        self.btn_excluir.clicked.connect(self.excluir)
        acoes_layout.addWidget(self.btn_excluir)
        
        main_layout.addLayout(acoes_layout)
        
        # Tabela de Pedidos
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                color: black;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Configurar tabela
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Num. Pedido", "Cliente", "Valor", "Data", "Vendedor"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.itemSelectionChanged.connect(self.selecionar_item)
        
        # Carregar dados do banco
        self.carregar_dados()
        
        main_layout.addWidget(self.tabela)
        
        # Garantir que todos os ComboBoxes comecem vazios
        for child in self.findChildren(ComboBoxEditavel):
            child.setCurrentIndex(-1)
            child.clearEditText()
    
    def carregar_dados(self, limpar_filtros=False):
        """Carrega dados do banco na tabela, com opção para limpar filtros"""
        try:
            # Limpar os filtros se solicitado
            if limpar_filtros:
                self.nome_input.setCurrentIndex(-1)
                self.nome_input.clearEditText()
                self.vendedor_input.setCurrentIndex(-1)
                self.vendedor_input.clearEditText()
                self.cidade_input.setCurrentIndex(-1)
                self.cidade_input.clearEditText()
                # Definir datas para o dia atual
                self.data_entrada.setDate(QDate.currentDate())
                self.data_saida.setDate(QDate.currentDate())
                
            # Limpar tabela
            self.tabela.setRowCount(0)
            
            # Obter filtros
            vendedor = self.vendedor_input.currentText()
            nome = self.nome_input.currentText()
            cidade = self.cidade_input.currentText()
            data_inicial = self.data_entrada.date().toString("dd/MM/yyyy")
            data_final = self.data_saida.date().toString("dd/MM/yyyy")
            
            # Buscar pedidos com os filtros
            pedidos = buscar_pedidos_por_filtro(
                vendedor=vendedor if vendedor else "",
                cliente=nome if nome else "",
                cidade=cidade if cidade else "",
                data_inicial=data_inicial if data_inicial else None,
                data_final=data_final if data_final else None
            )
            
            # Se não houver pedidos com os filtros, tentar buscar todos
            if not pedidos:
                try:
                    pedidos = listar_pedidos_venda()
                except Exception as e:
                    print(f"Erro ao listar pedidos: {e}")
                    # Criar alguns dados de exemplo se não houver dados no banco
                    pedidos = [
                        (1, "00001", "Empresa ABC Ltda", "Carlos", 2450.00, datetime.now(), "Pendente"),
                        (2, "00002", "João Silva", "Maria", 890.50, datetime.now(), "Pendente"),
                        (3, "00003", "Distribuidora XYZ", "Pedro", 5780.00, datetime.now(), "Pendente")
                    ]
            
            # Adicionar linhas na tabela
            for row, pedido in enumerate(pedidos):
                self.tabela.insertRow(row)
                
                # ID, NUMERO_PEDIDO, CLIENTE, VENDEDOR, VALOR, DATA_PEDIDO, STATUS
                id_pedido = pedido[0]
                num_pedido = pedido[1]
                cliente = pedido[2]
                vendedor = pedido[3]
                valor = pedido[4]
                data = pedido[5]
                
                # Formatar os dados
                valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if valor else ""
                
                if isinstance(data, datetime):
                    data_formatada = data.strftime("%d/%m/%Y")
                else:
                    data_formatada = str(data) if data else ""
                
                # Preencher as células
                self.tabela.setItem(row, 0, QTableWidgetItem(num_pedido))
                self.tabela.setItem(row, 1, QTableWidgetItem(cliente))
                self.tabela.setItem(row, 2, QTableWidgetItem(valor_formatado))
                self.tabela.setItem(row, 3, QTableWidgetItem(data_formatada))
                self.tabela.setItem(row, 4, QTableWidgetItem(vendedor))
                
                # Armazenar o ID na primeira coluna como dado oculto
                self.tabela.item(row, 0).setData(Qt.UserRole, id_pedido)
                
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar os pedidos: {str(e)}")
    
    def atualizar_apos_inclusao(self):
        """Método específico para atualizar a tabela após inclusão de um pedido"""
        print("Método atualizar_apos_inclusao chamado")
        # Carregar dados sem filtro para mostrar o novo pedido
        self.carregar_dados(limpar_filtros=True)
    
    def selecionar_item(self):
        """Preenche os campos quando uma linha é selecionada"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            
            # Preencher os campos de filtro com os dados da linha selecionada
            vendedor = self.tabela.item(row, 4).text()
            cliente = self.tabela.item(row, 1).text()
            
            # Definir os valores nos comboboxes
            index = self.vendedor_input.findText(vendedor)
            if index >= 0:
                self.vendedor_input.setCurrentIndex(index)
            else:
                self.vendedor_input.setCurrentText(vendedor)
            
            index = self.nome_input.findText(cliente)
            if index >= 0:
                self.nome_input.setCurrentIndex(index)
            else:
                self.nome_input.setCurrentText(cliente)
    
    def alterar(self):
        """Altera os dados de um pedido"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um pedido para alterar!")
            return
        
        row = selected_rows[0].row()
        id_pedido = self.tabela.item(row, 0).data(Qt.UserRole)  # Obter ID armazenado
        num_pedido = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        
        # Abrir o formulário para alteração
        self.abrir_formulario(num_pedido, nome)
    
    def excluir(self):
        """Exclui um pedido"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um pedido para excluir!")
            return
        
        row = selected_rows[0].row()
        id_pedido = self.tabela.item(row, 0).data(Qt.UserRole)  # Obter ID armazenado
        num_pedido = self.tabela.item(row, 0).text()
        
        # Criar uma caixa de diálogo de confirmação com estilo personalizado
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar Exclusão")
        msg_box.setText(f"Deseja realmente excluir o pedido {num_pedido}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #003b57;
            }
            QLabel { 
                color: white;
                background-color: #003b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.Yes:
            try:
                # Excluir do banco de dados
                sucesso = excluir_pedido(id_pedido)
                
                if sucesso:
                    # Remover da tabela
                    self.tabela.removeRow(row)
                    self.mostrar_mensagem("Sucesso", "Pedido excluído com sucesso!")
                else:
                    self.mostrar_mensagem("Erro", "Não foi possível excluir o pedido!")
            except Exception as e:
                print(f"Erro ao excluir pedido: {e}")
                self.mostrar_mensagem("Erro", f"Não foi possível excluir o pedido: {str(e)}")
    
    def cadastrar(self):
        """Abre a tela de cadastro de pedido"""
        # Limpar os filtros antes de abrir o formulário
        self.nome_input.setCurrentIndex(-1)
        self.nome_input.clearEditText()
        self.vendedor_input.setCurrentIndex(-1)
        self.vendedor_input.clearEditText()
        self.cidade_input.setCurrentIndex(-1)
        self.cidade_input.clearEditText()
        
        # Abrir o formulário
        self.abrir_formulario()
    
    def abrir_formulario(self, num_pedido=None, cliente=None):
        """Abre o formulário de pedido, para cadastro ou alteração"""
        try:
            # Criar uma instância do formulário diretamente
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Cadastro de Pedido de vendas")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("background-color: #003b57;")
            
            # Usar a classe FormularioPedidoVendas definida neste mesmo arquivo
            formulario_pedido_widget = FormularioPedidoVendas(
                janela_parent=self.form_window,
                num_pedido=num_pedido,
                cliente=cliente,
                tela_principal=self  # Passar uma referência direta para esta instância
            )
            self.form_window.setCentralWidget(formulario_pedido_widget)
            
            # Adicionar conexão para atualizar ao fechar o formulário
            self.form_window.closeEvent = lambda event: self.form_fechado(event)
            
            # Mostrar a janela de formulário
            self.form_window.show()
        except Exception as e:
            print(f"Erro ao abrir formulário: {e}")
            self.mostrar_mensagem("Erro", f"Não foi possível abrir o formulário: {str(e)}")
    
    def form_fechado(self, event):
        """Método chamado quando o formulário é fechado"""
        # Recarregar dados na tabela
        self.carregar_dados()
        
        # Continuar com o evento de fechamento normalmente
        event.accept()
    
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
                background-color: #003b57;
            }
            QLabel { 
                color: white;
                background-color: #003b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Verificar se a pasta de ícones existe, se não, criar
    icones_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico-img")
    if not os.path.exists(icones_dir):
        try:
            os.makedirs(icones_dir)
            print(f"Diretório de ícones criado: {icones_dir}")
        except Exception as e:
            print(f"Não foi possível criar o diretório de ícones: {e}")
    
    # Verificar se a tabela de pedidos existe
    try:
        verificar_tabela_pedidos_venda()
    except Exception as e:
        print(f"Erro ao verificar/criar tabela de pedidos: {e}")
    
    # Criar a janela principal
    window = QMainWindow()
    window.setWindowTitle("Sistema - Pedido de Vendas")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    # Criar o widget de pedidos de vendas
    pedido_vendas_widget = PedidoVendasWindow(window)
    window.setCentralWidget(pedido_vendas_widget)
    
    # Mostrar a janela
    window.show()
    
    # Iniciar o loop de eventos
    sys.exit(app.exec_())