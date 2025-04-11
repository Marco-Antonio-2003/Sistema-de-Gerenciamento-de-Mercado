#cadastro_pessoa.py
import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
try:
    # Importação relativa (mesmo pacote)
    from .formulario_pessoa import FormularioPessoa
except (ImportError, ModuleNotFoundError):
    try:
        # Importação do pacote geral
        from geral.formulario_pessoa import FormularioPessoa
    except (ImportError, ModuleNotFoundError):
        # Importação direta (mesmo diretório)
        from formulario_pessoa import FormularioPessoa


class CadastroPessoa(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título da tela
        title_label = QLabel("Cadastro de Pessoa")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setFont(QFont("Arial", 12))
        self.nome_label.setStyleSheet("color: white;")
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("background-color: #fffff0; padding: 8px; font-size: 12px;")
        self.nome_input.setMinimumHeight(35)
        form_layout.addRow(self.nome_label, self.nome_input)
        
        # Campo CNPJ/CPF
        self.documento_label = QLabel("CNPJ")
        self.documento_label.setFont(QFont("Arial", 12))
        self.documento_label.setStyleSheet("color: white;")
        self.documento_input = QLineEdit()
        self.documento_input.setStyleSheet("background-color: #fffff0; padding: 8px; font-size: 12px;")
        self.documento_input.setMinimumHeight(35)
        self.documento_input.textChanged.connect(self.formatar_documento)
        self.documento_input.setPlaceholderText("00.000.000/0001-00")
        form_layout.addRow(self.documento_label, self.documento_input)
        
        # Layout para Código e Tipo de Pessoa (lado a lado)
        codigo_tipo_layout = QHBoxLayout()
        
        # Campo Código
        codigo_form = QFormLayout()
        codigo_form.setLabelAlignment(Qt.AlignRight)
        codigo_form.setVerticalSpacing(15)
        codigo_form.setHorizontalSpacing(20)
        
        self.codigo_label = QLabel("Código")
        self.codigo_label.setFont(QFont("Arial", 12))
        self.codigo_label.setStyleSheet("color: white;")
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("background-color: #fffff0; padding: 8px; font-size: 12px;")
        self.codigo_input.setMinimumHeight(35)
        self.codigo_input.setMaximumWidth(150)
        codigo_form.addRow(self.codigo_label, self.codigo_input)
        
        # Tipo de Pessoa
        tipo_form = QFormLayout()
        tipo_form.setLabelAlignment(Qt.AlignRight)
        tipo_form.setVerticalSpacing(15)
        tipo_form.setHorizontalSpacing(20)
        
        self.tipo_label = QLabel("Tipo de Pessoa:")
        self.tipo_label.setFont(QFont("Arial", 12))
        self.tipo_label.setStyleSheet("color: white;")
        self.tipo_combo = QComboBox()
        # Atualizar o estilo do ComboBox Tipo de Pessoa
        # Substitua o estilo do ComboBox existente por este:

        self.tipo_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 8px;
                font-size: 12px;
                min-height: 35px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #cccccc;
                selection-background-color: #1a5f96;
                selection-color: white;
            }
        """)
        self.tipo_combo.addItems(["Jurídica", "Física"])
        self.tipo_combo.currentIndexChanged.connect(self.atualizar_tipo_documento)
        tipo_form.addRow(self.tipo_label, self.tipo_combo)
        
        codigo_tipo_layout.addLayout(codigo_form)
        codigo_tipo_layout.addStretch()
        codigo_tipo_layout.addLayout(tipo_form)
        
        # Campo Cidade
        cidade_form = QHBoxLayout()
        cidade_form.setSpacing(10)
        
        self.cidade_label = QLabel("Cidade")
        self.cidade_label.setFont(QFont("Arial", 12))
        self.cidade_label.setStyleSheet("color: white;")
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet("background-color: #fffff0; padding: 8px; font-size: 12px;")
        self.cidade_input.setMinimumHeight(35)
        
        cidade_layout = QFormLayout()
        cidade_layout.setLabelAlignment(Qt.AlignRight)
        cidade_layout.setVerticalSpacing(15)
        cidade_layout.setHorizontalSpacing(20)
        cidade_layout.addRow(self.cidade_label, self.cidade_input)
        
        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(10)
        
        self.btn_cadastrar = QPushButton("Cadastrar")
        # Usar ícone do sistema em vez de arquivo de imagem
        try:
            self.btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass  # Se falhar, continua sem ícone
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
        """)
        self.btn_cadastrar.clicked.connect(self.cadastrar_pessoa)
        
        self.btn_alterar = QPushButton("Alterar")
        # Usar ícone do sistema em vez de arquivo de imagem
        try:
            self.btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass  # Se falhar, continua sem ícone
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
        """)
        self.btn_alterar.clicked.connect(self.alterar_pessoa)
        
        self.btn_excluir = QPushButton("Excluir")
        # Usar ícone do sistema em vez de arquivo de imagem
        try:
            self.btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass  # Se falhar, continua sem ícone
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
        """)
        self.btn_excluir.clicked.connect(self.excluir_pessoa)
        
        botoes_layout.addWidget(self.btn_cadastrar)
        botoes_layout.addWidget(self.btn_alterar)
        botoes_layout.addWidget(self.btn_excluir)
        
        # Adicionar os layouts ao layout principal
        main_layout.addLayout(form_layout)
        main_layout.addLayout(codigo_tipo_layout)
        main_layout.addLayout(cidade_layout)
        main_layout.addLayout(botoes_layout)
        main_layout.addSpacing(20)
        
        # Tabela de pessoas
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Código", "Nome", "Tipo de pessoa"])
        self.table.horizontalHeader().setStyleSheet("background-color: #fffff0;")
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #fffff0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        # Ajustar largura das colunas
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table.itemClicked.connect(self.selecionar_pessoa)
        
        main_layout.addWidget(self.table)
        
        # Carregar dados de teste
        self.carregar_dados_teste()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")
    
    def atualizar_tipo_documento(self):
        """Atualiza o label CNPJ/CPF baseado no tipo de pessoa selecionado"""
        tipo_pessoa = self.tipo_combo.currentText()
        if tipo_pessoa == "Física":
            self.documento_label.setText("CPF")
            self.documento_input.setPlaceholderText("000.000.000-00")
            # Limpar o campo se já tiver um CNPJ digitado
            texto = self.documento_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) > 11:
                self.documento_input.clear()
        else:
            self.documento_label.setText("CNPJ")
            self.documento_input.setPlaceholderText("00.000.000/0001-00")
            # Limpar o campo se já tiver um CPF digitado
            texto = self.documento_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) <= 11 and len(''.join(filter(str.isdigit, texto))) > 0:
                self.documento_input.clear()
    
    def formatar_documento(self, texto):
        """Formata o CNPJ/CPF durante a digitação"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Verificar se é CPF ou CNPJ
        if self.documento_label.text() == "CPF":
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
            
            # Verifica se o texto realmente mudou para evitar loops
            if texto_formatado != texto:
                # Bloqueia sinais para evitar recursão
                self.documento_input.blockSignals(True)
                self.documento_input.setText(texto_formatado)
                
                # Posicionamento direto do cursor para CPF baseado no número de dígitos
                if len(texto_limpo) == 0:
                    nova_pos = 0
                elif len(texto_limpo) == 1:
                    nova_pos = 1
                elif len(texto_limpo) == 2:
                    nova_pos = 2
                elif len(texto_limpo) == 3:
                    nova_pos = 3
                elif len(texto_limpo) == 4:
                    nova_pos = 5  # Após o primeiro ponto: "123.4"
                elif len(texto_limpo) == 5:
                    nova_pos = 6
                elif len(texto_limpo) == 6:
                    nova_pos = 7
                elif len(texto_limpo) == 7:
                    nova_pos = 9  # Após o segundo ponto: "123.456.7"
                elif len(texto_limpo) == 8:
                    nova_pos = 10
                elif len(texto_limpo) == 9:
                    nova_pos = 11
                elif len(texto_limpo) == 10:
                    nova_pos = 13  # Após o hífen: "123.456.789-0"
                else:  # len(texto_limpo) == 11
                    nova_pos = 14
                
                # Define a nova posição do cursor
                self.documento_input.setCursorPosition(nova_pos)
                self.documento_input.blockSignals(False)
        else:
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
                self.documento_input.blockSignals(True)
                self.documento_input.setText(texto_formatado)
                
                # Posicionamento direto do cursor para CNPJ baseado no número de dígitos
                if len(texto_limpo) == 0:
                    nova_pos = 0
                elif len(texto_limpo) == 1:
                    nova_pos = 1
                elif len(texto_limpo) == 2:
                    nova_pos = 2
                elif len(texto_limpo) == 3:
                    nova_pos = 4  # Após o primeiro ponto: "12.3"
                elif len(texto_limpo) == 4:
                    nova_pos = 5
                elif len(texto_limpo) == 5:
                    nova_pos = 6
                elif len(texto_limpo) == 6:
                    nova_pos = 8  # Após o segundo ponto: "12.345.6"
                elif len(texto_limpo) == 7:
                    nova_pos = 9
                elif len(texto_limpo) == 8:
                    nova_pos = 10
                elif len(texto_limpo) == 9:
                    nova_pos = 12  # Após a barra: "12.345.678/9"
                elif len(texto_limpo) == 10:
                    nova_pos = 13
                elif len(texto_limpo) == 11:
                    nova_pos = 14
                elif len(texto_limpo) == 12:
                    nova_pos = 15
                elif len(texto_limpo) == 13:
                    nova_pos = 17  # Após o hífen: "12.345.678/9012-3"
                else:  # len(texto_limpo) == 14
                    nova_pos = 18
                
                # Define a nova posição do cursor
                self.documento_input.setCursorPosition(nova_pos)
                self.documento_input.blockSignals(False)
    
    def validar_documento(self):
        """Valida o CNPJ ou CPF informado"""
        documento = self.documento_input.text()
        # Remover caracteres não numéricos
        doc_nums = ''.join(filter(str.isdigit, documento))
        
        # Verificar se é CPF ou CNPJ
        if self.documento_label.text() == "CPF":
            # Verificar se tem 11 dígitos
            if len(doc_nums) != 11:
                QMessageBox.warning(self, "CPF inválido", "O CPF deve ter 11 dígitos.")
                return False
            
            # Verificar se todos os dígitos são iguais
            if len(set(doc_nums)) == 1:
                QMessageBox.warning(self, "CPF inválido", "CPF com dígitos repetidos é inválido.")
                return False
            
            return True
        else:
            # Verificar se tem 14 dígitos
            if len(doc_nums) != 14:
                QMessageBox.warning(self, "CNPJ inválido", "O CNPJ deve ter 14 dígitos.")
                return False
            
            # Verificar se todos os dígitos são iguais
            if len(set(doc_nums)) == 1:
                QMessageBox.warning(self, "CNPJ inválido", "CNPJ com dígitos repetidos é inválido.")
                return False
            
            return True
    
    def carregar_dados_teste(self):
        # Dados de exemplo para demonstração
        dados = [
            (1, "João Silva", "Física"),
            (2, "Maria Comercial Ltda.", "Jurídica"),
            (3, "Carlos Pereira", "Física")
        ]
        
        self.table.setRowCount(len(dados))
        
        for row, (codigo, nome, tipo) in enumerate(dados):
            self.table.setItem(row, 0, QTableWidgetItem(str(codigo)))
            self.table.setItem(row, 1, QTableWidgetItem(nome))
            self.table.setItem(row, 2, QTableWidgetItem(tipo))
    
    def selecionar_pessoa(self, item):
        row = item.row()
        
        # Preencher os campos com os dados da linha selecionada
        codigo = self.table.item(row, 0).text()
        nome = self.table.item(row, 1).text()
        tipo = self.table.item(row, 2).text()
        
        self.codigo_input.setText(codigo)
        self.nome_input.setText(nome)
        
        # Ajustar o combo de tipo de pessoa
        index = 0 if tipo == "Jurídica" else 1
        self.tipo_combo.setCurrentIndex(index)
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem para o usuário com estilo personalizado"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Aplicar estilo personalizado para texto branco e botões personalizados
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #043b57;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                min-width: 80px;
                min-height: 25px;
                padding: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        
        return msg_box.exec_()
    
    def load_formulario_pessoa(self):
        """Carrega dinamicamente o módulo FormularioPessoa"""
        try:
            # Tente primeiro com importação direta (para ambiente de desenvolvimento)
            try:
                # Importação direta usando o módulo
                from geral.formulario_pessoa import FormularioPessoa
                print("Importação direta de FormularioPessoa bem-sucedida")
                return FormularioPessoa
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_pessoa.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_pessoa.py")
                
                # Se o arquivo não existir, vamos criar um básico
                if not os.path.exists(module_path):
                    self.criar_formulario_pessoa_padrao(module_path)
                
                # Carregar o módulo dinamicamente
                module_name = "formulario_pessoa"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Não foi possível carregar o módulo {module_name}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Retornar a classe FormularioPessoa
                if hasattr(module, "FormularioPessoa"):
                    return getattr(module, "FormularioPessoa")
                else:
                    raise ImportError(f"A classe FormularioPessoa não foi encontrada no módulo {module_name}")
        except Exception as e:
            print(f"Erro ao carregar FormularioPessoa: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}", QMessageBox.Critical)
            return None
            
    def criar_formulario_pessoa_padrao(self, filepath):
        """Cria um arquivo formulario_pessoa.py básico se não existir"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''import sys
