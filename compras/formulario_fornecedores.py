#formulario_fornecedores
import sys
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit,
                            QDateEdit, QComboBox, QMessageBox, QFrame, QStyle,
                            QFormLayout, QTableWidgetItem, QDialog, QTableWidget,
                            QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate

# Importar o módulo de banco de dados
try:
    from base.banco import (verificar_tabela_fornecedores, verificar_tabela_tipos_fornecedores,
                        buscar_fornecedor_por_codigo, buscar_fornecedor_por_id,
                        criar_fornecedor, atualizar_fornecedor, excluir_fornecedor,
                        listar_tipos_fornecedores, adicionar_tipo_fornecedor,
                        atualizar_tipo_fornecedor, excluir_tipo_fornecedor)
except ImportError:
    # Tentar um caminho alternativo
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base.banco import (verificar_tabela_fornecedores, verificar_tabela_tipos_fornecedores,
                            buscar_fornecedor_por_codigo, buscar_fornecedor_por_id,
                            criar_fornecedor, atualizar_fornecedor, excluir_fornecedor,
                            listar_tipos_fornecedores, adicionar_tipo_fornecedor,
                            atualizar_tipo_fornecedor, excluir_tipo_fornecedor)
    except ImportError:
        print("ERRO: Não foi possível importar o módulo banco.py!")

