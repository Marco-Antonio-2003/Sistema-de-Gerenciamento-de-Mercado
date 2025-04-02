import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
                             QFrame, QFormLayout, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
from formulario_funcionario import FormularioFuncionario

class CadastroFuncionario(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título da tela
        title_label = QLabel("Cadastro de Funcionário")
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
        
        # Campo Telefone
        self.telefone_label = QLabel("Telefone:")
        self.telefone_label.setFont(QFont("Arial", 12))
        self.telefone_label.setStyleSheet("color: white;")
        self.telefone_input = QLineEdit()
        self.telefone_input.setStyleSheet("background-color: #fffff0; padding: 8px; font-size: 12px;")
        self.telefone_input.setMinimumHeight(35)
        form_layout.addRow(self.telefone_label, self.telefone_input)
        
        # Layout para Código e Tipo de Vendedor (lado a lado)
        codigo_tipo_layout = QHBoxLayout()
        
        # Campo Código
        codigo_form = QFormLayout()
        codigo_form.setLabelAlignment(Qt.AlignRight)
        codigo_form.setVerticalSpacing(15)
        codigo_form.setHorizontalSpacing(20)
        
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setFont(QFont("Arial", 12))
        self.codigo_label.setStyleSheet("color: white;")
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("background-color: #fffff0; padding: 8px; font-size: 12px;")
        self.codigo_input.setMinimumHeight(35)
        self.codigo_input.setMaximumWidth(150)
        codigo_form.addRow(self.codigo_label, self.codigo_input)
        
        # Tipo de Vendedor
        tipo_form = QFormLayout()
        tipo_form.setLabelAlignment(Qt.AlignRight)
        tipo_form.setVerticalSpacing(15)
        tipo_form.setHorizontalSpacing(20)
        
        self.tipo_label = QLabel("Tipo de Vendedor:")
        self.tipo_label.setFont(QFont("Arial", 12))
        self.tipo_label.setStyleSheet("color: white;")
        self.tipo_combo = QComboBox()
        self.tipo_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff; 
                padding: 8px; 
                font-size: 12px;
                min-height: 35px;
            }
        """)
        self.tipo_combo.addItems(["Interno", "Externo", "Representante"])
        tipo_form.addRow(self.tipo_label, self.tipo_combo)
        
        codigo_tipo_layout.addLayout(codigo_form)
        codigo_tipo_layout.addStretch()
        codigo_tipo_layout.addLayout(tipo_form)
        
        # Campo Cidade
        cidade_form = QHBoxLayout()
        cidade_form.setSpacing(10)
        
        self.cidade_label = QLabel("Cidade:")
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
        self.btn_cadastrar.clicked.connect(self.abrir_formulario_funcionario)
        
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
        self.btn_alterar.clicked.connect(self.alterar_funcionario)
        
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
        self.btn_excluir.clicked.connect(self.excluir_funcionario)
        
        botoes_layout.addWidget(self.btn_cadastrar)
        botoes_layout.addWidget(self.btn_alterar)
        botoes_layout.addWidget(self.btn_excluir)
        botoes_layout.addStretch()
        
        # Adicionar os layouts ao layout principal
        main_layout.addLayout(form_layout)
        main_layout.addLayout(codigo_tipo_layout)
        main_layout.addLayout(cidade_layout)
        main_layout.addLayout(botoes_layout)
        main_layout.addSpacing(20)
        
        # Tabela de funcionários
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Código", "Nome", "Tipo de Vendedor"])
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
        
        self.table.itemClicked.connect(self.selecionar_funcionario)
        
        main_layout.addWidget(self.table)
        
        # Carregar dados de teste
        self.carregar_dados_teste()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")
    
    def carregar_dados_teste(self):
        """Carrega alguns dados de teste na tabela"""
        dados_teste = [
            ("1", "João Silva", "Interno"),
            ("2", "Maria Oliveira", "Externo"),
            ("3", "Carlos Souza", "Representante")
        ]
        
        self.table.setRowCount(len(dados_teste))
        
        for row, (codigo, nome, tipo) in enumerate(dados_teste):
            self.table.setItem(row, 0, QTableWidgetItem(codigo))
            self.table.setItem(row, 1, QTableWidgetItem(nome))
            self.table.setItem(row, 2, QTableWidgetItem(tipo))
    
    def selecionar_funcionario(self, item):
        """Carrega os dados do funcionário selecionado nos campos do formulário"""
        row = item.row()
        
        # Preencher os campos com os dados da linha selecionada
        codigo = self.table.item(row, 0).text()
        nome = self.table.item(row, 1).text()
        tipo = self.table.item(row, 2).text()
        
        self.codigo_input.setText(codigo)
        self.nome_input.setText(nome)
        
        # Ajustar o combo de tipo de vendedor
        index = 0  # Padrão: Interno
        if tipo == "Externo":
            index = 1
        elif tipo == "Representante":
            index = 2
            
        self.tipo_combo.setCurrentIndex(index)
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem para o usuário"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def abrir_formulario_funcionario(self):
        """Abre o formulário para cadastro de funcionário"""
        # Criar uma nova janela para o formulário
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Formulário de Cadastro de Funcionário")
        self.janela_formulario.setGeometry(150, 150, 800, 600)
        self.janela_formulario.setStyleSheet("background-color: #043b57;")
        
        formulario = FormularioFuncionario(cadastro_tela=self, janela_parent=self.janela_formulario)
        self.janela_formulario.setCentralWidget(formulario)
        
        self.janela_formulario.show()
    
    def alterar_funcionario(self):
        """Altera os dados do funcionário"""
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        tipo = self.tipo_combo.currentText()
        
        if not codigo or not nome:
            self.mostrar_mensagem("Campos obrigatórios", 
                                 "Por favor, selecione um funcionário e preencha todos os campos",
                                 QMessageBox.Warning)
            return
        
        # Busca a linha pelo código
        encontrado = False
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == codigo:
                self.table.setItem(row, 1, QTableWidgetItem(nome))
                self.table.setItem(row, 2, QTableWidgetItem(tipo))
                
                # Limpa os campos
                self.codigo_input.clear()
                self.nome_input.clear()
                self.telefone_input.clear()
                self.cidade_input.clear()
                
                self.mostrar_mensagem("Sucesso", f"Funcionário código {codigo} alterado com sucesso!")
                encontrado = True
                break
        
        if not encontrado:
            self.mostrar_mensagem("Não encontrado", 
                                 f"Funcionário com código {codigo} não encontrado", 
                                 QMessageBox.Warning)
    
    def excluir_funcionario(self):
        """Exclui um funcionário"""
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Seleção necessária", 
                                 "Por favor, selecione um funcionário para excluir", 
                                 QMessageBox.Warning)
            return
            
        # Confirmar exclusão
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir o funcionário de código {codigo}?")
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
                self.telefone_input.clear()
                self.cidade_input.clear()
                
                self.mostrar_mensagem("Sucesso", f"Funcionário {nome} (código: {codigo}) excluído com sucesso!")
                encontrado = True
                break
        
        if not encontrado:
            self.mostrar_mensagem("Não encontrado", 
                                 f"Funcionário com código {codigo} não encontrado", 
                                 QMessageBox.Warning)


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Sistema de Cadastro de Funcionários")
    window.setGeometry(100, 100, 900, 700)
    window.setStyleSheet("background-color: #043b57;")
    
    cadastro_widget = CadastroFuncionario()
    window.setCentralWidget(cadastro_widget)
    
    window.show()
    sys.exit(app.exec_())