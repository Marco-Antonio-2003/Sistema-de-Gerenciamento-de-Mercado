# Seus imports e constantes iniciais
import sys
import os
import traceback
import importlib # REATORAÇÃO: Usar importlib ao invés de exec

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QStyle,
                             QGroupBox, QGridLayout)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt, QDate

from base.banco import buscar_fornecedor_por_id

# Importar o módulo de banco de dados
try:
    from base.banco import (verificar_tabela_fornecedores, listar_fornecedores,
                            buscar_fornecedor_por_codigo, criar_fornecedor, 
                            atualizar_fornecedor, excluir_fornecedor,
                            buscar_fornecedores_por_filtro)
except ImportError:
    print("ERRO: Não foi possível importar o módulo banco.py! Funcionalidades estarão indisponíveis.")
    # Definir funções dummy para evitar que o programa quebre
    def verificar_tabela_fornecedores(*args, **kwargs): pass
    def listar_fornecedores(*args, **kwargs): return []
    def buscar_fornecedores_por_filtro(*args, **kwargs): return []
    def buscar_fornecedor_por_codigo(*args, **kwargs): return None
    def excluir_fornecedor(*args, **kwargs): pass


JANELA_LARGURA = 800
JANELA_ALTURA = 600

# REATORAÇÃO: Centralizar os estilos para facilitar a manutenção
STYLE_GROUPBOX = """
    QGroupBox {
        /* Esta cor é para o título do GroupBox */
        color: white; 
        font-size: 14px; 
        font-weight: bold;
        border: 1px solid #cccccc; 
        border-radius: 5px;
        margin-top: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin; 
        subcontrol-position: top center; 
        padding: 0 10px;
    }
    /* NOVA REGRA: Altera a cor de todos os QLabels dentro do QGroupBox */
    QGroupBox QLabel {
        color: white;
        font-size: 13px;
        background-color: transparent;
    }
"""
STYLE_SEARCH_INPUT = """
    QLineEdit, QComboBox {
        background-color: #fffff0; border: 1px solid #cccccc; padding: 5px;
        font-size: 13px; border-radius: 4px; color: black;
    }
    QLineEdit:focus, QComboBox:focus { border: 1px solid #0078d7; }
"""
STYLE_BTN_PRIMARY = """
    QPushButton {
        background-color: #0078d7; color: white; border: none;
        padding: 8px 15px; font-size: 14px; border-radius: 4px;
    }
    QPushButton:hover { background-color: #005fa3; }
    QPushButton:pressed { background-color: #004c82; }
"""
STYLE_BTN_SECONDARY = """
    QPushButton {
        background-color: #e0e0e0; color: black; border: none;
        padding: 8px 15px; font-size: 14px; border-radius: 4px;
    }
    QPushButton:hover { background-color: #d0d0d0; }
    QPushButton:pressed { background-color: #c0c0c0; }
"""
STYLE_BTN_ACTION = """
    QPushButton {
        background-color: #fffff0; color: black; border: 1px solid #cccccc;
        padding: 8px 15px; font-size: 14px; border-radius: 4px;
    }
    QPushButton:hover { background-color: #e6e6e6; }
    QPushButton:pressed { background-color: #d6d6d6; }
"""
STYLE_TABLE = """
    QTableWidget {
        background-color: #fffff0; border: 1px solid #cccccc;
        font-size: 12px;
    }
    QTableWidget::item { padding: 5px; }
    QTableWidget::item:selected { background-color: #0078d7; color: white; }
    QHeaderView::section {
        background-color: #fffff0; padding: 5px;
        border: 1px solid #cccccc; font-weight: bold;
    }
"""

class FormularioFornecedoresDummy(QWidget):
    """Classe placeholder para o caso de falha na importação do formulário real."""
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ERRO: Formulário de Fornecedores não pôde ser carregado."))

