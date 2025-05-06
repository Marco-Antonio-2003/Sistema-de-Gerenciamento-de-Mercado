import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QMessageBox,
                           QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

class CustomMessageBox(QMessageBox):
    """Classe personalizada para QMessageBox com cores customizadas"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilo para os botões do MessageBox
        self.setStyleSheet("""
            QMessageBox {
                background-color: #003b57;
                color: white;
            }
            QLabel {
                color: white;
                background-color: #003b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: 1px solid #007ab3;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)

class ClientesWindow(QWidget):
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
        
        # Layout para o título centralizado (sem botão voltar)
        header_layout = QHBoxLayout()
        
        # Título centralizado
        titulo = QLabel("Clientes")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                min-height: 25px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Estilo para ComboBox
        combobox_style = """
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                min-height: 25px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #003b57;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
        """
        
        # Campos de filtro
        filtro_layout = QHBoxLayout()
        filtro_layout.setSpacing(10)
        
        # Campo Código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setFixedWidth(150)
        filtro_layout.addWidget(self.codigo_input)
        
        # Campo Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        filtro_layout.addWidget(self.nome_input, 1)
        
        main_layout.addLayout(filtro_layout)
        
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
        
        # Campo Tipo (Física/Jurídica)
        tipo_label = QLabel("Tipo:")
        tipo_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(tipo_label)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Todos", "Física", "Jurídica"])
        self.tipo_combo.setStyleSheet(combobox_style)
        self.tipo_combo.setFixedWidth(150)
        self.tipo_combo.currentIndexChanged.connect(self.tipo_alterado)
        filtro_layout2.addWidget(self.tipo_combo)
        
        # Campo CPF/CNPJ
        self.cpfcnpj_label = QLabel("CPF/CNPJ:")
        self.cpfcnpj_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(self.cpfcnpj_label)
        
        self.cpfcnpj_input = QLineEdit()
        self.cpfcnpj_input.setStyleSheet(lineedit_style)
        self.cpfcnpj_input.setPlaceholderText("000.000.000-00 ou 00.000.000/0001-00")
        self.cpfcnpj_input.textChanged.connect(self.formatar_cpf_cnpj)
        filtro_layout2.addWidget(self.cpfcnpj_input, 1)
        
        main_layout.addLayout(filtro_layout2)
        
        # Terceira linha de filtros
        filtro_layout3 = QHBoxLayout()
        filtro_layout3.setSpacing(10)
        
        # Campo Vendedor
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout3.addWidget(vendedor_label)
        
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setStyleSheet(lineedit_style)
        filtro_layout3.addWidget(self.vendedor_input, 1)
        
        main_layout.addLayout(filtro_layout3)
        
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
        
        # Tabela de clientes
        self.table = QTableWidget()  # Troquei o nome para 'table' para manter consistência
        self.table.setColumnCount(5)  # Adicionei coluna para o tipo (Física/Jurídica)
        self.table.setHorizontalHeaderLabels(["Código", "Nome", "Vendedor", "Tipo", "CPF/CNPJ"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                gridline-color: #cccccc;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        self.table.setMinimumHeight(300)
        
        main_layout.addWidget(self.table)
        
        # Adicionar alguns dados de exemplo na tabela
        self.carregar_dados_exemplo()
    
    def tipo_alterado(self, index):
        """Atualiza o rótulo e placeholder do campo CPF/CNPJ com base no tipo selecionado"""
        tipo = self.tipo_combo.currentText()
        
        if tipo == "Física":
            self.cpfcnpj_label.setText("CPF:")
            self.cpfcnpj_input.setPlaceholderText("000.000.000-00")
        elif tipo == "Jurídica":
            self.cpfcnpj_label.setText("CNPJ:")
            self.cpfcnpj_input.setPlaceholderText("00.000.000/0001-00")
        else:
            self.cpfcnpj_label.setText("CPF/CNPJ:")
            self.cpfcnpj_input.setPlaceholderText("000.000.000-00 ou 00.000.000/0001-00")
    
    def formatar_cpf_cnpj(self, texto):
        """Formata o CPF ou CNPJ durante a digitação"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Verificar o tipo selecionado
        tipo = self.tipo_combo.currentText()
        
        # Se o tipo for "Física" ou o texto tiver 11 dígitos ou menos quando "Todos"
        if tipo == "Física" or (tipo == "Todos" and len(texto_limpo) <= 11):
            # Limitar a 11 dígitos para CPF
            if len(texto_limpo) > 11:
                texto_limpo = texto_limpo[:11]
            
            # Formatar CPF: 000.000.000-00
            if len(texto_limpo) <= 3:
                texto_formatado = texto_limpo
            elif len(texto_limpo) <= 6:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:]}"
            elif len(texto_limpo) <= 9:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:6]}.{texto_limpo[6:]}"
            else:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:6]}.{texto_limpo[6:9]}-{texto_limpo[9:]}"
        
        # Se o tipo for "Jurídica" ou o texto tiver mais de 11 dígitos quando "Todos"
        elif tipo == "Jurídica" or (tipo == "Todos" and len(texto_limpo) > 11):
            # Limitar a 14 dígitos para CNPJ
            if len(texto_limpo) > 14:
                texto_limpo = texto_limpo[:14]
            
            # Formatar CNPJ: 00.000.000/0001-00
            if len(texto_limpo) <= 2:
                texto_formatado = texto_limpo
            elif len(texto_limpo) <= 5:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:]}"
            elif len(texto_limpo) <= 8:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:]}"
            elif len(texto_limpo) <= 12:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:8]}/{texto_limpo[8:]}"
            else:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:8]}/{texto_limpo[8:12]}-{texto_limpo[12:]}"
        else:
            texto_formatado = texto_limpo
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Bloqueia sinais para evitar recursão
            self.cpfcnpj_input.blockSignals(True)
            self.cpfcnpj_input.setText(texto_formatado)
            
            # Posição do cursor baseada no comprimento do texto formatado
            self.cpfcnpj_input.setCursorPosition(len(texto_formatado))
            self.cpfcnpj_input.blockSignals(False)
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        dados = [
            ("001", "Empresa ABC Ltda", "Carlos", "Jurídica", "12.345.678/0001-90"),
            ("002", "João Silva", "Maria", "Física", "123.456.789-00"),
            ("003", "Distribuidora XYZ", "Pedro", "Jurídica", "98.765.432/0001-10"),
            ("004", "Ana Souza", "Carlos", "Física", "987.654.321-00"),
            ("005", "Mercado Central", "Maria", "Jurídica", "45.678.901/0001-23")
        ]
        
        self.table.setRowCount(len(dados))
        for row, (codigo, nome, vendedor, tipo, cpfcnpj) in enumerate(dados):
            self.table.setItem(row, 0, QTableWidgetItem(codigo))
            self.table.setItem(row, 1, QTableWidgetItem(nome))
            self.table.setItem(row, 2, QTableWidgetItem(vendedor))
            self.table.setItem(row, 3, QTableWidgetItem(tipo))
            self.table.setItem(row, 4, QTableWidgetItem(cpfcnpj))
    
    # Método voltar removido
    
    def alterar(self):
        """Abre o formulário para alterar os dados do cliente selecionado"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um cliente para alterar!")
            return
        
        # Obter a linha selecionada
        row = self.table.currentRow()
        
        # Extrair dados do cliente
        dados_cliente = {
            "codigo": self.table.item(row, 0).text(),
            "nome": self.table.item(row, 1).text(),
            "vendedor": self.table.item(row, 2).text()
        }
        
        # Adicionar tipo e cpf_cnpj se existirem colunas para eles
        if self.table.columnCount() > 3:
            dados_cliente["tipo"] = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        if self.table.columnCount() > 4:
            dados_cliente["cpf_cnpj"] = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        
        # Carregar o FormularioPessoa dinamicamente
        FormularioPessoa = self.load_formulario_pessoa()
        
        if FormularioPessoa is None:
            self.mostrar_mensagem("Erro", "Não foi possível carregar o formulário de pessoas")
            return
            
        # Criar uma nova janela
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Alterar Cliente")
        self.janela_formulario.setGeometry(100, 100, 900, 600)  # Largura maior
        self.janela_formulario.setStyleSheet("background-color: #003b57;")
        
        try:
            # Instanciar o formulário de pessoa (sem enviar dados_cliente ou modo_edicao)
            formulario_pessoa_widget = FormularioPessoa(cadastro_tela=self, janela_parent=self.janela_formulario)
            
            # Tentar preencher manualmente os campos do formulário
            if hasattr(formulario_pessoa_widget, 'codigo_input'):
                formulario_pessoa_widget.codigo_input.setText(dados_cliente.get("codigo", ""))
            if hasattr(formulario_pessoa_widget, 'nome_input'):
                formulario_pessoa_widget.nome_input.setText(dados_cliente.get("nome", ""))
            if hasattr(formulario_pessoa_widget, 'vendedor_input'):
                formulario_pessoa_widget.vendedor_input.setText(dados_cliente.get("vendedor", ""))
            
            # Tentar preencher tipo e cpf_cnpj se os widgets existirem
            if hasattr(formulario_pessoa_widget, 'tipo_combo') and "tipo" in dados_cliente:
                index = formulario_pessoa_widget.tipo_combo.findText(dados_cliente["tipo"])
                if index >= 0:
                    formulario_pessoa_widget.tipo_combo.setCurrentIndex(index)
            
            if hasattr(formulario_pessoa_widget, 'cpf_cnpj_input') and "cpf_cnpj" in dados_cliente:
                formulario_pessoa_widget.cpf_cnpj_input.setText(dados_cliente["cpf_cnpj"])
            
            self.janela_formulario.setCentralWidget(formulario_pessoa_widget)
            
            # Mostrar a janela
            self.janela_formulario.show()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao criar o formulário: {str(e)}")
    
    def excluir(self):
        """Ação do botão excluir"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um cliente para excluir!")
            return
        
        # Obter a linha selecionada e dados do cliente
        row = self.table.currentRow()
        codigo = self.table.item(row, 0).text()
        nome = self.table.item(row, 1).text()
        
        # Criar uma mensagem de confirmação personalizada
        msg_box = CustomMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar Exclusão")
        msg_box.setText(f"Deseja realmente excluir o cliente '{nome}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.Yes:
            self.table.removeRow(row)
            self.mostrar_mensagem("Sucesso", f"Cliente {nome} excluído com sucesso!")

    def load_formulario_pessoa(self):
        """Carrega dinamicamente o módulo FormularioPessoa"""
        try:
            # Tente primeiro com importação direta 
            try:
                from formulario_pessoa import FormularioPessoa
                print("Importação direta de FormularioPessoa bem-sucedida")
                return FormularioPessoa
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Tente importar usando caminhos diferentes
                possibilidades = [
                    'FormularioPessoa', 
                    'geral.formulario_pessoa', 
                    'clientes.formulario_pessoa'
                ]
                
                for modulo in possibilidades:
                    try:
                        mod = __import__(modulo, fromlist=['FormularioPessoa'])
                        if hasattr(mod, 'FormularioPessoa'):
                            print(f"Importação bem-sucedida via {modulo}")
                            return getattr(mod, 'FormularioPessoa')
                    except ImportError:
                        continue
                
                # Se chegou aqui, nenhuma importação funcionou.
                # Vamos tentar carregar o arquivo diretamente
                
                # Lista de possíveis locais para o arquivo
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(script_dir)
                
                possibilidades_caminhos = [
                    os.path.join(script_dir, "formulario_pessoa.py"),
                    os.path.join(script_dir, "FormularioPessoa.py"),
                    os.path.join(project_root, "formulario_pessoa.py"),
                    os.path.join(project_root, "FormularioPessoa.py"),
                    os.path.join(project_root, "geral", "formulario_pessoa.py"),
                    os.path.join(project_root, "clientes", "formulario_pessoa.py")
                ]
                
                for caminho in possibilidades_caminhos:
                    if os.path.exists(caminho):
                        print(f"Arquivo encontrado em: {caminho}")
                        # Carregar o módulo dinamicamente
                        module_name = os.path.basename(caminho).split('.')[0]
                        spec = importlib.util.spec_from_file_location(module_name, caminho)
                        if spec is None:
                            continue
                            
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Retornar a classe FormularioPessoa
                        if hasattr(module, "FormularioPessoa"):
                            return getattr(module, "FormularioPessoa")
                
                # Se não encontrou o módulo, criar um formulário básico
                self.criar_formulario_pessoa_padrao()
                
                # Tentar carregar novamente
                caminho = os.path.join(script_dir, "formulario_pessoa.py")
                if os.path.exists(caminho):
                    module_name = "formulario_pessoa"
                    spec = importlib.util.spec_from_file_location(module_name, caminho)
                    if spec is not None:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Retornar a classe FormularioPessoa
                        if hasattr(module, "FormularioPessoa"):
                            return getattr(module, "FormularioPessoa")
                
                raise ImportError("Não foi possível encontrar o módulo FormularioPessoa")
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}")
            return None
    
    def criar_formulario_pessoa_padrao(self):
        """Cria um arquivo formulario_pessoa.py básico se não existir"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, "formulario_pessoa.py")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CustomMessageBox(QMessageBox):
    """Classe personalizada para QMessageBox com cores customizadas"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilo para os botões do MessageBox
        self.setStyleSheet("""
            QMessageBox {
                background-color: #003b57;
                color: white;
            }
            QLabel {
                color: white;
                background-color: #003b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: 1px solid #007ab3;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)

class FormularioPessoa(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None, dados_cliente=None, modo_edicao=False):
        super().__init__()
        self.cadastro_tela = cadastro_tela
        self.janela_parent = janela_parent
        self.dados_cliente = dados_cliente
        self.modo_edicao = modo_edicao
        self.initUI()
        
        # Preencher o formulário com os dados do cliente se for uma edição
        if self.modo_edicao and self.dados_cliente:
            self.preencher_formulario()
    
    def preencher_formulario(self):
        """Preenche o formulário com os dados do cliente para edição"""
        if not self.dados_cliente:
            return
            
        # Preencher os campos
        if hasattr(self, 'codigo_input') and 'codigo' in self.dados_cliente:
            self.codigo_input.setText(self.dados_cliente['codigo'])
            
        if hasattr(self, 'nome_input') and 'nome' in self.dados_cliente:
            self.nome_input.setText(self.dados_cliente['nome'])
            
        if hasattr(self, 'tipo_combo') and 'tipo' in self.dados_cliente:
            tipo = self.dados_cliente['tipo']
            index = self.tipo_combo.findText(tipo)
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)
            
        if hasattr(self, 'cpf_cnpj_input') and 'cpf_cnpj' in self.dados_cliente:
            self.cpf_cnpj_input.setText(self.dados_cliente['cpf_cnpj'])
            
        if hasattr(self, 'vendedor_input') and 'vendedor' in self.dados_cliente:
            self.vendedor_input.setText(self.dados_cliente['vendedor'])
            
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        titulo_texto = "Alterar Cliente" if self.modo_edicao else "Cadastro de Cliente"
        titulo = QLabel(titulo_texto)
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; }"
        
        # Estilo para os inputs
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 25px;
            }
        """
        
        # Estilo para ComboBox
        combobox_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #003b57;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
        """
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)
        
        # Campo Código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        if self.modo_edicao:
            self.codigo_input.setReadOnly(True)  # Código não pode ser alterado
        form_layout.addRow(codigo_label, self.codigo_input)
        
        # Campo Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet(label_style)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(input_style)
        form_layout.addRow(nome_label, self.nome_input)
        
        # Campo Tipo (Física/Jurídica)
        tipo_label = QLabel("Tipo:")
        tipo_label.setStyleSheet(label_style)
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Física", "Jurídica"])
        self.tipo_combo.setStyleSheet(combobox_style)
        self.tipo_combo.currentIndexChanged.connect(self.tipo_alterado)
        form_layout.addRow(tipo_label, self.tipo_combo)
        
        # Campo CPF/CNPJ
        self.cpf_cnpj_label = QLabel("CPF:")
        self.cpf_cnpj_label.setStyleSheet(label_style)
        self.cpf_cnpj_input = QLineEdit()
        self.cpf_cnpj_input.setStyleSheet(input_style)
        self.cpf_cnpj_input.setPlaceholderText("000.000.000-00")
        self.cpf_cnpj_input.textChanged.connect(self.formatar_cpf_cnpj)
        form_layout.addRow(self.cpf_cnpj_label, self.cpf_cnpj_input)
        
        # Campo Vendedor
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet(label_style)
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setStyleSheet(input_style)
        form_layout.addRow(vendedor_label, self.vendedor_input)
        
        # Campo Cidade
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet(label_style)
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(input_style)
        form_layout.addRow(cidade_label, self.cidade_input)
        
        # Campo Endereço
        endereco_label = QLabel("Endereço:")
        endereco_label.setStyleSheet(label_style)
        self.endereco_input = QLineEdit()
        self.endereco_input.setStyleSheet(input_style)
        form_layout.addRow(endereco_label, self.endereco_input)
        
        # Campo Telefone
        telefone_label = QLabel("Telefone:")
        telefone_label.setStyleSheet(label_style)
        self.telefone_input = QLineEdit()
        self.telefone_input.setStyleSheet(input_style)
        self.telefone_input.setPlaceholderText("(00) 00000-0000")
        form_layout.addRow(telefone_label, self.telefone_input)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(15)
        
        # Botão Cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        btn_cancelar.clicked.connect(self.cancelar)
        botoes_layout.addWidget(btn_cancelar)
        
        # Botão Salvar
        texto_botao = "Atualizar" if self.modo_edicao else "Salvar"
        btn_salvar = QPushButton(texto_botao)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        btn_salvar.clicked.connect(self.salvar)
        botoes_layout.addWidget(btn_salvar)
        
        # Container para centralizar os botões
        botoes_container = QHBoxLayout()
        botoes_container.addStretch()
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch()
        
        main_layout.addLayout(botoes_container)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #003b57;")
    
    def tipo_alterado(self, index):
        """Atualiza o rótulo e placeholder do campo CPF/CNPJ com base no tipo selecionado"""
        tipo = self.tipo_combo.currentText()
        
        if tipo == "Física":
            self.cpf_cnpj_label.setText("CPF:")
            self.cpf_cnpj_input.setPlaceholderText("000.000.000-00")
            self.formatar_cpf_cnpj(self.cpf_cnpj_input.text())  # Reformatar o texto atual
        else:  # Jurídica
            self.cpf_cnpj_label.setText("CNPJ:")
            self.cpf_cnpj_input.setPlaceholderText("00.000.000/0001-00")
            self.formatar_cpf_cnpj(self.cpf_cnpj_input.text())  # Reformatar o texto atual
    
    def formatar_cpf_cnpj(self, texto):
        """Formata o CPF ou CNPJ durante a digitação"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Verificar o tipo selecionado
        tipo = self.tipo_combo.currentText()
        
        if tipo == "Física":
            # Limitar a 11 dígitos para CPF
            if len(texto_limpo) > 11:
                texto_limpo = texto_limpo[:11]
            
            # Formatar CPF: 000.000.000-00
            if len(texto_limpo) <= 3:
                texto_formatado = texto_limpo
            elif len(texto_limpo) <= 6:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:]}"
            elif len(texto_limpo) <= 9:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:6]}.{texto_limpo[6:]}"
            else:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:6]}.{texto_limpo[6:9]}-{texto_limpo[9:]}"
        else:  # Jurídica
            # Limitar a 14 dígitos para CNPJ
            if len(texto_limpo) > 14:
                texto_limpo = texto_limpo[:14]
            
            # Formatar CNPJ: 00.000.000/0001-00
            if len(texto_limpo) <= 2:
                texto_formatado = texto_limpo
            elif len(texto_limpo) <= 5:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:]}"
            elif len(texto_limpo) <= 8:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:]}"
            elif len(texto_limpo) <= 12:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:8]}/{texto_limpo[8:]}"
            else:
                texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:8]}/{texto_limpo[8:12]}-{texto_limpo[12:]}"
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Bloqueia sinais para evitar recursão
            self.cpf_cnpj_input.blockSignals(True)
            self.cpf_cnpj_input.setText(texto_formatado)
            
            # Posição do cursor baseada no comprimento do texto formatado
            self.cpf_cnpj_input.setCursorPosition(len(texto_formatado))
            self.cpf_cnpj_input.blockSignals(False)
    
    def cancelar(self):
        """Cancela a operação e fecha a janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma mensagem personalizada com estilo"""
        msg = CustomMessageBox(self)
        msg.setIcon(tipo)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.exec_()
    
    def salvar(self):
        """Salva os dados do cliente"""
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        tipo = self.tipo_combo.currentText()
        cpf_cnpj = self.cpf_cnpj_input.text()
        vendedor = self.vendedor_input.text()
        cidade = self.cidade_input.text() if hasattr(self, 'cidade_input') else ""
        
        # Validação básica
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Os campos Código e Nome são obrigatórios", QMessageBox.Warning)
            return
        
        if not cpf_cnpj:
            self.mostrar_mensagem("Atenção", f"O campo {'CPF' if tipo == 'Física' else 'CNPJ'} é obrigatório", QMessageBox.Warning)
            return
        
        # Se for modo de edição (alterar)
        if self.modo_edicao and self.cadastro_tela:
            # Buscar o cliente na tabela da tela principal
            table = self.cadastro_tela.table
            for row in range(table.rowCount()):
                if table.item(row, 0).text() == codigo:
                    # Atualizar os dados na tabela
                    table.setItem(row, 1, QTableWidgetItem(nome))
                    table.setItem(row, 2, QTableWidgetItem(vendedor))
                    table.setItem(row, 3, QTableWidgetItem(tipo))
                    table.setItem(row, 4, QTableWidgetItem(cpf_cnpj))
                    
                    # Mensagem de sucesso
                    self.mostrar_mensagem("Sucesso", f"Cliente {nome} atualizado com sucesso!")
                    
                    # Fechar a janela
                    self.cancelar()
                    return
            
            # Se não encontrou o cliente
            self.mostrar_mensagem("Erro", "Não foi possível encontrar o cliente para atualização", QMessageBox.Warning)
        else:
            # Modo de inclusão - verificar se o código já existe
            if self.cadastro_tela:
                table = self.cadastro_tela.table
                for row in range(table.rowCount()):
                    if table.item(row, 0).text() == codigo:
                        self.mostrar_mensagem("Atenção", "Este código já está em uso", QMessageBox.Warning)
                        return
                
                # Adicionar à tabela
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(codigo))
                table.setItem(row, 1, QTableWidgetItem(nome))
                table.setItem(row, 2, QTableWidgetItem(vendedor))
                table.setItem(row, 3, QTableWidgetItem(tipo))
                table.setItem(row, 4, QTableWidgetItem(cpf_cnpj))
                
                # Mensagem de sucesso
                self.mostrar_mensagem("Sucesso", f"Cliente {nome} cadastrado com sucesso!")
                
                # Fechar a janela
                self.cancelar()
            else:
                # Caso não tenha acesso à tabela principal, apenas mostrar mensagem de teste
                self.mostrar_mensagem("Teste", f"Cliente seria salvo com os dados:\nCódigo: {codigo}\nNome: {nome}\nTipo: {tipo}\nCPF/CNPJ: {cpf_cnpj}\nVendedor: {vendedor}")
                self.cancelar()
''')
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Não foi possível criar o arquivo formulario_pessoa.py: {str(e)}")
    
    def cadastrar(self):
        """Ação do botão cadastrar"""
        print("Abrindo formulário para cadastro de pessoa")
        
        # Carregar o FormularioPessoa dinamicamente
        FormularioPessoa = self.load_formulario_pessoa()
        
        if FormularioPessoa is None:
            self.mostrar_mensagem("Erro", "Não foi possível carregar o formulário de pessoas")
            return
            
        # Criar uma nova janela
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Cadastro de Pessoa")
        self.janela_formulario.setGeometry(100, 100, 900, 600)  # Aumentei a largura para 900
        self.janela_formulario.setStyleSheet("background-color: #003b57;")
        
        try:
            # Instanciar o formulário de pessoa
            formulario_pessoa_widget = FormularioPessoa(cadastro_tela=self, janela_parent=self.janela_formulario)
            self.janela_formulario.setCentralWidget(formulario_pessoa_widget)
            
            # Mostrar a janela
            self.janela_formulario.show()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao criar o formulário: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem personalizada"""
        msg_box = CustomMessageBox(self)
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.exec_()


class ClientesMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema - Clientes")
        self.setGeometry(100, 100, 800, 600)  
        self.setStyleSheet("background-color: #003b57;")
        
        clientes_widget = ClientesWindow(self)  # Passa a janela como parent
        self.setCentralWidget(clientes_widget)

# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientesMainWindow()
    window.show()
    sys.exit(app.exec_())