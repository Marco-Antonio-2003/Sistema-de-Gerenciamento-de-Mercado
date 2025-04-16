#formulario_funcionario.py
import sys
import os
# Importação condicional do requests
# Adicionar o diretório raiz ao caminho de busca
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QFormLayout, QComboBox, QMessageBox, QTableWidgetItem,
                             QDateEdit, QCalendarWidget, QStyleFactory)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QDate

class CustomMessageBox(QMessageBox):
    """Classe personalizada para QMessageBox com cores customizadas"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilo para os botões do MessageBox
        self.setStyleSheet("""
            QMessageBox {
                background-color: #043b57;
                color: white;
            }
            QLabel {
                color: white;
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

class FormularioFuncionario(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None, dados_funcionario=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela  # Referência para a tela de cadastro
        self.janela_parent = janela_parent  # Referência para a janela que contém este widget
        self.dados_funcionario = dados_funcionario  # Dados do funcionário para edição
        self.initUI()
        
        # Se tiver dados para edição, preencher o formulário
        if self.dados_funcionario:
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
        titulo = QLabel("Cadastro de Funcionário")
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
                selection-background-color: #043b57;
                selection-color: white;
            }
        """
        
        # Estilo específico para DateEdit (fundo branco e texto branco no calendário)
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
                width: 16px;
                height: 16px;
                image: url(ico-img/calendar-outline.svg);
            }
            QCalendarWidget {
                background-color: #043b57;
            }
            QCalendarWidget QWidget {
                background-color: #043b57;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #043b57;
                color: white;
                selection-background-color: #005079;
                selection-color: white;
            }
            QCalendarWidget QToolButton {
                background-color: #043b57;
                color: white;
            }
            QCalendarWidget QMenu {
                background-color: #043b57;
                color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: #043b57;
                color: white;
                selection-background-color: #005079;
                selection-color: white;
            }
            QCalendarWidget QTableView {
                alternate-background-color: #032a40;
            }
            QCalendarWidget QTableView::item:hover {
                background-color: #005079;
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
        self.tipo_combo.addItems(["Física", "Jurídica"])  # Inverter a ordem dos itens
        self.tipo_combo.setCurrentIndex(0)  # Agora aponta para "Física"
        # CORRIGIDO: Conectar explicitamente o sinal de mudança do combobox
        self.tipo_combo.currentIndexChanged.connect(self.atualizar_tipo_documento)
        
        tipo_layout = QFormLayout()
        tipo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tipo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tipo_layout.addRow(self.tipo_label, self.tipo_combo)
        
        # Campo Tipo de Vendedor
        self.tipo_vendedor_label = QLabel("Tipo de Vendedor:")
        self.tipo_vendedor_label.setStyleSheet(label_style)
        self.tipo_vendedor_combo = QComboBox()
        self.tipo_vendedor_combo.setStyleSheet(combo_style)
        self.tipo_vendedor_combo.setFixedWidth(200)
        self.tipo_vendedor_combo.addItems(["Interno", "Externo", "Representante"])
        
        tipo_vendedor_layout = QFormLayout()
        tipo_vendedor_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tipo_vendedor_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tipo_vendedor_layout.addRow(self.tipo_vendedor_label, self.tipo_vendedor_combo)
        
        tipo_data_layout.addLayout(tipo_layout)
        tipo_data_layout.addLayout(tipo_vendedor_layout)
        
        # Campo Data de Cadastro
        self.data_label = QLabel("Data de Cadastro:")
        self.data_label.setStyleSheet(label_style)
        self.data_input = QDateEdit()
        self.data_input.setStyleSheet(date_style)  # Estilo específico para DateEdit
        self.data_input.setFixedWidth(150)  # Largura fixa reduzida
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        
        # Configurar o calendário
        try:
            calendar = self.data_input.calendarWidget()
            calendar.setStyleSheet(date_style)
            calendar.setGridVisible(True)
        except:
            pass
        
        data_layout = QFormLayout()
        data_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        data_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        data_layout.addRow(self.data_label, self.data_input)
        
        # Campo CPF (conforme a imagem, não mais CNPJ/CPF)
        self.cpf_label = QLabel("CPF:")
        self.cpf_label.setStyleSheet(label_style)
        self.cpf_input = QLineEdit()
        self.cpf_input.setStyleSheet(input_style)
        self.cpf_input.setFixedWidth(250)  # Largura fixa reduzida
        self.cpf_input.textChanged.connect(self.formatar_cpf)
        self.cpf_input.setPlaceholderText("000.000.000-00")
        
        cpf_layout = QFormLayout()
        cpf_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cpf_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cpf_layout.addRow(self.cpf_label, self.cpf_input)
        
        # Campo Sexo (novo campo visto na imagem)
        self.sexo_label = QLabel("Sexo:")
        self.sexo_label.setStyleSheet(label_style)
        self.sexo_combo = QComboBox()
        self.sexo_combo.setStyleSheet(combo_style)
        self.sexo_combo.setFixedWidth(150)
        self.sexo_combo.addItems(["Masculino", "Feminino", "Outro"])
        
        sexo_layout = QFormLayout()
        sexo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sexo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        sexo_layout.addRow(self.sexo_label, self.sexo_combo)
        
        # Adicionar sexo ao layout do CPF para ficar lado a lado
        sexo_cpf_layout = QHBoxLayout()
        sexo_cpf_layout.addLayout(cpf_layout)
        sexo_cpf_layout.addLayout(sexo_layout)
        
        # Título do Endereço
        endereco_titulo = QLabel("Endereço")
        endereco_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        endereco_titulo.setStyleSheet("color: white; margin-top: 20px;")
        endereco_titulo.setAlignment(Qt.AlignCenter)
        
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
        
        # Campo CEP
        self.cep_label = QLabel("CEP:")
        self.cep_label.setStyleSheet(label_style)
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet(input_style)
        self.cep_input.setFixedWidth(150)
        self.cep_input.textChanged.connect(self.formatar_cep)
        self.cep_input.setPlaceholderText("00000-000")
        
        cep_layout = QFormLayout()
        cep_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cep_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cep_layout.addRow(self.cep_label, self.cep_input)
        
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
        
        # Layout para CEP e botão de busca
        cep_busca_layout = QHBoxLayout()
        cep_busca_layout.addLayout(cep_layout)
        cep_busca_layout.addWidget(self.btn_buscar_cep)
        cep_busca_layout.addStretch()
        
        # Campo Cidade
        self.cidade_label = QLabel("Cidade:")
        self.cidade_label.setStyleSheet(label_style)
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(input_style)
        
        cidade_layout = QFormLayout()
        cidade_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cidade_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cidade_layout.addRow(self.cidade_label, self.cidade_input)
        
        # Botão Salvar (renomeado de "Incluir" para "Salvar" quando em modo de edição)
        botao_salvar_texto = "Atualizar" if self.dados_funcionario else "Incluir"
        
        incluir_layout = QHBoxLayout()
        incluir_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_incluir = QPushButton(botao_salvar_texto)
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
        self.btn_incluir.clicked.connect(self.salvar_funcionario)
        
        incluir_layout.addWidget(self.btn_incluir)
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(codigo_telefone_layout)
        main_layout.addLayout(nome_layout)
        main_layout.addLayout(tipo_data_layout)
        main_layout.addLayout(data_layout)
        main_layout.addLayout(sexo_cpf_layout)
        main_layout.addWidget(endereco_titulo)
        main_layout.addLayout(rua_layout)
        main_layout.addLayout(bairro_layout)
        main_layout.addLayout(cep_busca_layout)
        main_layout.addLayout(cidade_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(incluir_layout)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
        # CORRIGIDO: Chamar explicitamente o método para configurar o tipo de documento inicial
        self.atualizar_tipo_documento()
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            self.mostrar_mensagem("Atenção", 
                "O módulo 'requests' não está disponível. As funcionalidades de consulta de CEP não funcionarão.",
                QMessageBox.Warning)
            # Desabilitar botões de consulta
            self.btn_buscar_cep.setEnabled(False)
    
    def preencher_formulario(self):
        """Preenche o formulário com os dados do funcionário para edição"""
        if not self.dados_funcionario:
            return
            
        # Preencher dados do funcionário
        self.codigo_input.setText(self.dados_funcionario.get('codigo', ''))
        self.nome_input.setText(self.dados_funcionario.get('nome', ''))
        self.telefone_input.setText(self.dados_funcionario.get('telefone', ''))
        
        # Tipo de vendedor
        tipo_vendedor = self.dados_funcionario.get('tipo_vendedor', 'Interno')
        index = 0  # Padrão: Interno
        if tipo_vendedor == "Externo":
            index = 1
        elif tipo_vendedor == "Representante":
            index = 2
        self.tipo_vendedor_combo.setCurrentIndex(index)
        
        # Cidade (se disponível)
        self.cidade_input.setText(self.dados_funcionario.get('cidade', ''))
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem personalizada com estilos ajustados"""
        msg_box = CustomMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
    def atualizar_tipo_documento(self):
        """Atualiza o label e placeholder do campo de documento conforme o tipo de pessoa"""
        tipo_pessoa = self.tipo_combo.currentText()
        # DEBUG - remover após verificar funcionamento
        print("Tipo de Pessoa selecionado:", tipo_pessoa)
        
        if tipo_pessoa == "Jurídica":
            self.cpf_label.setText("CNPJ:")
            self.cpf_input.setPlaceholderText("00.000.000/0001-00")
            texto = self.cpf_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) <= 11 and len(''.join(filter(str.isdigit, texto))) > 0:
                self.cpf_input.clear()
        else:
            self.cpf_label.setText("CPF:")
            self.cpf_input.setPlaceholderText("000.000.000-00")
    
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
    
    def formatar_cpf(self, texto):
        """Formata o CPF durante a digitação"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Verificar se é CPF ou CNPJ
        if self.cpf_label.text() == "CPF:":
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
            self.cpf_input.blockSignals(True)
            self.cpf_input.setText(texto_formatado)
            
            # Posição do cursor baseada no comprimento do texto formatado
            self.cpf_input.setCursorPosition(len(texto_formatado))
            self.cpf_input.blockSignals(False)
    
    def formatar_cep(self, texto):
        """Formata o CEP durante a digitação e busca endereço quando completo"""
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
            # Bloqueia sinais para evitar recursão
            self.cep_input.blockSignals(True)
            self.cep_input.setText(texto_formatado)
            
            # Posição do cursor baseada no comprimento do texto formatado
            self.cep_input.setCursorPosition(len(texto_formatado))
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
                    self.mostrar_mensagem("CEP não encontrado", 
                                       "O CEP informado não foi encontrado.", 
                                       QMessageBox.Warning)
                    return
                    
                # Preencher os campos de endereço
                self.rua_input.setText(data.get("logradouro", ""))
                self.bairro_input.setText(data.get("bairro", ""))
                self.cidade_input.setText(data.get("localidade", ""))
                
                # Focar no próximo campo vazio
                if not self.rua_input.text():
                    self.rua_input.setFocus()
                elif not self.bairro_input.text():
                    self.bairro_input.setFocus()
                elif not self.cidade_input.text():
                    self.cidade_input.setFocus()
                
                # Mensagem de sucesso
                self.mostrar_mensagem("Sucesso", "Endereço encontrado e preenchido com sucesso!")
                
            else:
                self.mostrar_mensagem("Erro na consulta", 
                                   "Não foi possível consultar o CEP. Verifique sua conexão.", 
                                   QMessageBox.Warning)
                
        except Exception as e:
            self.mostrar_mensagem("Erro", 
                               f"Ocorreu um erro ao buscar o endereço: {str(e)}", 
                               QMessageBox.Critical)
    
    def validar_cpf(self, cpf):
        """Valida o CPF informado"""
        # Remover caracteres não numéricos
        cpf_nums = ''.join(filter(str.isdigit, cpf))
        
        # Verificar se tem 11 dígitos
        if len(cpf_nums) != 11:
            self.mostrar_mensagem("CPF inválido", "O CPF deve ter 11 dígitos.", QMessageBox.Warning)
            return False
        
        # Verificar se todos os dígitos são iguais
        if len(set(cpf_nums)) == 1:
            self.mostrar_mensagem("CPF inválido", 
                               "CPF com dígitos repetidos é inválido.", 
                               QMessageBox.Warning)
            return False
            
        # Calcular o primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf_nums[i]) * (10 - i)
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        # Verificar o primeiro dígito verificador
        if dv1 != int(cpf_nums[9]):
            self.mostrar_mensagem("CPF inválido", 
                               "O CPF informado não é válido.", 
                               QMessageBox.Warning)
            return False
        
        # Calcular o segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf_nums[i]) * (11 - i)
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        # Verificar o segundo dígito verificador
        if dv2 != int(cpf_nums[10]):
            self.mostrar_mensagem("CPF inválido", 
                               "O CPF informado não é válido.", 
                               QMessageBox.Warning)
            return False
            
        return True
    
    # Método para salvar o funcionário no banco de dados
    def salvar_funcionario(self):
        """Salva os dados do funcionário no banco de dados"""
        # Obter dados do formulário
        nome = self.nome_input.text()
        tipo_vendedor = self.tipo_vendedor_combo.currentText()
        telefone = self.telefone_input.text()
        tipo_pessoa = self.tipo_combo.currentText()
        data_cadastro = self.data_input.date().toString("dd/MM/yyyy")
        cpf_cnpj = self.cpf_input.text()
        sexo = self.sexo_combo.currentText()
        cep = self.cep_input.text()
        rua = self.rua_input.text()
        bairro = self.bairro_input.text()
        cidade = self.cidade_input.text()
        estado = "" if not hasattr(self, 'estado_input') else self.estado_input.text()
        codigo = self.codigo_input.text()  # Obtém o código se estiver preenchido
        
        # Validação básica
        if not nome:
            self.mostrar_mensagem("Campos obrigatórios", 
                            "Por favor, informe o nome do funcionário.", 
                            QMessageBox.Warning)
            self.nome_input.setFocus()
            return
            
        if not cpf_cnpj:
            documento_tipo = "CPF" if self.cpf_label.text() == "CPF:" else "CNPJ"
            self.mostrar_mensagem("Campos obrigatórios", 
                            f"Por favor, informe o {documento_tipo}.", 
                            QMessageBox.Warning)
            self.cpf_input.setFocus()
            return
        
        # Validar CPF/CNPJ
        if self.cpf_label.text() == "CPF:" and not self.validar_cpf(cpf_cnpj):
            self.cpf_input.setFocus()
            return
        
        try:
            # Importar funções do banco
            from base.banco import criar_funcionario, atualizar_funcionario, buscar_funcionario_por_id
            
            # Verificar se é uma atualização ou novo cadastro
            if self.btn_incluir.text() == "Atualizar" and codigo:
                # Verificar se o funcionário existe
                funcionario = buscar_funcionario_por_id(int(codigo))
                if not funcionario:
                    self.mostrar_mensagem("Erro", 
                                    f"Funcionário com código {codigo} não encontrado", 
                                    QMessageBox.Warning)
                    return
                    
                # Atualizar no banco de dados
                atualizar_funcionario(
                    int(codigo),
                    nome,
                    tipo_vendedor,
                    telefone,
                    tipo_pessoa,
                    data_cadastro,
                    cpf_cnpj,
                    sexo,
                    cep,
                    rua,
                    bairro,
                    cidade,
                    estado
                )
                
                self.mostrar_mensagem("Sucesso", 
                                f"Funcionário atualizado com sucesso!\nNome: {nome}")
                                
                # Atualizar a tabela principal
                if self.cadastro_tela:
                    self.cadastro_tela.carregar_funcionarios()
                    
                # Fechar a janela
                if self.janela_parent:
                    self.janela_parent.close()
            else:
                # Criar novo funcionário no banco de dados
                novo_id = criar_funcionario(
                    nome,
                    tipo_vendedor,
                    telefone,
                    tipo_pessoa,
                    data_cadastro,
                    cpf_cnpj,
                    sexo,
                    cep,
                    rua,
                    bairro,
                    cidade,
                    estado
                )
                
                self.mostrar_mensagem("Sucesso", 
                                f"Funcionário cadastrado com sucesso!\nNome: {nome}\nCódigo: {novo_id}")
                
                # Atualizar a tabela principal
                if self.cadastro_tela:
                    self.cadastro_tela.carregar_funcionarios()
                    
                # Fechar a janela
                if self.janela_parent:
                    self.janela_parent.close()
        
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao salvar funcionário: {str(e)}", QMessageBox.Critical)

    def preencher_formulario_do_banco(self, id_funcionario):
        """Preenche o formulário com dados do funcionário do banco de dados"""
        try:
            from base.banco import buscar_funcionario_por_id
            
            # Buscar dados do funcionário
            funcionario = buscar_funcionario_por_id(id_funcionario)
            if not funcionario:
                self.mostrar_mensagem("Erro", f"Funcionário com ID {id_funcionario} não encontrado", QMessageBox.Warning)
                return False
            
            # Preencher os campos do formulário
            # ID, NOME, TIPO_VENDEDOR, TELEFONE, TIPO_PESSOA, DATA_CADASTRO, CPF_CNPJ, SEXO, CEP, RUA, BAIRRO, CIDADE, ESTADO, OBSERVACAO
            self.codigo_input.setText(str(funcionario[0]))  # ID
            self.nome_input.setText(funcionario[1])         # NOME
            
            # Configurar o tipo de vendedor
            tipo_vendedor = funcionario[2]  # TIPO_VENDEDOR
            index = 0  # Padrão: Interno
            if tipo_vendedor == "Externo":
                index = 1
            elif tipo_vendedor == "Representante":
                index = 2
            self.tipo_vendedor_combo.setCurrentIndex(index)
            
            # Preencher telefone
            telefone = funcionario[3] or ""        # TELEFONE
            if telefone and len(telefone) > 10:    # Formatar telefone
                self.telefone_input.setText(f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}")
            elif telefone and len(telefone) > 2:
                self.telefone_input.setText(f"({telefone[:2]}) {telefone[2:]}")
            else:
                self.telefone_input.setText(telefone)
            
            # Configurar o tipo de pessoa
            if funcionario[4]:                     # TIPO_PESSOA
                tipo_pessoa = funcionario[4]
                index = 0 if tipo_pessoa == "Jurídica" else 1
                self.tipo_combo.setCurrentIndex(index)
            
            # Preencher data de cadastro
            if funcionario[5]:                     # DATA_CADASTRO
                try:
                    from PyQt5.QtCore import QDate
                    data = QDate.fromString(funcionario[5].strftime("%d/%m/%Y"), "dd/MM/yyyy")
                    self.data_input.setDate(data)
                except Exception as e:
                    print(f"Erro ao converter data: {e}")
                    self.data_input.setDate(QDate.currentDate())
            
            # Formatar CPF/CNPJ
            cpf_cnpj = funcionario[6]              # CPF_CNPJ
            if cpf_cnpj:
                if len(cpf_cnpj) <= 11:            # CPF
                    # Configurar o tipo de pessoa para Física
                    self.tipo_combo.setCurrentIndex(1)  # Índice 1: Física
                    # Formatar CPF
                    if len(cpf_cnpj) == 11:
                        cpf_formatado = f"{cpf_cnpj[:3]}.{cpf_cnpj[3:6]}.{cpf_cnpj[6:9]}-{cpf_cnpj[9:]}"
                        self.cpf_input.setText(cpf_formatado)
                    else:
                        self.cpf_input.setText(cpf_cnpj)
                else:                             # CNPJ
                    # Configurar o tipo de pessoa para Jurídica
                    self.tipo_combo.setCurrentIndex(0)  # Índice 0: Jurídica
                    # Formatar CNPJ
                    if len(cpf_cnpj) == 14:
                        cnpj_formatado = f"{cpf_cnpj[:2]}.{cpf_cnpj[2:5]}.{cpf_cnpj[5:8]}/{cpf_cnpj[8:12]}-{cpf_cnpj[12:]}"
                        self.cpf_input.setText(cnpj_formatado)
                    else:
                        self.cpf_input.setText(cpf_cnpj)
            
            # Preencher sexo
            if funcionario[7]:                    # SEXO
                sexo = funcionario[7]
                index = 0  # Padrão: Masculino
                if sexo == "Feminino":
                    index = 1
                elif sexo == "Outro":
                    index = 2
                self.sexo_combo.setCurrentIndex(index)
            
            # Preencher CEP
            cep = funcionario[8] or ""            # CEP
            if cep and len(cep) >= 8:
                self.cep_input.setText(f"{cep[:5]}-{cep[5:]}")
            else:
                self.cep_input.setText(cep)
            
            # Preencher campos de endereço
            self.rua_input.setText(funcionario[9] or "")     # RUA
            self.bairro_input.setText(funcionario[10] or "") # BAIRRO
            self.cidade_input.setText(funcionario[11] or "") # CIDADE

            # Verificar se o campo estado_input existe antes de tentar acessá-lo
            if hasattr(self, 'estado_input'):
                self.estado_input.setText(funcionario[12] or "") # ESTADO
            
            # Alterar texto do botão para Atualizar
            self.btn_incluir.setText("Atualizar")
            
            return True
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao carregar dados do funcionário: {e}", QMessageBox.Critical)
            return False


# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Formulário de Cadastro de Funcionário")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    # Configuração global para MessageBox
    app.setStyle(QStyleFactory.create("Fusion"))
    
    form_widget = FormularioFuncionario()
    window.setCentralWidget(form_widget)
    
    window.show()
    sys.exit(app.exec_())