# Importação condicional do requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QFormLayout, QComboBox, QMessageBox, QTableWidgetItem,
                             QDateEdit, QCalendarWidget)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate

class FormularioPessoa(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela  # Referência para a tela de cadastro
        self.janela_parent = janela_parent  # Referência para a janela que contém este widget
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Layout para o botão de voltar e título
        header_layout = QHBoxLayout()
        
        # Botão de voltar (diminuído horizontalmente)
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setFixedWidth(80)  # Largura fixa reduzida
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Título
        titulo_layout = QVBoxLayout()
        titulo = QLabel("Cadastro de Pessoa")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(titulo)
        
        # Adicionar botão de voltar e título ao header
        header_layout.addWidget(self.btn_voltar)
        header_layout.addLayout(titulo_layout)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; font-weight: bold; }"
        
        # Estilo para os inputs (reduzidos)
        input_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
        """
        
        # Estilo específico para ComboBox (fundo branco)
        combo_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #cccccc;
                selection-background-color: #e6e6e6;
            }
        """
        
        # Estilo específico para DateEdit (fundo branco)
        date_style = """
            QDateEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            /* Estilo para deixar o botão dropdown visível com fundo cinza */
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #cccccc;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #e0e0e0;
            }
            QDateEdit::down-arrow {
                image: none;
                width: 12px;
                height: 12px;
                background-color: #888888;
                margin-right: 4px;
                margin-top: 1px;
            }
            /* Estilo para o calendário em si */
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QWidget {
                background-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                color: black;
            }
            QCalendarWidget QToolButton {
                background-color: white;
                color: black;
            }
            QCalendarWidget QMenu {
                background-color: white;
            }
        """
        
        # Layout para Código e Telefone (lado a lado)
        codigo_telefone_layout = QHBoxLayout()
        
        # Campo Código
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        self.codigo_input.setFixedWidth(100)  # Largura fixa reduzida
        self.codigo_input.setReadOnly(True)  # Código é gerado automaticamente
        
        codigo_layout = QFormLayout()
        codigo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        codigo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        codigo_layout.addRow(self.codigo_label, self.codigo_input)
        
        # Campo Telefone
        self.telefone_label = QLabel("Telefone:")
        self.telefone_label.setStyleSheet(label_style)
        self.telefone_input = QLineEdit()
        self.telefone_input.setStyleSheet(input_style)
        self.telefone_input.setFixedWidth(200)  # Largura fixa reduzida
        self.telefone_input.textChanged.connect(self.formatar_telefone)
        self.telefone_input.setPlaceholderText("(00) 00000-0000")
        
        telefone_layout = QFormLayout()
        telefone_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        telefone_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        telefone_layout.addRow(self.telefone_label, self.telefone_input)
        
        codigo_telefone_layout.addLayout(codigo_layout)
        codigo_telefone_layout.addLayout(telefone_layout)
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setStyleSheet(label_style)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(input_style)
        self.nome_input.setMaximumHeight(30)  # Altura máxima reduzida
        
        nome_layout = QFormLayout()
        nome_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        nome_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        nome_layout.addRow(self.nome_label, self.nome_input)
        
        # Layout para Tipo de Pessoa e Data de Cadastro (lado a lado)
        tipo_data_layout = QHBoxLayout()
        
        # Campo Tipo de Pessoa
        self.tipo_label = QLabel("Tipo de Pessoa:")
        self.tipo_label.setStyleSheet(label_style)
        self.tipo_combo = QComboBox()
        self.tipo_combo.setStyleSheet(combo_style)  # Estilo específico para ComboBox
        self.tipo_combo.setFixedWidth(200)  # Largura fixa reduzida
        self.tipo_combo.addItems(["Jurídica", "Física"])
        self.tipo_combo.currentIndexChanged.connect(self.atualizar_tipo_documento)
        
        tipo_layout = QFormLayout()
        tipo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tipo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tipo_layout.addRow(self.tipo_label, self.tipo_combo)
        
        # Campo Data de Cadastro
        self.data_label = QLabel("Data de Cadastro:")
        self.data_label.setStyleSheet(label_style)
        self.data_input = QDateEdit()
        self.data_input.setStyleSheet(date_style)  # Estilo específico para DateEdit
        self.data_input.setFixedWidth(150)  # Largura fixa reduzida
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        
        data_layout = QFormLayout()
        data_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        data_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        data_layout.addRow(self.data_label, self.data_input)
        
        tipo_data_layout.addLayout(tipo_layout)
        tipo_data_layout.addLayout(data_layout)
        
        # Campo CNPJ/CPF
        self.documento_label = QLabel("CNPJ / CPF:")
        self.documento_label.setStyleSheet(label_style)
        self.documento_input = QLineEdit()
        self.documento_input.setStyleSheet(input_style)
        self.documento_input.setFixedWidth(250)  # Largura fixa reduzida
        self.documento_input.textChanged.connect(self.formatar_documento)
        self.documento_input.setPlaceholderText("00.000.000/0001-00")
        
        documento_layout = QFormLayout()
        documento_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        documento_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        documento_layout.addRow(self.documento_label, self.documento_input)
        
        # Título do Endereço
        endereco_titulo = QLabel("Endereço")
        endereco_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        endereco_titulo.setStyleSheet("color: white; margin-top: 20px;")
        endereco_titulo.setAlignment(Qt.AlignCenter)
        
        # Layout para CEP e botão de busca
        cep_layout = QHBoxLayout()
        
        # Campo CEP
        self.cep_label = QLabel("CEP:")
        self.cep_label.setStyleSheet(label_style)
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet(input_style)
        self.cep_input.textChanged.connect(self.formatar_cep)
        self.cep_input.setPlaceholderText("00000-000")
        
        # Botão de Busca CEP
        self.btn_buscar_cep = QPushButton("Buscar CEP")
        self.btn_buscar_cep.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_buscar_cep.clicked.connect(self.buscar_endereco_por_cep)
        
        cep_form_layout = QFormLayout()
        cep_form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cep_form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cep_form_layout.addRow(self.cep_label, self.cep_input)
        
        cep_layout.addLayout(cep_form_layout)
        cep_layout.addWidget(self.btn_buscar_cep)
        
        # Campo Rua
        self.rua_label = QLabel("Rua:")
        self.rua_label.setStyleSheet(label_style)
        self.rua_input = QLineEdit()
        self.rua_input.setStyleSheet(input_style)
        
        rua_layout = QFormLayout()
        rua_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rua_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rua_layout.addRow(self.rua_label, self.rua_input)
        
        # Campo Bairro
        self.bairro_label = QLabel("Bairro:")
        self.bairro_label.setStyleSheet(label_style)
        self.bairro_input = QLineEdit()
        self.bairro_input.setStyleSheet(input_style)
        
        bairro_layout = QFormLayout()
        bairro_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bairro_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        bairro_layout.addRow(self.bairro_label, self.bairro_input)
        
        # Campo Cidade e Estado (lado a lado)
        cidade_estado_layout = QHBoxLayout()
        
        # Campo Cidade
        self.cidade_label = QLabel("Cidade:")
        self.cidade_label.setStyleSheet(label_style)
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(input_style)
        
        cidade_layout = QFormLayout()
        cidade_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cidade_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cidade_layout.addRow(self.cidade_label, self.cidade_input)
        
        # Campo Estado (novo)
        self.estado_label = QLabel("Estado (UF):")
        self.estado_label.setStyleSheet(label_style)
        self.estado_input = QLineEdit()
        self.estado_input.setStyleSheet(input_style)
        self.estado_input.setMaxLength(2)
        
        estado_layout = QFormLayout()
        estado_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        estado_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        estado_layout.addRow(self.estado_label, self.estado_input)
        
        cidade_estado_layout.addLayout(cidade_layout)
        cidade_estado_layout.addLayout(estado_layout)
        
        # Botão Incluir
        incluir_layout = QHBoxLayout()
        incluir_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                font-weight: bold;
                padding: 12px 40px;
                font-size: 16px;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir.clicked.connect(self.salvar_pessoa)
        
        incluir_layout.addWidget(self.btn_incluir)
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(codigo_telefone_layout)
        main_layout.addLayout(nome_layout)
        main_layout.addLayout(tipo_data_layout)
        main_layout.addLayout(documento_layout)
        main_layout.addWidget(endereco_titulo)
        main_layout.addLayout(cep_layout)
        main_layout.addLayout(rua_layout)
        main_layout.addLayout(bairro_layout)
        main_layout.addLayout(cidade_estado_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(incluir_layout)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
        # Atualizar o tipo de documento com base no tipo de pessoa inicial
        self.atualizar_tipo_documento()
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Atenção", 
                "O módulo 'requests' não está disponível. As funcionalidades de consulta de CEP não funcionarão.")
            # Desabilitar botões de consulta
            self.btn_buscar_cep.setEnabled(False)
        
    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
    def atualizar_tipo_documento(self):
        """Atualiza o label e placeholder do campo de documento conforme o tipo de pessoa"""
        tipo_pessoa = self.tipo_combo.currentText()
        if tipo_pessoa == "Física":
            self.documento_label.setText("CPF:")
            self.documento_input.setPlaceholderText("000.000.000-00")
            # Limpar o campo se já tiver um CNPJ digitado
            texto = self.documento_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) > 11:
                self.documento_input.clear()
        else:
            self.documento_label.setText("CNPJ:")
            self.documento_input.setPlaceholderText("00.000.000/0001-00")
            # Limpar o campo se já tiver um CPF digitado
            texto = self.documento_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) <= 11 and len(''.join(filter(str.isdigit, texto))) > 0:
                self.documento_input.clear()
    
    def formatar_telefone(self, texto):
        """Formata o telefone para (XX) XXXXX-XXXX"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 11 dígitos
        if len(texto_limpo) > 11:
            texto_limpo = texto_limpo[:11]
        
        # Formatar o telefone
        if len(texto_limpo) == 0:
            texto_formatado = ""
        elif len(texto_limpo) <= 2:
            texto_formatado = f"({texto_limpo}"
        elif len(texto_limpo) <= 7:
            texto_formatado = f"({texto_limpo[:2]}) {texto_limpo[2:]}"
        else:
            texto_formatado = f"({texto_limpo[:2]}) {texto_limpo[2:7]}-{texto_limpo[7:]}"
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Bloqueia sinais para evitar recursão
            self.telefone_input.blockSignals(True)
            self.telefone_input.setText(texto_formatado)
            
            # Posiciona o cursor com base apenas no número de dígitos
            if len(texto_limpo) == 0:
                nova_pos = 0
            elif len(texto_limpo) == 1:
                nova_pos = 2  # Após o primeiro dígito no formato "(1"
            elif len(texto_limpo) == 2:
                nova_pos = 3  # Após o DDD no formato "(12"
            elif len(texto_limpo) <= 7:
                nova_pos = 5 + len(texto_limpo) - 2  # Posição na parte central do telefone
            else:
                nova_pos = 11 + len(texto_limpo) - 7  # Posição após o hífen
            
            # Define a nova posição do cursor
            self.telefone_input.setCursorPosition(nova_pos)
            self.telefone_input.blockSignals(False)
    
    def formatar_documento(self, texto):
        """Formata o CNPJ/CPF durante a digitação"""
        # Implementação completa de formatação de documento
        pass
        
    def formatar_cep(self, texto):
        """Formata o CEP durante a digitação"""
        # Implementação completa de formatação de CEP
        pass
        
    def buscar_endereco_por_cep(self):
        """Busca o endereço pelo CEP usando a API ViaCEP"""
        # Esta função depende do módulo requests
        # Implementação completa de busca de CEP
        pass
    
    def salvar_pessoa(self):
        """Salva os dados da pessoa na tabela da tela de cadastro"""
        nome = self.nome_input.text()
        documento = self.documento_input.text() if hasattr(self, 'documento_input') else ""
        tipo_pessoa = self.tipo_combo.currentText()
        codigo = self.codigo_input.text()  # Obtém o código se estiver preenchido
        
        # Validação básica para o nome
        if not nome:
            self.mostrar_mensagem("Campos obrigatórios", "Por favor, informe pelo menos o nome da pessoa.", QMessageBox.Warning)
            return
        
        # Verificar acesso à tabela
        if not self.cadastro_tela or not hasattr(self.cadastro_tela, 'table'):
            self.mostrar_mensagem("Erro", "Não foi possível acessar a tabela de pessoas.", QMessageBox.Critical)
            return
        
        # Verificar se é uma atualização ou novo cadastro
        if self.btn_incluir.text() == "Atualizar" and codigo:
            # Modo de atualização - procurar o item na tabela pelo código
            encontrado = False
            for row in range(self.cadastro_tela.table.rowCount()):
                if self.cadastro_tela.table.item(row, 0).text() == codigo:
                    # Atualizar os dados na tabela
                    self.cadastro_tela.table.setItem(row, 1, QTableWidgetItem(nome))
                    self.cadastro_tela.table.setItem(row, 2, QTableWidgetItem(tipo_pessoa))
                    
                    # Mensagem de sucesso
                    self.mostrar_mensagem("Sucesso", f"Pessoa atualizada com sucesso!\nNome: {nome}\nTipo: {tipo_pessoa}")
                    
                    encontrado = True
                    break
            
            if not encontrado:
                self.mostrar_mensagem("Erro", "Pessoa não encontrada para atualização.", QMessageBox.Warning)
                return
        else:
            # Gerar código para nova pessoa
            ultimo_codigo = 0
            if self.cadastro_tela.table.rowCount() > 0:
                for row in range(self.cadastro_tela.table.rowCount()):
                    codigo = int(self.cadastro_tela.table.item(row, 0).text())
                    if codigo > ultimo_codigo:
                        ultimo_codigo = codigo
            
            novo_codigo = ultimo_codigo + 1
            
            # Adicionar à tabela
            row_position = self.cadastro_tela.table.rowCount()
            self.cadastro_tela.table.insertRow(row_position)
            self.cadastro_tela.table.setItem(row_position, 0, QTableWidgetItem(str(novo_codigo)))
            self.cadastro_tela.table.setItem(row_position, 1, QTableWidgetItem(nome))
            self.cadastro_tela.table.setItem(row_position, 2, QTableWidgetItem(tipo_pessoa))
            
            # Mensagem de sucesso
            self.mostrar_mensagem("Sucesso", f"Pessoa cadastrada com sucesso!\nNome: {nome}\nCódigo: {novo_codigo}")
        
        # Fechar a janela em ambos os casos
        if self.janela_parent:
            self.janela_parent.close()
''')
        except Exception as e:
            print(f"Erro ao criar arquivo formulario_pessoa.py: {str(e)}")
    
    def cadastrar_pessoa(self):
        """Abre o formulário para cadastro de pessoa"""
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'form_window') and self.form_window.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
            self.form_window.activateWindow()
            self.form_window.raise_()
            return
        
        # Criar uma nova janela para o formulário
        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Formulário de Cadastro de Pessoa")
        self.form_window.setGeometry(100, 100, 800, 600)
        self.form_window.setStyleSheet("background-color: #043b57;")
        
        # Criar e definir o widget do formulário
        # Passar a própria instância e a tabela para que o formulário possa adicionar dados
        form_widget = FormularioPessoa(self, self.form_window)
        self.form_window.setCentralWidget(form_widget)
        
        # Mostrar a janela
        self.form_window.show()
    
    def alterar_pessoa(self):
        """Abre o formulário para alterar os dados da pessoa selecionada"""
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        tipo = self.tipo_combo.currentText()
        documento = self.documento_input.text()
        cidade = self.cidade_input.text()
        
        if not codigo or not nome:
            self.mostrar_mensagem("Seleção necessária", 
                                "Por favor, selecione uma pessoa para alterar",
                                QMessageBox.Warning)
            return
        
        # Carregar a classe FormularioPessoa
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'form_window') and self.form_window.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
            self.form_window.activateWindow()
            self.form_window.raise_()
            return
        
        # Criar uma nova janela para o formulário
        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Alterar Cadastro de Pessoa")
        self.form_window.setGeometry(100, 100, 800, 600)
        self.form_window.setStyleSheet("""
            background-color: #043b57;
            QMessageBox {
                background-color: #043b57;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                min-width: 80px;
                min-height: 25px;
                padding: 3px;
                font-size: 13px;
            }
            QMessageBox QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        
        # Criar e definir o widget do formulário
        form_widget = FormularioPessoa(self, self.form_window)
        self.form_window.setCentralWidget(form_widget)
        
        # Preencher os campos com os dados da pessoa selecionada
        form_widget.codigo_input.setText(codigo)
        form_widget.nome_input.setText(nome)
        
        # Configurar o combo de tipo de pessoa
        index = 0 if tipo == "Jurídica" else 1
        form_widget.tipo_combo.setCurrentIndex(index)
        
        # Preencher outros campos se disponíveis
        if documento:
            form_widget.documento_input.setText(documento)
        if cidade:
            form_widget.cidade_input.setText(cidade)
        
        # Alterando o título do botão para "Atualizar" em vez de "Incluir"
        form_widget.btn_incluir.setText("Atualizar")
        
        # Mostrar a janela
        self.form_window.show()
    
    def excluir_pessoa(self):
        """Exclui uma pessoa"""
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Seleção necessária", 
                                 "Por favor, selecione uma pessoa para excluir", 
                                 QMessageBox.Warning)
            return
            
        # Confirmar exclusão
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir a pessoa de código {codigo}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.No:
            return
        
        # Busca a linha pelo código
        encontrado = False
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == codigo:
                nome = self.table.item(row, 1).text()
                self.table.removeRow(row)
                
                # Limpa os campos
                self.codigo_input.clear()
                self.nome_input.clear()
                self.documento_input.clear()
                self.cidade_input.clear()
                
                self.mostrar_mensagem("Sucesso", f"Pessoa {nome} (código: {codigo}) excluída com sucesso!")
                encontrado = True
                break
        
        if not encontrado:
            self.mostrar_mensagem("Não encontrado", 
                                 f"Pessoa com código {codigo} não encontrada", 
                                 QMessageBox.Warning)


# Classe para executar o módulo como script principal
class CadastroPessoaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Pessoa")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #043b57;")
        
        cadastro_widget = CadastroPessoa()
        self.setCentralWidget(cadastro_widget)

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CadastroPessoaWindow()
    window.show()
    sys.exit(app.exec_())