def importar_formulario_fornecedores():
    """
    REATORAÇÃO: Tenta importar a classe FormularioFornecedores de forma mais segura e limpa.
    A melhor solução é corrigir a estrutura de pastas do projeto para que um import simples funcione.
    """
    modulos_tentativa = [
        "formulario_fornecedores",
        "geral.formulario_fornecedores",
        "compras.formulario_fornecedores"
    ]
    for nome_modulo in modulos_tentativa:
        try:
            modulo = importlib.import_module(nome_modulo)
            if hasattr(modulo, 'FormularioFornecedores'):
                print(f"Importação de FormularioFornecedores bem-sucedida a partir de '{nome_modulo}'")
                return modulo.FormularioFornecedores
        except ImportError:
            continue
    print("AVISO: Não foi possível encontrar o módulo 'FormularioFornecedores'. Usando versão dummy.")
    return FormularioFornecedoresDummy

# Importar a classe FormularioFornecedores de forma segura
FormularioFornecedores = importar_formulario_fornecedores()

# Coloque esta classe no início do seu arquivo, depois dos imports
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool

class Worker(QRunnable):
    """
    Worker thread genérico para executar funções em segundo plano.
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit((e, traceback.format_exc())) # Envia o erro
        else:
            self.signals.result.emit(result) # Envia o resultado
        finally:
            self.signals.finished.emit() # Sinaliza que terminou

class WorkerSignals(QObject):
    """Sinais disponíveis para um worker: finished, error, result."""
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)




class FornecedoresWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setMinimumSize(JANELA_LARGURA, JANELA_ALTURA)
        
        self.id_fornecedor_selecionado = None
        self.janela_formulario_aberta = None
        self.threadpool = QThreadPool()
        print(f"Multithreading com máximo de {self.threadpool.maxThreadCount()} threads.")

        try:
            verificar_tabela_fornecedores()
        except Exception as e:
            QMessageBox.critical(self, "Erro Crítico", f"Falha ao verificar/criar tabela de fornecedores: {e}")
        
        self.initUI()
        self.carregar_fornecedores()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor("#003b57"))
        self.setPalette(palette)
        
        titulo = QLabel("Fornecedores", self)
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white; background: transparent;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        search_group = QGroupBox("Pesquisar Fornecedores", self)
        # A nova regra em STYLE_GROUPBOX vai estilizar os QLabels abaixo automaticamente
        search_group.setStyleSheet(STYLE_GROUPBOX)
        search_layout = QGridLayout(search_group)
        
        self.codigo_search = QLineEdit(placeholderText="Digite o código")
        self.nome_search = QLineEdit(placeholderText="Digite o nome")
        self.cnpj_search = QLineEdit(placeholderText="Digite o CNPJ")
        self.tipo_search = QComboBox()
        self.tipo_search.addItems(["Todos", "Fabricante", "Distribuidor", "Atacadista", "Varejista", "Importador"])

        for widget in [self.codigo_search, self.nome_search, self.cnpj_search, self.tipo_search]:
            widget.setStyleSheet(STYLE_SEARCH_INPUT)

        # Estes QLabels agora terão a cor branca devido à nova regra de estilo
        search_layout.addWidget(QLabel("Código:", self), 0, 0)
        search_layout.addWidget(self.codigo_search, 0, 1)
        search_layout.addWidget(QLabel("Nome:", self), 0, 2)
        search_layout.addWidget(self.nome_search, 0, 3)
        search_layout.addWidget(QLabel("CNPJ:", self), 1, 0)
        search_layout.addWidget(self.cnpj_search, 1, 1)
        search_layout.addWidget(QLabel("Tipo:", self), 1, 2)
        search_layout.addWidget(self.tipo_search, 1, 3)

        self.btn_pesquisar = QPushButton("Pesquisar", icon=self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        self.btn_pesquisar.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_pesquisar.clicked.connect(self.pesquisar)
        
        self.btn_limpar = QPushButton("Limpar Filtros", icon=self.style().standardIcon(QStyle.SP_DialogResetButton))
        self.btn_limpar.setStyleSheet(STYLE_BTN_SECONDARY)
        self.btn_limpar.clicked.connect(self.limpar_filtros)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_pesquisar)
        button_layout.addWidget(self.btn_limpar)
        search_layout.addLayout(button_layout, 2, 0, 1, 4, Qt.AlignCenter)
        
        main_layout.addWidget(search_group)
        
        botoes_layout = QHBoxLayout()
        self.btn_alterar = QPushButton("Alterar", icon=self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.btn_excluir = QPushButton("Excluir", icon=self.style().standardIcon(QStyle.SP_TrashIcon))
        self.btn_cadastrar = QPushButton("Cadastrar", icon=self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        
        for btn in [self.btn_alterar, self.btn_excluir, self.btn_cadastrar]:
            btn.setStyleSheet(STYLE_BTN_ACTION)
            botoes_layout.addWidget(btn)

        self.btn_alterar.clicked.connect(self.alterar)
        self.btn_excluir.clicked.connect(self.excluir)
        self.btn_cadastrar.clicked.connect(self.cadastrar)
        
        botoes_container = QHBoxLayout()
        botoes_container.addStretch(1)
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch(1)
        main_layout.addLayout(botoes_container)
        
        self.tabela = QTableWidget(self)
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Fantasia", "Tipo"])
        self.tabela.setStyleSheet(STYLE_TABLE)
        
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.itemClicked.connect(self.selecionar_fornecedor)
        
        # NOVA ALTERAÇÃO: Adiciona a conexão do duplo clique ao método alterar
        self.tabela.itemDoubleClicked.connect(self.alterar)
        
        main_layout.addWidget(self.tabela)

    def _preencher_tabela(self, fornecedores):
        self.tabela.setRowCount(len(fornecedores))
        for i, fornecedor in enumerate(fornecedores):
            id_fornecedor, codigo, nome, fantasia, tipo = fornecedor[0], fornecedor[1], fornecedor[2], fornecedor[3], fornecedor[4]
            item_codigo = QTableWidgetItem(str(codigo))
            item_codigo.setData(Qt.UserRole, id_fornecedor)
            self.tabela.setItem(i, 0, item_codigo)
            self.tabela.setItem(i, 1, QTableWidgetItem(str(nome)))
            self.tabela.setItem(i, 2, QTableWidgetItem(str(fantasia or "")))
            self.tabela.setItem(i, 3, QTableWidgetItem(str(tipo or "")))

    def carregar_fornecedores(self):
        try:
            self.tabela.setRowCount(0)
            fornecedores = listar_fornecedores()
            self._preencher_tabela(fornecedores)
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao carregar fornecedores: {e}", QMessageBox.Critical)
    
    def selecionar_fornecedor(self, item):
        if item:
            self.id_fornecedor_selecionado = item.tableWidget().item(item.row(), 0).data(Qt.UserRole)
        else:
            self.id_fornecedor_selecionado = None

    def pesquisar(self):
        try:
            codigo = self.codigo_search.text().strip()
            nome = self.nome_search.text().strip()
            cnpj = self.cnpj_search.text().strip()
            tipo = self.tipo_search.currentText()
            self.tabela.setRowCount(0)
            fornecedores = buscar_fornecedores_por_filtro(codigo, nome, cnpj, tipo)
            if fornecedores:
                self._preencher_tabela(fornecedores)
            else:
                self.mostrar_mensagem("Aviso", "Nenhum fornecedor encontrado com os filtros selecionados.")
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao pesquisar fornecedores: {e}", QMessageBox.Critical)

    def limpar_filtros(self):
        self.codigo_search.clear()
        self.nome_search.clear()
        self.cnpj_search.clear()
        self.tipo_search.setCurrentIndex(0)
        self.carregar_fornecedores()

    def _abrir_formulario(self, fornecedor_id=None, fornecedor_data=None):
        if FormularioFornecedores == FormularioFornecedoresDummy:
            self.mostrar_mensagem("Erro", "O formulário de fornecedores não pôde ser carregado.", QMessageBox.Critical)
            return
        if self.janela_formulario_aberta and self.janela_formulario_aberta.isVisible():
            self.janela_formulario_aberta.activateWindow()
            return
        self.janela_formulario_aberta = QMainWindow(self)
        self.janela_formulario_aberta.setWindowModality(Qt.ApplicationModal)
        self.janela_formulario_aberta.setStyleSheet("background-color: #003b57;")
        formulario = FormularioFornecedores(cadastro_tela=self, janela_parent=self.janela_formulario_aberta)
        if fornecedor_data:
            self.janela_formulario_aberta.setWindowTitle("Alterar Cadastro de Fornecedor")
            try:
                fornecedor = buscar_fornecedor_por_id(fornecedor_id)
                if fornecedor:
                    if hasattr(formulario, 'preencher_dados'):
                        formulario.preencher_dados(fornecedor_data)
                    else:
                        print("AVISO: O formulário não possui o método 'preencher_dados'.")
                else:
                    self.mostrar_mensagem("Erro", "Fornecedor não encontrado.", QMessageBox.Critical)
                    return
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Erro ao carregar dados do fornecedor: {e}", QMessageBox.Critical)
                return
        else:
            self.janela_formulario_aberta.setWindowTitle("Cadastro de Fornecedores")
        self.janela_formulario_aberta.setCentralWidget(formulario)
        self.janela_formulario_aberta.setGeometry(150, 150, 600, 500)
        self.janela_formulario_aberta.show()

    def alterar(self, item=None):
        if self.tabela.currentRow() < 0:
            if self.id_fornecedor_selecionado is None:
                self.mostrar_mensagem("Atenção", "Selecione um fornecedor para alterar.", QMessageBox.Warning)
                return
        else:
            id_da_linha = self.tabela.item(self.tabela.currentRow(), 0).data(Qt.UserRole)
            self.id_fornecedor_selecionado = id_da_linha

        if self.id_fornecedor_selecionado is None:
            return

        # ---- INÍCIO DA LÓGICA ASSÍNCRONA ----
        # 1. Mostra ao usuário que algo está acontecendo
        self.setCursor(Qt.WaitCursor)
        self.tabela.setEnabled(False) # Desabilita a tabela para evitar outros cliques

        # 2. Cria o worker e a thread
        # A função que o worker vai executar é a que busca os dados no banco
        worker = Worker(buscar_fornecedor_por_id, self.id_fornecedor_selecionado)
        
        # 3. Conecta os sinais do worker aos métodos que vão processar o resultado
        worker.signals.result.connect(self._on_alterar_success)
        worker.signals.error.connect(self._on_alterar_error)
        # O 'finished' garante que a UI será reabilitada mesmo se der erro
        worker.signals.finished.connect(self._on_alterar_finished)

        # 4. Inicia a execução em segundo plano
        self.threadpool.start(worker)
        
    def _on_alterar_success(self, fornecedor):
        """Este método é chamado quando a busca no banco termina com sucesso."""
        if fornecedor:
            # A lógica de abrir o formulário agora fica aqui
            self._abrir_formulario(fornecedor_id=self.id_fornecedor_selecionado, fornecedor_data=fornecedor)
        else:
            self.mostrar_mensagem("Erro", "Fornecedor não encontrado no banco de dados.", QMessageBox.Critical)

    def _on_alterar_error(self, err_tuple):
        """Este método é chamado se a busca no banco der erro."""
        print("ERRO NA THREAD:", err_tuple[1]) # Mostra o erro detalhado no console
        self.mostrar_mensagem("Erro de Banco de Dados", f"Não foi possível carregar os dados do fornecedor: {err_tuple[0]}", QMessageBox.Critical)

    def _on_alterar_finished(self):
        """Este método é chamado sempre que a tarefa termina (sucesso ou erro)."""
        # Restaura a UI ao estado normal
        self.setCursor(Qt.ArrowCursor)
        self.tabela.setEnabled(True)
    
    def cadastrar(self):
        self._abrir_formulario()

    def excluir(self):
        if self.id_fornecedor_selecionado is None:
            self.mostrar_mensagem("Atenção", "Selecione um fornecedor para excluir.", QMessageBox.Warning)
            return
        selected_row = self.tabela.currentRow()
        nome = self.tabela.item(selected_row, 1).text()
        codigo = self.tabela.item(selected_row, 0).text()
        resposta = QMessageBox.question(self, "Confirmar Exclusão",
                                      f"Deseja realmente excluir o fornecedor '{nome}' (Código: {codigo})?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resposta == QMessageBox.Yes:
            try:
                excluir_fornecedor(self.id_fornecedor_selecionado)
                self.mostrar_mensagem("Sucesso", f"Fornecedor '{nome}' excluído com sucesso!")
                self.id_fornecedor_selecionado = None
                self.carregar_fornecedores()
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Erro ao excluir fornecedor: {e}", QMessageBox.Critical)
    
    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        msg_box = QMessageBox(tipo, titulo, mensagem, QMessageBox.Ok, self)
        msg_box.setStyleSheet("background-color: white; color: black;")
        msg_box.exec_()