import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class GrupoProdutos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        # Dados locais para armazenar grupos de produtos
        self.grupos_data = [
            {"codigo": "001", "nome": "Alimentos", "grupo": "Grupo 1"},
            {"codigo": "002", "nome": "Bebidas", "grupo": "Grupo 2"},
            {"codigo": "003", "nome": "Limpeza", "grupo": "Grupo 1"},
            {"codigo": "004", "nome": "Higiene", "grupo": "Grupo 3"}
        ]
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
        
        # Layout para o título centralizado (sem botão voltar)
        header_layout = QHBoxLayout()
        
        # Título centralizado
        titulo = QLabel("Grupo de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Layout para campos superiores
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(20)
        
        # Campo Código
        codigo_layout = QVBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        codigo_layout.addWidget(self.codigo_input)
        fields_layout.addLayout(codigo_layout)
        
        # Campo Nome
        nome_layout = QVBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        nome_layout.addWidget(self.nome_input)
        fields_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(fields_layout)
        # Campo Grupo de Produtos (dropdown)
        grupo_layout = QVBoxLayout()
        grupo_label = QLabel("Grupo de Produtos:")
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
                selection-background-color: #043b57;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #043b57;
                color: white;
            }
        """)
        # Adicionar itens ao ComboBox
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Grupo 1")
        self.grupo_combo.addItem("Grupo 2")
        self.grupo_combo.addItem("Grupo 3")
        grupo_layout.addWidget(self.grupo_combo)
        
        main_layout.addLayout(grupo_layout)
        
        # Layout para botões de ação (horizontal e abaixo do combo)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Estilo comum para os botões
        btn_style = """
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6d9;
            }
        """
        
        # Botão Alterar
        btn_alterar = QPushButton("Alterar")
        # Adicionar ícone para o botão Alterar usando ícones do sistema
        try:
            btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        btn_alterar.setStyleSheet(btn_style)
        btn_alterar.clicked.connect(self.alterar)
        buttons_layout.addWidget(btn_alterar)
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        # Adicionar ícone para o botão Excluir usando ícones do sistema
        try:
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet(btn_style)
        btn_excluir.clicked.connect(self.excluir)
        buttons_layout.addWidget(btn_excluir)
        
        # Botão Cadastrar
        btn_cadastrar = QPushButton("Cadastrar")
        # Adicionar ícone para o botão Cadastrar usando ícones do sistema
        try:
            btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        btn_cadastrar.setStyleSheet(btn_style)
        btn_cadastrar.clicked.connect(self.cadastrar)
        buttons_layout.addWidget(btn_cadastrar)
        
        # Adicionar espaço para empurrar os botões para a esquerda
        buttons_layout.addStretch(1)
        
        main_layout.addLayout(buttons_layout)
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
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Grupo"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.itemSelectionChanged.connect(self.selecionar_item)
        
        # Carregar dados
        self.carregar_dados()
        
        main_layout.addWidget(self.tabela)
    
    def carregar_dados(self):
        """Carrega dados na tabela a partir da lista local"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Adicionar linhas
        for row, produto in enumerate(self.grupos_data):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(produto["codigo"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto["nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(produto["grupo"]))
    
    def selecionar_item(self):
        """Preenche os campos quando uma linha é selecionada"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.codigo_input.setText(self.tabela.item(row, 0).text())
            self.nome_input.setText(self.tabela.item(row, 1).text())
            
            # Encontrar e selecionar o grupo correto
            grupo_text = self.tabela.item(row, 2).text()
            index = self.grupo_combo.findText(grupo_text)
            if index >= 0:
                self.grupo_combo.setCurrentIndex(index)
    
    # Método voltar foi removido
    
    def alterar(self):
        """Abre o formulário para alterar os dados do grupo selecionado"""
        # Verificar se um grupo foi selecionado
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Seleção necessária", 
                                 "Por favor, selecione um grupo para alterar", 
                                 QMessageBox.Warning)
            return
        
        # Buscar os dados completos do grupo selecionado
        dados_grupo = None
        
        for grupo in self.grupos_data:
            if grupo["codigo"] == codigo:
                dados_grupo = grupo
                break
        
        if not dados_grupo:
            self.mostrar_mensagem("Erro", 
                                "Não foi possível encontrar os dados do grupo selecionado", 
                                QMessageBox.Critical)
            return
        
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'form_window') and self.form_window.isVisible():
            # Se existir, fechá-la para abrir uma nova com os dados atualizados
            self.form_window.close()
        
        # Carregar dinamicamente a classe FormularioGrupo
        FormularioGrupo = self.load_formulario_grupo()
        if not FormularioGrupo:
            return
            
        # Criar uma nova janela para o formulário
        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Alterar Grupo de Produtos")
        self.form_window.setGeometry(150, 150, 800, 600)
        self.form_window.setStyleSheet("background-color: #043b57;")
        # Criar o widget do formulário e passá-lo como widget central
        formulario = FormularioGrupo(self)
        
        # Preencher os campos com os dados do grupo
        if hasattr(formulario, 'codigo_input'):
            formulario.codigo_input.setText(dados_grupo["codigo"])
            # Desabilitar edição do código para evitar problemas de identificação
            formulario.codigo_input.setReadOnly(True)
        
        if hasattr(formulario, 'nome_input'):
            formulario.nome_input.setText(dados_grupo["nome"])
        
        # Configurar grupo se houver
        if hasattr(formulario, 'grupo_combo'):
            index = formulario.grupo_combo.findText(dados_grupo["grupo"])
            if index >= 0:
                formulario.grupo_combo.setCurrentIndex(index)
        
        # Se o botão existe, alterar texto para "Salvar Alterações"
        if hasattr(formulario, 'btn_salvar'):
            formulario.btn_salvar.setText("Salvar Alterações")
            # Armazenar o código original para facilitar a atualização
            formulario.codigo_original = dados_grupo["codigo"]
        
        self.form_window.setCentralWidget(formulario)
        
        # Exibir a janela
        self.form_window.show()
    
    def excluir(self):
        """Exclui um produto"""
        selected_rows = self.tabela.selectionModel().selectedRows()
        if not selected_rows:
            self.mostrar_mensagem("Atenção", "Selecione um produto para excluir!")
            return
        
        row = selected_rows[0].row()
        codigo = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        
        # Criar uma mensagem de confirmação personalizada com estilo
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir o grupo '{nome}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Aplicar estilo personalizado
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #043b57;
            }
            QLabel { 
                color: white;
                background-color: #043b57;
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
        
        if resposta == QMessageBox.No:
            return
        
        # Remover da lista de dados
        for i, item in enumerate(self.grupos_data):
            if item["codigo"] == codigo:
                del self.grupos_data[i]
                break
        
        # Remover da tabela
        self.tabela.removeRow(row)
        
        # Limpar os campos
        self.codigo_input.clear()
        self.nome_input.clear()
        self.grupo_combo.setCurrentIndex(0)
        
        self.mostrar_mensagem("Sucesso", "Grupo excluído com sucesso!")
    
    def load_formulario_grupo(self):
        """
        Carrega dinamicamente o módulo formulario_grupo.py
        Isso permite que o arquivo seja encontrado mesmo quando compilado para .exe
        """
        try:
            # Tente primeiro com importação direta (para ambiente de desenvolvimento)
            try:
                # Importação direta usando o módulo
                from geral.formulario_grupo import FormularioGrupo
                print("Importação direta de FormularioGrupo bem-sucedida")
                return FormularioGrupo
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_grupo.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_grupo.py")
                
                # Se o arquivo não existir, vamos criar um básico
                if not os.path.exists(module_path):
                    self.criar_formulario_grupo_padrao(module_path)
                
                # Carregar o módulo dinamicamente
                module_name = "formulario_grupo"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Não foi possível carregar o módulo {module_name}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Retornar a classe FormularioGrupo
                if hasattr(module, "FormularioGrupo"):
                    return getattr(module, "FormularioGrupo")
                else:
                    raise ImportError(f"A classe FormularioGrupo não foi encontrada no módulo {module_name}")
        except Exception as e:
            print(f"Erro ao carregar FormularioGrupo: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}", QMessageBox.Critical)
            return None
    
    def criar_formulario_grupo_padrao(self, filepath):
        """Cria um arquivo formulario_grupo.py básico se não existir"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FormularioGrupo(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.codigo_original = None  # Para armazenar o código original em caso de alteração
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Cadastro de Grupo de Produtos")
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
            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 30px;
            }
        """
        
        combo_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #043b57;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #043b57;
                color: white;
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
        
        # Campo Grupo
        self.grupo_label = QLabel("Grupo:")
        self.grupo_label.setStyleSheet(label_style)
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(combo_style)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Grupo 1")
        self.grupo_combo.addItem("Grupo 2")
        self.grupo_combo.addItem("Grupo 3")
        form_layout.addRow(self.grupo_label, self.grupo_combo)
        
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
        
        # Botão Salvar (único botão após remoção do botão Voltar)
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet(btn_style)
        self.btn_salvar.clicked.connect(self.salvar)
        
        botoes_layout.addWidget(self.btn_salvar)
        
        botoes_container = QHBoxLayout()
        botoes_container.addStretch()
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch()
        
        main_layout.addLayout(botoes_container)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
    
    def salvar(self):
        """Salva os dados do grupo de produtos"""
        # Validação básica
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        grupo = self.grupo_combo.currentText()
        
        if not codigo or not nome or grupo == "Selecione um grupo":
            self.mostrar_mensagem("Campos obrigatórios", "Todos os campos são obrigatórios.")
            return
        
        # Verificar se é uma alteração
        if self.codigo_original is not None and self.btn_salvar.text() == "Salvar Alterações":
            # Modo de alteração
            for i, item in enumerate(self.parent.grupos_data):
                if item["codigo"] == self.codigo_original:
                    # Atualizar dados do grupo
                    self.parent.grupos_data[i]["codigo"] = codigo
                    self.parent.grupos_data[i]["nome"] = nome
                    self.parent.grupos_data[i]["grupo"] = grupo
                    
                    # Atualizar a tabela
                    self.parent.carregar_dados()
                    
                    # Mostrar mensagem de sucesso
                    self.mostrar_mensagem("Sucesso", "Grupo de produtos alterado com sucesso!")
                    
                    # Fechar o formulário
                    if self.parent and hasattr(self.parent, 'form_window'):
                        self.parent.form_window.close()
                    return
                    
            # Se chegou aqui, o grupo não foi encontrado
            self.mostrar_mensagem("Erro", "Grupo não encontrado para alteração.")
            return
        else:
            # Modo de inclusão - verificar se o código já existe
            for produto in self.parent.grupos_data:
                if produto["codigo"] == codigo:
                    self.mostrar_mensagem("Código duplicado", "Já existe um grupo com este código.")
                    return
            
            # Adicionar novo grupo à lista
            novo_grupo = {
                "codigo": codigo,
                "nome": nome,
                "grupo": grupo
            }
            
            # Adicionar à lista de dados
            self.parent.grupos_data.append(novo_grupo)
            
            # Atualizar a tabela
            self.parent.carregar_dados()
            
            # Mostrar mensagem de sucesso
            self.mostrar_mensagem("Sucesso", "Grupo de produtos cadastrado com sucesso!")
            
            # Fechar o formulário
            if self.parent and hasattr(self.parent, 'form_window'):
                self.parent.form_window.close()
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Campos" in titulo or "Código" in titulo or "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(tipo)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #043b57;
            }
            QLabel { 
                color: white;
                background-color: #043b57;
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormularioGrupo()
    window.show()
    sys.exit(app.exec_())
''')
        except Exception as e:
            print(f"Erro ao criar arquivo: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível criar o arquivo: {str(e)}", QMessageBox.Critical)
    
    def cadastrar(self):
        """Abre a tela de cadastro de grupo de produtos"""
        try:
            # Verificar se já existe uma janela de formulário aberta
            if hasattr(self, 'form_window') and self.form_window.isVisible():
                # Se existir, apenas ativá-la em vez de criar uma nova
                self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
                self.form_window.activateWindow()
                self.form_window.raise_()
                return
            
            # Carregar dinamicamente a classe FormularioGrupo
            FormularioGrupo = self.load_formulario_grupo()
            if FormularioGrupo is None:
                return
            
            # Criar uma nova janela para o formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Cadastro de Grupo de Produtos")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("background-color: #043b57;")
            
            # Configurar o widget central
            formulario_grupo_widget = FormularioGrupo(self)
            self.form_window.setCentralWidget(formulario_grupo_widget)
            
            # Mostrar a janela de formulário
            self.form_window.show()
        except AttributeError as e:
            self.mostrar_mensagem("Erro", f"Módulo de formulários carregado, mas há um problema com a classe: {str(e)}")
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao abrir o formulário: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem personalizada"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #043b57;
            }
            QLabel { 
                color: white;
                background-color: #043b57;
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


class GrupoProdutosWindow(QMainWindow):
    """Classe para gerenciar a janela de grupo de produtos quando executado como script principal"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grupo de Produtos")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #043b57;")
        
        # Configurando o widget central
        self.grupo_produtos_widget = GrupoProdutos(self)
        self.setCentralWidget(self.grupo_produtos_widget)


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrupoProdutosWindow()
    window.show()
    sys.exit(app.exec_())