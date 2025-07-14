import sys
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QDialog,
                             QDateEdit, QComboBox, QMessageBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QGridLayout)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QDate

# Importar o módulo de banco de dados
try:
    from base.banco import (verificar_tabela_fornecedores, verificar_tabela_tipos_fornecedores,
                            buscar_fornecedor_por_id, criar_fornecedor, atualizar_fornecedor,
                            listar_tipos_fornecedores, adicionar_tipo_fornecedor,
                            atualizar_tipo_fornecedor, excluir_tipo_fornecedor)
except ImportError:
    print("ERRO: Não foi possível importar o módulo banco.py! O programa pode não funcionar corretamente.")
    # Definir funções dummy para evitar que o programa quebre se o import falhar
    def verificar_tabela_fornecedores(*args, **kwargs): pass
    def verificar_tabela_tipos_fornecedores(*args, **kwargs): pass
    def buscar_fornecedor_por_id(*args, **kwargs): return None
    def criar_fornecedor(*args, **kwargs): pass
    def atualizar_fornecedor(*args, **kwargs): pass
    def listar_tipos_fornecedores(*args, **kwargs): return []
    def adicionar_tipo_fornecedor(*args, **kwargs): pass
    def atualizar_tipo_fornecedor(*args, **kwargs): pass
    def excluir_tipo_fornecedor(*args, **kwargs): pass


