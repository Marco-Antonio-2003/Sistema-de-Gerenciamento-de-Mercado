import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class CadastroEmpresa(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título da tela
        title_label = QLabel("Cadastro de empresa")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px; background-color: #043b57;")
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
        
        # Campo CNPJ
        self.cnpj_label = QLabel("CNPJ")
        self.cnpj_label.setFont(QFont("Arial", 12))
        self.cnpj_label.setStyleSheet("color: white;")
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setStyleSheet("background-color: #fffff0; padding: 8px; font-size: 12px;")
        self.cnpj_input.setMinimumHeight(35)
        form_layout.addRow(self.cnpj_label, self.cnpj_input)
        
        # Layout para Código e botões
        codigo_botoes_layout = QHBoxLayout()
        
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
        
        codigo_botoes_layout.addLayout(codigo_form)
        codigo_botoes_layout.addStretch()
        
        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(10)
        
        self.btn_cadastrar = QPushButton("+ Cadastrar")
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
        self.btn_cadastrar.clicked.connect(self.cadastrar_empresa)
        
        self.btn_alterar = QPushButton("✎ Alterar")
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
        self.btn_alterar.clicked.connect(self.alterar_empresa)  # Conectar à função correta
        
        self.btn_excluir = QPushButton("✖ Excluir")
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
        self.btn_excluir.clicked.connect(self.excluir_empresa)
        
        botoes_layout.addWidget(self.btn_cadastrar)
        botoes_layout.addWidget(self.btn_alterar)
        botoes_layout.addWidget(self.btn_excluir)
        
        codigo_botoes_layout.addLayout(botoes_layout)
        
        main_layout.addLayout(form_layout)
        main_layout.addLayout(codigo_botoes_layout)
        main_layout.addSpacing(20)
        
        # Tabela de empresas
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Código", "Nome", "CNPJ"])
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
        
        self.table.itemClicked.connect(self.selecionar_empresa)
        
        main_layout.addWidget(self.table)
        
        # Carregar dados de teste (remover ou modificar quando conectar ao banco de dados)
        self.carregar_dados_teste()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")
        
    def carregar_dados_teste(self):
        # Dados de exemplo para demonstração
        dados = [
            (1, "Empresa A", "12.345.678/0001-90"),
            (2, "Empresa B", "98.765.432/0001-10"),
            (3, "Empresa C", "45.678.901/0001-23")
        ]
        
        self.table.setRowCount(len(dados))
        
        for row, (codigo, nome, cnpj) in enumerate(dados):
            self.table.setItem(row, 0, QTableWidgetItem(str(codigo)))
            self.table.setItem(row, 1, QTableWidgetItem(nome))
            self.table.setItem(row, 2, QTableWidgetItem(cnpj))
    
    def selecionar_empresa(self, item):
        row = item.row()
        
        # Preencher os campos com os dados da linha selecionada
        codigo = self.table.item(row, 0).text()
        nome = self.table.item(row, 1).text()
        cnpj = self.table.item(row, 2).text()
        
        self.codigo_input.setText(codigo)
        self.nome_input.setText(nome)
        self.cnpj_input.setText(cnpj)
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem para o usuário"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    def validar_cnpj(self, cnpj):
        """Validação básica de CNPJ - apenas formato"""
        # Remover caracteres não numéricos para verificação
        cnpj_nums = ''.join(filter(str.isdigit, cnpj))
        
        # Verificar se tem 14 dígitos
        if len(cnpj_nums) != 14:
            return False
        
        # Verificar se todos os dígitos são iguais (00000000000000, 11111111111111, etc)
        if len(set(cnpj_nums)) == 1:
            return False
            
        # Para uma validação mais completa, implementar algoritmo de validação de dígitos verificadores
        return True
        
    def cadastrar_empresa(self):
        """Abre o formulário de cadastro de empresa"""
        from formulario_empresa import FormularioEmpresa
        
        # Criar uma nova janela para o formulário
        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Formulário de Cadastro de Empresa")
        self.form_window.setGeometry(100, 100, 800, 600)
        self.form_window.setStyleSheet("background-color: #043b57;")
        
        # Criar e definir o widget do formulário
        # Passar a própria instância e a tabela para que o formulário possa adicionar dados
        form_widget = FormularioEmpresa(self, self.form_window)
        self.form_window.setCentralWidget(form_widget)
        
        # Mostrar a janela
        self.form_window.show()
    
    def alterar_empresa(self):
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        cnpj = self.cnpj_input.text()
        
        if not codigo or not nome or not cnpj:
            self.mostrar_mensagem(
                "Campos obrigatórios", 
                "Por favor, selecione uma empresa e preencha todos os campos",
                QMessageBox.Warning
            )
            return
            
        # Validar formato do CNPJ
        if not self.validar_cnpj(cnpj):
            self.mostrar_mensagem(
                "CNPJ inválido", 
                "O CNPJ informado não é válido. Verifique o formato.", 
                QMessageBox.Warning
            )
            return
            
        # Verificar se o CNPJ já existe em outra empresa
        codigo_atual = int(codigo)
        for row in range(self.table.rowCount()):
            row_codigo = int(self.table.item(row, 0).text())
            row_cnpj = self.table.item(row, 2).text()
            
            if row_cnpj == cnpj and row_codigo != codigo_atual:
                self.mostrar_mensagem(
                    "CNPJ duplicado", 
                    "Já existe outra empresa cadastrada com este CNPJ.", 
                    QMessageBox.Warning
                )
                return
        
        # Busca a linha pelo código
        encontrado = False
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == codigo:
                self.table.setItem(row, 1, QTableWidgetItem(nome))
                self.table.setItem(row, 2, QTableWidgetItem(cnpj))
                
                # Limpa os campos
                self.codigo_input.clear()
                self.nome_input.clear()
                self.cnpj_input.clear()
                
                self.mostrar_mensagem("Sucesso", f"Empresa código {codigo} alterada com sucesso!")
                encontrado = True
                break
        
        if not encontrado:
            self.mostrar_mensagem(
                "Não encontrado", 
                f"Empresa com código {codigo} não encontrada", 
                QMessageBox.Warning
            )
    
    def excluir_empresa(self):
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Seleção necessária", "Por favor, selecione uma empresa para excluir", QMessageBox.Warning)
            return
            
        # Confirmar exclusão
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir a empresa de código {codigo}?")
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
                self.cnpj_input.clear()
                
                self.mostrar_mensagem("Sucesso", f"Empresa {nome} (código: {codigo}) excluída com sucesso!")
                encontrado = True
                break
        
        if not encontrado:
            self.mostrar_mensagem("Não encontrado", f"Empresa com código {codigo} não encontrada", QMessageBox.Warning)


# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Cadastro de Empresa")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("QMainWindow, QWidget { background-color: #043b57; }")
    
    cadastro_widget = CadastroEmpresa()
    window.setCentralWidget(cadastro_widget)
    
    window.show()
    sys.exit(app.exec_())