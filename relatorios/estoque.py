#Estoque.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

# Importar a classe do formulário de produtos
import sys
import os
# Adicionar o diretório raiz do projeto ao path para encontrar o módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Importar o módulo de outra pasta
from produtos_e_servicos.formulario_produtos import FormularioProdutos


class EstoqueWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.form_window = None  # Referência para a janela de formulário
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
        titulo = QLabel("Estoque")
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
        
        # Estilo para QComboBox
        combobox_style = """
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
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #0078d7;
                selection-color: white;
            }
        """
        
        # Primeira linha: Código e Nome
        linha1_layout = QHBoxLayout()
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 16px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setFixedWidth(200)
        codigo_layout.addWidget(self.codigo_input)
        
        linha1_layout.addLayout(codigo_layout)
        
        # Espaçamento
        linha1_layout.addSpacing(30)
        
        # Campo Nome
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 16px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        nome_layout.addWidget(self.nome_input, 1)  # 1 para expandir
        
        linha1_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha: Marca e Grupo
        linha2_layout = QHBoxLayout()
        
        # Campo Marca
        marca_layout = QHBoxLayout()
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet("color: white; font-size: 16px;")
        marca_layout.addWidget(marca_label)
        
        self.marca_input = QLineEdit()
        self.marca_input.setStyleSheet(lineedit_style)
        marca_layout.addWidget(self.marca_input, 1)  # 1 para expandir
        
        linha2_layout.addLayout(marca_layout)
        
        # Espaçamento
        linha2_layout.addSpacing(30)
        
        # Campo Grupo
        grupo_layout = QHBoxLayout()
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet("color: white; font-size: 16px;")
        grupo_layout.addWidget(grupo_label)
        
        self.grupo_input = QComboBox()
        self.grupo_input.addItems(["Selecione um grupo", "Alimentos", "Bebidas", "Limpeza", "Higiene", "Eletrônicos", "Vestuário", "Outros"])
        self.grupo_input.setStyleSheet(combobox_style)
        grupo_layout.addWidget(self.grupo_input, 1)  # 1 para expandir
        
        linha2_layout.addLayout(grupo_layout)
        
        main_layout.addLayout(linha2_layout)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(15)
        
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
        
        # Botão Cadastrar
        btn_cadastrar = QPushButton("Cadastrar")
        try:
            btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        btn_cadastrar.setStyleSheet(btn_style)
        btn_cadastrar.clicked.connect(self.cadastrar)
        acoes_layout.addWidget(btn_cadastrar)
        
        main_layout.addLayout(acoes_layout)
        
        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Código", "Cliente", "Quant. Estoque", "Grupo", "Marca"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                gridline-color: #cccccc;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        main_layout.addWidget(self.tabela)
        
        # Adicionar alguns dados de exemplo na tabela
        self.carregar_dados_exemplo()
        
        # Conectar evento de seleção de linha na tabela
        self.tabela.itemClicked.connect(self.selecionar_item)
        
        # Lista para armazenar os dados dos produtos
        self.produtos_data = self.obter_dados_exemplo()
    
    def obter_dados_exemplo(self):
        """Retorna os dados de exemplo em formato de dicionário"""
        return [
            {
                "codigo": "001",
                "nome": "Notebook Dell",
                "quantidade_estoque": 10,
                "grupo": "Eletrônicos",
                "marca": "Dell",
                "preco_venda": 3999.99,
                "preco_custo": 3200.00,
                "codigo_barras": "7891234567890",
                "unidade": "Unidade (un)"
            },
            {
                "codigo": "002",
                "nome": "Smartphone Galaxy",
                "quantidade_estoque": 15,
                "grupo": "Eletrônicos",
                "marca": "Samsung",
                "preco_venda": 1999.99,
                "preco_custo": 1500.00,
                "codigo_barras": "7891234567891",
                "unidade": "Unidade (un)"
            },
            {
                "codigo": "003",
                "nome": "Camiseta Polo",
                "quantidade_estoque": 25,
                "grupo": "Vestuário",
                "marca": "Lacoste",
                "preco_venda": 199.99,
                "preco_custo": 120.00,
                "codigo_barras": "7891234567892",
                "unidade": "Unidade (un)"
            },
            {
                "codigo": "004",
                "nome": "Sabão em Pó",
                "quantidade_estoque": 30,
                "grupo": "Limpeza",
                "marca": "OMO",
                "preco_venda": 15.99,
                "preco_custo": 10.50,
                "codigo_barras": "7891234567893",
                "unidade": "Pacote (pct)"
            },
            {
                "codigo": "005",
                "nome": "Refrigerante Cola",
                "quantidade_estoque": 50,
                "grupo": "Bebidas",
                "marca": "Coca-Cola",
                "preco_venda": 8.99,
                "preco_custo": 5.50,
                "codigo_barras": "7891234567894",
                "unidade": "Garrafa (gf)"
            }
        ]
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        dados = [
            ("001", "Notebook Dell", "10", "Eletrônicos", "Dell"),
            ("002", "Smartphone Galaxy", "15", "Eletrônicos", "Samsung"),
            ("003", "Camiseta Polo", "25", "Vestuário", "Lacoste"),
            ("004", "Sabão em Pó", "30", "Limpeza", "OMO"),
            ("005", "Refrigerante Cola", "50", "Bebidas", "Coca-Cola")
        ]
        
        self.tabela.setRowCount(len(dados))
        for row, (codigo, nome, quantidade, grupo, marca) in enumerate(dados):
            self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(quantidade))
            self.tabela.setItem(row, 3, QTableWidgetItem(grupo))
            self.tabela.setItem(row, 4, QTableWidgetItem(marca))
    
    def carregar_produtos(self):
        """Atualiza a tabela de produtos com os dados do self.produtos_data"""
        self.tabela.setRowCount(len(self.produtos_data))
        for row, produto in enumerate(self.produtos_data):
            self.tabela.setItem(row, 0, QTableWidgetItem(produto["codigo"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto["nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(str(produto["quantidade_estoque"])))
            self.tabela.setItem(row, 3, QTableWidgetItem(produto["grupo"] if produto["grupo"] else ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(produto["marca"] if produto["marca"] else ""))
    
    def selecionar_item(self, item):
        """Quando um item da tabela é selecionado, preenche os campos"""
        row = item.row()
        
        # Preencher os campos com os dados da linha selecionada
        self.codigo_input.setText(self.tabela.item(row, 0).text())
        self.nome_input.setText(self.tabela.item(row, 1).text())
        
        # Definir o grupo
        grupo_selecionado = self.tabela.item(row, 3).text()
        index = self.grupo_input.findText(grupo_selecionado)
        if index >= 0:
            self.grupo_input.setCurrentIndex(index)
        
        # Definir a marca
        self.marca_input.setText(self.tabela.item(row, 4).text())
    
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
    
    def abrir_formulario_produto(self, produto_para_editar=None):
        """Abre o formulário de produtos para cadastro ou edição"""
        # Cria uma nova janela para o formulário
        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Formulário de Produtos")
        self.form_window.setGeometry(150, 150, 800, 500)
        self.form_window.setStyleSheet("background-color: #043b57;")
        
        # Cria o widget do formulário
        form_widget = FormularioProdutos(self)
        self.form_window.setCentralWidget(form_widget)
        
        # Se for edição, preenche o formulário com os dados do produto
        if produto_para_editar:
            form_widget.codigo_input.setText(produto_para_editar["codigo"])
            form_widget.nome_input.setText(produto_para_editar["nome"])
            
            # Se tiver código de barras
            if "codigo_barras" in produto_para_editar and produto_para_editar["codigo_barras"]:
                form_widget.barras_input.setText(produto_para_editar["codigo_barras"])
            
            # Se tiver marca
            if "marca" in produto_para_editar and produto_para_editar["marca"]:
                index = form_widget.marca_combo.findText(produto_para_editar["marca"])
                if index >= 0:
                    form_widget.marca_combo.setCurrentIndex(index)
            
            # Se tiver grupo
            if "grupo" in produto_para_editar and produto_para_editar["grupo"]:
                index = form_widget.grupo_combo.findText(produto_para_editar["grupo"])
                if index >= 0:
                    form_widget.grupo_combo.setCurrentIndex(index)
            
            # Se tiver preço de venda
            if "preco_venda" in produto_para_editar:
                form_widget.preco_venda_input.setText(str(produto_para_editar["preco_venda"]).replace(".", ","))
            
            # Se tiver preço de custo
            if "preco_custo" in produto_para_editar:
                form_widget.preco_compra_input.setText(str(produto_para_editar["preco_custo"]).replace(".", ","))
            
            # Se tiver unidade
            if "unidade" in produto_para_editar and produto_para_editar["unidade"]:
                index = form_widget.unidade_combo.findText(produto_para_editar["unidade"])
                if index >= 0:
                    form_widget.unidade_combo.setCurrentIndex(index)
            
            # Muda o texto do botão Incluir para Atualizar
            form_widget.btn_incluir.setText("Atualizar")
            
            # Desabilita o campo de código (não pode ser alterado)
            form_widget.codigo_input.setReadOnly(True)
        
        # Mostra a janela
        self.form_window.show()
    
    def alterar(self):
        """Ação do botão alterar"""
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um produto para alterar!")
            return
        
        # Obter a linha selecionada
        row = self.tabela.currentRow()
        
        # Encontrar o produto selecionado nos dados
        codigo = self.tabela.item(row, 0).text()
        produto_para_editar = None
        
        for produto in self.produtos_data:
            if produto["codigo"] == codigo:
                produto_para_editar = produto
                break
        
        if produto_para_editar:
            # Abrir o formulário para edição
            self.abrir_formulario_produto(produto_para_editar)
        else:
            self.mostrar_mensagem("Erro", "Produto não encontrado no banco de dados.")
    
    def excluir(self):
        """Ação do botão excluir"""
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um produto para excluir!")
            return
        
        # Obter a linha selecionada
        row = self.tabela.currentRow()
        codigo = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        
        # Confirmar exclusão
        from PyQt5.QtWidgets import QMessageBox
        confirma = QMessageBox()
        confirma.setIcon(QMessageBox.Question)
        confirma.setWindowTitle("Confirmar Exclusão")
        confirma.setText(f"Deseja realmente excluir o produto {codigo} - {nome}?")
        confirma.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirma.setStyleSheet("""
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
        
        resposta = confirma.exec_()
        
        if resposta == QMessageBox.Yes:
            # Remover o produto da lista de dados
            for i, produto in enumerate(self.produtos_data):
                if produto["codigo"] == codigo:
                    del self.produtos_data[i]
                    break
            
            # Remover a linha da tabela
            self.tabela.removeRow(row)
            self.mostrar_mensagem("Sucesso", "Produto excluído com sucesso!")
            
            # Limpar os campos
            self.limpar_campos()
    
    def cadastrar(self):
        """Ação do botão cadastrar - abre o formulário para cadastro"""
        # Abrir o formulário de produtos sem dados (para novo cadastro)
        self.abrir_formulario_produto()
    
    def limpar_campos(self):
        """Limpa os campos do formulário"""
        self.codigo_input.clear()
        self.nome_input.clear()
        self.marca_input.clear()
        self.grupo_input.setCurrentIndex(0)
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        from PyQt5.QtWidgets import QMessageBox
        
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Sucesso" in titulo:
            msg_box.setIcon(QMessageBox.Information)
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
    window.setWindowTitle("Sistema - Estoque")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    estoque_widget = EstoqueWindow(window)  # Passa a janela como parent
    window.setCentralWidget(estoque_widget)
    
    window.show()
    sys.exit(app.exec_())