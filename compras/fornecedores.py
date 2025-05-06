#fornercedores
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QStyle,
                             QGroupBox, QGridLayout)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

# Importar o módulo de banco de dados
try:
    from base.banco import (verificar_tabela_fornecedores, listar_fornecedores,
                        buscar_fornecedor_por_id, buscar_fornecedor_por_codigo,
                        criar_fornecedor, atualizar_fornecedor, excluir_fornecedor,
                        buscar_fornecedores_por_filtro)
except ImportError:
    # Tentar um caminho alternativo
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base.banco import (verificar_tabela_fornecedores, listar_fornecedores,
                            buscar_fornecedor_por_id, buscar_fornecedor_por_codigo,
                            criar_fornecedor, atualizar_fornecedor, excluir_fornecedor,
                            buscar_fornecedores_por_filtro)
    except ImportError:
        print("ERRO: Não foi possível importar o módulo banco.py!")

JANELA_LARGURA = 800
JANELA_ALTURA = 600

# Definir classe placeholder para o caso de falha na importação
class FormularioFornecedoresDummy(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela
        self.janela_parent = janela_parent
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Formulário de Fornecedores não disponível"))
        self.codigo_input = QLineEdit()
        self.nome_input = QLineEdit()
        self.fantasia_input = QLineEdit()
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Selecione um tipo", "Fabricante", "Distribuidor", "Atacadista", "Varejista", "Importador"])

# Tentar diferentes caminhos de importação
def importar_formulario_fornecedores():
    # Lista de possíveis caminhos de importação
    caminhos_tentativa = [
        # Importação direta
        "from formulario_fornecedores import FormularioFornecedores",
        # Com prefixo da pasta
        "from geral.formulario_fornecedores import FormularioFornecedores",
        # Um nível acima
        "import sys, os; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from formulario_fornecedores import FormularioFornecedores",
        # Tentar a pasta específica "compras"
        "from compras.formulario_fornecedores import FormularioFornecedores"
    ]
    
    # Classe que será retornada, inicialmente é a dummy
    formulario_class = FormularioFornecedoresDummy
    
    for tentativa in caminhos_tentativa:
        try:
            # Usar um namespace local para evitar conflitos
            local_vars = {}
            exec(tentativa, globals(), local_vars)
            print(f"Importação de FormularioFornecedores bem-sucedida com: {tentativa}")
            # Se chegou aqui, a importação funcionou - obter a classe do namespace local
            formulario_class = local_vars.get('FormularioFornecedores')
            break
        except ImportError:
            continue
        except Exception as e:
            print(f"Erro ao tentar importação: {tentativa} - {str(e)}")
            continue
    
    return formulario_class

# Importar a classe FormularioFornecedores
FormularioFornecedores = importar_formulario_fornecedores()

class FornecedoresWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Definir tamanho mínimo para o widget
        self.setMinimumSize(JANELA_LARGURA, JANELA_ALTURA)
        
        # Verificar e criar a tabela de fornecedores se não existir
        try:
            verificar_tabela_fornecedores()
        except Exception as e:
            print(f"ERRO ao verificar/criar tabela de fornecedores: {e}")
        
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
        
        # Layout para o título centralizado
        header_layout = QHBoxLayout()
        
        # Título centralizado
        titulo = QLabel("Fornecedores")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Grupo de Pesquisa
        search_group = QGroupBox("Pesquisar Fornecedores")
        search_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }
        """)
        
        search_layout = QGridLayout(search_group)
        search_layout.setSpacing(10)
        
        # Estilo comum para campos de pesquisa
        search_style = """
            QLineEdit, QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 5px;
                font-size: 13px;
                border-radius: 4px;
                color: black;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Campo Código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white;")
        search_layout.addWidget(codigo_label, 0, 0)
        
        self.codigo_search = QLineEdit()
        self.codigo_search.setStyleSheet(search_style)
        self.codigo_search.setPlaceholderText("Digite o código")
        search_layout.addWidget(self.codigo_search, 0, 1)
        
        # Campo Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white;")
        search_layout.addWidget(nome_label, 0, 2)
        
        self.nome_search = QLineEdit()
        self.nome_search.setStyleSheet(search_style)
        self.nome_search.setPlaceholderText("Digite o nome")
        search_layout.addWidget(self.nome_search, 0, 3)
        
        # Campo CNPJ
        cnpj_label = QLabel("CNPJ:")
        cnpj_label.setStyleSheet("color: white;")
        search_layout.addWidget(cnpj_label, 1, 0)
        
        self.cnpj_search = QLineEdit()
        self.cnpj_search.setStyleSheet(search_style)
        self.cnpj_search.setPlaceholderText("Digite o CNPJ")
        search_layout.addWidget(self.cnpj_search, 1, 1)
        
        # Campo Tipo
        tipo_label = QLabel("Tipo:")
        tipo_label.setStyleSheet("color: white;")
        search_layout.addWidget(tipo_label, 1, 2)
        
        self.tipo_search = QComboBox()
        self.tipo_search.setStyleSheet(search_style)
        self.tipo_search.addItem("Todos")
        self.tipo_search.addItem("Fabricante")
        self.tipo_search.addItem("Distribuidor")
        self.tipo_search.addItem("Atacadista")
        self.tipo_search.addItem("Varejista")
        self.tipo_search.addItem("Importador")
        search_layout.addWidget(self.tipo_search, 1, 3)
        
        # Botões de Pesquisa
        button_layout = QHBoxLayout()
        
        # Botão Pesquisar
        self.btn_pesquisar = QPushButton("Pesquisar")
        try:
            self.btn_pesquisar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        except:
            pass
        self.btn_pesquisar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #004c82;
            }
        """)
        self.btn_pesquisar.clicked.connect(self.pesquisar)
        button_layout.addWidget(self.btn_pesquisar)
        
        # Botão Limpar Filtros
        self.btn_limpar = QPushButton("Limpar Filtros")
        try:
            self.btn_limpar.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        except:
            pass
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: black;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        self.btn_limpar.clicked.connect(self.limpar_filtros)
        button_layout.addWidget(self.btn_limpar)
        
        search_layout.addLayout(button_layout, 2, 0, 1, 4, Qt.AlignCenter)
        
        main_layout.addWidget(search_group)
        
        # Layout para os botões de ação
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(20)
        
        # Botão Alterar
        self.btn_alterar = QPushButton("Alterar")
        try:
            self.btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        self.btn_alterar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #d6d6d6;
            }
        """)
        self.btn_alterar.clicked.connect(self.alterar)
        botoes_layout.addWidget(self.btn_alterar)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        try:
            self.btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        self.btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #d6d6d6;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir)
        botoes_layout.addWidget(self.btn_excluir)
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        try:
            self.btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        self.btn_cadastrar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #d6d6d6;
            }
        """)
        self.btn_cadastrar.clicked.connect(self.cadastrar)
        botoes_layout.addWidget(self.btn_cadastrar)
        
        # Centraliza os botões
        botoes_container = QHBoxLayout()
        botoes_container.addStretch(1)
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch(1)
        
        main_layout.addLayout(botoes_container)
        
        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Fantasia", "Tipo"])
        
        # Configurar cabeçalhos da tabela
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Estilo da tabela
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #fffff0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        # Permitir seleção de linha completa
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        
        # Para manter a funcionalidade de seleção, mas sem os campos visíveis
        self.codigo_input = QLineEdit()
        self.codigo_input.setVisible(False)
        self.nome_input = QLineEdit()
        self.nome_input.setVisible(False)
        self.fantasia_input = QLineEdit()
        self.fantasia_input.setVisible(False)
        self.tipo_combo = QComboBox()
        self.tipo_combo.setVisible(False)
        
        self.tabela.itemClicked.connect(self.selecionar_fornecedor)
        
        # Adicionar tabela ao layout principal
        main_layout.addWidget(self.tabela)
        
        # Carregar dados do banco de dados
        self.carregar_fornecedores()
    
    def carregar_fornecedores(self):
        """Carrega os fornecedores do banco de dados na tabela"""
        try:
            # Limpar a tabela
            self.tabela.setRowCount(0)
            
            # Buscar fornecedores no banco de dados
            fornecedores = listar_fornecedores()
            
            if not fornecedores:
                print("Nenhum fornecedor encontrado")
                return
            
            # Preencher a tabela com os dados
            self.tabela.setRowCount(len(fornecedores))
            
            for i, fornecedor in enumerate(fornecedores):
                # Assumindo que a função listar_fornecedores retorna os campos na ordem:
                # ID, CODIGO, NOME, FANTASIA, TIPO
                self.tabela.setItem(i, 0, QTableWidgetItem(str(fornecedor[1])))  # CODIGO
                self.tabela.setItem(i, 1, QTableWidgetItem(str(fornecedor[2])))  # NOME
                self.tabela.setItem(i, 2, QTableWidgetItem(str(fornecedor[3] or "")))  # FANTASIA
                self.tabela.setItem(i, 3, QTableWidgetItem(str(fornecedor[4] or "")))  # TIPO
                
                # Armazenar o ID como dado (não visível)
                self.tabela.item(i, 0).setData(Qt.UserRole, fornecedor[0])
            
        except Exception as e:
            print(f"Erro ao carregar fornecedores: {e}")
            self.mostrar_mensagem("Erro", f"Erro ao carregar fornecedores: {str(e)}", QMessageBox.Critical)
    
    def selecionar_fornecedor(self, item):
        """Seleciona um fornecedor na tabela e armazena os dados (sem exibir nos campos)"""
        row = item.row()
        
        codigo = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        fantasia = self.tabela.item(row, 2).text()
        tipo = self.tabela.item(row, 3).text()
        
        # Armazenar valores nos campos ocultos
        self.codigo_input.setText(codigo)
        self.nome_input.setText(nome)
        self.fantasia_input.setText(fantasia)
        
        index = self.tipo_combo.findText(tipo)
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)
    
    def pesquisar(self):
        """Pesquisa fornecedores com base nos filtros selecionados"""
        codigo = self.codigo_search.text().strip()
        nome = self.nome_search.text().strip()
        cnpj = self.cnpj_search.text().strip()
        tipo = self.tipo_search.currentText()
        
        try:
            # Limpar tabela para os novos resultados
            self.tabela.setRowCount(0)
            
            # Buscar fornecedores com base nos filtros
            fornecedores = buscar_fornecedores_por_filtro(codigo, nome, cnpj, tipo)
            
            # Verificar se encontrou resultados
            if fornecedores and len(fornecedores) > 0:
                # Preencher a tabela com os resultados
                self.tabela.setRowCount(len(fornecedores))
                
                for i, fornecedor in enumerate(fornecedores):
                    # ID, CODIGO, NOME, FANTASIA, TIPO, CNPJ
                    self.tabela.setItem(i, 0, QTableWidgetItem(str(fornecedor[1])))  # CODIGO
                    self.tabela.setItem(i, 1, QTableWidgetItem(str(fornecedor[2])))  # NOME
                    self.tabela.setItem(i, 2, QTableWidgetItem(str(fornecedor[3] or "")))  # FANTASIA
                    self.tabela.setItem(i, 3, QTableWidgetItem(str(fornecedor[4] or "")))  # TIPO
                    
                    # Armazenar o ID como dado (não visível)
                    self.tabela.item(i, 0).setData(Qt.UserRole, fornecedor[0])
            else:
                # Mensagem quando nenhum fornecedor corresponde aos filtros
                self.mostrar_mensagem("Aviso", "Nenhum fornecedor encontrado com os filtros selecionados.")
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao pesquisar fornecedores: {str(e)}", QMessageBox.Critical)

    def limpar_filtros(self):
        """Limpa todos os campos de pesquisa e carrega todos os fornecedores novamente"""
        self.codigo_search.clear()
        self.nome_search.clear()
        self.cnpj_search.clear()
        self.tipo_search.setCurrentIndex(0)  # "Todos"
        
        # Recarregar todos os fornecedores
        self.carregar_fornecedores()
    
    def alterar(self):
        """Abre o formulário para alteração de fornecedor selecionado"""
        # Verificar se há uma linha selecionada
        if not self.codigo_input.text():
            self.mostrar_mensagem("Seleção necessária", 
                                "Selecione um fornecedor para alterar.", 
                                QMessageBox.Warning)
            return
        
        # Verificar se FormularioFornecedores está disponível
        global FormularioFornecedores
        if FormularioFornecedores is None or FormularioFornecedores == FormularioFornecedoresDummy:
            self.mostrar_mensagem("Erro", 
                                "Não foi possível carregar o formulário de fornecedores.", 
                                QMessageBox.Critical)
            return
        
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Alterar Cadastro de Fornecedor")
        self.janela_formulario.setGeometry(150, 150, 600, 500)
        self.janela_formulario.setStyleSheet("background-color: #003b57;")
        
        formulario = FormularioFornecedores(cadastro_tela=self, janela_parent=self.janela_formulario)
        
        # Buscar fornecedor no banco de dados pelo código
        try:
            codigo = self.codigo_input.text()
            fornecedor = buscar_fornecedor_por_codigo(codigo)
            
            if fornecedor:
                # Guardar o ID do fornecedor para atualização
                formulario.fornecedor_id = fornecedor[0]
                
                # Preencher os dados do fornecedor selecionado no formulário
                formulario.codigo_input.setText(str(fornecedor[1]))  # CODIGO
                formulario.nome_input.setText(str(fornecedor[2]))  # NOME
                formulario.fantasia_input.setText(str(fornecedor[3] or ""))  # FANTASIA
                
                # Selecionar o tipo no combobox
                tipo = str(fornecedor[4] or "")
                tipo_index = formulario.tipo_combo.findText(tipo)
                if tipo_index >= 0:
                    formulario.tipo_combo.setCurrentIndex(tipo_index)
                
                # Preencher o CNPJ e outros campos
                # CNPJ é o campo 5
                if fornecedor[5]:
                    formulario.cnpj_input.setText(str(fornecedor[5]))
                
                # Data de cadastro é o campo 6
                if fornecedor[6]:
                    from PyQt5.QtCore import QDate
                    data = fornecedor[6]
                    if hasattr(data, 'year') and hasattr(data, 'month') and hasattr(data, 'day'):
                        formulario.data_input.setDate(QDate(data.year, data.month, data.day))
                
                # Endereço: CEP(7), RUA(8), BAIRRO(9), CIDADE(10), ESTADO(11)
                if fornecedor[7]:
                    formulario.cep_input.setText(str(fornecedor[7]))
                if fornecedor[8]:
                    formulario.rua_input.setText(str(fornecedor[8]))
                if fornecedor[9]:
                    formulario.bairro_input.setText(str(fornecedor[9]))
                if fornecedor[10]:
                    formulario.cidade_input.setText(str(fornecedor[10]))
                if fornecedor[11]:
                    formulario.estado_input.setText(str(fornecedor[11]))
            else:
                self.mostrar_mensagem("Não encontrado", 
                                    f"Fornecedor com código {codigo} não encontrado no banco de dados.", 
                                    QMessageBox.Warning)
                return
                
        except Exception as e:
            print(f"Erro ao buscar fornecedor para alteração: {e}")
            self.mostrar_mensagem("Erro", 
                                f"Erro ao buscar fornecedor: {str(e)}", 
                                QMessageBox.Critical)
            return
        
        self.janela_formulario.setCentralWidget(formulario)
        self.janela_formulario.show()
    
    def excluir(self):
        """Exclui o fornecedor selecionado na tabela"""
        # Verificar se há uma linha selecionada
        if not self.codigo_input.text():
            self.mostrar_mensagem("Seleção necessária", 
                                "Selecione um fornecedor para excluir.", 
                                QMessageBox.Warning)
            return
        
        # Confirmar exclusão
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir o fornecedor '{nome}' (Código: {codigo})?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("QMessageBox { background-color: white; }")
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.Yes:
            try:
                # Buscar fornecedor no banco de dados
                fornecedor = buscar_fornecedor_por_codigo(codigo)
                
                if fornecedor:
                    # Excluir o fornecedor
                    excluir_fornecedor(fornecedor[0])  # Passar o ID
                    
                    # Limpar os campos
                    self.codigo_input.clear()
                    self.nome_input.clear()
                    self.fantasia_input.clear()
                    self.tipo_combo.setCurrentIndex(0)
                    
                    # Recarregar a tabela
                    self.carregar_fornecedores()
                    
                    self.mostrar_mensagem("Sucesso", f"Fornecedor '{nome}' excluído com sucesso!")
                else:
                    self.mostrar_mensagem("Não encontrado", 
                                        f"Fornecedor com código {codigo} não encontrado no banco de dados.", 
                                        QMessageBox.Warning)
            except Exception as e:
                print(f"Erro ao excluir fornecedor: {e}")
                self.mostrar_mensagem("Erro", 
                                    f"Erro ao excluir fornecedor: {str(e)}", 
                                    QMessageBox.Critical)
    
    def cadastrar(self):
        """Abre a tela de cadastro de fornecedores"""
        # Verificar se FormularioFornecedores está disponível
        global FormularioFornecedores
        if FormularioFornecedores is None or FormularioFornecedores == FormularioFornecedoresDummy:
            self.mostrar_mensagem("Erro", 
                                "Não foi possível carregar o formulário de fornecedores.", 
                                QMessageBox.Critical)
            return
            
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Cadastro de Fornecedores")
        self.janela_formulario.setGeometry(150, 150, 600, 500)
        self.janela_formulario.setStyleSheet("background-color: #003b57;")
        
        formulario = FormularioFornecedores(cadastro_tela=self, janela_parent=self.janela_formulario)
        self.janela_formulario.setCentralWidget(formulario)
        
        self.janela_formulario.show()
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem para o usuário"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStyleSheet("QMessageBox { background-color: white; }")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


# Classe principal para janela independente
class FornecedoresMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Cadastro de Fornecedores")
        self.setGeometry(100, 100, JANELA_LARGURA, JANELA_ALTURA)
        self.setMinimumSize(JANELA_LARGURA, JANELA_ALTURA)  # Garante tamanho mínimo
        self.setStyleSheet("background-color: #003b57;")
        
        cadastro_widget = FornecedoresWindow(self)
        self.setCentralWidget(cadastro_widget)

    def abrir_fornecedores_sistema_principal(parent=None):
        """
        Função para abrir a janela de fornecedores a partir do sistema principal
        """
        janela = QMainWindow(parent)
        janela.setWindowTitle("Fornecedores")
        janela.setGeometry(100, 100, JANELA_LARGURA, JANELA_ALTURA)
        janela.setMinimumSize(JANELA_LARGURA, JANELA_ALTURA)  # Define tamanho mínimo
        janela.setStyleSheet("background-color: #003b57;")
        
        # Criar o widget principal
        fornecedores_widget = FornecedoresWindow(janela)
        janela.setCentralWidget(fornecedores_widget)
        
        # Mostrar como janela independente
        janela.setWindowFlags(Qt.Window)
        janela.show()
        
        return janela
    
# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FornecedoresMainWindow()
    window.show()
    sys.exit(app.exec_())