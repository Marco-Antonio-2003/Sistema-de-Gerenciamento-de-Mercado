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
from base.banco import listar_empresas, excluir_empresa, verificar_tabela_empresas, buscar_empresa_por_id

class CadastroEmpresa(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Inicializar banco de dados
        self.inicializar_bd()
        self.initUI()
        
    def inicializar_bd(self):
        """Inicializa a tabela de empresas no banco de dados"""
        try:
            verificar_tabela_empresas()
        except Exception as e:
            self.mostrar_mensagem(
                "Erro", 
                f"Erro ao inicializar tabela de empresas: {e}", 
                QMessageBox.Critical
            )
        
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
        self.codigo_input.setReadOnly(True)  # Código é gerado pelo banco
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
        
        # Carregar dados do banco de dados
        self.carregar_empresas()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")
        
    def carregar_empresas(self):
        """Carrega as empresas do banco de dados na tabela"""
        try:
            empresas = listar_empresas()
            
            # Limpar tabela atual
            self.table.setRowCount(0)
            
            # Adicionar empresas na tabela
            if empresas:
                self.table.setRowCount(len(empresas))
                
                for row, (id_empresa, nome, documento) in enumerate(empresas):
                    # Formatar CNPJ/CPF para exibição
                    if documento and len(documento) == 14:  # CNPJ
                        documento_formatado = f"{documento[:2]}.{documento[2:5]}.{documento[5:8]}/{documento[8:12]}-{documento[12:]}"
                    elif documento and len(documento) == 11:  # CPF
                        documento_formatado = f"{documento[:3]}.{documento[3:6]}.{documento[6:9]}-{documento[9:]}"
                    else:
                        documento_formatado = documento
                    
                    self.table.setItem(row, 0, QTableWidgetItem(str(id_empresa)))
                    self.table.setItem(row, 1, QTableWidgetItem(nome))
                    self.table.setItem(row, 2, QTableWidgetItem(documento_formatado))
                    
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao carregar empresas: {e}", QMessageBox.Critical)
    
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
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: white;
            }
            QLabel { 
                color: black;
                background-color: white;
            }
            QPushButton {
                background-color: #003b57;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 2px;
            }
        """)
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
                from geral.formulario_empresa import FormularioEmpresa  # Alterado aqui
                print("Importação direta de FormularioEmpresa bem-sucedida")
                return FormularioEmpresa
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_empresa.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_empresa.py")
                
                # Se o arquivo não existir na pasta atual, tente na pasta geral
                if not os.path.exists(module_path):
                    module_path = os.path.join(os.path.dirname(script_dir), "geral", "formulario_empresa.py")
                    
                # Se ainda não existir, crie um básico
                if not os.path.exists(module_path):
                    # Crie a pasta geral se não existir
                    os.makedirs(os.path.join(os.path.dirname(script_dir), "geral"), exist_ok=True)
                    module_path = os.path.join(os.path.dirname(script_dir), "geral", "formulario_empresa.py")
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
from data.banco import criar_empresa, atualizar_empresa, buscar_empresa_por_id

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
        
        # Campo Código (apenas para edição)
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setFont(QFont("Arial", 12))
        self.codigo_label.setStyleSheet("color: white;")
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setReadOnly(True)
        form_layout.addRow(self.codigo_label, self.codigo_input)
        
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
        codigo = self.codigo_input.text()
        
        # Validação básica
        if not nome or not cnpj:
            QMessageBox.warning(self, "Campos obrigatórios", "Por favor, preencha todos os campos.")
            return
        
        try:
            # Verificar se é uma edição ou um novo cadastro
            if codigo:  # Edição
                # Atualizar empresa no banco de dados
                atualizar_empresa(
                    int(codigo),
                    nome,
                    "",  # nome_pessoa
                    cnpj,
                    "CNPJ",  # tipo_documento
                    "Simples Nacional",  # regime
                    "",  # telefone
                    "",  # cep
                    "",  # rua
                    "",  # numero
                    "",  # bairro
                    "",  # cidade
                    ""   # estado
                )
                QMessageBox.information(self, "Sucesso", "Empresa atualizada com sucesso!")
            else:  # Novo cadastro
                # Criar empresa no banco de dados
                novo_id = criar_empresa(
                    nome,
                    "",  # nome_pessoa
                    cnpj,
                    "CNPJ",  # tipo_documento
                    "Simples Nacional",  # regime
                    "",  # telefone
                    "",  # cep
                    "",  # rua
                    "",  # numero
                    "",  # bairro
                    "",  # cidade
                    ""   # estado
                )
                QMessageBox.information(self, "Sucesso", "Empresa cadastrada com sucesso!")
                
            # Recarregar a lista de empresas na tela principal
            self.parent_window.carregar_empresas()
            
            # Fechar o formulário
            if self.form_window:
                self.form_window.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar empresa: {str(e)}")
''')
            print(f"Arquivo formulario_empresa.py criado em {filepath}")
            
        except Exception as e:
            print(f"Erro ao criar arquivo formulario_empresa.py: {str(e)}")
    
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
        
        # Limpar os campos para um novo cadastro
        if hasattr(form_widget, 'codigo_input'):
            form_widget.codigo_input.clear()
        if hasattr(form_widget, 'nome_empresa_input'):
            form_widget.nome_empresa_input.clear()
        if hasattr(form_widget, 'documento_input'):
            form_widget.documento_input.clear()
        
        # Mostrar a janela
        self.form_window.show()
    
    def alterar_empresa(self):
        """Abre o formulário para alterar os dados da empresa selecionada"""
        codigo = self.codigo_input.text()
        
        if not codigo:
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
        
        # Buscar dados completos da empresa
        try:
            empresa = buscar_empresa_por_id(int(codigo))
            if not empresa:
                self.mostrar_mensagem("Erro", f"Empresa com código {codigo} não encontrada", QMessageBox.Warning)
                return
                
            # Criar uma nova janela para o formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Alterar Cadastro de Empresa")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("background-color: #043b57;")
            
            # Criar e definir o widget do formulário
            form_widget = FormularioEmpresa(self, self.form_window)
            self.form_window.setCentralWidget(form_widget)
            
            # Preencher os campos com os dados da empresa - COM VERIFICAÇÃO DE ATRIBUTOS
            # Código
            if hasattr(form_widget, 'codigo_input'):
                form_widget.codigo_input.setText(str(empresa[0]))  # ID
            
            # Nome da empresa - tenta diferentes variações do nome do campo
            if hasattr(form_widget, 'nome_input'):
                form_widget.nome_input.setText(empresa[1])  # NOME_EMPRESA
            elif hasattr(form_widget, 'nome_empresa_input'):
                form_widget.nome_empresa_input.setText(empresa[1])
                
            # Nome da pessoa
            if hasattr(form_widget, 'nome_pessoa_input') and len(empresa) > 2:
                form_widget.nome_pessoa_input.setText(empresa[2])  # NOME_PESSOA
                
            # Documento (CNPJ/CPF)
            documento = empresa[3] if len(empresa) > 3 else ""  # DOCUMENTO
            
            # Formatar CNPJ/CPF para exibição
            if documento and len(documento) == 14:  # CNPJ
                documento_formatado = f"{documento[:2]}.{documento[2:5]}.{documento[5:8]}/{documento[8:12]}-{documento[12:]}"
            elif documento and len(documento) == 11:  # CPF
                documento_formatado = f"{documento[:3]}.{documento[3:6]}.{documento[6:9]}-{documento[9:]}"
            else:
                documento_formatado = documento
            
            # Tenta diferentes variações do nome do campo
            if hasattr(form_widget, 'cnpj_input'):
                form_widget.cnpj_input.setText(documento_formatado)
            elif hasattr(form_widget, 'documento_input'):
                form_widget.documento_input.setText(documento_formatado)
                
            # Tipo de documento
            if hasattr(form_widget, 'tipo_documento') and len(empresa) > 4:
                tipo_doc = empresa[4]
                # Se tiver um QComboBox para selecionar o tipo
                if hasattr(form_widget.tipo_documento, 'setCurrentText'):
                    form_widget.tipo_documento.setCurrentText(tipo_doc)
                    
            # Preencher campos adicionais se existirem
            if len(empresa) > 5 and hasattr(form_widget, 'regime_combo'):
                form_widget.regime_combo.setCurrentText(empresa[5] or "Simples Nacional")
                
            if len(empresa) > 6 and hasattr(form_widget, 'telefone_input'):
                form_widget.telefone_input.setText(empresa[6] or "")
                
            if len(empresa) > 7 and hasattr(form_widget, 'cep_input'):
                cep = empresa[7] or ""
                if cep and len(cep) == 8:
                    cep = f"{cep[:5]}-{cep[5:]}"
                form_widget.cep_input.setText(cep)
                
            if len(empresa) > 8 and hasattr(form_widget, 'rua_input'):
                form_widget.rua_input.setText(empresa[8] or "")
                
            if len(empresa) > 9 and hasattr(form_widget, 'numero_input'):
                form_widget.numero_input.setText(empresa[9] or "")
                
            if len(empresa) > 10 and hasattr(form_widget, 'bairro_input'):
                form_widget.bairro_input.setText(empresa[10] or "")
                
            if len(empresa) > 11 and hasattr(form_widget, 'cidade_input'):
                form_widget.cidade_input.setText(empresa[11] or "")
                
            if len(empresa) > 12 and hasattr(form_widget, 'estado_input'):
                form_widget.estado_input.setText(empresa[12] or "")
            
            # Mostrar a janela
            self.form_window.show()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao buscar dados da empresa: {e}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()  # Imprime o stack trace completo para depuração
    
    def excluir_empresa(self):
        """Exclui a empresa selecionada do banco de dados"""
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem(
                "Seleção necessária", 
                "Por favor, selecione uma empresa para excluir", 
                QMessageBox.Warning
            )
            return
            
        # Confirmar exclusão
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir a empresa de código {codigo}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: white;
            }
            QLabel { 
                color: black;
                background-color: white;
            }
            QPushButton {
                background-color: #003b57;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 2px;
            }
        """)
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.No:
            return
        
        # Excluir a empresa do banco de dados
        try:
            nome = self.nome_input.text()
            
            # Excluir empresa
            excluir_empresa(int(codigo))
            
            # Limpar os campos
            self.codigo_input.clear()
            self.nome_input.clear()
            self.cnpj_input.clear()
            
            # Recarregar a lista de empresas
            self.carregar_empresas()
            
            self.mostrar_mensagem("Sucesso", f"Empresa {nome} (código: {codigo}) excluída com sucesso!")
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao excluir empresa: {e}", QMessageBox.Critical)


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