import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

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
        self.tipo_combo.setStyleSheet("""
            QComboBox {
                background-color: #fffff0; 
                padding: 8px; 
                font-size: 12px;
                min-height: 35px;
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
        
        # Atualizar o texto sem disparar o evento novamente
        if texto_formatado != texto:
            cursor_pos = self.documento_input.cursorPosition()
            self.documento_input.blockSignals(True)
            self.documento_input.setText(texto_formatado)
            # Ajustar a posição do cursor
            if cursor_pos < len(texto_formatado):
                self.documento_input.setCursorPosition(cursor_pos)
            else:
                self.documento_input.setCursorPosition(len(texto_formatado))
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
        """Exibe uma mensagem para o usuário"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def cadastrar_pessoa(self):
        """Abre o formulário para cadastro de pessoa"""
        from formulario_pessoa import FormularioPessoa
        
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
        """Altera os dados da pessoa"""
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        tipo = self.tipo_combo.currentText()
        documento = self.documento_input.text()
        cidade = self.cidade_input.text()
        
        if not codigo or not nome:
            self.mostrar_mensagem("Campos obrigatórios", 
                                 "Por favor, selecione uma pessoa e preencha todos os campos",
                                 QMessageBox.Warning)
            return
            
        # Validar documento
        if documento and not self.validar_documento():
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
                self.documento_input.clear()
                self.cidade_input.clear()
                
                self.mostrar_mensagem("Sucesso", f"Pessoa código {codigo} alterada com sucesso!")
                encontrado = True
                break
        
        if not encontrado:
            self.mostrar_mensagem("Não encontrado", 
                                 f"Pessoa com código {codigo} não encontrada", 
                                 QMessageBox.Warning)
    
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


# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Cadastro de Pessoa")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    cadastro_widget = CadastroPessoa()
    window.setCentralWidget(cadastro_widget)
    
    window.show()
    sys.exit(app.exec_())