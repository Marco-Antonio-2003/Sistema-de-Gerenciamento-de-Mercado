#formulario_empresa.py
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
                             QFormLayout, QComboBox, QMessageBox, QTableWidgetItem)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

class FormularioEmpresa(QWidget):
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
        titulo = QLabel("Cadastro de empresa")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(titulo)
        
        # Adicionar botão de voltar e título ao header
        header_layout.addWidget(self.btn_voltar)
        header_layout.addLayout(titulo_layout)
        header_layout.setStretch(1, 1)  # Dar mais espaço ao título
        
        main_layout.addLayout(header_layout)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setVerticalSpacing(20)
        form_layout.setHorizontalSpacing(20)
        
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
        
        # Campo Código
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        self.codigo_input.setReadOnly(True)  # Código é gerado automaticamente
        self.codigo_input.setFixedWidth(100)  # Reduzido de 200 para 100
        form_layout.addRow(self.codigo_label, self.codigo_input)
        
        # Layout para CNPJ/CPF e botão de consulta
        documento_layout = QHBoxLayout()
        documento_layout.setSpacing(0)
        
        # Campo CNPJ/CPF
        self.documento_label = QLabel("CNPJ:")
        self.documento_label.setStyleSheet(label_style)
        
        # Criar layout horizontal para o campo de documento e o botão de consulta
        documento_field_layout = QHBoxLayout()
        documento_field_layout.setSpacing(0)
        documento_field_layout.setContentsMargins(0, 0, 0, 0)
        
        # Input de CNPJ/CPF com borda direita removida
        self.documento_input = QLineEdit()
        self.documento_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-right: none;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        self.documento_input.setFixedWidth(220)  # Largura ajustada
        self.documento_input.textChanged.connect(self.formatar_documento)
        self.documento_input.setPlaceholderText("00.000.000/0001-00")
        
        # Botão de consulta CNPJ/CPF
        self.btn_consultar = QPushButton("Consultar")
        self.btn_consultar.setFixedWidth(80)
        self.btn_consultar.setFixedHeight(30)
        self.btn_consultar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: 1px solid #cccccc;
                border-left: none;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_consultar.clicked.connect(self.consultar_documento)
        
        # Adicionar os widgets ao layout do campo de documento
        documento_field_layout.addWidget(self.documento_input)
        documento_field_layout.addWidget(self.btn_consultar)
        
        # Layout para o label e o campo de documento com botão
        documento_form_layout = QFormLayout()
        documento_form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        documento_form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        documento_form_layout.addRow(self.documento_label, documento_field_layout)
        
        main_layout.addLayout(documento_form_layout)
        main_layout.addSpacing(10)
        
        # Campo Nome da pessoa
        self.nome_pessoa_label = QLabel("Nome da pessoa:")
        self.nome_pessoa_label.setStyleSheet(label_style)
        self.nome_pessoa_input = QLineEdit()
        self.nome_pessoa_input.setStyleSheet(input_style)
        self.nome_pessoa_input.setMaximumHeight(30)  # Altura máxima reduzida
        form_layout.addRow(self.nome_pessoa_label, self.nome_pessoa_input)
        
        # Campo Nome da Empresa
        self.nome_empresa_label = QLabel("Nome da Empresa:")
        self.nome_empresa_label.setStyleSheet(label_style)
        self.nome_empresa_input = QLineEdit()
        self.nome_empresa_input.setStyleSheet(input_style)
        self.nome_empresa_input.setMaximumHeight(30)  # Altura máxima reduzida
        form_layout.addRow(self.nome_empresa_label, self.nome_empresa_input)
        
        # Layout para Tipo de Regime e Telefone (lado a lado)
        regime_telefone_layout = QHBoxLayout()
        
        # Campo Tipo de Regime
        self.regime_label = QLabel("Tipo de Regime:")
        self.regime_label.setStyleSheet(label_style)
        self.regime_combo = QComboBox()
        self.regime_combo.setStyleSheet(combo_style)  # Estilo específico para ComboBox com seleção azul
        self.regime_combo.setFixedWidth(200)  # Largura fixa reduzida
        self.regime_combo.addItems(["Simples Nacional", "Lucro Presumido", "Lucro Real", "MEI"])
        self.regime_combo.currentIndexChanged.connect(self.atualizar_tipo_documento)
        
        regime_layout = QFormLayout()
        regime_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        regime_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        regime_layout.addRow(self.regime_label, self.regime_combo)
        
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
        
        regime_telefone_layout.addLayout(regime_layout)
        regime_telefone_layout.addLayout(telefone_layout)
        
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(regime_telefone_layout)
        
        # Adicionar campos para endereço
        endereco_titulo = QLabel("Endereço")
        endereco_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        endereco_titulo.setStyleSheet("color: white; margin-top: 20px;")
        endereco_titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(endereco_titulo)
        
        # Layout para CEP e botão de busca
        cep_layout = QHBoxLayout()
        
        # Campo CEP
        self.cep_label = QLabel("CEP:")
        self.cep_label.setStyleSheet(label_style)
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet(input_style)
        self.cep_input.setFixedWidth(120)  # Largura fixa reduzida
        self.cep_input.textChanged.connect(self.formatar_cep)
        self.cep_input.setPlaceholderText("00000-000")
        
        # Botão de Busca CEP (reduzido)
        self.btn_buscar_cep = QPushButton("Buscar CEP")
        self.btn_buscar_cep.setFixedWidth(100)  # Largura fixa reduzida
        self.btn_buscar_cep.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 6px 10px;
                font-size: 12px;
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
        cep_layout.addStretch(1)  # Adiciona espaço flexível à direita
        
        main_layout.addLayout(cep_layout)
        
        # Campo Rua
        self.rua_label = QLabel("Rua:")
        self.rua_label.setStyleSheet(label_style)
        self.rua_input = QLineEdit()
        self.rua_input.setStyleSheet(input_style)
        self.rua_input.setMaximumHeight(30)  # Altura máxima reduzida
        
        rua_layout = QFormLayout()
        rua_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rua_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rua_layout.addRow(self.rua_label, self.rua_input)
        
        main_layout.addLayout(rua_layout)
        
        # Layout para Bairro e Número (lado a lado)
        bairro_numero_layout = QHBoxLayout()
        
        # Campo Bairro
        self.bairro_label = QLabel("Bairro:")
        self.bairro_label.setStyleSheet(label_style)
        self.bairro_input = QLineEdit()
        self.bairro_input.setStyleSheet(input_style)
        self.bairro_input.setMaximumHeight(30)  # Altura máxima reduzida
        
        bairro_layout = QFormLayout()
        bairro_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bairro_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        bairro_layout.addRow(self.bairro_label, self.bairro_input)
        
        # Campo Número
        self.numero_label = QLabel("Número:")
        self.numero_label.setStyleSheet(label_style)
        self.numero_input = QLineEdit()
        self.numero_input.setStyleSheet(input_style)
        self.numero_input.setFixedWidth(100)  # Largura fixa reduzida
        
        numero_layout = QFormLayout()
        numero_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        numero_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        numero_layout.addRow(self.numero_label, self.numero_input)
        
        bairro_numero_layout.addLayout(bairro_layout)
        bairro_numero_layout.addLayout(numero_layout)
        
        main_layout.addLayout(bairro_numero_layout)
        
        # Campo Cidade e Estado (lado a lado)
        cidade_estado_layout = QHBoxLayout()
        
        # Campo Cidade
        self.cidade_label = QLabel("Cidade:")
        self.cidade_label.setStyleSheet(label_style)
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(input_style)
        self.cidade_input.setFixedWidth(250)  # Largura fixa reduzida
        
        cidade_layout = QFormLayout()
        cidade_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cidade_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cidade_layout.addRow(self.cidade_label, self.cidade_input)
        
        # Campo Estado (UF)
        self.estado_label = QLabel("Estado (UF):")
        self.estado_label.setStyleSheet(label_style)
        self.estado_input = QLineEdit()
        self.estado_input.setStyleSheet(input_style)
        self.estado_input.setFixedWidth(80)  # Largura fixa reduzida
        self.estado_input.setMaxLength(2)
        
        estado_layout = QFormLayout()
        estado_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        estado_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        estado_layout.addRow(self.estado_label, self.estado_input)
        
        cidade_estado_layout.addLayout(cidade_layout)
        cidade_estado_layout.addLayout(estado_layout)
        
        main_layout.addLayout(cidade_estado_layout)
        main_layout.addSpacing(20)
        
        # Botão Incluir (reduzido na altura)
        incluir_layout = QHBoxLayout()
        incluir_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                font-weight: bold;
                padding: 10px 40px;
                font-size: 16px;
                border-radius: 4px;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir.clicked.connect(self.salvar_empresa)
        
        incluir_layout.addWidget(self.btn_incluir)
        main_layout.addLayout(incluir_layout)
        
        # Adicionar espaço na parte inferior
        main_layout.addStretch(1)
        
        # Definir estilo do widget principal com estilo para QTableWidget e QMessageBox
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
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Atenção", 
                "O módulo 'requests' não está disponível. As funcionalidades de consulta de CNPJ e CEP não funcionarão.")
            # Desabilitar botões de consulta
            self.btn_consultar.setEnabled(False)
            self.btn_buscar_cep.setEnabled(False)
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem para o usuário com estilo personalizado"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Aplicar estilo personalizado
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
        
    def atualizar_tipo_documento(self):
        """Atualiza o label CNPJ/CPF baseado no tipo de regime selecionado"""
        regime = self.regime_combo.currentText()
        if regime == "MEI":
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
                
                # Se o CNPJ estiver completo (14 dígitos), consultar automaticamente
                if len(texto_limpo) == 14 and REQUESTS_AVAILABLE:
                    self.consultar_documento()
    
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
                
                # Focar no campo número
                self.numero_input.setFocus()
                
            else:
                self.mostrar_mensagem("Erro na consulta", "Não foi possível consultar o CEP. Verifique sua conexão.", QMessageBox.Warning)
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao buscar o endereço: {str(e)}", QMessageBox.Critical)
    
    def consultar_documento(self):
        """Consulta informações da empresa pelo CNPJ ou pessoa pelo CPF"""
        # Verificar se o módulo requests está disponível
        if not REQUESTS_AVAILABLE:
            self.mostrar_mensagem("Funcionalidade indisponível", 
                               "A consulta de CNPJ/CPF requer o módulo 'requests' que não está disponível.",
                               QMessageBox.Warning)
            return
            
        # Obter o documento sem formatação
        doc_limpo = ''.join(filter(str.isdigit, self.documento_input.text()))
        
        # Verificar se é CPF ou CNPJ
        if self.documento_label.text() == "CPF:":
            # Para CPF, implementação depende de integração com banco de dados
            self.mostrar_mensagem("Informação", "Consulta de CPF requer integração com banco de dados interno.", QMessageBox.Information)
            return
        else:
            # Verificar se o CNPJ tem 14 dígitos
            if len(doc_limpo) != 14:
                self.mostrar_mensagem("CNPJ inválido", "O CNPJ deve ter 14 dígitos.", QMessageBox.Warning)
                return
            
            try:
                # Fazer a requisição à API BrasilAPI
                url = f"https://brasilapi.com.br/api/cnpj/v1/{doc_limpo}"
                response = requests.get(url)
                
                # Verificar se a requisição foi bem-sucedida
                if response.status_code == 200:
                    data = response.json()
                    
                    # Preencher os campos do formulário
                    self.nome_empresa_input.setText(data.get("razao_social", ""))
                    self.nome_pessoa_input.setText(data.get("nome_fantasia", ""))
                    
                    # Atualizar tipo de regime (aproximado, requer validação)
                    regime_atual = ""
                    if "opcao_pelo_simples" in data and data["opcao_pelo_simples"]:
                        regime_atual = "Simples Nacional"
                    elif "opcao_pelo_mei" in data and data["opcao_pelo_mei"]:
                        regime_atual = "MEI"
                    elif "natureza_juridica" in data:
                        natureza = data["natureza_juridica"].lower()
                        if "limitada" in natureza:
                            regime_atual = "Lucro Presumido"  # Aproximação
                        elif "anônima" in natureza:
                            regime_atual = "Lucro Real"      # Aproximação
                    
                    if regime_atual:
                        index = self.regime_combo.findText(regime_atual)
                        if index >= 0:
                            self.regime_combo.setCurrentIndex(index)
                    
                    # Configurar telefone (se disponível)
                    if "ddd_telefone_1" in data and data["ddd_telefone_1"]:
                        tel = data["ddd_telefone_1"].replace(" ", "")
                        self.telefone_input.setText(tel)
                    
                    # Preencher endereço
                    if "cep" in data and data["cep"]:
                        cep_formatado = data["cep"][:5] + "-" + data["cep"][5:] if len(data["cep"]) == 8 else data["cep"]
                        self.cep_input.setText(cep_formatado)
                    
                    self.rua_input.setText(data.get("logradouro", ""))
                    self.numero_input.setText(data.get("numero", ""))
                    self.bairro_input.setText(data.get("bairro", ""))
                    self.cidade_input.setText(data.get("municipio", ""))
                    self.estado_input.setText(data.get("uf", ""))
                    
                    self.mostrar_mensagem("Sucesso", f"Dados da empresa '{data.get('razao_social')}' foram carregados.")
                    
                elif response.status_code == 404:
                    self.mostrar_mensagem("CNPJ não encontrado", "O CNPJ informado não foi encontrado na base de dados.", QMessageBox.Warning)
                else:
                    self.mostrar_mensagem("Erro na consulta", "Não foi possível consultar o CNPJ. Verifique sua conexão.", QMessageBox.Warning)
                    
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Ocorreu um erro ao consultar o CNPJ: {str(e)}", QMessageBox.Critical)
    
    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
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
    
    def salvar_empresa(self):
        """Salva os dados da empresa na tabela da tela de cadastro"""
        nome_pessoa = self.nome_pessoa_input.text()
        nome_empresa = self.nome_empresa_input.text()
        telefone = self.telefone_input.text()
        documento = self.documento_input.text()
        regime = self.regime_combo.currentText()
        codigo = self.codigo_input.text()  # Obtém o código se estiver preenchido
        
        # Validação básica
        if not nome_empresa:
            self.mostrar_mensagem("Campos obrigatórios", "Por favor, informe o nome da empresa.", QMessageBox.Warning)
            return
            
        if not documento:
            tipo_doc = "CPF" if self.documento_label.text() == "CPF:" else "CNPJ"
            self.mostrar_mensagem("Campos obrigatórios", f"Por favor, informe o {tipo_doc}.", QMessageBox.Warning)
            return
        
        # Validar documento
        if not self.validar_documento():
            return
        
        # Verificar acesso à tabela
        if not self.cadastro_tela or not hasattr(self.cadastro_tela, 'table'):
            self.mostrar_mensagem("Erro", "Não foi possível acessar a tabela de empresas.", QMessageBox.Critical)
            return
        
        # Verificar se é um cadastro novo ou uma atualização
        if self.btn_incluir.text() == "Atualizar" and codigo:
            # Modo de atualização - procurar o item na tabela pelo código
            encontrado = False
            for row in range(self.cadastro_tela.table.rowCount()):
                if self.cadastro_tela.table.item(row, 0).text() == codigo:
                    # Se o documento (CNPJ/CPF) foi alterado, verificar se não existe duplicado
                    doc_atual = self.cadastro_tela.table.item(row, 2).text()
                    if doc_atual != documento:
                        # Verificar se o novo documento já existe em outro registro
                        for check_row in range(self.cadastro_tela.table.rowCount()):
                            if check_row != row and self.cadastro_tela.table.item(check_row, 2).text() == documento:
                                tipo_doc = "CPF" if self.documento_label.text() == "CPF:" else "CNPJ"
                                self.mostrar_mensagem(f"{tipo_doc} duplicado", 
                                                 f"Já existe outra empresa cadastrada com este {tipo_doc}.", 
                                                 QMessageBox.Warning)
                                return
                    
                    # Atualizar os dados na tabela
                    self.cadastro_tela.table.setItem(row, 1, QTableWidgetItem(nome_empresa))
                    self.cadastro_tela.table.setItem(row, 2, QTableWidgetItem(documento))
                    
                    # Mensagem de sucesso
                    tipo_doc = "CPF" if self.documento_label.text() == "CPF:" else "CNPJ"
                    self.mostrar_mensagem("Sucesso", 
                                      f"Empresa atualizada com sucesso!\nNome: {nome_empresa}\n{tipo_doc}: {documento}")
                    
                    encontrado = True
                    break
            
            if not encontrado:
                self.mostrar_mensagem("Erro", "Empresa não encontrada para atualização.", QMessageBox.Warning)
                return
        else:
            # Modo de inclusão - verificar documento duplicado
            for row in range(self.cadastro_tela.table.rowCount()):
                if self.cadastro_tela.table.item(row, 2).text() == documento:
                    tipo_doc = "CPF" if self.documento_label.text() == "CPF:" else "CNPJ"
                    self.mostrar_mensagem(f"{tipo_doc} duplicado", 
                                       f"Já existe uma empresa cadastrada com este {tipo_doc}.", 
                                       QMessageBox.Warning)
                    return
            
            # Gerar código
            ultimo_codigo = 0
            if self.cadastro_tela.table.rowCount() > 0:
                for row in range(self.cadastro_tela.table.rowCount()):
                    row_codigo = int(self.cadastro_tela.table.item(row, 0).text())
                    if row_codigo > ultimo_codigo:
                        ultimo_codigo = row_codigo
            
            novo_codigo = ultimo_codigo + 1
            
            # Adicionar à tabela
            row_position = self.cadastro_tela.table.rowCount()
            self.cadastro_tela.table.insertRow(row_position)
            self.cadastro_tela.table.setItem(row_position, 0, QTableWidgetItem(str(novo_codigo)))
            self.cadastro_tela.table.setItem(row_position, 1, QTableWidgetItem(nome_empresa))
            self.cadastro_tela.table.setItem(row_position, 2, QTableWidgetItem(documento))
            
            # Mensagem de sucesso
            tipo_doc = "CPF" if self.documento_label.text() == "CPF:" else "CNPJ"
            self.mostrar_mensagem("Sucesso", 
                              f"Empresa cadastrada com sucesso!\nNome: {nome_empresa}\n{tipo_doc}: {documento}")
        
        # Fechar a janela em ambos os casos
        if self.janela_parent:
            self.janela_parent.close()


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
    window.setWindowTitle("Formulário de Cadastro de Empresa")
    window.setGeometry(100, 100, 800, 600)  # Aumentado para acomodar campos de endereço
    window.setStyleSheet("background-color: #043b57;")
    
    form_widget = FormularioEmpresa()
    window.setCentralWidget(form_widget)
    
    window.show()
    sys.exit(app.exec_())