#formulario_pessoa.py
import sys
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
        titulo = QLabel("Cadastro de Clientes")
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
        
        # Estilo específico para ComboBox (fundo branco e seleção azul)
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
                selection-background-color: #1a5f96;
                selection-color: white;
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
        self.tipo_combo.setStyleSheet(combo_style)  # Estilo específico para ComboBox com seleção azul
        self.tipo_combo.setFixedWidth(200)  # Largura fixa reduzida
        self.tipo_combo.addItems(["Jurídica", "Física"])
        self.tipo_combo.currentIndexChanged.connect(self.atualizar_tipo_documento)
        
        tipo_layout = QFormLayout()
        tipo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tipo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tipo_layout.addRow(self.tipo_label, self.tipo_combo)
        
        # Campo Data de Cadastro (VERSÃO CORRIGIDA COM ÍCONE)
        self.data_label = QLabel("Data de Cadastro:")
        self.data_label.setStyleSheet(label_style)
        self.data_input = QDateEdit()
        
        # Aplicar estilo com ícone de calendário
        self.data_input.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #cccccc;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #e0e0e0;
            }
            /* Usar icone personalizado */
            QDateEdit::down-arrow {
                image: url(ico-img/calendar-outline.svg);
                width: 16px;
                height: 16px;
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
                selection-background-color: #1a5f96;
                selection-color: white;
            }
            QCalendarWidget QToolButton {
                background-color: white;
                color: black;
            }
            QCalendarWidget QMenu {
                background-color: white;
            }
        """)
        
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
        
        # Definir estilo do widget principal e QMessageBox
        self.setStyleSheet("""
            background-color: #043b57;
            QTableWidget::item:selected {
                background-color: #1a5f96;
                color: white;
            }
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
        
        # Atualizar o tipo de documento com base no tipo de pessoa inicial
        self.atualizar_tipo_documento()
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            self.mostrar_mensagem("Atenção", 
                "O módulo 'requests' não está disponível. As funcionalidades de consulta de CEP não funcionarão.",
                QMessageBox.Warning)
            # Desabilitar botões de consulta
            self.btn_buscar_cep.setEnabled(False)
    
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
            # Isso evita problemas de cálculo de posição relativa
            if len(texto_limpo) == 0:
                nova_pos = 0
            elif len(texto_limpo) == 1:
                nova_pos = 2  # Após o primeiro dígito no formato "(1"
            elif len(texto_limpo) == 2:
                nova_pos = 3  # Após o DDD no formato "(12"
            elif len(texto_limpo) == 3:
                nova_pos = 6  # Após o primeiro dígito do número no formato "(12) 3"
            elif len(texto_limpo) == 4:
                nova_pos = 7  # Após o segundo dígito do número no formato "(12) 34"
            elif len(texto_limpo) == 5:
                nova_pos = 8  # Após o terceiro dígito do número no formato "(12) 345"
            elif len(texto_limpo) == 6:
                nova_pos = 9  # Após o quarto dígito do número no formato "(12) 3456"
            elif len(texto_limpo) == 7:
                nova_pos = 10  # Após o quinto dígito do número no formato "(12) 34567"
            elif len(texto_limpo) == 8:
                nova_pos = 12  # Após o primeiro dígito após o hífen no formato "(12) 34567-8"
            elif len(texto_limpo) == 9:
                nova_pos = 13  # Após o segundo dígito após o hífen no formato "(12) 34567-89"
            elif len(texto_limpo) == 10:
                nova_pos = 14  # Após o terceiro dígito após o hífen no formato "(12) 34567-890"
            else:  # len(texto_limpo) == 11
                nova_pos = 15  # Após o último dígito no formato "(12) 34567-8901"
            
            # Define a nova posição do cursor
            self.telefone_input.setCursorPosition(nova_pos)
            self.telefone_input.blockSignals(False)
    
    def formatar_documento(self, texto):
        """Formata o CNPJ/CPF durante a digitação"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Verificar se é CPF ou CNPJ
        if self.documento_label.text() == "CPF:":
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
        if len(texto_limpo) == 8 and REQUESTS_AVAILABLE:
            self.buscar_endereco_por_cep()
    
    def buscar_endereco_por_cep(self):
        """Busca o endereço pelo CEP usando a API ViaCEP"""
        # Verificar se o módulo requests está disponível
        if not REQUESTS_AVAILABLE:
            self.mostrar_mensagem("Funcionalidade indisponível", 
                               "A consulta de CEP requer o módulo 'requests' que não está disponível.",
                               QMessageBox.Warning)
            return
            
        # Obter o CEP sem formatação
        cep = ''.join(filter(str.isdigit, self.cep_input.text()))
        
        # Verificar se o CEP tem 8 dígitos
        if len(cep) != 8:
            self.mostrar_mensagem("CEP inválido", "O CEP deve ter 8 dígitos.", QMessageBox.Warning)
            return
            
        try:
            # Fazer a requisição à API ViaCEP
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url)
            
            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se há erro no CEP
                if "erro" in data and data["erro"]:
                    self.mostrar_mensagem("CEP não encontrado", "O CEP informado não foi encontrado.", QMessageBox.Warning)
                    return
                    
                # Preencher os campos de endereço
                self.rua_input.setText(data.get("logradouro", ""))
                self.bairro_input.setText(data.get("bairro", ""))
                self.cidade_input.setText(data.get("localidade", ""))
                self.estado_input.setText(data.get("uf", ""))
                
                # Focar no campo número (se existir) ou no próximo campo vazio
                # Como não temos campo de número, vamos focar no próximo campo após o CEP
                if not self.rua_input.text():
                    self.rua_input.setFocus()
                elif not self.bairro_input.text():
                    self.bairro_input.setFocus()
                elif not self.cidade_input.text():
                    self.cidade_input.setFocus()
                
            else:
                self.mostrar_mensagem("Erro na consulta", "Não foi possível consultar o CEP. Verifique sua conexão.", QMessageBox.Warning)
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao buscar o endereço: {str(e)}", QMessageBox.Critical)
    
    def validar_documento(self):
        """Valida o CNPJ ou CPF informado"""
        documento = self.documento_input.text()
        # Remover caracteres não numéricos
        doc_nums = ''.join(filter(str.isdigit, documento))
        
        # Verificar se é CPF ou CNPJ
        if self.documento_label.text() == "CPF:":
            # Verificar se tem 11 dígitos
            if len(doc_nums) != 11:
                self.mostrar_mensagem("CPF inválido", "O CPF deve ter 11 dígitos.", QMessageBox.Warning)
                return False
            
            # Verificar se todos os dígitos são iguais
            if len(set(doc_nums)) == 1:
                self.mostrar_mensagem("CPF inválido", "CPF com dígitos repetidos é inválido.", QMessageBox.Warning)
                return False
            
            return True
        else:
            # Verificar se tem 14 dígitos
            if len(doc_nums) != 14:
                self.mostrar_mensagem("CNPJ inválido", "O CNPJ deve ter 14 dígitos.", QMessageBox.Warning)
                return False
            
            # Verificar se todos os dígitos são iguais
            if len(set(doc_nums)) == 1:
                self.mostrar_mensagem("CNPJ inválido", "CNPJ com dígitos repetidos é inválido.", QMessageBox.Warning)
                return False
            
            return True
    def preencher_formulario_do_banco(self, id_pessoa):
        """Preenche o formulário com dados da pessoa do banco de dados"""
        try:
            from base.banco import buscar_pessoa_por_id
            
            # Buscar dados da pessoa
            pessoa = buscar_pessoa_por_id(id_pessoa)
            if not pessoa:
                self.mostrar_mensagem("Erro", f"Pessoa com ID {id_pessoa} não encontrada", QMessageBox.Warning)
                return False
            
            # ID, NOME, TIPO_PESSOA, DOCUMENTO, TELEFONE, DATA_CADASTRO, CEP, RUA, BAIRRO, CIDADE, ESTADO, OBSERVACAO
            self.codigo_input.setText(str(pessoa[0]))
            self.nome_input.setText(pessoa[1])
            
            # Configurar o tipo de pessoa
            index = 0 if pessoa[2] == "Jurídica" else 1
            self.tipo_combo.setCurrentIndex(index)
            
            # Formatar CNPJ/CPF para exibição
            documento = pessoa[3]
            if documento and len(documento) == 14:  # CNPJ
                documento_formatado = f"{documento[:2]}.{documento[2:5]}.{documento[5:8]}/{documento[8:12]}-{documento[12:]}"
            elif documento and len(documento) == 11:  # CPF
                documento_formatado = f"{documento[:3]}.{documento[3:6]}.{documento[6:9]}-{documento[9:]}"
            else:
                documento_formatado = documento
                
            self.documento_input.setText(documento_formatado)
            
            # Preencher telefone
            telefone = pessoa[4] or ""
            if telefone and len(telefone) > 10:  # Formatar telefone
                self.telefone_input.setText(f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}")
            elif telefone and len(telefone) > 2:
                self.telefone_input.setText(f"({telefone[:2]}) {telefone[2:]}")
            else:
                self.telefone_input.setText(telefone)
            
            # Preencher data de cadastro
            if pessoa[5]:  # DATA_CADASTRO
                try:
                    from PyQt5.QtCore import QDate
                    data = QDate.fromString(pessoa[5].strftime("%d/%m/%Y"), "dd/MM/yyyy")
                    self.data_input.setDate(data)
                except Exception as e:
                    print(f"Erro ao converter data: {e}")
                    self.data_input.setDate(QDate.currentDate())
            
            # Preencher CEP
            cep = pessoa[6] or ""
            if cep and len(cep) >= 8:
                self.cep_input.setText(f"{cep[:5]}-{cep[5:]}")
            else:
                self.cep_input.setText(cep)
            
            # Preencher outros campos de endereço
            self.rua_input.setText(pessoa[7] or "")  # RUA
            self.bairro_input.setText(pessoa[8] or "")  # BAIRRO
            self.cidade_input.setText(pessoa[9] or "")  # CIDADE
            self.estado_input.setText(pessoa[10] or "")  # ESTADO
            
            # Alterar texto do botão para Atualizar
            self.btn_incluir.setText("Atualizar")
            
            return True
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao carregar dados da pessoa: {e}", QMessageBox.Critical)
            return False
    
    def salvar_pessoa(self):
        """Salva os dados da pessoa no banco de dados"""
        nome = self.nome_input.text()
        tipo_pessoa = self.tipo_combo.currentText()
        documento = self.documento_input.text()
        telefone = self.telefone_input.text()
        data_cadastro = self.data_input.date().toString("dd/MM/yyyy")
        cep = self.cep_input.text()
        rua = self.rua_input.text()
        bairro = self.bairro_input.text()
        cidade = self.cidade_input.text()
        estado = self.estado_input.text().upper()
        codigo = self.codigo_input.text()  # Obtém o código se estiver preenchido
        
        # Validação básica
        if not nome:
            self.mostrar_mensagem("Campos obrigatórios", "Por favor, informe pelo menos o nome da pessoa.", QMessageBox.Warning)
            return
            
        if not documento:
            tipo_doc = "CPF" if self.documento_label.text() == "CPF:" else "CNPJ"
            self.mostrar_mensagem("Campos obrigatórios", f"Por favor, informe o {tipo_doc}.", QMessageBox.Warning)
            return
        
        # Validar documento
        if not self.validar_documento():
            return
        
        try:
            # Importar funções do banco de dados
            from base.banco import criar_pessoa, atualizar_pessoa, buscar_pessoa_por_id
            
            # Verificar se é uma atualização ou novo cadastro
            if self.btn_incluir.text() == "Atualizar" and codigo:
                # Verificar se a pessoa existe
                pessoa = buscar_pessoa_por_id(int(codigo))
                if not pessoa:
                    self.mostrar_mensagem("Erro", f"Pessoa com código {codigo} não encontrada", QMessageBox.Warning)
                    return
                    
                # Atualizar no banco de dados
                atualizar_pessoa(
                    int(codigo),
                    nome,
                    tipo_pessoa,
                    documento,
                    telefone,
                    data_cadastro,
                    cep,
                    rua,
                    bairro,
                    cidade,
                    estado
                )
                
                self.mostrar_mensagem("Sucesso", f"Pessoa atualizada com sucesso!\nNome: {nome}")
            else:
                # Criar nova pessoa no banco de dados
                novo_id = criar_pessoa(
                    nome,
                    tipo_pessoa,
                    documento,
                    telefone,
                    data_cadastro,
                    cep,
                    rua,
                    bairro,
                    cidade,
                    estado
                )
                
                self.mostrar_mensagem("Sucesso", f"Pessoa cadastrada com sucesso!\nNome: {nome}\nCódigo: {novo_id}")
            
            # Atualizar a tabela na tela principal
            if self.cadastro_tela:
                self.cadastro_tela.carregar_pessoas()
            
            # Fechar a janela
            if self.janela_parent:
                self.janela_parent.close()
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao salvar pessoa: {str(e)}", QMessageBox.Critical)

        
    def abrir_calendario(self):
        """Abre o calendário quando o botão ou o campo de data é clicado"""
        # Criar um calendário personalizado para garantir fundo branco
        calendario = QCalendarWidget(self)
        calendario.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                color: black;
            }
            QCalendarWidget QToolButton {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e6e6e6;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: black;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                color: black;
                selection-background-color: #1a5f96;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                color: black;
                selection-background-color: #1a5f96;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: white;
            }
        """)
        
        # Configurar o novo calendário
        calendario.setGridVisible(True)
        calendario.setSelectedDate(self.data_input.date())
        
        # Conectar o sinal de clique na data
        calendario.clicked.connect(self.selecionar_data)
        
        # Configurar o tamanho e posição do calendário
        pos = self.data_input.mapToGlobal(self.data_input.rect().bottomLeft())
        calendario.move(pos)
        calendario.setWindowFlags(Qt.Popup)
        calendario.show()
        
        # Armazenar referência ao calendário
        self.calendario_popup = calendario
        
    def selecionar_data(self, date):
        """Quando uma data é selecionada no calendário"""
        self.data_input.setDate(date)
        if hasattr(self, 'calendario_popup') and self.calendario_popup:
            self.calendario_popup.close()
            self.calendario_popup = None


# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aplicar estilo global para QMessageBox
    app.setStyleSheet("""
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
    
    window = QMainWindow()
    window.setWindowTitle("Formulário de Cadastro de Pessoa")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    form_widget = FormularioPessoa()
    window.setCentralWidget(form_widget)
    
    window.show()
    sys.exit(app.exec_())