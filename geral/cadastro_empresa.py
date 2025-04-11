#cadastro_empresa.py
import sys
import os
import importlib.util
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
        
    def load_formulario_empresa(self):
        try:
            # Tente primeiro com importação direta (para ambiente de desenvolvimento)
            try:
                # Importação direta usando o módulo
                from geral.formulario_empresa import FormularioEmpresa
                print("Importação direta de FormularioEmpresa bem-sucedida")
                return FormularioEmpresa
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_empresa.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_empresa.py")
                
                # Se o arquivo não existir, vamos criar um básico
                if not os.path.exists(module_path):
                    self.criar_formulario_empresa_padrao(module_path)
                
                # Carregar o módulo dinamicamente
                module_name = "formulario_empresa"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Não foi possível carregar o módulo {module_name}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Retornar a classe FormularioEmpresa
                if hasattr(module, "FormularioEmpresa"):
                    return getattr(module, "FormularioEmpresa")
                else:
                    raise ImportError(f"A classe FormularioEmpresa não foi encontrada no módulo {module_name}")
        except Exception as e:
            print(f"Erro ao carregar FormularioEmpresa: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}", QMessageBox.Critical)
            return None
            
    def criar_formulario_empresa_padrao(self, filepath):
        """Cria um arquivo formulario_empresa.py básico se não existir"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                                         QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FormularioEmpresa(QWidget):
    def __init__(self, parent_window, form_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.form_window = form_window
        self.initUI()
        
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("Cadastro de Empresa")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: #fffff0;
                padding: 8px;
                font-size: 12px;
                min-height: 35px;
            }
        """
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setFont(QFont("Arial", 12))
        self.nome_label.setStyleSheet("color: white;")
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        form_layout.addRow(self.nome_label, self.nome_input)
        
        # Campo CNPJ
        self.cnpj_label = QLabel("CNPJ:")
        self.cnpj_label.setFont(QFont("Arial", 12))
        self.cnpj_label.setStyleSheet("color: white;")
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setStyleSheet(lineedit_style)
        form_layout.addRow(self.cnpj_label, self.cnpj_input)
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 10px 20px;
                border: 1px solid #cccccc;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar_empresa)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(self.btn_salvar, 0, Qt.AlignCenter)
        
        # Estilo de fundo
        self.setStyleSheet("background-color: #043b57;")
        
    def salvar_empresa(self):
        nome = self.nome_input.text()
        cnpj = self.cnpj_input.text()
        
        # Validação básica
        if not nome or not cnpj:
            QMessageBox.warning(self, "Campos obrigatórios", "Por favor, preencha todos os campos.")
            return
        
        # Obter o próximo código disponível (exemplo simplificado)
        ultimo_codigo = 0
        for row in range(self.parent_window.table.rowCount()):
            codigo = int(self.parent_window.table.item(row, 0).text())
            if codigo > ultimo_codigo:
                ultimo_codigo = codigo
        
        novo_codigo = ultimo_codigo + 1
        
        # Adicionar à tabela
        row = self.parent_window.table.rowCount()
        self.parent_window.table.insertRow(row)
        self.parent_window.table.setItem(row, 0, QTableWidgetItem(str(novo_codigo)))
        self.parent_window.table.setItem(row, 1, QTableWidgetItem(nome))
        self.parent_window.table.setItem(row, 2, QTableWidgetItem(cnpj))
        
        # Mostrar mensagem de sucesso
        QMessageBox.information(self, "Sucesso", "Empresa cadastrada com sucesso!")
        
        # Limpar campos
        self.nome_input.clear()
        self.cnpj_input.clear()
        
        # Fechar o formulário, se necessário
        if self.form_window:
            self.form_window.close()
''')
            print(f"Arquivo formulario_empresa.py criado em {filepath}")
            
        except Exception as e:
            print(f"Erro ao criar arquivo formulario_empresa.py: {str(e)}")
            
    # Substitua o método cadastrar_empresa no arquivo cadastro_empresa.py

    def cadastrar_empresa(self):
        """Abre o formulário para cadastro de empresa"""
        # Carregar dinamicamente a classe FormularioEmpresa
        FormularioEmpresa = self.load_formulario_empresa()
        if FormularioEmpresa is None:
            return
        
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'form_window') and self.form_window.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
            self.form_window.activateWindow()
            self.form_window.raise_()
            return
        
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
    
    # Função alterar_empresa modificada no arquivo cadastro_empresa.py
    def alterar_empresa(self):
        """Abre o formulário para alterar os dados da empresa selecionada"""
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        cnpj = self.cnpj_input.text()
        
        if not codigo or not nome or not cnpj:
            self.mostrar_mensagem(
                "Seleção necessária", 
                "Por favor, selecione uma empresa para alterar",
                QMessageBox.Warning
            )
            return
        
        # Carregar dinamicamente a classe FormularioEmpresa
        FormularioEmpresa = self.load_formulario_empresa()
        if FormularioEmpresa is None:
            return
        
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'form_window') and self.form_window.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
            self.form_window.activateWindow()
            self.form_window.raise_()
            return
        
        # Criar uma nova janela para o formulário
        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Alterar Cadastro de Empresa")
        self.form_window.setGeometry(100, 100, 800, 600)
        self.form_window.setStyleSheet("background-color: #043b57;")
        
        # Criar e definir o widget do formulário
        form_widget = FormularioEmpresa(self, self.form_window)
        self.form_window.setCentralWidget(form_widget)
        
        # Preencher os campos com os dados da empresa selecionada
        form_widget.codigo_input.setText(codigo)
        form_widget.documento_input.setText(cnpj)
        form_widget.nome_empresa_input.setText(nome)
        
        # Encontrar os dados adicionais na tabela se necessário
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == codigo:
                # Aqui você poderia obter mais dados da tabela se necessário
                break
        
        # Alterando o título do botão para "Atualizar" em vez de "Incluir"
        form_widget.btn_incluir.setText("Atualizar")
        
        # Mostrar a janela
        self.form_window.show()
    
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


# Se este arquivo for executado como script principal
class CadastroEmpresaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Empresa")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("QMainWindow, QWidget { background-color: #043b57; }")
        
        cadastro_widget = CadastroEmpresa()
        self.setCentralWidget(cadastro_widget)

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CadastroEmpresaWindow()
    window.show()
    sys.exit(app.exec_())