import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class Produtos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        # Dados locais para armazenar produtos (substituindo a necessidade de API)
        self.produtos_data = []
        self.initUI()
        
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
        titulo = QLabel("Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Primeira linha de campos
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(20)
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        codigo_layout.addWidget(self.codigo_input)
        linha1_layout.addLayout(codigo_layout)
        
        # Campo Nome
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        nome_layout.addWidget(self.nome_input)
        linha1_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha de campos
        linha2_layout = QHBoxLayout()
        linha2_layout.setSpacing(20)
        
        # Campo Código de Barras
        barras_layout = QHBoxLayout()
        barras_label = QLabel("Código de Barras:")
        barras_label.setStyleSheet("color: white; font-size: 14px;")
        barras_layout.addWidget(barras_label)
        
        self.barras_input = QLineEdit()
        self.barras_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        barras_layout.addWidget(self.barras_input)
        linha2_layout.addLayout(barras_layout, 1)  # 1 para expandir
        
        # Campo Grupo
        grupo_layout = QHBoxLayout()
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet("color: white; font-size: 14px;")
        grupo_layout.addWidget(grupo_label)
        
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Alimentos")
        self.grupo_combo.addItem("Bebidas")
        self.grupo_combo.addItem("Limpeza")
        self.grupo_combo.addItem("Higiene")
        self.grupo_combo.addItem("Hortifruti")
        grupo_layout.addWidget(self.grupo_combo)
        linha2_layout.addLayout(grupo_layout)
        
        main_layout.addLayout(linha2_layout)
        
        # Terceira linha de campos
        linha3_layout = QHBoxLayout()
        linha3_layout.setSpacing(20)
        
        # Campo Marca
        marca_layout = QHBoxLayout()
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet("color: white; font-size: 14px;")
        marca_layout.addWidget(marca_label)
        
        self.marca_input = QLineEdit()
        self.marca_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        marca_layout.addWidget(self.marca_input)
        linha3_layout.addLayout(marca_layout, 1)  # 1 para expandir
        
        # Botões de ação
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(10)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
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
        botoes_layout.addWidget(btn_alterar)
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        try:
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet(btn_style)
        btn_excluir.clicked.connect(self.excluir)
        botoes_layout.addWidget(btn_excluir)
        
        # Botão Cadastrar
        btn_cadastrar = QPushButton("Cadastrar")
        try:
            btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        btn_cadastrar.setStyleSheet(btn_style)
        btn_cadastrar.clicked.connect(self.cadastrar)
        botoes_layout.addWidget(btn_cadastrar)
        
        linha3_layout.addLayout(botoes_layout)
        
        main_layout.addLayout(linha3_layout)
        
        # Tabela de Produtos
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                color: black;
            }
            QHeaderView::section {
                background-color: #fffff0;
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
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Preço de Venda", "Quant. Estoque"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.itemSelectionChanged.connect(self.selecionar_item)
        
        # Carregar dados locais
        self.carregar_produtos()
        
        main_layout.addWidget(self.tabela)
    
    def carregar_produtos(self):
        """Carrega dados de produtos (dados locais)"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Se não existirem dados ainda, inicializar com dados de exemplo
        if not self.produtos_data:
            self.produtos_data = [
                {
                    "codigo": "001",
                    "nome": "Arroz Tipo 1 - 5kg",
                    "preco_venda": 23.90,
                    "quantidade_estoque": 50,
                    "codigo_barras": "7891234567890",
                    "marca": "Tio João",
                    "grupo": "Alimentos"
                },
                {
                    "codigo": "002",
                    "nome": "Feijão Carioca - 1kg",
                    "preco_venda": 8.50,
                    "quantidade_estoque": 75,
                    "codigo_barras": "7892345678901",
                    "marca": "Camil",
                    "grupo": "Alimentos"
                },
                {
                    "codigo": "003",
                    "nome": "Leite Integral - 1L",
                    "preco_venda": 4.99,
                    "quantidade_estoque": 120,
                    "codigo_barras": "7893456789012",
                    "marca": "Piracanjuba",
                    "grupo": "Bebidas"
                },
                {
                    "codigo": "004",
                    "nome": "Café Moído - 500g",
                    "preco_venda": 15.90,
                    "quantidade_estoque": 65,
                    "codigo_barras": "7894567890123",
                    "marca": "Três Corações",
                    "grupo": "Alimentos"
                }
            ]
        
        # Preencher tabela com os dados
        for row, produto in enumerate(self.produtos_data):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(produto["codigo"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto["nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}".replace('.', ',')))
            self.tabela.setItem(row, 3, QTableWidgetItem(str(produto["quantidade_estoque"])))
    
    def selecionar_item(self):
        """Preenche os campos quando uma linha é selecionada"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            codigo = self.tabela.item(row, 0).text()
            
            # Encontrar o produto correspondente nos dados locais
            produto = next((p for p in self.produtos_data if p["codigo"] == codigo), None)
            
            if produto:
                self.codigo_input.setText(str(produto["codigo"]))
                self.nome_input.setText(produto["nome"])
                
                # Verificar se os dados existem antes de atribuir
                if "codigo_barras" in produto and produto["codigo_barras"]:
                    self.barras_input.setText(produto["codigo_barras"])
                else:
                    self.barras_input.setText("")
                    
                if "marca" in produto and produto["marca"]:
                    self.marca_input.setText(produto["marca"])
                else:
                    self.marca_input.setText("")
                    
                # Selecionar o grupo, se existir
                if "grupo" in produto and produto["grupo"]:
                    index = self.grupo_combo.findText(produto["grupo"])
                    if index >= 0:
                        self.grupo_combo.setCurrentIndex(index)
                    else:
                        self.grupo_combo.setCurrentIndex(0)
                else:
                    self.grupo_combo.setCurrentIndex(0)
            else:
                # Fallback para os dados da tabela
                self.codigo_input.setText(self.tabela.item(row, 0).text())
                self.nome_input.setText(self.tabela.item(row, 1).text())
                self.barras_input.setText("")
                self.marca_input.setText("")
                self.grupo_combo.setCurrentIndex(0)
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual se estiver em uma janela separada
        if hasattr(self, 'parent_window') and self.parent_window:
            self.parent_window.close()
        # Alternativamente, você pode implementar a lógica para voltar para outra tela
        print("Voltando para a tela anterior")
    
    def alterar(self):
        """Altera os dados de um produto"""
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        codigo_barras = self.barras_input.text()
        marca = self.marca_input.text()
        grupo = self.grupo_combo.currentText()
        
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Preencha pelo menos o código e o nome!")
            return
            
        if grupo == "Selecione um grupo":
            grupo = ""  # Não enviar grupo se não foi selecionado
        
        # Encontrar o produto a ser alterado
        produto_encontrado = False
        for i, produto in enumerate(self.produtos_data):
            if produto["codigo"] == codigo:
                # Atualizar os dados do produto
                self.produtos_data[i]["nome"] = nome
                self.produtos_data[i]["codigo_barras"] = codigo_barras
                self.produtos_data[i]["marca"] = marca
                self.produtos_data[i]["grupo"] = grupo if grupo != "" else None
                
                produto_encontrado = True
                break
        
        if produto_encontrado:
            # Recarregar a tabela
            self.carregar_produtos()
            self.mostrar_mensagem("Sucesso", "Produto alterado com sucesso!")
            
            # Limpar campos
            self.codigo_input.clear()
            self.nome_input.clear()
            self.barras_input.clear()
            self.marca_input.clear()
            self.grupo_combo.setCurrentIndex(0)
        else:
            self.mostrar_mensagem("Erro", "Produto não encontrado!")
    
    def excluir(self):
        """Exclui um produto"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um produto para excluir!")
            return
            
        row = selected_rows[0].row()
        codigo = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        
        # Confirmar exclusão
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar exclusão", 
            f"Deseja realmente excluir o produto '{nome}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirmacao == QMessageBox.No:
            return
        
        # Encontrar e remover o produto
        for i, produto in enumerate(self.produtos_data):
            if produto["codigo"] == codigo:
                del self.produtos_data[i]
                break
        
        # Atualizar a tabela
        self.tabela.removeRow(row)
        
        # Limpar os campos
        self.codigo_input.clear()
        self.nome_input.clear()
        self.barras_input.clear()
        self.marca_input.clear()
        self.grupo_combo.setCurrentIndex(0)
        
        self.mostrar_mensagem("Sucesso", "Produto excluído com sucesso!")
    
    def load_formulario_produtos(self):
        """
        Carrega dinamicamente o módulo formulario_produtos.py
        Isso permite que o arquivo seja encontrado mesmo quando compilado para .exe
        """
        try:
            # Tente primeiro com importação direta (para ambiente de desenvolvimento)
            try:
                # Importação direta usando o módulo
                from geral.formulario_produtos import FormularioProdutos
                print("Importação direta de FormularioProdutos bem-sucedida")
                return FormularioProdutos
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_produtos.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_produtos.py")
                
                # Se o arquivo não existir, vamos criar um básico
                if not os.path.exists(module_path):
                    self.criar_formulario_produtos_padrao(module_path)
                
                # Carregar o módulo dinamicamente
                module_name = "formulario_produtos"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Não foi possível carregar o módulo {module_name}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Retornar a classe FormularioProdutos
                if hasattr(module, "FormularioProdutos"):
                    return getattr(module, "FormularioProdutos")
                else:
                    raise ImportError(f"A classe FormularioProdutos não foi encontrada no módulo {module_name}")
        except Exception as e:
            print(f"Erro ao carregar FormularioProdutos: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}", QMessageBox.Critical)
            return None
            
    def criar_formulario_produtos_padrao(self, filepath):
        """Cria um arquivo formulario_produtos.py básico se não existir"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''\
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox, QFormLayout,
                             QDoubleSpinBox, QSpinBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FormularioProdutos(QWidget):
    def __init__(self, parent=None, api_url=None):
        super().__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Cadastro de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; }"
        
        # Estilo para os inputs
        input_style = """
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 30px;
            }
        """
        
        # Campo Código
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        form_layout.addRow(self.codigo_label, self.codigo_input)
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setStyleSheet(label_style)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(input_style)
        form_layout.addRow(self.nome_label, self.nome_input)
        
        # Campo Código de Barras
        self.barras_label = QLabel("Código de Barras:")
        self.barras_label.setStyleSheet(label_style)
        self.barras_input = QLineEdit()
        self.barras_input.setStyleSheet(input_style)
        form_layout.addRow(self.barras_label, self.barras_input)
        
        # Campo Marca
        self.marca_label = QLabel("Marca:")
        self.marca_label.setStyleSheet(label_style)
        self.marca_input = QLineEdit()
        self.marca_input.setStyleSheet(input_style)
        form_layout.addRow(self.marca_label, self.marca_input)
        
        # Campo Grupo
        self.grupo_label = QLabel("Grupo:")
        self.grupo_label.setStyleSheet(label_style)
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(input_style)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Alimentos")
        self.grupo_combo.addItem("Bebidas")
        self.grupo_combo.addItem("Limpeza")
        self.grupo_combo.addItem("Higiene")
        self.grupo_combo.addItem("Hortifruti")
        form_layout.addRow(self.grupo_label, self.grupo_combo)
        
        # Campo Preço de Custo
        self.preco_custo_label = QLabel("Preço de Custo:")
        self.preco_custo_label.setStyleSheet(label_style)
        self.preco_custo_input = QDoubleSpinBox()
        self.preco_custo_input.setStyleSheet(input_style)
        self.preco_custo_input.setRange(0.01, 99999.99)
        self.preco_custo_input.setDecimals(2)
        self.preco_custo_input.setSingleStep(0.10)
        self.preco_custo_input.setPrefix("R$ ")
        form_layout.addRow(self.preco_custo_label, self.preco_custo_input)
        
        # Campo Preço de Venda
        self.preco_venda_label = QLabel("Preço de Venda:")
        self.preco_venda_label.setStyleSheet(label_style)
        self.preco_venda_input = QDoubleSpinBox()
        self.preco_venda_input.setStyleSheet(input_style)
        self.preco_venda_input.setRange(0.01, 99999.99)
        self.preco_venda_input.setDecimals(2)
        self.preco_venda_input.setSingleStep(0.10)
        self.preco_venda_input.setPrefix("R$ ")
        form_layout.addRow(self.preco_venda_label, self.preco_venda_input)
        
        # Campo Estoque
        self.estoque_label = QLabel("Quantidade em Estoque:")
        self.estoque_label.setStyleSheet(label_style)
        self.estoque_input = QSpinBox()
        self.estoque_input.setStyleSheet(input_style)
        self.estoque_input.setRange(0, 99999)
        form_layout.addRow(self.estoque_label, self.estoque_input)
        
        main_layout.addLayout(form_layout)
        
        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(15)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """
        
        # Botão Voltar
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setStyleSheet(btn_style)
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet(btn_style)
        self.btn_salvar.clicked.connect(self.salvar)
        
        botoes_layout.addWidget(self.btn_voltar)
        botoes_layout.addWidget(self.btn_salvar)
        
        botoes_container = QHBoxLayout()
        botoes_container.addStretch()
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch()
        
        main_layout.addLayout(botoes_container)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
    def voltar(self):
        """Fecha a janela e volta para a tela anterior"""
        if self.parent and hasattr(self.parent, 'form_window'):
            self.parent.form_window.close()
    
    def salvar(self):
        """Salva os dados do produto"""
        # Validação básica
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        
        if not codigo or not nome:
            QMessageBox.warning(self, "Campos obrigatórios", "Os campos Código e Nome são obrigatórios.")
            return
        
        # Capturar outros dados
        codigo_barras = self.barras_input.text()
        marca = self.marca_input.text()
        grupo = self.grupo_combo.currentText()
        if grupo == "Selecione um grupo":
            grupo = ""
            
        preco_custo = self.preco_custo_input.value()
        preco_venda = self.preco_venda_input.value()
        estoque = self.estoque_input.value()
        
        # Verificar se o código já existe
        for produto in self.parent.produtos_data:
            if produto["codigo"] == codigo:
                QMessageBox.warning(self, "Código duplicado", "Já existe um produto com este código.")
                return
        
        # Criar novo produto
        novo_produto = {
            "codigo": codigo,
            "nome": nome,
            "codigo_barras": codigo_barras,
            "marca": marca,
            "grupo": grupo if grupo != "" else None,
            "preco_custo": preco_custo,
            "preco_venda": preco_venda,
            "quantidade_estoque": estoque
        }
        
        # Adicionar à lista de produtos
        self.parent.produtos_data.append(novo_produto)
        
        # Atualizar a tabela na tela principal
        if hasattr(self.parent, 'carregar_produtos'):
            self.parent.carregar_produtos()
        
        # Mostrar mensagem de sucesso
        QMessageBox.information(self, "Sucesso", "Produto cadastrado com sucesso!")
        
        # Fechar o formulário
        if self.parent and hasattr(self.parent, 'form_window'):
            self.parent.form_window.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormularioProdutos()
    window.show()
    sys.exit(app.exec_())
''')
        except Exception as e:
            print(f"Erro ao criar arquivo formulario_produtos.py: {str(e)}")
            
    def cadastrar(self):
        """Abre a tela de cadastro de produto"""
        try:
            # Verificar se já existe uma janela de formulário aberta
            if hasattr(self, 'form_window') and self.form_window.isVisible():
                # Se existir, apenas ativá-la em vez de criar uma nova
                self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
                self.form_window.activateWindow()
                self.form_window.raise_()
                return
            
            # Carregar dinamicamente a classe FormularioProdutos
            FormularioProdutos = self.load_formulario_produtos()
            if FormularioProdutos is None:
                return
            
            # Criar uma nova janela para o formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Cadastro de Produtos")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("background-color: #043b57;")
            
            # Configurar o widget central
            formulario_produtos_widget = FormularioProdutos(self)
            self.form_window.setCentralWidget(formulario_produtos_widget)
            
            # Mostrar a janela de formulário
            self.form_window.show()
        except AttributeError as e:
            self.mostrar_mensagem("Erro", f"Módulo de formulários carregado, mas há um problema com a classe: {str(e)}")
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao abrir o formulário: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        
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


class ProdutosWindow(QMainWindow):
    """Classe para gerenciar a janela de produtos quando executado como script principal"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Produtos")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #043b57;")
        
        # Configurando o widget central
        self.produtos_widget = Produtos(self)
        self.setCentralWidget(self.produtos_widget)


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProdutosWindow()
    window.show()
    sys.exit(app.exec_())