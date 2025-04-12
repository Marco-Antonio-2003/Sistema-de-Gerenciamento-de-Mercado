import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

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
        
        # Linha 1: Código e Nome
        linha1_layout = QHBoxLayout()
        
        # Campo Código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        linha1_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        self.codigo_input.setFixedWidth(150)
        linha1_layout.addWidget(self.codigo_input)
        
        # Campo Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        linha1_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        linha1_layout.addWidget(self.nome_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha1_layout)
        
        # Linha 2: Fantasia e Tipo
        linha2_layout = QHBoxLayout()
        
        # Campo Fantasia
        fantasia_label = QLabel("Fantasia:")
        fantasia_label.setStyleSheet("color: white; font-size: 14px;")
        linha2_layout.addWidget(fantasia_label)
        
        self.fantasia_input = QLineEdit()
        self.fantasia_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        linha2_layout.addWidget(self.fantasia_input, 1)  # 1 para expandir
        
        # Campo Tipo
        tipo_label = QLabel("Tipo:")
        tipo_label.setStyleSheet("color: white; font-size: 14px;")
        linha2_layout.addWidget(tipo_label)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.setStyleSheet("""
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.tipo_combo.addItem("Selecione um tipo")
        self.tipo_combo.addItem("Fabricante")
        self.tipo_combo.addItem("Distribuidor")
        self.tipo_combo.addItem("Atacadista")
        self.tipo_combo.addItem("Varejista")
        self.tipo_combo.addItem("Importador")
        self.tipo_combo.setFixedWidth(300)
        linha2_layout.addWidget(self.tipo_combo)
        
        main_layout.addLayout(linha2_layout)
        
        # Layout para os botões
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
        
        self.tabela.itemClicked.connect(self.selecionar_fornecedor)
        
        # Adicionar tabela ao layout principal
        main_layout.addWidget(self.tabela)
        
        # Dados iniciais para testes
        self.carregar_dados_teste()
    
    def carregar_dados_teste(self):
        """Carrega alguns dados de teste na tabela"""
        dados_teste = [
            ("1", "Fornecedor A LTDA", "Empresa A", "Fabricante"),
            ("2", "Distribuidora Nacional S.A.", "Nacional", "Distribuidor"),
            ("3", "Importadora Internacional", "Imp. Int.", "Importador")
        ]
        
        self.tabela.setRowCount(len(dados_teste))
        
        for i, (codigo, nome, fantasia, tipo) in enumerate(dados_teste):
            self.tabela.setItem(i, 0, QTableWidgetItem(codigo))
            self.tabela.setItem(i, 1, QTableWidgetItem(nome))
            self.tabela.setItem(i, 2, QTableWidgetItem(fantasia))
            self.tabela.setItem(i, 3, QTableWidgetItem(tipo))
    
    def selecionar_fornecedor(self, item):
        """Seleciona um fornecedor na tabela e preenche os campos"""
        row = item.row()
        
        codigo = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        fantasia = self.tabela.item(row, 2).text()
        tipo = self.tabela.item(row, 3).text()
        
        self.codigo_input.setText(codigo)
        self.nome_input.setText(nome)
        self.fantasia_input.setText(fantasia)
        
        index = self.tipo_combo.findText(tipo)
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)
    
    # Método voltar foi removido
    
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
        
        # Preencher os dados do fornecedor selecionado no formulário
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        fantasia = self.fantasia_input.text()
        tipo = self.tipo_combo.currentText()
        
        formulario.codigo_input.setText(codigo)
        formulario.nome_input.setText(nome)
        formulario.fantasia_input.setText(fantasia)
        
        # Selecionar o tipo no combobox
        tipo_index = formulario.tipo_combo.findText(tipo)
        if tipo_index >= 0:
            formulario.tipo_combo.setCurrentIndex(tipo_index)
        
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
            # Busca a linha pelo código
            encontrado = False
            for row in range(self.tabela.rowCount()):
                if self.tabela.item(row, 0).text() == codigo:
                    self.tabela.removeRow(row)
                    
                    # Limpa os campos
                    self.codigo_input.clear()
                    self.nome_input.clear()
                    self.fantasia_input.clear()
                    self.tipo_combo.setCurrentIndex(0)
                    
                    self.mostrar_mensagem("Sucesso", f"Fornecedor '{nome}' excluído com sucesso!")
                    encontrado = True
                    break
            
            if not encontrado:
                self.mostrar_mensagem("Não encontrado", 
                                    f"Fornecedor com código {codigo} não encontrado.", 
                                    QMessageBox.Warning)
    
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
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #003b57;")
        
        cadastro_widget = FornecedoresWindow(self)
        self.setCentralWidget(cadastro_widget)

# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FornecedoresMainWindow()
    window.show()
    sys.exit(app.exec_())