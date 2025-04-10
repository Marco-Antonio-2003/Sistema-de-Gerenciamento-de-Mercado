import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QDateEdit, QDialog,
                             QRadioButton, QButtonGroup)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate
import os
import importlib.util

# Função para importar a classe AbrirCaixa de forma dinâmica
def importar_abrir_caixa():
    try:
        # Tente importar normalmente
        from abrir_caixa import AbrirCaixa
        return AbrirCaixa
    except ImportError:
        try:
            # Se falhar, importe dinamicamente do arquivo no mesmo diretório
            current_dir = os.path.dirname(os.path.abspath(__file__))
            module_path = os.path.join(current_dir, 'abrir_caixa.py')
            
            if not os.path.exists(module_path):
                print(f"Arquivo 'abrir_caixa.py' não encontrado em: {current_dir}")
                return None
                
            spec = importlib.util.spec_from_file_location("abrir_caixa", module_path)
            abrir_caixa_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(abrir_caixa_module)
            
            return abrir_caixa_module.AbrirCaixa
        except Exception as e:
            print(f"Erro ao importar 'abrir_caixa.py': {e}")
            return None

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

class ControleCaixaWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho com botão voltar e título
        header_layout = QHBoxLayout()
        
        # Botão Voltar com texto
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_voltar.setMinimumWidth(90)
        self.btn_voltar.clicked.connect(self.voltar)
        header_layout.addWidget(self.btn_voltar)
        
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
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(dropdown.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QComboBox:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.codigo_combo.currentIndexChanged.connect(self.filtrar_por_ordem)
        ordem_layout.addWidget(self.codigo_combo)
        
        # Adicionar o layout da ordem ao layout de filtros
        filtros_layout.addLayout(ordem_layout)
        
        # Espaçamento entre ordem e conta
        filtros_layout.addSpacing(20)
        
        # Label Conta
        conta_label = QLabel("Conta:")
        conta_label.setFont(QFont("Arial", 14))
        conta_label.setStyleSheet("color: white;")
        filtros_layout.addWidget(conta_label)
        
        # Campo de texto para Conta
        self.conta_input = QLineEdit()
        self.conta_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.conta_input.setMinimumWidth(400)
        filtros_layout.addWidget(self.conta_input, 1)  # 1 = stretch factor
        
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
        
        # DataEdit para data inicial
        self.data_inicial = QDateEdit(QDate.currentDate())
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setStyleSheet("""
            QDateEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-height: 30px;
                min-width: 200px;
            }
            QDateEdit::drop-down {
                border: 0px;
            }
            QDateEdit::down-arrow {
                width: 12px;
                height: 12px;
            }
            QDateEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
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
        self.data_final.setStyleSheet("""
            QDateEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-height: 30px;
                min-width: 200px;
            }
            QDateEdit::drop-down {
                border: 0px;
            }
            QDateEdit::down-arrow {
                width: 12px;
                height: 12px;
            }
            QDateEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
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
            }
        """)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                alternate-background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
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
        
        # Layout do botão centralizado
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_abrir)
        btn_layout.addStretch(1)
        
        main_layout.addLayout(btn_layout)
        
        # Carregar dados de teste
        self.carregar_dados_teste()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #003353; }")
        
    def carregar_dados_teste(self):
        # Dados de exemplo para demonstração
        dados = [
            ("001", "03/04/2025 08:15", "03/04/2025 18:30", "Caixa 01", "João Silva"),
            ("002", "04/04/2025 09:00", "04/04/2025 17:45", "Caixa 02", "Maria Souza"),
            ("003", "05/04/2025 08:30", "05/04/2025 18:00", "Caixa 01", "Carlos Santos"),
            ("004", "06/04/2025 09:15", "06/04/2025 17:30", "Caixa 03", "Ana Oliveira"),
            ("005", "07/04/2025 08:00", "", "Caixa 02", "Pedro Almeida")
        ]
        
        self.table.setRowCount(len(dados))
        
        for row, (codigo, abertura, fechamento, estacao, usuario) in enumerate(dados):
            self.table.setItem(row, 0, QTableWidgetItem(codigo))
            self.table.setItem(row, 1, QTableWidgetItem(abertura))
            self.table.setItem(row, 2, QTableWidgetItem(fechamento))
            self.table.setItem(row, 3, QTableWidgetItem(estacao))
            self.table.setItem(row, 4, QTableWidgetItem(usuario))
    
    def selecionar_linha(self, item):
        # Aqui você pode implementar ações quando uma linha é selecionada
        row = item.row()
        codigo = self.table.item(row, 0).text()
        # Adicionar mais ações conforme necessário
        
    def voltar(self):
        """Fecha a tela atual quando o botão voltar for clicado"""
        # Obtém a janela principal e a fecha
        self.window().close()
    
    def abrir_caixa(self):
        """Abre a janela de diálogo para escolher entre entrada e saída"""
        row = self.table.currentRow()
        if row >= 0:
            codigo = self.table.item(row, 0).text()
            
            # Criar e exibir o diálogo para escolher a operação
            dialogo = DialogoEscolhaOperacao(self)
            
            if dialogo.exec_() == QDialog.Accepted:
                tipo_operacao = dialogo.tipo_operacao
                
                # Dependendo da escolha, abrir a tela apropriada
                try:
                    # Importar a classe AbrirCaixa dinamicamente
                    AbrirCaixa = importar_abrir_caixa()
                    
                    if AbrirCaixa is None:
                        # Se não conseguir importar, exibe mensagem de erro
                        msg_box = QMessageBox(
                            QMessageBox.Warning,
                            "Arquivo não encontrado",
                            f"O arquivo 'abrir_caixa.py' não foi encontrado. Operação: {tipo_operacao}, Código: {codigo}",
                            QMessageBox.Ok,
                            self
                        )
                        
                        # Aplicar estilo com texto branco
                        msg_box.setStyleSheet("""
                            QMessageBox QLabel {
                                color: white;
                                font-weight: bold;
                            }
                        """)
                        
                        # Obter o botão OK e aplicar estilo diretamente nele
                        ok_button = msg_box.button(QMessageBox.Ok)
                        if ok_button:
                            ok_button.setStyleSheet("""
                                QPushButton {
                                    color: white;
                                    background-color: #004465;
                                    border: none;
                                    border-radius: 3px;
                                    min-width: 80px;
                                    min-height: 25px;
                                    font-weight: bold;
                                }
                                QPushButton:hover {
                                    background-color: #00354f;
                                }
                                QPushButton:pressed {
                                    background-color: #0078d7;
                                }
                            """)
                        
                        msg_box.exec_()
                        return
                    
                    # Cria uma instância da classe AbrirCaixa
                    tela_caixa = AbrirCaixa(codigo=codigo, 
                                          tipo_operacao=tipo_operacao,
                                          parent=self)
                    
                    # Aqui você pode lidar com o retorno da tela
                    if tela_caixa.exec_() == QDialog.Accepted:
                        # Exibe mensagem de sucesso com texto branco
                        msg_box = QMessageBox(
                            QMessageBox.Information,
                            "Sucesso", 
                            f"Operação de {tipo_operacao} no caixa {codigo} realizada com sucesso!",
                            QMessageBox.Ok,
                            self
                        )
                        
                        # Aplicar estilo com texto branco
                        msg_box.setStyleSheet("""
                            QMessageBox QLabel {
                                color: white;
                                font-weight: bold;
                            }
                        """)
                        
                        # Obter o botão OK e aplicar estilo diretamente nele
                        ok_button = msg_box.button(QMessageBox.Ok)
                        if ok_button:
                            ok_button.setStyleSheet("""
                                QPushButton {
                                    color: white;
                                    background-color: #004465;
                                    border: none;
                                    border-radius: 3px;
                                    min-width: 80px;
                                    min-height: 25px;
                                    font-weight: bold;
                                }
                                QPushButton:hover {
                                    background-color: #00354f;
                                }
                                QPushButton:pressed {
                                    background-color: #0078d7;
                                }
                            """)
                        
                        msg_box.exec_()
                
                except Exception as e:
                    # Se ocorrer qualquer erro, exibe uma mensagem
                    msg_box = QMessageBox(
                        QMessageBox.Warning,
                        "Erro",
                        f"Ocorreu um erro ao abrir o caixa: {str(e)}",
                        QMessageBox.Ok,
                        self
                    )
                    
                    # Aplicar estilo com texto branco
                    msg_box.setStyleSheet("""
                        QMessageBox QLabel {
                            color: white;
                            font-weight: bold;
                        }
                    """)
                    
                    # Obter o botão OK e aplicar estilo diretamente nele
                    ok_button = msg_box.button(QMessageBox.Ok)
                    if ok_button:
                        ok_button.setStyleSheet("""
                            QPushButton {
                                color: white;
                                background-color: #004465;
                                border: none;
                                border-radius: 3px;
                                min-width: 80px;
                                min-height: 25px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #00354f;
                            }
                            QPushButton:pressed {
                                background-color: #0078d7;
                            }
                        """)
                    
                    msg_box.exec_()
        else:
            # Se nenhuma linha estiver selecionada, exibe uma mensagem
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "Seleção necessária", 
                "Por favor, selecione um caixa para abrir",
                QMessageBox.Ok,
                self
            )
            
            # Aplicar estilo com texto branco
            msg_box.setStyleSheet("""
                QMessageBox QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
            
            # Obter o botão OK e aplicar estilo diretamente nele
            ok_button = msg_box.button(QMessageBox.Ok)
            if ok_button:
                ok_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 80px;
                        min-height: 25px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            msg_box.exec_()

    def filtrar_por_ordem(self):
        """Filtra os dados da tabela com base na seleção de ordem"""
        criterio = self.codigo_combo.currentText()
        # Aqui você implementaria a lógica real de ordenação/filtro
        # Exemplo simples para demonstração:
        if criterio == "Código":
            self.table.sortItems(0)  # Ordena pela coluna 0 (Código)
        elif criterio == "Data de Abertura":
            self.table.sortItems(1)  # Ordena pela coluna 1 (Abertura)
        elif criterio == "Data de Fechamento":
            self.table.sortItems(2)  # Ordena pela coluna 2 (Fechamento)
        elif criterio == "Estação":
            self.table.sortItems(3)  # Ordena pela coluna 3 (Estação)
        elif criterio == "Usuário (A-Z)":
            self.table.sortItems(4)  # Ordena pela coluna 4 (Usuário)

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Controle de Caixa")
    window.setGeometry(100, 100, 1000, 650)
    window.setStyleSheet("QMainWindow, QWidget { background-color: #003353; }")
    
    controle_caixa = ControleCaixaWindow()
    window.setCentralWidget(controle_caixa)
    
    window.show()
    sys.exit(app.exec_())