class TiposFornecedoresDialog(QDialog):
    """Diálogo otimizado para gerenciar os tipos de fornecedores com botões estilizados."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Tipos de Fornecedores")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: #003b57;")
        self.initUI()
        self.carregar_tipos()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        titulo = QLabel("Gerenciar Tipos de Fornecedores")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(2)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setStyleSheet("""
            QTableWidget { background-color: #fffff0; border: 1px solid #cccccc; color: black; }
            QTableWidget::item:selected { background-color: #0078d7; color: white; }
            QHeaderView::section { background-color: #fffff0; border: 1px solid #cccccc; font-weight: bold; color: black; }
        """)
        layout.addWidget(self.tabela)

        botoes_layout = QHBoxLayout()
        
        btn_adicionar = QPushButton("Adicionar", clicked=self.adicionar_tipo)
        btn_editar = QPushButton("Editar", clicked=self.editar_tipo)
        btn_excluir = QPushButton("Excluir", clicked=self.excluir_tipo)
        btn_fechar = QPushButton("Fechar", clicked=self.accept)
        
        # --- CORREÇÃO DEFINITIVA DOS ESTILOS ---
        # Definindo estilos completos e individuais para cada botão para garantir a aplicação.
        STYLE_BTN_ADD = """
            QPushButton {
                background-color: #28a745; color: white; border: none; padding: 8px 16px;
                font-size: 14px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #218838; }
        """
        STYLE_BTN_EDIT = """
            QPushButton {
                background-color: #ffc107; color: black; border: none; padding: 8px 16px;
                font-size: 14px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #e0a800; }
        """
        STYLE_BTN_DELETE = """
            QPushButton {
                background-color: #dc3545; color: white; border: none; padding: 8px 16px;
                font-size: 14px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #c82333; }
        """
        STYLE_BTN_CLOSE = """
            QPushButton {
                background-color: #6c757d; color: white; border: none; padding: 8px 16px;
                font-size: 14px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #5a6268; }
        """
        
        btn_adicionar.setStyleSheet(STYLE_BTN_ADD)
        btn_editar.setStyleSheet(STYLE_BTN_EDIT)
        btn_excluir.setStyleSheet(STYLE_BTN_DELETE)
        btn_fechar.setStyleSheet(STYLE_BTN_CLOSE)
        
        botoes_layout.addWidget(btn_adicionar)
        botoes_layout.addWidget(btn_editar)
        botoes_layout.addWidget(btn_excluir)
        botoes_layout.addStretch()
        botoes_layout.addWidget(btn_fechar)
        
        layout.addLayout(botoes_layout)

    def carregar_tipos(self):
        try:
            self.tabela.setRowCount(0)
            tipos = listar_tipos_fornecedores()
            self.tabela.setRowCount(len(tipos))
            for i, (id_tipo, nome) in enumerate(tipos):
                self.tabela.setItem(i, 0, QTableWidgetItem(str(id_tipo)))
                self.tabela.setItem(i, 1, QTableWidgetItem(nome))
        except Exception as e:
            self._mostrar_mensagem("Erro", f"Erro ao carregar tipos: {e}", QMessageBox.Critical)

    def _obter_texto_dialogo(self, titulo, label, texto_inicial=""):
        dialog = QDialog(self)
        dialog.setWindowTitle(titulo)
        dialog.setStyleSheet("background-color: #003b57;")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(label, self, styleSheet="color: white;"))
        input_field = QLineEdit(texto_inicial, self, styleSheet="background-color: #004a6e; color: white;")
        layout.addWidget(input_field)
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK", clicked=dialog.accept)
        btn_cancel = QPushButton("Cancelar", clicked=dialog.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        return input_field.text().strip() if dialog.exec_() == QDialog.Accepted else None

    def adicionar_tipo(self):
        nome = self._obter_texto_dialogo("Novo Tipo", "Digite o nome do novo tipo:")
        if nome:
            try:
                adicionar_tipo_fornecedor(nome)
                self.carregar_tipos()
                self._mostrar_mensagem("Sucesso", f"Tipo '{nome}' adicionado com sucesso!")
            except Exception as e:
                self._mostrar_mensagem("Erro", f"Erro ao adicionar tipo: {e}", QMessageBox.Critical)

    def editar_tipo(self):
        if not self.tabela.selectedItems():
            self._mostrar_mensagem("Aviso", "Selecione um tipo para editar.")
            return
        row = self.tabela.currentRow()
        id_tipo = int(self.tabela.item(row, 0).text())
        nome_atual = self.tabela.item(row, 1).text()
        
        novo_nome = self._obter_texto_dialogo("Editar Tipo", "Digite o novo nome:", nome_atual)
        if novo_nome and novo_nome != nome_atual:
            try:
                atualizar_tipo_fornecedor(id_tipo, novo_nome)
                self.carregar_tipos()
                self._mostrar_mensagem("Sucesso", "Tipo atualizado com sucesso!")
            except Exception as e:
                self._mostrar_mensagem("Erro", f"Erro ao atualizar tipo: {e}", QMessageBox.Critical)

    def excluir_tipo(self):
        if not self.tabela.selectedItems():
            self._mostrar_mensagem("Aviso", "Selecione um tipo para excluir.")
            return
        row = self.tabela.currentRow()
        id_tipo = int(self.tabela.item(row, 0).text())
        nome = self.tabela.item(row, 1).text()
        
        resposta = QMessageBox.question(self, "Confirmar Exclusão", 
                                        f"Tem certeza que deseja excluir o tipo '{nome}'?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resposta == QMessageBox.Yes:
            try:
                excluir_tipo_fornecedor(id_tipo)
                self.carregar_tipos()
                self._mostrar_mensagem("Sucesso", f"Tipo '{nome}' excluído com sucesso!")
            except Exception as e:
                self._mostrar_mensagem("Erro", f"Erro ao excluir tipo: {e}", QMessageBox.Critical)

    def _mostrar_mensagem(self, titulo, texto, icon=QMessageBox.Information):
        msg_box = QMessageBox(icon, titulo, texto, QMessageBox.Ok, self)
        msg_box.setStyleSheet("QMessageBox { background-color: #003b57; } QLabel { color: white; }")
        msg_box.exec_()


class FormularioFornecedores(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela
        self.janela_parent = janela_parent
        self.fornecedor_id = None
        self.codigo_fornecedor = None

        self._setup_styles()

        try:
            verificar_tabela_fornecedores()
            verificar_tabela_tipos_fornecedores()
        except Exception as e:
            QMessageBox.critical(self, "Erro Crítico", f"Falha ao verificar tabelas: {e}")
        
        self.initUI()

    def _setup_styles(self):
        """Define os estilos como atributos da classe para não poluir o initUI."""
        self.STYLE_LABEL = "color: white; font-size: 13px; background-color: transparent;"
        self.STYLE_LINEEDIT = """
            QLineEdit {
                background-color: #004a6e; color: white; border: 1px solid #7F9DB9;
                padding: 6px; border-radius: 4px;
            }
            QLineEdit:focus { border: 1px solid #00aaff; }
        """
        self.STYLE_COMBOBOX = """
            QComboBox {
                background-color: #004a6e; color: white; border: 1px solid #7F9DB9;
                padding: 6px; border-radius: 4px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #004a6e; color: white; selection-background-color: #0078d7;
            }
        """
        self.STYLE_DATEEDIT = """
            QDateEdit {
                background-color: #004a6e; color: white; border: 1px solid #7F9DB9;
                padding: 6px; border-radius: 4px;
            }
            QDateEdit::drop-down { border: none; }
            QDateEdit QAbstractItemView { background-color: #004a6e; color: white; selection-background-color: #0078d7; }
        """
        # --- NOVOS ESTILOS PARA OS BOTÕES ---
        self.STYLE_BTN_NEUTRO = """
            QPushButton {
                background-color: #6c757d; color: white; border: none;
                padding: 6px 12px; font-size: 13px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #5a6268; }
        """
        self.STYLE_BTN_ADDON = """
            QPushButton {
                background-color: #005a9e; color: white; border: none;
                padding: 6px 12px; font-size: 14px; font-weight: bold; 
                border-top-right-radius: 4px; border-bottom-right-radius: 4px;
            }
            QPushButton:hover { background-color: #006ac1; }
        """
        self.STYLE_BTN_SALVAR = """
            QPushButton {
                background-color: #007bff; color: white; border: none; padding: 12px;
                font-size: 16px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #0069d9; }
        """

    def initUI(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor("#003b57"))
        self.setPalette(palette)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self._setup_header(main_layout)
        
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)
        
        self._setup_main_fields(grid_layout)
        self._setup_address_fields(grid_layout)
        
        main_layout.addLayout(grid_layout)
        main_layout.addStretch(1)
        
        self._setup_actions(main_layout)

    def _setup_header(self, layout):
        header_layout = QHBoxLayout()
        btn_voltar = QPushButton("Voltar", clicked=self.voltar)
        # Aplicando estilo
        btn_voltar.setStyleSheet(self.STYLE_BTN_NEUTRO)
        
        self.titulo_label = QLabel("Cadastro de Fornecedores")
        self.titulo_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.titulo_label.setStyleSheet(self.STYLE_LABEL)
        self.titulo_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(btn_voltar, 0)
        header_layout.addWidget(self.titulo_label, 1)
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer, 0)

        layout.addLayout(header_layout)

    def _setup_main_fields(self, grid):
        grid.addWidget(QLabel("Nome:", styleSheet=self.STYLE_LABEL), 0, 0)
        self.nome_input = QLineEdit(styleSheet=self.STYLE_LINEEDIT)
        grid.addWidget(self.nome_input, 1, 0)
        
        self.documento_label = QLabel("CNPJ:")
        self.documento_label.setStyleSheet(self.STYLE_LABEL)
        grid.addWidget(self.documento_label, 0, 1)
        self.documento_input = QLineEdit(styleSheet=self.STYLE_LINEEDIT)
        self.documento_input.textChanged.connect(self.formatar_documento)
        grid.addWidget(self.documento_input, 1, 1)

        grid.addWidget(QLabel("Nome Fantasia:", styleSheet=self.STYLE_LABEL), 2, 0)
        self.fantasia_input = QLineEdit(styleSheet=self.STYLE_LINEEDIT)
        grid.addWidget(self.fantasia_input, 3, 0)

        grid.addWidget(QLabel("Tipo:", styleSheet=self.STYLE_LABEL), 2, 1)
        tipo_layout = QHBoxLayout()
        tipo_layout.setContentsMargins(0,0,0,0)
        tipo_layout.setSpacing(0) # Remove o espaçamento entre o combo e o botão
        self.tipo_combo = QComboBox(styleSheet=self.STYLE_COMBOBOX.replace("border-radius: 4px;", "border-top-right-radius: 0px; border-bottom-right-radius: 0px;")) # Ajusta borda
        self.carregar_tipos_fornecedores()
        btn_gerenciar_tipos = QPushButton("+", clicked=self.gerenciar_tipos)
        # Aplicando estilo
        btn_gerenciar_tipos.setStyleSheet(self.STYLE_BTN_ADDON)
        tipo_layout.addWidget(self.tipo_combo, 1)
        tipo_layout.addWidget(btn_gerenciar_tipos)
        grid.addLayout(tipo_layout, 3, 1)

        grid.addWidget(QLabel("Data de Cadastro:", styleSheet=self.STYLE_LABEL), 4, 1)
        self.data_input = QDateEdit(calendarPopup=True, date=QDate.currentDate(), styleSheet=self.STYLE_DATEEDIT)
        grid.addWidget(self.data_input, 5, 1)
        
    def _setup_address_fields(self, grid):
        endereco_label = QLabel("Endereço")
        endereco_label.setFont(QFont("Arial", 16, QFont.Bold))
        endereco_label.setStyleSheet(self.STYLE_LABEL)
        grid.addWidget(endereco_label, 6, 0, 1, 2)

        grid.addWidget(QLabel("CEP:", styleSheet=self.STYLE_LABEL), 7, 0, 1, 2)
        cep_layout = QHBoxLayout()
        cep_layout.setContentsMargins(0,0,0,0)
        cep_layout.setSpacing(0) # Remove espaçamento
        self.cep_input = QLineEdit(placeholderText="00000-000", styleSheet=self.STYLE_LINEEDIT.replace("border-radius: 4px;", "border-top-right-radius: 0px; border-bottom-right-radius: 0px;"))
        self.cep_input.textChanged.connect(self.formatar_cep)
        btn_busca_cep = QPushButton("Buscar", clicked=self.buscar_endereco_por_cep)
        # Aplicando estilo
        btn_busca_cep.setStyleSheet(self.STYLE_BTN_ADDON)
        cep_layout.addWidget(self.cep_input, 1)
        cep_layout.addWidget(btn_busca_cep)
        grid.addLayout(cep_layout, 8, 0, 1, 2)

        grid.addWidget(QLabel("Rua:", styleSheet=self.STYLE_LABEL), 9, 0, 1, 2)
        self.rua_input = QLineEdit(styleSheet=self.STYLE_LINEEDIT)
        grid.addWidget(self.rua_input, 10, 0, 1, 2)

        grid.addWidget(QLabel("Bairro:", styleSheet=self.STYLE_LABEL), 11, 0, 1, 2)
        self.bairro_input = QLineEdit(styleSheet=self.STYLE_LINEEDIT)
        grid.addWidget(self.bairro_input, 12, 0, 1, 2)

        grid.addWidget(QLabel("Cidade:", styleSheet=self.STYLE_LABEL), 13, 0)
        self.cidade_input = QLineEdit(styleSheet=self.STYLE_LINEEDIT)
        grid.addWidget(self.cidade_input, 14, 0)

        grid.addWidget(QLabel("Estado (UF):", styleSheet=self.STYLE_LABEL), 13, 1)
        self.estado_input = QLineEdit(maxLength=2, placeholderText="UF", styleSheet=self.STYLE_LINEEDIT)
        grid.addWidget(self.estado_input, 14, 1)

    def _setup_actions(self, layout):
        self.btn_salvar = QPushButton("Incluir", clicked=self.salvar)
        # Aplicando estilo
        self.btn_salvar.setStyleSheet(self.STYLE_BTN_SALVAR)
        layout.addWidget(self.btn_salvar)

    # O restante dos métodos (preencher_dados, salvar, etc.) permanece o mesmo.
    # ... cole aqui todos os outros métodos da classe FormularioFornecedores ...
    def preencher_dados(self, fornecedor):
        if not fornecedor: return
        self.fornecedor_id, self.codigo_fornecedor, nome, fantasia, tipo, doc, data_str, cep, rua, bairro, cidade, estado = fornecedor[:12]
        self.nome_input.setText(nome)
        self.fantasia_input.setText(fantasia or "")
        index = self.tipo_combo.findText(tipo or "")
        self.tipo_combo.setCurrentIndex(index if index >= 0 else 0)
        self.documento_input.setText(doc)
        try:
            data_obj = datetime.strptime(data_str, "%d/%m/%Y").date()
            self.data_input.setDate(QDate(data_obj.year, data_obj.month, data_obj.day))
        except (ValueError, TypeError):
            self.data_input.setDate(QDate.currentDate())
        self.cep_input.setText(cep or "")
        self.rua_input.setText(rua or "")
        self.bairro_input.setText(bairro or "")
        self.cidade_input.setText(cidade or "")
        self.estado_input.setText(estado or "")
        self.btn_salvar.setText("Salvar Alterações")
        self.titulo_label.setText("Alterar Cadastro de Fornecedor")

    def salvar(self):
        nome = self.nome_input.text().strip()
        if not nome or self.tipo_combo.currentIndex() == 0:
            self._mostrar_mensagem("Atenção", "Preencha os campos obrigatórios (Nome e Tipo)!")
            return
        dados = {
            "nome": nome, "fantasia": self.fantasia_input.text().strip(),
            "tipo": self.tipo_combo.currentText(), "documento": self.documento_input.text().strip(),
            "data_cadastro": self.data_input.date().toString("dd/MM/yyyy"),
            "cep": self.cep_input.text().strip(), "rua": self.rua_input.text().strip(),
            "bairro": self.bairro_input.text().strip(), "cidade": self.cidade_input.text().strip(),
            "estado": self.estado_input.text().strip(),
        }
        try:
            if self.fornecedor_id is None:
                criar_fornecedor("", *dados.values())
                mensagem = "Fornecedor incluído com sucesso!"
            else:
                atualizar_fornecedor(self.fornecedor_id, self.codigo_fornecedor, *dados.values())
                mensagem = "Fornecedor atualizado com sucesso!"
            self._mostrar_mensagem("Sucesso", mensagem)
            if self.cadastro_tela: self.cadastro_tela.carregar_fornecedores()
            if self.janela_parent: self.janela_parent.close()
        except Exception as e:
            self._mostrar_mensagem("Erro", f"Não foi possível salvar: {e}", QMessageBox.Critical)

    def carregar_tipos_fornecedores(self):
        try:
            self.tipo_combo.clear()
            self.tipo_combo.addItem("Selecione um tipo")
            tipos = listar_tipos_fornecedores()
            if tipos:
                for id_tipo, nome in tipos:
                    self.tipo_combo.addItem(nome, id_tipo)
        except Exception as e:
            self._mostrar_mensagem("Erro", f"Erro ao carregar tipos: {e}")

    def buscar_endereco_por_cep(self):
        cep = ''.join(filter(str.isdigit, self.cep_input.text()))
        if len(cep) != 8:
            self._mostrar_mensagem("Atenção", "CEP deve ter 8 dígitos.")
            return
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            if response.status_code == 200 and "erro" not in response.json():
                data = response.json()
                self.rua_input.setText(data.get("logradouro", ""))
                self.bairro_input.setText(data.get("bairro", ""))
                self.cidade_input.setText(data.get("localidade", ""))
                self.estado_input.setText(data.get("uf", ""))
            else:
                self._mostrar_mensagem("Atenção", "CEP não encontrado.")
        except requests.RequestException as e:
            self._mostrar_mensagem("Erro", f"Erro de conexão ao buscar CEP: {e}")

    def formatar_cep(self, texto):
        texto_limpo = ''.join(filter(str.isdigit, texto))[:8]
        if len(texto_limpo) > 5:
            texto_formatado = f"{texto_limpo[:5]}-{texto_limpo[5:]}"
        else:
            texto_formatado = texto_limpo
        if texto_formatado != self.cep_input.text():
            self.cep_input.blockSignals(True)
            self.cep_input.setText(texto_formatado)
            self.cep_input.setCursorPosition(len(texto_formatado))
            self.cep_input.blockSignals(False)
        if len(texto_limpo) == 8: self.buscar_endereco_por_cep()
    
    def formatar_documento(self, texto):
        pass

    def gerenciar_tipos(self):
        dialog = TiposFornecedoresDialog(self)
        dialog.exec_()
        self.carregar_tipos_fornecedores()

    def voltar(self):
        if self.janela_parent: self.janela_parent.close()

    def _mostrar_mensagem(self, titulo, texto, icon=QMessageBox.Information):
        msg_box = QMessageBox(icon, titulo, texto, QMessageBox.Ok, self)
        msg_box.setStyleSheet("QMessageBox { background-color: #003b57; } QLabel { color: white; }")
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setCentralWidget(FormularioFornecedores())
    window.show()
    sys.exit(app.exec_())