import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QCheckBox, QDialog,
                             QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

# Importe as funções do banco.py
from base.banco import (verificar_tabela_classes_financeiras, listar_classes_financeiras, 
                       criar_classe_financeira, buscar_classe_financeira_por_id,
                       atualizar_classe_financeira, excluir_classe_financeira)

class ClassesFinanceirasWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho com título centralizado
        header_layout = QHBoxLayout()
        
        # Título centralizado
        title_label = QLabel("Classe Financeira")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addLayout(header_layout)
        
        # Formulário de filtros
        filtros_frame = QFrame()
        filtros_frame.setFrameShape(QFrame.StyledPanel)
        filtros_frame.setStyleSheet("""
            QFrame {
                background-color: #003353;
                border: 1px solid #00253e;
                border-radius: 5px;
            }
        """)
        
        filtros_layout = QHBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(15, 15, 15, 15)
        filtros_layout.setSpacing(10)
        
        # Código
        codigo_label = QLabel("Código:")
        codigo_label.setFont(QFont("Arial", 11))
        codigo_label.setStyleSheet("color: white;")
        filtros_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 12px;
                min-height: 18px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        self.codigo_input.setFixedWidth(100)
        filtros_layout.addWidget(self.codigo_input)
        
        # Espaço entre código e descrição
        filtros_layout.addSpacing(20)
        
        # Descrição
        descricao_label = QLabel("Descrição:")
        descricao_label.setFont(QFont("Arial", 11))
        descricao_label.setStyleSheet("color: white;")
        filtros_layout.addWidget(descricao_label)
        
        self.descricao_input = QLineEdit()
        self.descricao_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 12px;
                min-height: 18px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        self.descricao_input.setMinimumWidth(250)
        filtros_layout.addWidget(self.descricao_input)
        
        main_layout.addWidget(filtros_frame)
        
        # Tabela de classes financeiras
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Agora incluiremos o ID
        self.table.setHorizontalHeaderLabels(["ID", "Código", "Descrição"])
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                font-size: 12px;
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
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Ajustar largura das colunas
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        self.table.itemClicked.connect(self.selecionar_linha)
        
        main_layout.addWidget(self.table)
        
        # Botões de controle
        btn_control_layout = QHBoxLayout()
        btn_control_layout.addStretch(1)  # Adiciona espaço elástico à esquerda
        
        # Botão Alterar
        self.btn_alterar = QPushButton("Alterar")
        self.btn_alterar.setIcon(QIcon("ico-img/pencil-outline.svg"))
        self.btn_alterar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 6px 12px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_alterar.clicked.connect(self.alterar_classe)
        btn_control_layout.addWidget(self.btn_alterar)
        
        # Espaçamento entre botões
        btn_control_layout.addSpacing(10)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setIcon(QIcon("ico-img/trash-outline.svg"))
        self.btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 6px 12px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir_classe)
        btn_control_layout.addWidget(self.btn_excluir)
        
        # Espaçamento entre botões
        btn_control_layout.addSpacing(10)
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setIcon(QIcon("ico-img/plus-circle-outline.svg"))
        self.btn_cadastrar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 6px 12px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_cadastrar.clicked.connect(self.cadastrar_classe)
        btn_control_layout.addWidget(self.btn_cadastrar)
        
        main_layout.addLayout(btn_control_layout)
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #003353; }")
        
        # Inicializar o banco e carregar dados
        self.inicializar_banco()
        self.carregar_dados_do_banco()
    
    def inicializar_banco(self):
        """Inicializa o banco de dados e cria a tabela se não existir"""
        try:
            verificar_tabela_classes_financeiras()
        except Exception as e:
            self.mostrar_erro(f"Erro ao inicializar o banco de dados: {str(e)}")
    
    def carregar_dados_do_banco(self):
        """Carrega os dados do banco para a tabela"""
        try:
            classes = listar_classes_financeiras()
            self.table.setRowCount(len(classes))
            
            for row, (id_classe, codigo, descricao) in enumerate(classes):
                self.table.setItem(row, 0, QTableWidgetItem(str(id_classe)))
                self.table.setItem(row, 1, QTableWidgetItem(codigo))
                self.table.setItem(row, 2, QTableWidgetItem(descricao))
                
        except Exception as e:
            self.mostrar_erro(f"Erro ao carregar dados: {str(e)}")
    
    def selecionar_linha(self, item):
        """Implementar ações quando uma linha é selecionada"""
        row = item.row()
        codigo = self.table.item(row, 1).text()
        descricao = self.table.item(row, 2).text()
        
        # Preencher os campos de filtro com os dados da linha selecionada
        self.codigo_input.setText(codigo)
        self.descricao_input.setText(descricao)
    
    def cadastrar_classe(self):
        """Abre o formulário para cadastrar nova classe financeira"""
        dialog = FormularioClasseFinanceira(self)
        result = dialog.exec_()
        
        # Se o diálogo foi aceito (usuário clicou em Incluir/Salvar)
        if result == QDialog.Accepted:
            try:
                # Obter os dados do formulário
                codigo = dialog.codigo_edit.text().strip()
                descricao = dialog.descricao_edit.text().strip()
                
                # Salvar no banco de dados
                id_classe = criar_classe_financeira(codigo, descricao)
                
                # Atualizar a tabela
                self.carregar_dados_do_banco()
                
                # Mensagem de sucesso
                self.mostrar_sucesso(f"Classe financeira {codigo} cadastrada com sucesso!")
                
            except Exception as e:
                self.mostrar_erro(f"Erro ao cadastrar classe: {str(e)}")
    
    def alterar_classe(self):
        """Abre o formulário para alterar classe financeira selecionada"""
        row = self.table.currentRow()
        if row >= 0:
            id_classe = int(self.table.item(row, 0).text())
            codigo = self.table.item(row, 1).text()
            descricao = self.table.item(row, 2).text()
            
            dialog = FormularioClasseFinanceira(self, codigo=codigo, descricao=descricao, modo_edicao=True)
            result = dialog.exec_()
            
            # Se o diálogo foi aceito (usuário clicou em Salvar)
            if result == QDialog.Accepted:
                try:
                    # Obter os dados atualizados do formulário
                    novo_codigo = dialog.codigo_edit.text().strip()
                    nova_descricao = dialog.descricao_edit.text().strip()
                    
                    # Atualizar no banco de dados
                    atualizar_classe_financeira(id_classe, novo_codigo, nova_descricao)
                    
                    # Atualizar a tabela
                    self.carregar_dados_do_banco()
                    
                    # Mensagem de sucesso
                    self.mostrar_sucesso(f"Classe financeira {novo_codigo} alterada com sucesso!")
                    
                except Exception as e:
                    self.mostrar_erro(f"Erro ao alterar classe: {str(e)}")
        else:
            self.mostrar_aviso("Seleção necessária", "Por favor, selecione uma classe para alterar.")
    
    def excluir_classe(self):
        """Exclui a classe financeira selecionada após confirmação"""
        row = self.table.currentRow()
        if row >= 0:
            id_classe = int(self.table.item(row, 0).text())
            codigo = self.table.item(row, 1).text()
            descricao = self.table.item(row, 2).text()
            
            # Pedir confirmação
            confirmacao = self.pedir_confirmacao(
                "Confirmar exclusão", 
                f"Deseja realmente excluir a classe {codigo} - {descricao}?"
            )
            
            if confirmacao:
                try:
                    # Excluir do banco de dados
                    excluir_classe_financeira(id_classe)
                    
                    # Atualizar a tabela
                    self.carregar_dados_do_banco()
                    
                    # Limpar os campos
                    self.codigo_input.clear()
                    self.descricao_input.clear()
                    
                    # Mensagem de sucesso
                    self.mostrar_sucesso(f"A classe {codigo} foi excluída com sucesso.")
                    
                except Exception as e:
                    self.mostrar_erro(f"Erro ao excluir classe: {str(e)}")
        else:
            self.mostrar_aviso("Seleção necessária", "Por favor, selecione uma classe para excluir.")
    
    def mostrar_erro(self, mensagem):
        """Exibe uma mensagem de erro"""
        msg_box = QMessageBox(
            QMessageBox.Critical,
            "Erro", 
            mensagem,
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
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
                    min-width: 70px;
                    min-height: 20px;
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
    
    def mostrar_aviso(self, titulo, mensagem):
        """Exibe uma mensagem de aviso"""
        msg_box = QMessageBox(
            QMessageBox.Warning,
            titulo, 
            mensagem,
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
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
                    min-width: 70px;
                    min-height: 20px;
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
    
    def mostrar_sucesso(self, mensagem):
        """Exibe uma mensagem de sucesso"""
        msg_box = QMessageBox(
            QMessageBox.Information,
            "Sucesso", 
            mensagem,
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
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
                    min-width: 70px;
                    min-height: 20px;
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
    
    def pedir_confirmacao(self, titulo, mensagem):
        """Exibe uma mensagem de confirmação e retorna True se confirmado"""
        msg_box = QMessageBox(
            QMessageBox.Question,
            titulo, 
            mensagem,
            QMessageBox.Yes | QMessageBox.No,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
            QMessageBox QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        # Estilizar botões
        yes_button = msg_box.button(QMessageBox.Yes)
        if yes_button:
            yes_button.setText("Sim")
            yes_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #004465;
                    border: none;
                    border-radius: 3px;
                    min-width: 70px;
                    min-height: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00354f;
                }
                QPushButton:pressed {
                    background-color: #0078d7;
                }
            """)
        
        no_button = msg_box.button(QMessageBox.No)
        if no_button:
            no_button.setText("Não")
            no_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #004465;
                    border: none;
                    border-radius: 3px;
                    min-width: 70px;
                    min-height: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00354f;
                }
                QPushButton:pressed {
                    background-color: #0078d7;
                }
            """)
        
        return msg_box.exec_() == QMessageBox.Yes


class FormularioClasseFinanceira(QDialog):
    def __init__(self, parent=None, codigo="", descricao="", modo_edicao=False):
        super().__init__(parent)
        self.parent = parent
        self.modo_edicao = modo_edicao
        self.codigo_original = codigo
        self.initUI(codigo, descricao)
        
    def initUI(self, codigo, descricao):
        # Configuração da janela
        self.setWindowTitle("Cadastro de Classe Financeira")
        self.setMinimumWidth(400)
        self.setMinimumHeight(180)
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Título centralizado
        title_label = QLabel("Cadastro de Classe Financeira")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Estilo para inputs
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 12px;
                min-height: 18px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Form layout para os campos
        form_layout = QFormLayout()
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Código
        codigo_label = QLabel("Código:")
        codigo_label.setFont(QFont("Arial", 11))
        codigo_label.setStyleSheet("color: white;")
        
        self.codigo_edit = QLineEdit(codigo)
        self.codigo_edit.setStyleSheet(input_style)
        self.codigo_edit.setFixedWidth(100)
        form_layout.addRow(codigo_label, self.codigo_edit)
        
        # Descrição
        descricao_label = QLabel("Descrição:")
        descricao_label.setFont(QFont("Arial", 11))
        descricao_label.setStyleSheet("color: white;")
        
        self.descricao_edit = QLineEdit(descricao)
        self.descricao_edit.setStyleSheet(input_style)
        self.descricao_edit.setMinimumWidth(200)
        form_layout.addRow(descricao_label, self.descricao_edit)
        
        main_layout.addLayout(form_layout)
        
        # Botão de Incluir/Salvar
        self.btn_salvar = QPushButton("Incluir" if not self.modo_edicao else "Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: black;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00b248;
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar_classe)
        
        # Layout do botão centralizado
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addStretch(1)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch(1)  # Adiciona espaço extra no final
    
    def salvar_classe(self):
        """Salva os dados da classe financeira"""
        # Validar formulário
        codigo = self.codigo_edit.text().strip()
        descricao = self.descricao_edit.text().strip()
        
        # Validações
        if not codigo:
            self.mostrar_erro("O código da classe é obrigatório.")
            return
            
        if not descricao:
            self.mostrar_erro("A descrição da classe é obrigatória.")
            return
        
        # Os dados serão salvos quando o diálogo for fechado
        self.accept()
        
    def mostrar_erro(self, mensagem):
        """Exibe uma mensagem de erro"""
        msg_box = QMessageBox(
            QMessageBox.Warning,
            "Erro",
            mensagem,
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
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
                    min-width: 70px;
                    min-height: 20px;
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

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Classe Financeira")
    window.setGeometry(100, 100, 700, 400)
    window.setStyleSheet("QMainWindow { background-color: #003353; }")
    
    classe_financeira = ClassesFinanceirasWindow()
    window.setCentralWidget(classe_financeira)
    
    window.show()
    sys.exit(app.exec_())