# Diálogo para gerenciar os tipos de fornecedores
class TiposFornecedoresDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Tipos de Fornecedores")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: #003b57;")
        self.initUI()
        self.carregar_tipos()
        
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Gerenciar Tipos de Fornecedores")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabela de tipos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(2)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome"])
        
        # Configurar cabeçalhos da tabela
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Estilo da tabela
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #fffff0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        # Permitir seleção de linha completa
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        
        layout.addWidget(self.tabela)
        
        # Botões de ação
        botoes_layout = QHBoxLayout()
        
        # Botão Adicionar
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_adicionar.clicked.connect(self.adicionar_tipo)
        botoes_layout.addWidget(self.btn_adicionar)
        
        # Botão Editar
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #ffbf00;
                color: black;
                border: none;
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.btn_editar.clicked.connect(self.editar_tipo)
        botoes_layout.addWidget(self.btn_editar)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e60000;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir_tipo)
        botoes_layout.addWidget(self.btn_excluir)
        
        # Botão Fechar
        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: black;
                border: none;
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
        """)
        self.btn_fechar.clicked.connect(self.accept)
        botoes_layout.addWidget(self.btn_fechar)
        
        layout.addLayout(botoes_layout)
    
    def carregar_tipos(self):
        """Carrega os tipos de fornecedores na tabela"""
        try:
            # Limpar a tabela
            self.tabela.setRowCount(0)
            
            # Buscar tipos no banco de dados
            tipos = listar_tipos_fornecedores()
            
            if not tipos:
                print("Nenhum tipo de fornecedor encontrado")
                return
            
            # Preencher a tabela com os dados
            self.tabela.setRowCount(len(tipos))
            
            for i, (id_tipo, nome) in enumerate(tipos):
                self.tabela.setItem(i, 0, QTableWidgetItem(str(id_tipo)))
                self.tabela.setItem(i, 1, QTableWidgetItem(nome))
            
        except Exception as e:
            print(f"Erro ao carregar tipos de fornecedores: {e}")
            self.mostrar_mensagem("Erro", f"Erro ao carregar tipos de fornecedores: {str(e)}")
    
    def adicionar_tipo(self):
        """Adiciona um novo tipo de fornecedor"""
        # Criar diálogo personalizado em vez de usar QInputDialog padrão
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Tipo")
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #003b57;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #004a6e;
                color: white;
                border: 1px solid #0078d7;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #0078d7;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)
        
        # Layout do diálogo
        layout = QVBoxLayout(dialog)
        
        # Label
        label = QLabel("Digite o nome do novo tipo de fornecedor:")
        layout.addWidget(label)
        
        # Campo de entrada
        input_field = QLineEdit()
        input_field.setPlaceholderText("Nome do tipo")
        layout.addWidget(input_field)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancelar")
        
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # Mostrar diálogo
        result = dialog.exec_()
        
        # Processar resultado
        if result == QDialog.Accepted and input_field.text().strip():
            nome = input_field.text().strip()
            try:
                # Adicionar no banco de dados
                adicionar_tipo_fornecedor(nome)
                
                # Recarregar a tabela
                self.carregar_tipos()
                
                # Notificar o usuário
                self.mostrar_mensagem("Sucesso", f"Tipo '{nome}' adicionado com sucesso!")
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Erro ao adicionar tipo: {str(e)}")
    
    def editar_tipo(self):
        """Edita um tipo de fornecedor selecionado"""
        # Verificar se há uma linha selecionada
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Aviso", "Selecione um tipo de fornecedor para editar.")
            return
        
        # Obter dados da linha selecionada
        row = selected_items[0].row()
        id_tipo = int(self.tabela.item(row, 0).text())
        nome_atual = self.tabela.item(row, 1).text()
        
        # Criar diálogo personalizado
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Tipo")
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #003b57;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #004a6e;
                color: white;
                border: 1px solid #0078d7;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #0078d7;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)
        
        # Layout do diálogo
        layout = QVBoxLayout(dialog)
        
        # Label
        label = QLabel("Digite o novo nome:")
        layout.addWidget(label)
        
        # Campo de entrada
        input_field = QLineEdit()
        input_field.setText(nome_atual)
        input_field.selectAll()  # Seleciona todo o texto para facilitar a edição
        layout.addWidget(input_field)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancelar")
        
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # Mostrar diálogo
        result = dialog.exec_()
        
        # Processar resultado
        if result == QDialog.Accepted and input_field.text().strip() and input_field.text().strip() != nome_atual:
            novo_nome = input_field.text().strip()
            try:
                # Atualizar no banco de dados
                atualizar_tipo_fornecedor(id_tipo, novo_nome)
                
                # Recarregar a tabela
                self.carregar_tipos()
                
                # Notificar o usuário
                self.mostrar_mensagem("Sucesso", f"Tipo atualizado com sucesso!")
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Erro ao atualizar tipo: {str(e)}")
    
    def excluir_tipo(self):
        """Exclui um tipo de fornecedor selecionado"""
        # Verificar se há uma linha selecionada
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Aviso", "Selecione um tipo de fornecedor para excluir.")
            return
        
        # Obter dados da linha selecionada
        row = selected_items[0].row()
        id_tipo = int(self.tabela.item(row, 0).text())
        nome = self.tabela.item(row, 1).text()
        
        # Criar mensagem de confirmação personalizada
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar Exclusão")
        msg_box.setText(f"Tem certeza que deseja excluir o tipo '{nome}'?")
        
        # Personalizar botões em português
        btn_sim = msg_box.addButton("Sim", QMessageBox.YesRole)
        btn_nao = msg_box.addButton("Não", QMessageBox.NoRole)
        msg_box.setDefaultButton(btn_nao)  # Define "Não" como padrão (mais seguro)
        
        # Aplicar estilo para texto branco
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
                padding: 5px 15px;
                border-radius: 2px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)

        btn_sim.setStyleSheet("""
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
                padding: 5px 15px;
                border-radius: 2px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)

        btn_nao.setStyleSheet("""
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
                padding: 5px 15px;
                border-radius: 2px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)
        
        # Exibir a mensagem
        msg_box.exec_()
        
        # Verificar qual botão foi clicado
        if msg_box.clickedButton() == btn_sim:
            try:
                # Excluir do banco de dados
                excluir_tipo_fornecedor(id_tipo)
                
                # Recarregar a tabela
                self.carregar_tipos()
                
                # Notificar o usuário
                self.mostrar_mensagem("Sucesso", f"Tipo '{nome}' excluído com sucesso!")
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Erro ao excluir tipo: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox(self)
        if "Aviso" in titulo or "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        
        # Personalizar botão Ok
        btn_ok = msg_box.addButton("OK", QMessageBox.AcceptRole)
        
        # Remover botões padrão
        msg_box.setStandardButtons(QMessageBox.NoButton)
        
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
                padding: 5px 15px;
                border-radius: 2px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)
        
        msg_box.exec_()

class FormularioFornecedores(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela
        self.janela_parent = janela_parent
        
        # ID do fornecedor (para modo de edição)
        self.fornecedor_id = None
        
        # Verificar e criar as tabelas se necessário
        try:
            verificar_tabela_fornecedores()
            verificar_tabela_tipos_fornecedores()
        except Exception as e:
            print(f"ERRO ao verificar/criar tabelas: {e}")
        
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
        titulo = QLabel("Cadastro de Fornecedores")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
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
                background-color: #004a6e;
                color: white;
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
        
        # Estilo comum para QComboBox
        combobox_style = """
            QComboBox {
                background-color: #004a6e;
                color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #004a6e;
                color: white;
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
        """
        
        # Estilo comum para QDateEdit
        dateedit_style = """
            QDateEdit {
                background-color: #004a6e;
                color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit:hover {
                border: 1px solid #0078d7;
            }
            QDateEdit QAbstractItemView {
                background-color: #004a6e;
                color: white;
                selection-background-color: #0078d7;
            }
        """
        
        # Linha 1: Nome e Tipo de Pessoa
        linha1_layout = QHBoxLayout()
        
        # Campo Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        linha1_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        linha1_layout.addWidget(self.nome_input, 1)  # 1 para expandir
        
        # Campo Tipo de Pessoa
        tipo_pessoa_label = QLabel("Tipo de Pessoa:")
        tipo_pessoa_label.setStyleSheet("color: white; font-size: 14px;")
        linha1_layout.addWidget(tipo_pessoa_label)
        
        self.tipo_pessoa_combo = QComboBox()
        self.tipo_pessoa_combo.setStyleSheet(combobox_style)
        self.tipo_pessoa_combo.addItem("Jurídica")
        self.tipo_pessoa_combo.addItem("Física")
        self.tipo_pessoa_combo.setFixedWidth(150)
        self.tipo_pessoa_combo.currentIndexChanged.connect(self.alternar_tipo_pessoa)
        linha1_layout.addWidget(self.tipo_pessoa_combo)
        
        main_layout.addLayout(linha1_layout)
        
        # Linha 2: Nome Fantasia e Documento (CNPJ/CPF)
        linha2_layout = QHBoxLayout()
        
        # Campo Nome Fantasia
        fantasia_label = QLabel("Nome Fantasia:")
        fantasia_label.setStyleSheet("color: white; font-size: 14px;")
        linha2_layout.addWidget(fantasia_label)
        
        self.fantasia_input = QLineEdit()
        self.fantasia_input.setStyleSheet(lineedit_style)
        linha2_layout.addWidget(self.fantasia_input, 1)  # 1 para expandir
        
        # Campo CNPJ/CPF (dinâmico)
        self.documento_label = QLabel("CNPJ:")
        self.documento_label.setStyleSheet("color: white; font-size: 14px;")
        linha2_layout.addWidget(self.documento_label)
        
        self.documento_input = QLineEdit()
        self.documento_input.setStyleSheet(lineedit_style)
        self.documento_input.setFixedWidth(180)
        self.documento_input.setPlaceholderText("00.000.000/0001-00")
        self.documento_input.textChanged.connect(self.formatar_documento)
        linha2_layout.addWidget(self.documento_input)
        
        main_layout.addLayout(linha2_layout)
        
        # Linha 3: Tipo e Data de Cadastro
        linha3_layout = QHBoxLayout()
        
        # Campo Tipo
        tipo_label = QLabel("Tipo:")
        tipo_label.setStyleSheet("color: white; font-size: 14px;")
        linha3_layout.addWidget(tipo_label)
        
        tipo_container = QHBoxLayout()
        tipo_container.setSpacing(0)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.setStyleSheet(combobox_style)
        self.carregar_tipos_fornecedores()
        self.tipo_combo.setFixedWidth(180)
        tipo_container.addWidget(self.tipo_combo)
        
        # Botão + para gerenciar tipos
        btn_gerenciar_tipos = QPushButton("+")
        btn_gerenciar_tipos.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 1px solid #cccccc;
                border-left: none;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                padding: 0px 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        btn_gerenciar_tipos.clicked.connect(self.gerenciar_tipos)
        tipo_container.addWidget(btn_gerenciar_tipos)
        
        linha3_layout.addLayout(tipo_container)
        
        # Campo Data de Cadastro
        data_label = QLabel("Data de Cadastro:")
        data_label.setStyleSheet("color: white; font-size: 14px;")
        linha3_layout.addWidget(data_label)
        
        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        self.data_input.setStyleSheet(dateedit_style)
        self.data_input.setFixedWidth(130)
        linha3_layout.addWidget(self.data_input)
        
        # Adicionar um espaço para alinhar com os demais campos
        linha3_layout.addStretch(1)
        
        main_layout.addLayout(linha3_layout)
        
        # Título Endereço
        endereco_titulo = QLabel("Endereço")
        endereco_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        endereco_titulo.setStyleSheet("color: white;")
        endereco_titulo.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(endereco_titulo)
        
        # Linha 4: Rua
        linha4_layout = QHBoxLayout()
        
        # Campo Rua
        rua_label = QLabel("Rua:")
        rua_label.setStyleSheet("color: white; font-size: 14px;")
        linha4_layout.addWidget(rua_label)
        
        self.rua_input = QLineEdit()
        self.rua_input.setStyleSheet(lineedit_style)
        linha4_layout.addWidget(self.rua_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha4_layout)
        
        # Linha 5: Bairro
        linha5_layout = QHBoxLayout()
        
        # Campo Bairro
        bairro_label = QLabel("Bairro:")
        bairro_label.setStyleSheet("color: white; font-size: 14px;")
        linha5_layout.addWidget(bairro_label)
        
        self.bairro_input = QLineEdit()
        self.bairro_input.setStyleSheet(lineedit_style)
        linha5_layout.addWidget(self.bairro_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha5_layout)
        
        # Linha 6: CEP e Cidade
        linha6_layout = QHBoxLayout()
        
        # Campo CEP
        cep_label = QLabel("CEP:")
        cep_label.setStyleSheet("color: white; font-size: 14px;")
        linha6_layout.addWidget(cep_label)
        
        cep_busca_layout = QHBoxLayout()
        cep_busca_layout.setSpacing(0)
        
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet(lineedit_style)
        self.cep_input.setFixedWidth(150)
        self.cep_input.setPlaceholderText("00000-000")
        self.cep_input.textChanged.connect(self.formatar_cep)
        cep_busca_layout.addWidget(self.cep_input)
        
        # Botão de busca para o CEP (lupa)
        btn_busca_cep = QPushButton()
        try:
            btn_busca_cep.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        except:
            pass
        btn_busca_cep.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 1px solid #cccccc;
                border-left: none;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        btn_busca_cep.clicked.connect(self.buscar_endereco_por_cep)
        cep_busca_layout.addWidget(btn_busca_cep)
        
        linha6_layout.addLayout(cep_busca_layout)
        
        # Campo Cidade
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet("color: white; font-size: 14px;")
        linha6_layout.addWidget(cidade_label)
        
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(lineedit_style)
        linha6_layout.addWidget(self.cidade_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha6_layout)
        
        # Linha 7: Estado (UF)
        linha7_layout = QHBoxLayout()
        
        # Campo Estado
        estado_label = QLabel("Estado (UF):")
        estado_label.setStyleSheet("color: white; font-size: 14px;")
        linha7_layout.addWidget(estado_label)
        
        self.estado_input = QLineEdit()
        self.estado_input.setStyleSheet(lineedit_style)
        self.estado_input.setFixedWidth(100)
        self.estado_input.setMaxLength(2)
        self.estado_input.setPlaceholderText("UF")
        linha7_layout.addWidget(self.estado_input)
        
        # Adicionar espaço para alinhar com os campos anteriores
        linha7_layout.addStretch(1)
        
        main_layout.addLayout(linha7_layout)
        
        # Botão Incluir/Salvar
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 15px 0;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 20px 100px 0;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
            QPushButton:pressed {
                background-color: #00cc7a;
            }
        """)
        self.btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(self.btn_incluir)
        
        # Adicionar espaço no final
        main_layout.addStretch()
        
        # Inicializar UI para CNPJ (padrão)
        self.alternar_tipo_pessoa(0)
    
    def carregar_tipos_fornecedores(self):
        """Carrega os tipos de fornecedores no combobox"""
        try:
            # Limpar o combobox
            self.tipo_combo.clear()
            
            # Adicionar opção padrão
            self.tipo_combo.addItem("Selecione um tipo")
            
            # Buscar tipos no banco de dados
            tipos = listar_tipos_fornecedores()
            
            if tipos:
                # Adicionar os tipos ao combobox
                for id_tipo, nome in tipos:
                    self.tipo_combo.addItem(nome, id_tipo)
            
        except Exception as e:
            print(f"Erro ao carregar tipos de fornecedores: {e}")
            self.mostrar_mensagem("Erro", f"Erro ao carregar tipos de fornecedores: {str(e)}")
    
    def gerenciar_tipos(self):
        """Abre o diálogo para gerenciar tipos de fornecedores"""
        dialog = TiposFornecedoresDialog(self)
        result = dialog.exec_()
        
        # Recarregar os tipos após fechar o diálogo
        self.carregar_tipos_fornecedores()
    
    def alternar_tipo_pessoa(self, index):
        """Alterna entre pessoa física e jurídica"""
        if index == 0:  # Jurídica
            self.documento_label.setText("CNPJ:")
            self.documento_input.setPlaceholderText("00.000.000/0001-00")
            self.documento_input.setText("")  # Limpar o campo
        else:  # Física
            self.documento_label.setText("CPF:")
            self.documento_input.setPlaceholderText("000.000.000-00")
            self.documento_input.setText("")  # Limpar o campo
    
    def formatar_documento(self, texto):
        """Formata o documento (CNPJ/CPF) durante a digitação"""
        # Definir se é CNPJ ou CPF baseado no tipo de pessoa
        eh_cnpj = self.tipo_pessoa_combo.currentIndex() == 0
        
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar o tamanho (14 para CNPJ, 11 para CPF)
        max_digitos = 14 if eh_cnpj else 11
        if len(texto_limpo) > max_digitos:
            texto_limpo = texto_limpo[:max_digitos]
        
        # Formatar o texto
        if eh_cnpj:
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
            # Formatar CPF: 000.000.000-00
            if len(texto_limpo) <= 3:
                texto_formatado = texto_limpo
            elif len(texto_limpo) <= 6:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:]}"
            elif len(texto_limpo) <= 9:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:6]}.{texto_limpo[6:]}"
            else:
                texto_formatado = f"{texto_limpo[:3]}.{texto_limpo[3:6]}.{texto_limpo[6:9]}-{texto_limpo[9:]}"
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Bloqueia sinais para evitar recursão
            self.documento_input.blockSignals(True)
            self.documento_input.setText(texto_formatado)
            
            # Calcular a nova posição do cursor
            nova_pos = len(texto_formatado)
            
            # Define a nova posição do cursor
            self.documento_input.setCursorPosition(nova_pos)
            self.documento_input.blockSignals(False)
    
    def buscar_endereco_por_cep(self):
        """Busca endereço baseado no CEP informado utilizando a API de CEP"""
        # Obter CEP, removendo caracteres não numéricos
        cep = ''.join(filter(str.isdigit, self.cep_input.text()))
        
        # Verificar se o CEP tem 8 dígitos
        if len(cep) != 8:
            self.mostrar_mensagem("Atenção", "Por favor, informe um CEP válido com 8 dígitos.")
            return
        
        try:
            # Fazer a requisição à API ViaCEP
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url)
            
            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se o CEP foi encontrado
                if "erro" not in data:
                    # Preencher os campos com os dados retornados
                    self.rua_input.setText(data.get("logradouro", ""))
                    self.bairro_input.setText(data.get("bairro", ""))
                    self.cidade_input.setText(data.get("localidade", ""))
                    self.estado_input.setText(data.get("uf", ""))
                    return
            
            # Se chegou aqui, o CEP não foi encontrado ou houve erro
            self.mostrar_mensagem("Atenção", "CEP não encontrado ou inválido.")
        
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao buscar o CEP: {str(e)}")

    def formatar_cep(self, texto):
        """Formata o CEP durante a digitação e busca endereço quando completo"""
        # Guarda a posição atual do cursor
        cursor_pos = self.cep_input.cursorPosition()
        
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 8 dígitos
        if len(texto_limpo) > 8:
            texto_limpo = texto_limpo[:8]
        
        # Formatar CEP: 00000-000
        if len(texto_limpo) <= 5:
            texto_formatado = texto_limpo
        else:
            texto_formatado = f"{texto_limpo[:5]}-{texto_limpo[5:]}"
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Calcula quantos caracteres foram adicionados ou removidos
            dif_tamanho = len(texto_formatado) - len(texto)
            
            # Bloqueia sinais para evitar recursão
            self.cep_input.blockSignals(True)
            self.cep_input.setText(texto_formatado)
            
            # Ajuste especial para o hífen: se o usuário acabou de digitar o 5º dígito
            if len(texto_limpo) == 5 and len(''.join(filter(str.isdigit, texto))) == 5:
                # Posiciona o cursor depois do hífen
                nova_pos = 6
            else:
                # Ajusta a posição do cursor considerando a mudança de tamanho do texto
                nova_pos = cursor_pos + dif_tamanho
                # Garante que a posição está dentro dos limites do texto
                if nova_pos < 0:
                    nova_pos = 0
                elif nova_pos > len(texto_formatado):
                    nova_pos = len(texto_formatado)
            
            # Define a nova posição do cursor
            self.cep_input.setCursorPosition(nova_pos)
            self.cep_input.blockSignals(False)
        
        # Se o CEP estiver completo (8 dígitos), buscar endereço automaticamente
        if len(texto_limpo) == 8:
            self.buscar_endereco_por_cep()
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual 
        if self.janela_parent:
            self.janela_parent.close()
        else:
            # Caso esteja rodando independentemente
            print("Voltar para a tela de fornecedores")
    
    def incluir(self):
        """Inclui um novo fornecedor ou atualiza um existente"""
        # Validar campos obrigatórios
        nome = self.nome_input.text()
        fantasia = self.fantasia_input.text()
        tipo_index = self.tipo_combo.currentIndex()
        documento = self.documento_input.text()
        
        if not nome or tipo_index == 0 or not documento:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos obrigatórios (Nome, Tipo e Documento)!")
            return
        
        # Obter o tipo de pessoa e definir o código
        tipo_pessoa = "Jurídica" if self.tipo_pessoa_combo.currentIndex() == 0 else "Física"
        tipo = self.tipo_combo.currentText()
        
        # Obter os dados complementares
        cep = self.cep_input.text()
        rua = self.rua_input.text()
        bairro = self.bairro_input.text()
        cidade = self.cidade_input.text()
        estado = self.estado_input.text()
        
        # Obter a data de cadastro
        data_cadastro = self.data_input.date().toString("dd/MM/yyyy")
        
        try:
            # Verificar se é inclusão ou atualização
            if self.fornecedor_id is None:
                # Criar novo fornecedor - o código será gerado automaticamente pelo método criar_fornecedor
                id_fornecedor = criar_fornecedor(
                    # Passamos uma string vazia e o banco gerará o código
                    "",
                    nome, fantasia, tipo, documento, data_cadastro,
                    cep, rua, bairro, cidade, estado
                )
                
                mensagem = "Fornecedor incluído com sucesso!"
            else:
                # Para atualização, precisamos obter o código existente
                fornecedor_existente = buscar_fornecedor_por_id(self.fornecedor_id)
                codigo_existente = fornecedor_existente[1] if fornecedor_existente else ""
                
                # Atualizar fornecedor existente
                atualizar_fornecedor(
                    self.fornecedor_id, codigo_existente, nome, fantasia, tipo, documento, 
                    data_cadastro, cep, rua, bairro, cidade, estado
                )
                
                mensagem = "Fornecedor atualizado com sucesso!"
            
            # Recarregar a tabela da tela de cadastro
            if self.cadastro_tela and hasattr(self.cadastro_tela, 'carregar_fornecedores'):
                self.cadastro_tela.carregar_fornecedores()
            
            # Mostrar mensagem de sucesso
            self.mostrar_mensagem("Sucesso", mensagem)
            
            # Fechar a janela de formulário após a inclusão
            if self.janela_parent:
                self.janela_parent.close()
                
        except Exception as e:
            print(f"Erro ao salvar fornecedor: {e}")
            self.mostrar_mensagem("Erro", f"Não foi possível salvar o fornecedor: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox(self)
        if "Aviso" in titulo or "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        
        # Personalizar botão Ok
        btn_ok = msg_box.addButton("OK", QMessageBox.AcceptRole)
        
        # Remover botões padrão
        msg_box.setStandardButtons(QMessageBox.NoButton)
        
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
                padding: 5px 15px;
                border-radius: 2px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)
        
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Cadastro de Fornecedores")
    window.setGeometry(100, 100, 800, 600)
    window.setMinimumSize(800, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    formulario_fornecedores_widget = FormularioFornecedores()
    window.setCentralWidget(formulario_fornecedores_widget)
    
    window.show()
    sys.exit(app.exec_())