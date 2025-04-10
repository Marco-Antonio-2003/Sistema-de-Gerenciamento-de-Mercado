import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

class ClientesWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.initUI()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#003b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
    
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Fundo para todo o aplicativo
        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())
        
        # Layout para o título e botão voltar
        header_layout = QHBoxLayout()
        
        # Botão Voltar
        btn_voltar = QPushButton("Voltar")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        btn_voltar.clicked.connect(self.voltar)
        header_layout.addWidget(btn_voltar)
        
        # Título
        titulo = QLabel("Clientes")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Campos de filtro
        filtro_layout = QHBoxLayout()
        filtro_layout.setSpacing(10)
        
        # Campo Código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setFixedWidth(150)
        filtro_layout.addWidget(self.codigo_input)
        
        # Campo Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        filtro_layout.addWidget(self.nome_input, 1)
        
        main_layout.addLayout(filtro_layout)
        
        # Segunda linha de filtros
        filtro_layout2 = QHBoxLayout()
        filtro_layout2.setSpacing(10)
        
        # Campo Cidade
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(cidade_label)
        
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(lineedit_style)
        filtro_layout2.addWidget(self.cidade_input, 1)
        
        # Campo CPF/CNPJ
        cpfcnpj_label = QLabel("CPF/ CNPJ:")
        cpfcnpj_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout2.addWidget(cpfcnpj_label)
        
        self.cpfcnpj_input = QLineEdit()
        self.cpfcnpj_input.setStyleSheet(lineedit_style)
        filtro_layout2.addWidget(self.cpfcnpj_input, 1)
        
        main_layout.addLayout(filtro_layout2)
        
        # Terceira linha de filtros
        filtro_layout3 = QHBoxLayout()
        filtro_layout3.setSpacing(10)
        
        # Campo Vendedor
        vendedor_label = QLabel("Vendador:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        filtro_layout3.addWidget(vendedor_label)
        
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setStyleSheet(lineedit_style)
        filtro_layout3.addWidget(self.vendedor_input, 1)
        
        main_layout.addLayout(filtro_layout3)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(15)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
                border: 1px solid #0078d7;
            }
        """
        
        # Botão Alterar
        btn_alterar = QPushButton("Alterar")
        try:
            btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        btn_alterar.setStyleSheet(btn_style)
        btn_alterar.clicked.connect(self.alterar)
        acoes_layout.addWidget(btn_alterar)
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        try:
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet(btn_style)
        btn_excluir.clicked.connect(self.excluir)
        acoes_layout.addWidget(btn_excluir)
        
        # Botão Cadastrar
        btn_cadastrar = QPushButton("Cadastrar")
        try:
            btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        btn_cadastrar.setStyleSheet(btn_style)
        btn_cadastrar.clicked.connect(self.cadastrar)
        acoes_layout.addWidget(btn_cadastrar)
        
        main_layout.addLayout(acoes_layout)
        
        # Tabela de clientes
        self.table = QTableWidget()  # Troquei o nome para 'table' para manter consistência
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Código", "Nome", "Vendedor"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                gridline-color: #cccccc;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        main_layout.addWidget(self.table)
        
        # Adicionar alguns dados de exemplo na tabela
        self.carregar_dados_exemplo()
    
    # As funções de ícones personalizados foram removidas pois agora estamos usando os ícones do sistema
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        dados = [
            ("001", "Empresa ABC Ltda", "Carlos"),
            ("002", "João Silva", "Maria"),
            ("003", "Distribuidora XYZ", "Pedro"),
            ("004", "Ana Souza", "Carlos"),
            ("005", "Mercado Central", "Maria")
        ]
        
        self.table.setRowCount(len(dados))
        for row, (codigo, nome, vendedor) in enumerate(dados):
            self.table.setItem(row, 0, QTableWidgetItem(codigo))
            self.table.setItem(row, 1, QTableWidgetItem(nome))
            self.table.setItem(row, 2, QTableWidgetItem(vendedor))
    
    def voltar(self):
        """Ação do botão voltar"""
        # Se a janela foi criada a partir de outra janela (tem um parent)
        if self.janela_parent:
            # Verifica se o parent é um QMainWindow
            if isinstance(self.janela_parent, QMainWindow):
                self.janela_parent.close()
            # Se o parent for um widget dentro de uma aplicação
            else:
                from PyQt5.QtWidgets import QApplication
                # Verifica se há uma janela principal ativa
                main_window = QApplication.activeWindow()
                if main_window:
                    main_window.close()
                    
        # Se estiver sendo executado como aplicação principal (sem parent)
        else:
            # Encerra a aplicação
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().quit()
    
    def alterar(self):
        """Ação do botão alterar"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um cliente para alterar!")
            return
        
        # Obter a linha selecionada
        row = self.table.currentRow()
        codigo = self.table.item(row, 0).text()
        nome = self.table.item(row, 1).text()
        vendedor = self.table.item(row, 2).text()
        
        print(f"Alterando cliente: {codigo} - {nome} - {vendedor}")
        # Aqui você poderia abrir o formulário de pessoas preenchido com os dados
        # do cliente selecionado para alteração
    
    def excluir(self):
        """Ação do botão excluir"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um cliente para excluir!")
            return
        
        # Obter a linha selecionada
        row = self.table.currentRow()
        self.table.removeRow(row)
        print(f"Cliente excluído da linha {row}")

    def load_formulario_pessoa(self):
        """Carrega dinamicamente o módulo FormularioPessoa"""
        try:
            # Tente primeiro com importação direta 
            try:
                from formulario_pessoa import FormularioPessoa
                print("Importação direta de FormularioPessoa bem-sucedida")
                return FormularioPessoa
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Tente importar usando caminhos diferentes
                possibilidades = [
                    'FormularioPessoa', 
                    'geral.formulario_pessoa', 
                    'clientes.formulario_pessoa'
                ]
                
                for modulo in possibilidades:
                    try:
                        mod = __import__(modulo, fromlist=['FormularioPessoa'])
                        if hasattr(mod, 'FormularioPessoa'):
                            print(f"Importação bem-sucedida via {modulo}")
                            return getattr(mod, 'FormularioPessoa')
                    except ImportError:
                        continue
                
                # Se chegou aqui, nenhuma importação funcionou.
                # Vamos tentar carregar o arquivo diretamente
                
                # Lista de possíveis locais para o arquivo
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(script_dir)
                
                possibilidades_caminhos = [
                    os.path.join(script_dir, "formulario_pessoa.py"),
                    os.path.join(script_dir, "FormularioPessoa.py"),
                    os.path.join(project_root, "formulario_pessoa.py"),
                    os.path.join(project_root, "FormularioPessoa.py"),
                    os.path.join(project_root, "geral", "formulario_pessoa.py"),
                    os.path.join(project_root, "clientes", "formulario_pessoa.py")
                ]
                
                for caminho in possibilidades_caminhos:
                    if os.path.exists(caminho):
                        print(f"Arquivo encontrado em: {caminho}")
                        # Carregar o módulo dinamicamente
                        module_name = os.path.basename(caminho).split('.')[0]
                        spec = importlib.util.spec_from_file_location(module_name, caminho)
                        if spec is None:
                            continue
                            
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Retornar a classe FormularioPessoa
                        if hasattr(module, "FormularioPessoa"):
                            return getattr(module, "FormularioPessoa")
                
                raise ImportError("Não foi possível encontrar o módulo FormularioPessoa")
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}")
            return None
    
    def cadastrar(self):
        """Ação do botão cadastrar"""
        print("Abrindo formulário para cadastro de pessoa")
        
        # Carregar o FormularioPessoa dinamicamente
        FormularioPessoa = self.load_formulario_pessoa()
        
        if FormularioPessoa is None:
            self.mostrar_mensagem("Erro", "Não foi possível carregar o formulário de pessoas")
            return
            
        # Criar uma nova janela
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Cadastro de Pessoa")
        self.janela_formulario.setGeometry(100, 100, 700, 600)
        self.janela_formulario.setStyleSheet("background-color: #003b57;")
        
        try:
            # Instanciar o formulário de pessoa
            formulario_pessoa_widget = FormularioPessoa(cadastro_tela=self, janela_parent=self.janela_formulario)
            self.janela_formulario.setCentralWidget(formulario_pessoa_widget)
            
            # Mostrar a janela
            self.janela_formulario.show()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao criar o formulário: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
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


class ClientesMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema - Clientes")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #003b57;")
        
        clientes_widget = ClientesWindow(self)  # Passa a janela como parent
        self.setCentralWidget(clientes_widget)

# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientesMainWindow()
    window.show()
    sys.exit(app.exec_())