import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QDateEdit)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize, QDate


class PedidoVendas(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.initUI()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
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
        
        # Layout para o título e botão voltar
        header_layout = QHBoxLayout()
        
        # Botão Voltar
        btn_voltar = QPushButton("Voltar")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        btn_voltar.clicked.connect(self.voltar)
        header_layout.addWidget(btn_voltar)
        
        # Título
        titulo = QLabel("Pedido de vendas")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Estilo para DateEdit
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
                border: none;
            }
        """
        
        # Primeira linha de filtros
        filtro_layout1 = QHBoxLayout()
        filtro_layout1.setSpacing(10)
        
        # Campo Vendedor
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout1.addWidget(vendedor_label)
        
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setStyleSheet(lineedit_style)
        filtro_layout1.addWidget(self.vendedor_input, 1)
        
        main_layout.addLayout(filtro_layout1)
        
        # Segunda linha de filtros
        filtro_layout2 = QHBoxLayout()
        filtro_layout2.setSpacing(10)
        
        # Campo Cidade
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(cidade_label)
        
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(lineedit_style)
        filtro_layout2.addWidget(self.cidade_input, 1)
        
        # Campo Data de Entrada
        data_entrada_label = QLabel("Data de Entrada")
        data_entrada_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(data_entrada_label)
        
        self.data_entrada = QDateEdit()
        self.data_entrada.setCalendarPopup(True)
        self.data_entrada.setDate(QDate.currentDate())
        self.data_entrada.setStyleSheet(dateedit_style)
        filtro_layout2.addWidget(self.data_entrada)
        
        main_layout.addLayout(filtro_layout2)
        
        # Terceira linha de filtros
        filtro_layout3 = QHBoxLayout()
        filtro_layout3.setSpacing(10)
        
        # Espaço para manter alinhamento
        spacer2 = QWidget()
        filtro_layout3.addWidget(spacer2)
        
        # Campo Data de Saída
        data_saida_label = QLabel("Data de Saída")
        data_saida_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout3.addWidget(data_saida_label)
        
        self.data_saida = QDateEdit()
        self.data_saida.setCalendarPopup(True)
        self.data_saida.setDate(QDate.currentDate())
        self.data_saida.setStyleSheet(dateedit_style)
        filtro_layout3.addWidget(self.data_saida)
        
        main_layout.addLayout(filtro_layout3)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(15)
        
        # Espaço para alinhar os botões como na imagem
        acoes_layout.addStretch()
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px 20px;
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
        btn_cadastrar = QPushButton("Cadastrar")
        try:
            btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        btn_cadastrar.setStyleSheet(btn_style)
        btn_cadastrar.clicked.connect(self.cadastrar)
        acoes_layout.addWidget(btn_cadastrar)
        
        # Botão Alterar
        btn_alterar = QPushButton("Alterar")
        try:
            btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        btn_alterar.setStyleSheet(btn_style)
        btn_alterar.clicked.connect(self.alterar)
        acoes_layout.addWidget(btn_alterar)
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        try:
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet(btn_style)
        btn_excluir.clicked.connect(self.excluir)
        acoes_layout.addWidget(btn_excluir)
        
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
        self.tabela.setHorizontalHeaderLabels(["Num. Pedido", "Nome", "Valor", "Data", "Vendedor"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.itemSelectionChanged.connect(self.selecionar_item)
        
        # Adicionar alguns exemplos de dados
        self.carregar_dados_exemplo()
        
        main_layout.addWidget(self.tabela)
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Dados de exemplo (número do pedido, nome, valor, data, vendedor)
        dados = [
            ("00001", "Empresa ABC Ltda", "R$ 2.450,00", "01/04/2023", "Carlos"),
            ("00002", "João Silva", "R$ 890,50", "05/04/2023", "Maria"),
            ("00003", "Distribuidora XYZ", "R$ 5.780,00", "08/04/2023", "Pedro"),
            ("00004", "Ana Souza", "R$ 1.200,00", "12/04/2023", "Carlos"),
            ("00005", "Mercado Central", "R$ 3.450,00", "15/04/2023", "Maria")
        ]
        
        # Adicionar linhas
        for row, (num_pedido, nome, valor, data, vendedor) in enumerate(dados):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(num_pedido))
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(valor))
            self.tabela.setItem(row, 3, QTableWidgetItem(data))
            self.tabela.setItem(row, 4, QTableWidgetItem(vendedor))
    
    def selecionar_item(self):
        """Preenche os campos quando uma linha é selecionada"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            # Aqui você poderia preencher campos se necessário
    
    def voltar(self):
        """Ação do botão voltar"""
        # Se a janela foi criada a partir de outra janela (tem um parent)
        if self.janela_parent:
            # Verifica se o parent é um QMainWindow
            if isinstance(self.janela_parent, QMainWindow):
                self.janela_parent.close()
            # Se o parent for um widget dentro de uma aplicação
            else:
                from PyQt5.QtWidgets import QApplication
                # Verifica se há uma janela principal ativa
                main_window = QApplication.activeWindow()
                if main_window:
                    main_window.close()
                    
        # Se estiver sendo executado como aplicação principal (sem parent)
        else:
            # Encerra a aplicação
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().quit()
    
    def alterar(self):
        """Altera os dados de um pedido"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um pedido para alterar!")
            return
        
        row = selected_rows[0].row()
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
        self.tabela.removeRow(row)
        
        self.mostrar_mensagem("Sucesso", "Pedido excluído com sucesso!")
    
    def cadastrar(self):
        """Abre a tela de cadastro de pedido"""
        self.abrir_formulario()
    
    def abrir_formulario(self, num_pedido=None, cliente=None):
        """Abre o formulário de pedido, para cadastro ou alteração"""
        try:
            # Importar o formulário de pedidos
            from formulario_pedido_vendas import FormularioPedidoVendas
            
            # Criar uma instância do formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Cadastro de Pedido de vendas")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("background-color: #003b57;")
            
            # Configurar o widget central
            formulario_pedido_widget = FormularioPedidoVendas(
                janela_parent=self.form_window,
                num_pedido=num_pedido,
                cliente=cliente
            )
            self.form_window.setCentralWidget(formulario_pedido_widget)
            
            # Mostrar a janela de formulário
            self.form_window.show()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Não foi possível abrir o formulário: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        from PyQt5.QtWidgets import QMessageBox
        
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
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
                background-color: #003b57;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 2px;
            }
        """)
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Sistema - Pedido de Vendas")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    pedido_vendas_widget = PedidoVendas(window)  # Passa a janela como parent
    window.setCentralWidget(pedido_vendas_widget)
    
    window.show()
    sys.exit(app.exec_())