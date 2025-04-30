import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QDateEdit, QDialog,
                             QRadioButton, QButtonGroup, QDoubleSpinBox, QTimeEdit,
                             QCalendarWidget) # Adicionar QCalendarWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette # Adicionar QColor, QPalette
from PyQt5.QtCore import Qt, QDate, QTime
import os
import importlib.util
import datetime

# Importar funções do banco de dados
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "base"))
try:
    import base.banco
except ImportError:
    print("Erro ao importar o módulo banco.py")
    sys.exit(1)

class DialogoEscolhaOperacao(QDialog):
    """Diálogo para escolher entre entrada e saída"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tipo_operacao = "Entrada"  # Valor padrão
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Selecionar Operação")
        self.setStyleSheet("background-color: #003353; color: white;")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Selecione o tipo de operação:")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        layout.addWidget(titulo)
        
        # Opções
        self.radio_entrada = QRadioButton("Entrada")
        self.radio_entrada.setFont(QFont("Arial", 12))
        self.radio_entrada.setStyleSheet("color: white;")
        self.radio_entrada.setChecked(True)
        
        self.radio_saida = QRadioButton("Saída")
        self.radio_saida.setFont(QFont("Arial", 12))
        self.radio_saida.setStyleSheet("color: white;")
        
        # Grupo de botões
        self.grupo_opcoes = QButtonGroup(self)
        self.grupo_opcoes.addButton(self.radio_entrada)
        self.grupo_opcoes.addButton(self.radio_saida)
        
        layout.addWidget(self.radio_entrada)
        layout.addWidget(self.radio_saida)
        
        # Botões
        botoes_layout = QHBoxLayout()
        
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_confirmar.clicked.connect(self.confirmar)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 8px 15px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #cccccc;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        botoes_layout.addWidget(self.btn_cancelar)
        botoes_layout.addWidget(self.btn_confirmar)
        
        layout.addLayout(botoes_layout)
    
    def confirmar(self):
        if self.radio_entrada.isChecked():
            self.tipo_operacao = "Entrada"
        else:
            self.tipo_operacao = "Saída"
        self.accept()

class AbrirCaixa(QDialog):
    def __init__(self, codigo=None, tipo_operacao=None, parent=None):
        super().__init__(parent)
        self.codigo = codigo
        self.tipo_operacao = tipo_operacao
        self.initUI()
        
    def initUI(self):
        # Configuração da janela
        self.setWindowTitle(f"Operação de {self.tipo_operacao} - Caixa {self.codigo}")
        self.setMinimumWidth(500)
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        titulo = QLabel(f"Operação de {self.tipo_operacao}")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Informações do caixa
        info_layout = QHBoxLayout()
        
        codigo_label = QLabel(f"Código do Caixa: {self.codigo}")
        codigo_label.setFont(QFont("Arial", 12))
        codigo_label.setStyleSheet("color: white;")
        info_layout.addWidget(codigo_label)
        
        # Mostrar o usuário logado
        usuario = base.banco.get_usuario_logado()
        if usuario and usuario["nome"]:
            usuario_label = QLabel(f"Usuário: {usuario['nome']}")
            usuario_label.setFont(QFont("Arial", 12))
            usuario_label.setStyleSheet("color: white;")
            info_layout.addWidget(usuario_label)
        
        info_layout.addStretch(1)
        
        main_layout.addLayout(info_layout)
        
        # Linha separadora
        separator = QLabel()
        separator.setStyleSheet("background-color: #004465; min-height: 2px; margin: 10px 0px;")
        main_layout.addWidget(separator)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Estilo para labels
        label_style = "color: white; font-size: 14px;"
        
        # Estilo para inputs
        input_style = """
            background-color: #fffff0;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 8px;
            font-size: 14px;
            min-height: 25px;
            color: black;
        """
        combo_style = input_style + """
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(ico-img/dropdown.png); /* Ícone padrão se houver */
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
        """
        
        # Data e Hora
        data_label = QLabel("Data:")
        data_label.setStyleSheet(label_style)
        self.data_edit = QDateEdit(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)
        self.data_edit.setStyleSheet(input_style)
        form_layout.addRow(data_label, self.data_edit)
        
        hora_label = QLabel("Hora:")
        hora_label.setStyleSheet(label_style)
        self.hora_edit = QTimeEdit(QTime.currentTime())
        self.hora_edit.setStyleSheet(input_style)
        form_layout.addRow(hora_label, self.hora_edit)
        
        # Estação/Terminal
        estacao_label = QLabel("Estação:")
        estacao_label.setStyleSheet(label_style)
        self.estacao_combo = QComboBox()
        self.estacao_combo.addItems([f"Caixa {i:02d}" for i in range(1, 11)])
        self.estacao_combo.setStyleSheet(combo_style)
        form_layout.addRow(estacao_label, self.estacao_combo)
        
        # Campos específicos para Entrada ou Saída
        if self.tipo_operacao == "Entrada":
            # Campos específicos para entrada
            valor_label = QLabel("Valor de Entrada:")
            valor_label.setStyleSheet(label_style)
            self.valor_spin = QDoubleSpinBox()
            self.valor_spin.setRange(0.00, 9999999.99)
            self.valor_spin.setDecimals(2)
            self.valor_spin.setSingleStep(10.00)
            self.valor_spin.setPrefix("R$ ")
            self.valor_spin.setValue(0.00)
            self.valor_spin.setStyleSheet(input_style)
            form_layout.addRow(valor_label, self.valor_spin)
            
            motivo_label = QLabel("Motivo da Entrada:")
            motivo_label.setStyleSheet(label_style)
            self.motivo_combo = QComboBox()
            self.motivo_combo.addItems(["Abertura de Caixa", "Reforço", "Correção", "Outros"])
            self.motivo_combo.setStyleSheet(combo_style)
            form_layout.addRow(motivo_label, self.motivo_combo)
            
        else:  # Saída
            # Campos específicos para saída
            valor_label = QLabel("Valor de Saída:")
            valor_label.setStyleSheet(label_style)
            self.valor_spin = QDoubleSpinBox()
            self.valor_spin.setRange(0.00, 9999999.99)
            self.valor_spin.setDecimals(2)
            self.valor_spin.setSingleStep(10.00)
            self.valor_spin.setPrefix("R$ ")
            self.valor_spin.setValue(0.00)
            self.valor_spin.setStyleSheet(input_style)
            form_layout.addRow(valor_label, self.valor_spin)
            
            motivo_label = QLabel("Motivo da Saída:")
            motivo_label.setStyleSheet(label_style)
            self.motivo_combo = QComboBox()
            self.motivo_combo.addItems(["Sangria", "Fechamento", "Devolução", "Cancelamento", "Outros"])
            self.motivo_combo.setStyleSheet(combo_style)
            form_layout.addRow(motivo_label, self.motivo_combo)
        
        # Campo de observação (comum para ambos)
        obs_label = QLabel("Observação:")
        obs_label.setStyleSheet(label_style)
        self.obs_edit = QLineEdit()
        self.obs_edit.setStyleSheet(input_style)
        self.obs_edit.setPlaceholderText("Digite uma observação (opcional)")
        form_layout.addRow(obs_label, self.obs_edit)
        
        # Adicionar o formulário ao layout principal
        main_layout.addLayout(form_layout)
        
        # Botões
        btns_layout = QHBoxLayout()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 8px 15px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #cccccc;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_confirmar.clicked.connect(self.confirmar_operacao)
        
        btns_layout.addStretch(1)
        btns_layout.addWidget(self.btn_cancelar)
        btns_layout.addWidget(self.btn_confirmar)
        
        main_layout.addLayout(btns_layout)
    
    def confirmar_operacao(self):
        """Confirma a operação e salva os dados"""
        try:
            # Verificar se o usuário está logado
            usuario = base.banco.get_usuario_logado()
            if not usuario["id"]:
                QMessageBox.warning(self, "Atenção", "Você precisa estar logado para abrir um caixa.")
                return
                
            # Validação básica
            if self.valor_spin.value() < 0:
                QMessageBox.warning(self, "Atenção", "O valor não pode ser negativo!")
                return
            
            # Obter os dados do formulário
            data = self.data_edit.date().toString("dd/MM/yyyy")
            hora = self.hora_edit.time().toString("hh:mm")
            valor = self.valor_spin.value()
            motivo = self.motivo_combo.currentText()
            observacao = self.obs_edit.text()
            estacao = self.estacao_combo.currentText()
            
            # Abrir o caixa no banco de dados
            if self.tipo_operacao == "Entrada":
                # Abrir o caixa
                id_caixa = base.banco.abrir_caixa(
                    codigo=self.codigo,
                    data_abertura=data,
                    hora_abertura=hora,
                    valor_abertura=valor,
                    estacao=estacao,
                    observacao=observacao
                )
                
                # Exibir mensagem de sucesso
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Caixa {self.codigo} aberto com sucesso!\n"
                    f"Data: {data} {hora}\n"
                    f"Valor inicial: R$ {valor:.2f}"
                )
            else:
                # Registrar movimento de saída (implementação futura)
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Operação de {self.tipo_operacao} registrada com sucesso!\n"
                    f"Data: {data} {hora}\n"
                    f"Valor: R$ {valor:.2f}\n"
                    f"Motivo: {motivo}"
                )
            
            # Fechar o diálogo retornando Accepted
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar operação: {str(e)}")

class FecharCaixa(QDialog):
    def __init__(self, id_caixa, codigo, parent=None):
        super().__init__(parent)
        self.id_caixa = id_caixa
        self.codigo = codigo
        self.dados_caixa = None
        self.carregar_dados_caixa()
        self.initUI()
        
    def carregar_dados_caixa(self):
        """Carrega os dados do caixa a ser fechado"""
        try:
            self.dados_caixa = base.banco.obter_caixa_por_id(self.id_caixa)
            if not self.dados_caixa:
                raise Exception(f"Caixa com ID {self.id_caixa} não encontrado.")
                
            # Verificar se o caixa já está fechado
            if self.dados_caixa[4]:  # data_fechamento
                raise Exception(f"Caixa {self.codigo} já está fechado.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados do caixa: {str(e)}")
            self.reject()
        
    def initUI(self):
        # Configuração da janela
        self.setWindowTitle(f"Fechamento de Caixa - Caixa {self.codigo}")
        self.setMinimumWidth(500)
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Fechamento de Caixa")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Informações do caixa
        info_layout = QHBoxLayout()
        
        codigo_label = QLabel(f"Código do Caixa: {self.codigo}")
        codigo_label.setFont(QFont("Arial", 12))
        codigo_label.setStyleSheet("color: white;")
        info_layout.addWidget(codigo_label)
        
        # Mostrar o usuário logado
        usuario = base.banco.get_usuario_logado()
        if usuario and usuario["nome"]:
            usuario_label = QLabel(f"Usuário: {usuario['nome']}")
            usuario_label.setFont(QFont("Arial", 12))
            usuario_label.setStyleSheet("color: white;")
            info_layout.addWidget(usuario_label)
        
        info_layout.addStretch(1)
        
        main_layout.addLayout(info_layout)
        
        # Linha separadora
        separator = QLabel()
        separator.setStyleSheet("background-color: #004465; min-height: 2px; margin: 10px 0px;")
        main_layout.addWidget(separator)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Estilo para labels
        label_style = "color: white; font-size: 14px;"
        
        # Estilo para inputs
        input_style = """
            background-color: #fffff0;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 8px;
            font-size: 14px;
            min-height: 25px;
            color: black;
        """
        
        # Informações da abertura (somente leitura)
        if self.dados_caixa:
            abertura_label = QLabel("Abertura:")
            abertura_label.setStyleSheet(label_style)
            abertura_valor = QLabel(f"{self.dados_caixa[2]} {self.dados_caixa[3]}")
            abertura_valor.setStyleSheet("color: #fffff0; font-size: 14px;")
            form_layout.addRow(abertura_label, abertura_valor)
            
            valor_abertura_label = QLabel("Valor de Abertura:")
            valor_abertura_label.setStyleSheet(label_style)
            valor_abertura_valor = QLabel(f"R$ {self.dados_caixa[6]:.2f}")
            valor_abertura_valor.setStyleSheet("color: #fffff0; font-size: 14px;")
            form_layout.addRow(valor_abertura_label, valor_abertura_valor)
        
        # Data e Hora de Fechamento
        data_label = QLabel("Data de Fechamento:")
        data_label.setStyleSheet(label_style)
        self.data_edit = QDateEdit(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)
        self.data_edit.setStyleSheet(input_style)
        form_layout.addRow(data_label, self.data_edit)
        
        hora_label = QLabel("Hora de Fechamento:")
        hora_label.setStyleSheet(label_style)
        self.hora_edit = QTimeEdit(QTime.currentTime())
        self.hora_edit.setStyleSheet(input_style)
        form_layout.addRow(hora_label, self.hora_edit)
        
        # Valor de Fechamento
        valor_label = QLabel("Valor de Fechamento:")
        valor_label.setStyleSheet(label_style)
        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setRange(0.00, 9999999.99)
        self.valor_spin.setDecimals(2)
        self.valor_spin.setSingleStep(10.00)
        self.valor_spin.setPrefix("R$ ")
        
        # Definir o valor inicial como o valor de abertura (se disponível)
        if self.dados_caixa and self.dados_caixa[6]:
            self.valor_spin.setValue(float(self.dados_caixa[6]))
        else:
            self.valor_spin.setValue(0.00)
            
        self.valor_spin.setStyleSheet(input_style)
        form_layout.addRow(valor_label, self.valor_spin)
        
        # Campo de observação
        obs_label = QLabel("Observação:")
        obs_label.setStyleSheet(label_style)
        self.obs_edit = QLineEdit()
        self.obs_edit.setStyleSheet(input_style)
        self.obs_edit.setPlaceholderText("Digite uma observação (opcional)")
        form_layout.addRow(obs_label, self.obs_edit)
        
        # Adicionar o formulário ao layout principal
        main_layout.addLayout(form_layout)
        
        # Botões
        btns_layout = QHBoxLayout()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 8px 15px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #cccccc;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_confirmar.clicked.connect(self.confirmar_fechamento)
        
        btns_layout.addStretch(1)
        btns_layout.addWidget(self.btn_cancelar)
        btns_layout.addWidget(self.btn_confirmar)
        
        main_layout.addLayout(btns_layout)
    
    def confirmar_fechamento(self):
        """Confirma o fechamento do caixa e salva os dados"""
        try:
            # Validação básica
            if self.valor_spin.value() < 0:
                QMessageBox.warning(self, "Atenção", "O valor não pode ser negativo!")
                return
            
            # Obter os dados do formulário
            data = self.data_edit.date().toString("dd/MM/yyyy")
            hora = self.hora_edit.time().toString("hh:mm")
            valor = self.valor_spin.value()
            observacao = self.obs_edit.text()
            
            # Fechar o caixa no banco de dados
            base.banco.fechar_caixa(
                id_caixa=self.id_caixa,
                data_fechamento=data,
                hora_fechamento=hora,
                valor_fechamento=valor,
                observacao=observacao
            )
            
            # Exibir mensagem de sucesso
            QMessageBox.information(
                self,
                "Sucesso",
                f"Caixa {self.codigo} fechado com sucesso!\n"
                f"Data: {data} {hora}\n"
                f"Valor: R$ {valor:.2f}"
            )
            
            # Fechar o diálogo retornando Accepted
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao fechar caixa: {str(e)}")

class ControleCaixaWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.carregar_dados_reais()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho com botão voltar e título
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("Controle de Caixa")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-left: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label, 1)  # 1 = stretch factor
        
        # Adicionar espaço à direita para balancear o botão voltar
        spacer = QWidget()
        spacer.setMinimumWidth(90)
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Formulário de filtros
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(15)
        
        # Layout para Ordem e Código
        ordem_layout = QHBoxLayout()
        ordem_layout.setSpacing(10)
        
        # Label Ordem
        ordem_label = QLabel("Ordem:")
        ordem_label.setFont(QFont("Arial", 14))
        ordem_label.setStyleSheet("color: white;")
        ordem_layout.addWidget(ordem_label)
        
        # ComboBox de Código com ícone dropdown
        self.codigo_combo = QComboBox()
        self.codigo_combo.addItem("Código")
        self.codigo_combo.addItem("Data de Abertura")
        self.codigo_combo.addItem("Data de Fechamento")
        self.codigo_combo.addItem("Estação")
        self.codigo_combo.addItem("Usuário (A-Z)")
        self.codigo_combo.setStyleSheet("""
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-width: 150px;
                min-height: 30px;
                color: black; /* Cor do texto */
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(ico-img/dropdown.png); /* Ícone padrão */
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView { /* Estilo da lista dropdown */
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
            }
            QComboBox:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.codigo_combo.currentIndexChanged.connect(self.filtrar_e_ordenar)
        ordem_layout.addWidget(self.codigo_combo)
        
        # Adicionar o layout da ordem ao layout de filtros
        filtros_layout.addLayout(ordem_layout)
        
        # Espaçamento entre ordem e conta
        filtros_layout.addSpacing(20)
        
        usuario_label = QLabel("Usuario:")
        usuario_label.setFont(QFont("Arial", 14))
        usuario_label.setStyleSheet("color: white;")
        filtros_layout.addWidget(usuario_label)
        
        # Campo de texto para Usuario (antigo Conta)
        self.usuario_input = QLineEdit()  # Renomeando a variável para consistência
        self.usuario_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-height: 30px;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.usuario_input.setMinimumWidth(400)
        self.usuario_input.textChanged.connect(self.filtrar_e_ordenar)  # Conectar o sinal de mudança de texto
        filtros_layout.addWidget(self.usuario_input, 1)  # 1 = stretch factor
        
        # Adicionar layout de filtros ao layout principal
        main_layout.addLayout(filtros_layout)
        
        # Layout para período
        periodo_layout = QHBoxLayout()
        periodo_layout.setSpacing(15)
        
        # Label Período de Abertura
        periodo_label = QLabel("Período de\nAbertura")
        periodo_label.setFont(QFont("Arial", 14))
        periodo_label.setStyleSheet("color: white;")
        periodo_label.setAlignment(Qt.AlignCenter)
        periodo_layout.addWidget(periodo_label)
        
        # Correção do ícone no DateEdit para período de abertura
        date_edit_style = """
            QDateEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-height: 30px;
                min-width: 200px;
                color: black;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QDateEdit::down-arrow {
                /* Usar caractere unicode para o ícone do calendário */
                image: none;
                width: 16px;
                height: 16px;
                color: black;
                font: 16px;
                text-align: center;
            }
            QDateEdit:focus {
                border: 2px solid #0078d7;
            }
            /* Estilo para o Calendário Popup */
            QDateEdit QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #e0e0e0; 
            }
            QDateEdit QCalendarWidget QToolButton { 
                color: black; 
                background-color: #f0f0f0; 
                border: none; 
                margin: 5px; 
                padding: 5px; 
            }
            QDateEdit QCalendarWidget QToolButton:hover { 
                background-color: #d0d0d0; 
            }
            QDateEdit QCalendarWidget QMenu { 
                background-color: white; 
                color: black; 
            }
            QDateEdit QCalendarWidget QSpinBox { 
                color: black; 
                background-color: white; 
                border: 1px solid #cccccc; 
            }
            QDateEdit QCalendarWidget QTableView { 
                background-color: white; 
                color: black; 
                selection-background-color: #0078d7; 
                selection-color: white; 
            }
            QDateEdit QCalendarWidget QWidget#qt_calendar_calendarview { 
                background-color: white; 
                alternate-background-color: #f9f9f9; 
            }
            QDateEdit QCalendarWidget QAbstractItemView:enabled { 
                color: black; 
            }
            QDateEdit QCalendarWidget QAbstractItemView:disabled { 
                color: #a0a0a0; 
            }
        """
        
        # DataEdit para data inicial
        self.data_inicial = QDateEdit(QDate.currentDate())
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setStyleSheet(date_edit_style)
        self.data_inicial.dateChanged.connect(self.filtrar_e_ordenar)
        periodo_layout.addWidget(self.data_inicial)
        
        # Label Até
        ate_label = QLabel("Até:")
        ate_label.setFont(QFont("Arial", 14))
        ate_label.setStyleSheet("color: white;")
        ate_label.setAlignment(Qt.AlignCenter)
        periodo_layout.addWidget(ate_label)
        
        # DataEdit para data final
        self.data_final = QDateEdit(QDate.currentDate())
        self.data_final.setCalendarPopup(True)
        self.data_final.setStyleSheet(date_edit_style)
        self.data_final.dateChanged.connect(self.filtrar_e_ordenar)
        periodo_layout.addWidget(self.data_final)
        
        # Espaço para alinhar com o campo de conta
        periodo_layout.addStretch(1)
        
        # Adicionar layout de período ao layout principal
        main_layout.addLayout(periodo_layout)
        
        # Tabela de controle de caixa
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Código", "Abertura", "Fechamento", "Estação", "Usuario"])
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #fffff0;
                padding: 6px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #cccccc;
                color: black; /* Cor do texto do cabeçalho */
            }
        """)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                alternate-background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
                color: black; /* Cor do texto da tabela */
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Ajustar largura das colunas
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        self.table.itemClicked.connect(self.selecionar_linha)
        
        main_layout.addWidget(self.table)
        
        # Layout para botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        # Botão Abrir
        self.btn_abrir = QPushButton("Abrir")
        self.btn_abrir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 10px 15px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_abrir.clicked.connect(self.abrir_caixa)
        btn_layout.addWidget(self.btn_abrir)
        
        # Botão Fechar
        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 10px 15px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_fechar.clicked.connect(self.fechar_caixa)
        self.btn_fechar.setEnabled(False)  # Inicialmente desabilitado
        btn_layout.addWidget(self.btn_fechar)

        
        btn_layout.addStretch(1)
        
        main_layout.addLayout(btn_layout)
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #003353; }")
        
        # Inicializar variáveis de controle
        self.caixa_selecionado = None
        self.dados_originais = []  # Armazenar dados originais para filtragem
        
    def carregar_dados_reais(self):
        """Carrega dados reais do banco de dados"""
        try:
            # Verificar se as tabelas existem
            base.banco.verificar_tabelas_caixa()
            
            # Carregar caixas do banco de dados
            caixas = base.banco.listar_caixas()
            
            # Armazenar dados originais para filtragem
            self.dados_originais = []
            for caixa in caixas:
                # Extrair dados do caixa
                id_caixa = caixa[0]
                codigo = caixa[1]
                data_abertura = caixa[2]
                hora_abertura = caixa[3]
                data_fechamento = caixa[4]
                hora_fechamento = caixa[5]
                estacao = caixa[8]
                usuario = caixa[9]
                
                # Formatar datas e horas
                abertura = f"{data_abertura} {hora_abertura}" if data_abertura else ""
                fechamento = f"{data_fechamento} {hora_fechamento}" if data_fechamento else ""
                
                # Armazenar dados originais para filtragem
                self.dados_originais.append({
                    'id': id_caixa,
                    'codigo': codigo,
                    'abertura': abertura,
                    'data_abertura': data_abertura,
                    'hora_abertura': hora_abertura,
                    'fechamento': fechamento,
                    'data_fechamento': data_fechamento,
                    'hora_fechamento': hora_fechamento,
                    'estacao': estacao,
                    'usuario': usuario
                })
            
            # Aplicar filtro e ordenação iniciais
            self.filtrar_e_ordenar()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {str(e)}")
    
    def filtrar_e_ordenar(self):
        """Filtra os dados pelo período de data, termo de pesquisa e ordena conforme a seleção"""
        try:
            # --- Filtragem por Data --- 
            data_inicial_str = self.data_inicial.date().toString("dd/MM/yyyy")
            data_final_str = self.data_final.date().toString("dd/MM/yyyy")
            
            # Converter para objetos date para comparação (sem hora)
            data_inicial_dt = datetime.datetime.strptime(data_inicial_str, "%d/%m/%Y").date()
            data_final_dt = datetime.datetime.strptime(data_final_str, "%d/%m/%Y").date()
            
            # --- Filtragem por Usuário ---
            termo_pesquisa = self.usuario_input.text().lower().strip()
            
            dados_filtrados = []
            for item in self.dados_originais:
                # Verificar se está dentro do período de data
                if item['data_abertura']:
                    try:
                        data_abertura_dt = datetime.datetime.strptime(item['data_abertura'], "%d/%m/%Y").date()
                        # Se não estiver no período, pular para o próximo item
                        if not (data_inicial_dt <= data_abertura_dt <= data_final_dt):
                            continue
                    except ValueError:
                        print(f"Aviso: Data de abertura inválida encontrada: {item['data_abertura']}")
                        continue
                else:
                    # Se não tiver data de abertura, pular
                    continue
                
                # Verificar se corresponde à pesquisa de usuário
                if termo_pesquisa:
                    # Verificar se o termo de pesquisa está presente no código, estação ou usuário
                    if (termo_pesquisa in item['codigo'].lower() or 
                        termo_pesquisa in item['usuario'].lower() or 
                        termo_pesquisa in item['estacao'].lower()):
                        dados_filtrados.append(item)
                else:
                    # Se não houver termo de pesquisa, incluir todos os itens que passaram no filtro de data
                    dados_filtrados.append(item)
            
            # --- Ordenação --- 
            ordem_selecionada = self.codigo_combo.currentText()
            
            # Função auxiliar para converter data/hora para ordenação
            def converter_datetime_safe(data_str, hora_str, default_value):
                if not data_str:
                    return default_value
                try:
                    data_parts = data_str.split('/')
                    hora_parts = hora_str.split(':') if hora_str else ['0', '0']
                    # Garantir que as partes têm o tamanho esperado
                    if len(data_parts) == 3 and len(hora_parts) >= 2:
                        return datetime.datetime(
                            int(data_parts[2]), int(data_parts[1]), int(data_parts[0]),
                            int(hora_parts[0]), int(hora_parts[1])
                        )
                    else:
                        # Tentar apenas com a data se a hora for inválida
                        return datetime.datetime(
                            int(data_parts[2]), int(data_parts[1]), int(data_parts[0])
                        )
                except (ValueError, IndexError, TypeError):
                    print(f"Aviso: Falha ao converter data/hora: {data_str} {hora_str}")
                    return default_value

            # Ordenar conforme a seleção
            if ordem_selecionada == "Código":
                # Ordenar numericamente se possível, senão alfabeticamente
                dados_filtrados.sort(key=lambda x: int(x['codigo']) if x['codigo'].isdigit() else float('inf'))
            elif ordem_selecionada == "Data de Abertura":
                dados_filtrados.sort(key=lambda x: converter_datetime_safe(x['data_abertura'], x['hora_abertura'], datetime.datetime.min))
            elif ordem_selecionada == "Data de Fechamento":
                # Coloca os não fechados por último (datetime.max)
                dados_filtrados.sort(key=lambda x: converter_datetime_safe(x['data_fechamento'], x['hora_fechamento'], datetime.datetime.max))
            elif ordem_selecionada == "Estação":
                dados_filtrados.sort(key=lambda x: x['estacao'].lower() if x['estacao'] else '')
            elif ordem_selecionada == "Usuário (A-Z)":
                dados_filtrados.sort(key=lambda x: x['usuario'].lower() if x['usuario'] else '')
            
            # Atualizar a tabela com os dados filtrados e ordenados
            self.atualizar_tabela_com_dados(dados_filtrados)
            
        except Exception as e:
            print(f"Erro ao filtrar e ordenar: {e}")
            import traceback
            traceback.print_exc() # Imprimir traceback detalhado
    
    def atualizar_tabela_com_dados(self, dados):
        """Atualiza a tabela com os dados fornecidos"""
        # Desconectar temporariamente o sinal para evitar chamadas recursivas
        try:
            self.table.itemClicked.disconnect(self.selecionar_linha)
        except TypeError:
            pass # Já estava desconectado
            
        self.table.setRowCount(0) # Limpar tabela
        self.table.clearContents()
        
        # Preencher a tabela com os dados filtrados/ordenados
        for row, item in enumerate(dados):
            self.table.insertRow(row)
            
            # Adicionar dados à tabela
            self.table.setItem(row, 0, QTableWidgetItem(item['codigo']))
            self.table.setItem(row, 1, QTableWidgetItem(item['abertura']))
            self.table.setItem(row, 2, QTableWidgetItem(item['fechamento']))
            self.table.setItem(row, 3, QTableWidgetItem(item['estacao']))
            self.table.setItem(row, 4, QTableWidgetItem(item['usuario']))
            
            # Armazenar o ID do caixa como dado oculto
            self.table.item(row, 0).setData(Qt.UserRole, item['id'])
            
        # Reconectar o sinal
        self.table.itemClicked.connect(self.selecionar_linha)
        # Limpar seleção e desabilitar botão fechar após recarregar
        self.table.clearSelection()
        self.caixa_selecionado = None
        self.btn_fechar.setEnabled(False)
    
    def selecionar_linha(self, item):
        """Armazena o caixa selecionado quando uma linha é clicada"""
        row = item.row()
        # Certificar que a linha clicada ainda existe (após filtro/ordenação)
        if row < self.table.rowCount():
            try:
                self.caixa_selecionado = {
                    'id': self.table.item(row, 0).data(Qt.UserRole),
                    'codigo': self.table.item(row, 0).text(),
                    'abertura': self.table.item(row, 1).text(),
                    'fechamento': self.table.item(row, 2).text(),
                    'estacao': self.table.item(row, 3).text(),
                    'usuario': self.table.item(row, 4).text()
                }
                
                # Habilitar o botão Fechar apenas se o caixa estiver aberto (sem data de fechamento)
                fechamento_texto = self.table.item(row, 2).text().strip()
                self.btn_fechar.setEnabled(fechamento_texto == "")
                
                # print(f"Caixa selecionado: {self.caixa_selecionado}") # Debug
                # print(f"Botão fechar habilitado: {self.btn_fechar.isEnabled()}") # Debug
            except AttributeError:
                 # Pode ocorrer se a linha for removida enquanto o clique é processado
                 print("Aviso: Falha ao selecionar linha, item pode não existir mais.")
                 self.caixa_selecionado = None
                 self.btn_fechar.setEnabled(False)
        else:
            self.caixa_selecionado = None
            self.btn_fechar.setEnabled(False)

    
    def abrir_caixa(self):
        """Abre um novo caixa"""
        try:
            # Verificar se o usuário está logado
            usuario = base.banco.get_usuario_logado()
            if not usuario["id"]:
                QMessageBox.warning(self, "Atenção", "Você precisa estar logado para abrir um caixa.")
                return
            
            # Obter o próximo código de caixa disponível
            codigo = base.banco.obter_proximo_codigo_caixa()
            
            # Criar e exibir o diálogo de abertura de caixa
            dialogo = AbrirCaixa(codigo=codigo, tipo_operacao="Entrada", parent=self)
            if dialogo.exec_() == QDialog.Accepted:
                # Recarregar os dados após a abertura
                self.carregar_dados_reais()
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir caixa: {str(e)}")
    
    def fechar_caixa(self):
        """Fecha o caixa selecionado"""
        try:
            # Verificar se há um caixa selecionado
            if not self.caixa_selecionado:
                QMessageBox.warning(self, "Atenção", "Selecione um caixa para fechar.")
                return
            
            # Verificar se o caixa já está fechado
            if self.caixa_selecionado['fechamento']:
                QMessageBox.warning(self, "Atenção", "Este caixa já está fechado.")
                return
            
            # Verificar se o usuário está logado
            usuario = base.banco.get_usuario_logado()
            if not usuario["id"]:
                QMessageBox.warning(self, "Atenção", "Você precisa estar logado para fechar um caixa.")
                return
            
            # Obter dados do caixa selecionado
            id_caixa = self.caixa_selecionado['id']
            codigo = self.caixa_selecionado['codigo']
            
            # Criar e exibir o diálogo de fechamento de caixa
            dialogo = FecharCaixa(id_caixa=id_caixa, codigo=codigo, parent=self)
            if dialogo.exec_() == QDialog.Accepted:
                # Recarregar os dados após o fechamento
                self.carregar_dados_reais()
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao fechar caixa: {str(e)}")

# Para teste individual
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo mais moderno
    
    # Simular login para teste
    # Certifique-se que base.banco está acessível e configurado
    try:
        base.banco.usuario_logado = {
            "id": 1,
            "nome": "Usuário de Teste",
            "empresa": "Empresa Teste"
        }
        # Tentar verificar tabelas para garantir que o banco está acessível
        base.banco.verificar_tabelas_caixa()
    except Exception as e_db:
        print(f"Erro ao inicializar banco para teste: {e_db}")
        # Você pode querer mostrar uma mensagem de erro aqui ou sair
        # QMessageBox.critical(None, "Erro de Banco", f"Não foi possível conectar ou inicializar o banco: {e_db}")
        # sys.exit(1)
    
    # Criar e exibir a janela
    window = QMainWindow()
    window.setWindowTitle("Controle de caixa (PDV) - Corrigido")
    window.setGeometry(100, 100, 900, 700) # Aumentar tamanho para melhor visualização
    
    caixa_widget = ControleCaixaWindow(window)
    window.setCentralWidget(caixa_widget)
    
    window.show()
    
    sys.exit(app.exec_())
