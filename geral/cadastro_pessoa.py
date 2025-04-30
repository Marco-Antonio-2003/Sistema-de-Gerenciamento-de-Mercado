#cadastro_pessoa.py
import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QGridLayout)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
try:
    # Importação relativa (mesmo pacote)
    from .formulario_pessoa import FormularioPessoa
except (ImportError, ModuleNotFoundError):
    try:
        # Importação do pacote geral
        from geral.formulario_pessoa import FormularioPessoa
    except (ImportError, ModuleNotFoundError):
        # Importação direta (mesmo diretório)
        from formulario_pessoa import FormularioPessoa

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Classe para os ComboBox editáveis
class ComboBoxEditavel(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxEditavel, self).__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer().setCaseSensitivity(Qt.CaseInsensitive)
        
        # Definir como vazio ao inicializar
        self.clearEditText()  # Limpa o texto no editor
        
        # Estilo do ComboBox com seta para baixo
        self.setStyleSheet("""
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
                image: url(ico-img/down-arrow.png);
            }
            QComboBox QAbstractItemView {
                background-color: #fffff0;
                selection-background-color: #0078d7;
                selection-color: white;
                border: 1px solid #cccccc;
            }
        """)
        
    def showPopup(self):
        """Sobrescreve o método de mostrar popup para garantir que o texto atual não seja selecionado"""
        super().showPopup()
        
    def addItems(self, items):
        """Sobrescreve o método addItems para não selecionar o primeiro item"""
        super().addItems(items)
        self.setCurrentIndex(-1)  # Definir índice como -1 (nenhum selecionado)
        self.clearEditText()  # Limpar o texto do editor

class CadastroPessoa(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Inicializar banco de dados
        self.inicializar_bd()
        self.initUI()

    def inicializar_bd(self):
        """Inicializa a tabela de pessoas no banco de dados"""
        try:
            # Tente importação absoluta
            from base.banco import verificar_tabela_pessoas
            verificar_tabela_pessoas()
        except ImportError:
            try:
                # Tente importação relativa
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from base.banco import verificar_tabela_pessoas
                verificar_tabela_pessoas()
            except Exception as e:
                self.mostrar_mensagem(
                    "Erro", 
                    f"Erro ao inicializar tabela de pessoas: {e}", 
                    QMessageBox.Critical
                )

    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título da tela
        title_label = QLabel("Cadastro de Clientes")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Área de pesquisa
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #043b57;")
        search_layout = QVBoxLayout(search_frame)
        
        # Estilos
        label_style = "color: white; font-size: 14px;"
        
        # Linha de pesquisa
        search_grid = QGridLayout()
        search_grid.setColumnStretch(1, 1)  # Coluna do campo de texto se expande
        search_grid.setColumnStretch(3, 1)  # Coluna do campo de texto se expande
        
        # Código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet(label_style)
        self.codigo_search = ComboBoxEditavel()
        self.codigo_search.setPlaceholderText("Digite o código")
        search_grid.addWidget(codigo_label, 0, 0)
        search_grid.addWidget(self.codigo_search, 0, 1)
        
        # Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet(label_style)
        self.nome_search = ComboBoxEditavel()
        self.nome_search.setPlaceholderText("Digite o nome da pessoa")
        search_grid.addWidget(nome_label, 0, 2)
        search_grid.addWidget(self.nome_search, 0, 3)
        
        # CNPJ/CPF
        documento_label = QLabel("CNPJ/CPF:")
        documento_label.setStyleSheet(label_style)
        self.documento_search = ComboBoxEditavel()
        self.documento_search.setPlaceholderText("Digite o CNPJ ou CPF")
        search_grid.addWidget(documento_label, 1, 0)
        search_grid.addWidget(self.documento_search, 1, 1)
        
        # Tipo de Pessoa
        tipo_label = QLabel("Tipo:")
        tipo_label.setStyleSheet(label_style)
        self.tipo_search = QComboBox()
        self.tipo_search.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 25px;
                max-height: 25px;
            }
            QComboBox::drop-down { 
                border: none; 
            }
            QComboBox:hover { 
                border: 1px solid #0078d7; 
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
                border: 1px solid #cccccc;
            }
        """)
        self.tipo_search.addItems(["Todos", "Jurídica", "Física"])
        search_grid.addWidget(tipo_label, 1, 2)
        search_grid.addWidget(self.tipo_search, 1, 3)
        
        # Botões de pesquisa
        search_btn_layout = QHBoxLayout()
        
        # Botão Pesquisar
        self.btn_pesquisar = QPushButton("Pesquisar")
        self.btn_pesquisar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 5px 15px;
                font-size: 12px;
                border-radius: 4px;
                min-height: 25px;
                max-height: 25px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        try:
            self.btn_pesquisar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        except:
            pass
        self.btn_pesquisar.clicked.connect(self.pesquisar)
        search_btn_layout.addWidget(self.btn_pesquisar)
        
        # Botão Limpar Filtros
        self.btn_limpar = QPushButton("Limpar Filtros")
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #717171;
                color: white;
                border: none;
                padding: 5px 15px;
                font-size: 12px;
                border-radius: 4px;
                min-height: 25px;
                max-height: 25px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        try:
            self.btn_limpar.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        except:
            pass
        self.btn_limpar.clicked.connect(self.limpar_filtros)
        search_btn_layout.addWidget(self.btn_limpar)
        
        # Adicionar os botões à grid
        search_grid.addLayout(search_btn_layout, 2, 3, 1, 1, Qt.AlignRight)
        
        search_layout.addLayout(search_grid)
        main_layout.addWidget(search_frame)
        
        # Linha horizontal que separa a área de pesquisa da tabela
        separator = QLabel("")
        separator.setStyleSheet("""
            QLabel {
                background-color: #1e5a78;
                min-height: 1px;
                max-height: 1px;
                margin-top: 3px;
                margin-bottom: 3px;
            }
        """)
        main_layout.addWidget(separator)
        
        # Botões de ação na parte inferior
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(10)
        
        # Criar um layout para o campo de código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                padding: 8px;
                font-size: 12px;
                border-radius: 4px;
                color: black;
            }
        """)
        self.codigo_input.setReadOnly(True)
        self.codigo_input.setMaximumWidth(100)
        codigo_layout.addWidget(codigo_label)
        codigo_layout.addWidget(self.codigo_input)
        codigo_layout.addStretch()
        
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
                padding: 8px 15px;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        self.btn_cadastrar.clicked.connect(self.cadastrar_pessoa)
        
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
                padding: 8px 15px;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        self.btn_alterar.clicked.connect(self.alterar_pessoa)
        
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
                padding: 8px 15px;
                border: 1px solid #cccccc;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir_pessoa)
        
        # Adicionar à direita
        botoes_direita = QHBoxLayout()
        botoes_direita.addWidget(self.btn_cadastrar)
        botoes_direita.addWidget(self.btn_alterar)
        botoes_direita.addWidget(self.btn_excluir)
        
        botoes_layout.addLayout(codigo_layout)
        botoes_layout.addLayout(botoes_direita)
        
        main_layout.addLayout(botoes_layout)
        
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
        
        main_layout.addWidget(self.table, 1)  # Dar maior prioridade de espaço para a tabela
        
        # Carregar dados do banco de dados
        self.carregar_pessoas()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")

    # Método para selecionar pessoa (modificado para simplificar)
    def selecionar_pessoa(self, item):
        """
        Preenche apenas o campo de código quando uma linha é selecionada
        """
        row = item.row()
        
        # Obter o código da linha selecionada
        codigo = self.table.item(row, 0).text()
        
        # Preencher apenas o campo de código que mantivemos
        self.codigo_input.setText(codigo)
        
        # Destacar visualmente a linha selecionada na tabela
        self.table.selectRow(row)

    # Métodos de pesquisa e limpeza de filtros
    def pesquisar(self):
        """Pesquisa pessoas com base nos filtros selecionados"""
        codigo = self.codigo_search.currentText().strip()
        nome = self.nome_search.currentText().strip()
        documento = self.documento_search.currentText().strip()
        tipo = self.tipo_search.currentText()
        
        try:
            # Limpar tabela para os novos resultados
            self.table.setRowCount(0)
            
            # Construir consulta SQL base
            query = """
            SELECT ID, NOME, TIPO_PESSOA
            FROM PESSOAS
            WHERE 1=1
            """
            
            # Lista para armazenar os parâmetros de filtro
            params = []
            
            # Adicionar condições conforme os filtros fornecidos
            if codigo:
                query += " AND ID = ?"
                params.append(int(codigo))
                
            if nome:
                query += " AND UPPER(NOME) LIKE UPPER(?)"
                params.append(f"%{nome}%")  # Busca parcial, case-insensitive
                
            if documento:
                # Remover caracteres não numéricos para busca
                documento_limpo = ''.join(filter(str.isdigit, documento))
                if documento_limpo:
                    query += " AND DOCUMENTO LIKE ?"
                    params.append(f"%{documento_limpo}%")
            
            # Filtrar pelo tipo de pessoa
            if tipo != "Todos":
                query += " AND TIPO_PESSOA = ?"
                params.append(tipo)
            
            # Adicionar ordenação
            query += " ORDER BY ID"
            
            # Executar a consulta
            from base.banco import execute_query
            pessoas = execute_query(query, tuple(params) if params else None)
            
            # Verificar se encontrou resultados
            if pessoas and len(pessoas) > 0:
                # Preencher a tabela com os resultados
                self.table.setRowCount(len(pessoas))
                
                for row, (id_pessoa, nome, tipo_pessoa) in enumerate(pessoas):
                    self.table.setItem(row, 0, QTableWidgetItem(str(id_pessoa)))
                    self.table.setItem(row, 1, QTableWidgetItem(nome))
                    self.table.setItem(row, 2, QTableWidgetItem(tipo_pessoa))
            else:
                # Mensagem quando nenhuma pessoa corresponde aos filtros
                self.mostrar_mensagem("Aviso", "Nenhuma pessoa encontrada com os filtros selecionados.")
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao pesquisar pessoas: {str(e)}", QMessageBox.Critical)

    def limpar_filtros(self):
        """Limpa todos os campos de pesquisa e carrega todas as pessoas novamente"""
        self.codigo_search.setCurrentIndex(-1)
        self.codigo_search.clearEditText()
        
        self.nome_search.setCurrentIndex(-1)
        self.nome_search.clearEditText()
        
        self.documento_search.setCurrentIndex(-1)
        self.documento_search.clearEditText()
        
        self.tipo_search.setCurrentIndex(0)  # "Todos"
        
        # Recarregar todas as pessoas
        self.carregar_pessoas()
    
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
        # Remover caracteres não numéricos para verificação
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
            
            # Verifica se o texto realmente mudou para evitar loops
            if texto_formatado != texto:
                # Bloqueia sinais para evitar recursão
                self.documento_input.blockSignals(True)
                self.documento_input.setText(texto_formatado)
                
                # Posicionamento direto do cursor para CPF baseado no número de dígitos
                if len(texto_limpo) == 0:
                    nova_pos = 0
                elif len(texto_limpo) == 1:
                    nova_pos = 1
                elif len(texto_limpo) == 2:
                    nova_pos = 2
                elif len(texto_limpo) == 3:
                    nova_pos = 3
                elif len(texto_limpo) == 4:
                    nova_pos = 5  # Após o primeiro ponto: "123.4"
                elif len(texto_limpo) == 5:
                    nova_pos = 6
                elif len(texto_limpo) == 6:
                    nova_pos = 7
                elif len(texto_limpo) == 7:
                    nova_pos = 9  # Após o segundo ponto: "123.456.7"
                elif len(texto_limpo) == 8:
                    nova_pos = 10
                elif len(texto_limpo) == 9:
                    nova_pos = 11
                elif len(texto_limpo) == 10:
                    nova_pos = 13  # Após o hífen: "123.456.789-0"
                else:  # len(texto_limpo) == 11
                    nova_pos = 14
                
                # Define a nova posição do cursor
                self.documento_input.setCursorPosition(nova_pos)
                self.documento_input.blockSignals(False)
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
            
            # Verifica se o texto realmente mudou para evitar loops
            if texto_formatado != texto:
                # Bloqueia sinais para evitar recursão
                self.documento_input.blockSignals(True)
                self.documento_input.setText(texto_formatado)
                
                # Posicionamento direto do cursor para CNPJ baseado no número de dígitos
                if len(texto_limpo) == 0:
                    nova_pos = 0
                elif len(texto_limpo) == 1:
                    nova_pos = 1
                elif len(texto_limpo) == 2:
                    nova_pos = 2
                elif len(texto_limpo) == 3:
                    nova_pos = 4  # Após o primeiro ponto: "12.3"
                elif len(texto_limpo) == 4:
                    nova_pos = 5
                elif len(texto_limpo) == 5:
                    nova_pos = 6
                elif len(texto_limpo) == 6:
                    nova_pos = 8  # Após o segundo ponto: "12.345.6"
                elif len(texto_limpo) == 7:
                    nova_pos = 9
                elif len(texto_limpo) == 8:
                    nova_pos = 10
                elif len(texto_limpo) == 9:
                    nova_pos = 12  # Após a barra: "12.345.678/9"
                elif len(texto_limpo) == 10:
                    nova_pos = 13
                elif len(texto_limpo) == 11:
                    nova_pos = 14
                elif len(texto_limpo) == 12:
                    nova_pos = 15
                elif len(texto_limpo) == 13:
                    nova_pos = 17  # Após o hífen: "12.345.678/9012-3"
                else:  # len(texto_limpo) == 14
                    nova_pos = 18
                
                # Define a nova posição do cursor
                self.documento_input.setCursorPosition(nova_pos)
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
    
    def carregar_pessoas(self):
        """Carrega as pessoas do banco de dados na tabela"""
        try:
            from base.banco import listar_pessoas
            pessoas = listar_pessoas()
            
            # Limpar tabela atual
            self.table.setRowCount(0)
            
            # Adicionar pessoas na tabela
            if pessoas:
                self.table.setRowCount(len(pessoas))
                
                for row, (id_pessoa, nome, tipo_pessoa) in enumerate(pessoas):
                    self.table.setItem(row, 0, QTableWidgetItem(str(id_pessoa)))
                    self.table.setItem(row, 1, QTableWidgetItem(nome))
                    self.table.setItem(row, 2, QTableWidgetItem(tipo_pessoa))
                
                # Preencher os ComboBoxes com valores únicos
                codigos = set()
                nomes = set()
                documentos = set()
                tipos = set()
                
                # Obter dados específicos para os ComboBoxes
                try:
                    # Consulta para obter códigos, nomes e documentos
                    from base.banco import execute_query
                    pessoas_detalhadas = execute_query("""
                        SELECT ID, NOME, DOCUMENTO, TIPO_PESSOA
                        FROM PESSOAS
                        ORDER BY ID
                    """)
                    
                    if pessoas_detalhadas:
                        for id_pessoa, nome, documento, tipo_pessoa in pessoas_detalhadas:
                            codigos.add(str(id_pessoa))
                            if nome:
                                nomes.add(nome)
                            if documento:
                                # Formatar CNPJ/CPF para exibição
                                if len(documento) == 14:  # CNPJ
                                    documento_formatado = f"{documento[:2]}.{documento[2:5]}.{documento[5:8]}/{documento[8:12]}-{documento[12:]}"
                                elif len(documento) == 11:  # CPF
                                    documento_formatado = f"{documento[:3]}.{documento[3:6]}.{documento[6:9]}-{documento[9:]}"
                                else:
                                    documento_formatado = documento
                                documentos.add(documento_formatado)
                            if tipo_pessoa:
                                tipos.add(tipo_pessoa)
                except Exception as e:
                    print(f"Erro ao obter dados detalhados: {e}")
                
                # Limpar e adicionar aos ComboBoxes
                self.codigo_search.clear()
                self.nome_search.clear()
                self.documento_search.clear()
                
                self.codigo_search.addItems(sorted(codigos))
                self.nome_search.addItems(sorted(nomes))
                self.documento_search.addItems(sorted(documentos))
                    
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao carregar pessoas: {e}", QMessageBox.Critical)

    def mostrar_mensagem(self, titulo, mensagem, tipo=QMessageBox.Information):
        """Exibe uma mensagem para o usuário com estilo personalizado"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensagem)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Aplicar estilo personalizado para texto branco e botões personalizados
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #043b57;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                min-width: 80px;
                min-height: 25px;
                padding: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        
        return msg_box.exec_()
    
    def load_formulario_pessoa(self):
        """Carrega dinamicamente o módulo FormularioPessoa"""
        try:
            # Tente primeiro com importação direta (para ambiente de desenvolvimento)
            try:
                # Importação direta usando o módulo
                from geral.formulario_pessoa import FormularioPessoa
                print("Importação direta de FormularioPessoa bem-sucedida")
                return FormularioPessoa
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_pessoa.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_pessoa.py")
                
                # Se o arquivo não existir, vamos criar um básico
                if not os.path.exists(module_path):
                    self.criar_formulario_pessoa_padrao(module_path)
                
                # Carregar o módulo dinamicamente
                module_name = "formulario_pessoa"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Não foi possível carregar o módulo {module_name}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Retornar a classe FormularioPessoa
                if hasattr(module, "FormularioPessoa"):
                    return getattr(module, "FormularioPessoa")
                else:
                    raise ImportError(f"A classe FormularioPessoa não foi encontrada no módulo {module_name}")
        except Exception as e:
            print(f"Erro ao carregar FormularioPessoa: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}", QMessageBox.Critical)
            return None
            
    def criar_formulario_pessoa_padrao(self, filepath):
        """Cria um arquivo formulario_pessoa.py básico se não existir"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''import sys
# Importação condicional do requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QFormLayout, QComboBox, QMessageBox, QTableWidgetItem,
                             QDateEdit, QCalendarWidget)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate

class FormularioPessoa(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela  # Referência para a tela de cadastro
        self.janela_parent = janela_parent  # Referência para a janela que contém este widget
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Layout para o botão de voltar e título
        header_layout = QHBoxLayout()
        
        # Botão de voltar (diminuído horizontalmente)
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setFixedWidth(80)  # Largura fixa reduzida
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Título
        titulo_layout = QVBoxLayout()
        titulo = QLabel("Cadastro de Clientes")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(titulo)
        
        # Adicionar botão de voltar e título ao header
        header_layout.addWidget(self.btn_voltar)
        header_layout.addLayout(titulo_layout)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; font-weight: bold; }"
        
        # Estilo para os inputs (reduzidos)
        input_style = """
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
        """
        
        # Estilo específico para ComboBox (fundo branco)
        combo_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #cccccc;
                selection-background-color: #e6e6e6;
            }
        """
        
        # Estilo específico para DateEdit (fundo branco)
        date_style = """
            QDateEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            /* Estilo para deixar o botão dropdown visível com fundo cinza */
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #cccccc;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #e0e0e0;
            }
            QDateEdit::down-arrow {
                image: none;
                width: 12px;
                height: 12px;
                background-color: #888888;
                margin-right: 4px;
                margin-top: 1px;
            }
            /* Estilo para o calendário em si */
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QWidget {
                background-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                color: black;
            }
            QCalendarWidget QToolButton {
                background-color: white;
                color: black;
            }
            QCalendarWidget QMenu {
                background-color: white;
            }
        """
        
        # Layout para Código e Telefone (lado a lado)
        codigo_telefone_layout = QHBoxLayout()
        
        # Campo Código
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        self.codigo_input.setFixedWidth(100)  # Largura fixa reduzida
        self.codigo_input.setReadOnly(True)  # Código é gerado automaticamente
        
        codigo_layout = QFormLayout()
        codigo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        codigo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        codigo_layout.addRow(self.codigo_label, self.codigo_input)
        
        # Campo Telefone
        self.telefone_label = QLabel("Telefone:")
        self.telefone_label.setStyleSheet(label_style)
        self.telefone_input = QLineEdit()
        self.telefone_input.setStyleSheet(input_style)
        self.telefone_input.setFixedWidth(200)  # Largura fixa reduzida
        self.telefone_input.textChanged.connect(self.formatar_telefone)
        self.telefone_input.setPlaceholderText("(00) 00000-0000")
        
        telefone_layout = QFormLayout()
        telefone_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        telefone_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        telefone_layout.addRow(self.telefone_label, self.telefone_input)
        
        codigo_telefone_layout.addLayout(codigo_layout)
        codigo_telefone_layout.addLayout(telefone_layout)
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setStyleSheet(label_style)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(input_style)
        self.nome_input.setMaximumHeight(30)  # Altura máxima reduzida
        
        nome_layout = QFormLayout()
        nome_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        nome_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        nome_layout.addRow(self.nome_label, self.nome_input)
        
        # Layout para Tipo de Pessoa e Data de Cadastro (lado a lado)
        tipo_data_layout = QHBoxLayout()
        
        # Campo Tipo de Pessoa
        self.tipo_label = QLabel("Tipo de Pessoa:")
        self.tipo_label.setStyleSheet(label_style)
        self.tipo_combo = QComboBox()
        self.tipo_combo.setStyleSheet(combo_style)  # Estilo específico para ComboBox
        self.tipo_combo.setFixedWidth(200)  # Largura fixa reduzida
        self.tipo_combo.addItems(["Jurídica", "Física"])
        self.tipo_combo.currentIndexChanged.connect(self.atualizar_tipo_documento)
        
        tipo_layout = QFormLayout()
        tipo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tipo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tipo_layout.addRow(self.tipo_label, self.tipo_combo)
        
        # Campo Data de Cadastro
        self.data_label = QLabel("Data de Cadastro:")
        self.data_label.setStyleSheet(label_style)
        self.data_input = QDateEdit()
        self.data_input.setStyleSheet(date_style)  # Estilo específico para DateEdit
        self.data_input.setFixedWidth(150)  # Largura fixa reduzida
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        
        data_layout = QFormLayout()
        data_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        data_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        data_layout.addRow(self.data_label, self.data_input)
        
        tipo_data_layout.addLayout(tipo_layout)
        tipo_data_layout.addLayout(data_layout)
        
        # Campo CNPJ/CPF
        self.documento_label = QLabel("CNPJ / CPF:")
        self.documento_label.setStyleSheet(label_style)
        self.documento_input = QLineEdit()
        self.documento_input.setStyleSheet(input_style)
        self.documento_input.setFixedWidth(250)  # Largura fixa reduzida
        self.documento_input.textChanged.connect(self.formatar_documento)
        self.documento_input.setPlaceholderText("00.000.000/0001-00")
        
        documento_layout = QFormLayout()
        documento_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        documento_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        documento_layout.addRow(self.documento_label, self.documento_input)
        
        # Título do Endereço
        endereco_titulo = QLabel("Endereço")
        endereco_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        endereco_titulo.setStyleSheet("color: white; margin-top: 20px;")
        endereco_titulo.setAlignment(Qt.AlignCenter)
        
        # Layout para CEP e botão de busca
        cep_layout = QHBoxLayout()
        
        # Campo CEP
        self.cep_label = QLabel("CEP:")
        self.cep_label.setStyleSheet(label_style)
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet(input_style)
        self.cep_input.textChanged.connect(self.formatar_cep)
        self.cep_input.setPlaceholderText("00000-000")
        
        # Botão de Busca CEP
        self.btn_buscar_cep = QPushButton("Buscar CEP")
        self.btn_buscar_cep.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_buscar_cep.clicked.connect(self.buscar_endereco_por_cep)
        
        cep_form_layout = QFormLayout()
        cep_form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cep_form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cep_form_layout.addRow(self.cep_label, self.cep_input)
        
        cep_layout.addLayout(cep_form_layout)
        cep_layout.addWidget(self.btn_buscar_cep)
        
        # Campo Rua
        self.rua_label = QLabel("Rua:")
        self.rua_label.setStyleSheet(label_style)
        self.rua_input = QLineEdit()
        self.rua_input.setStyleSheet(input_style)
        
        rua_layout = QFormLayout()
        rua_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rua_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rua_layout.addRow(self.rua_label, self.rua_input)
        
        # Campo Bairro
        self.bairro_label = QLabel("Bairro:")
        self.bairro_label.setStyleSheet(label_style)
        self.bairro_input = QLineEdit()
        self.bairro_input.setStyleSheet(input_style)
        
        bairro_layout = QFormLayout()
        bairro_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bairro_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        bairro_layout.addRow(self.bairro_label, self.bairro_input)
        
        # Campo Cidade e Estado (lado a lado)
        cidade_estado_layout = QHBoxLayout()
        
        # Campo Cidade
        self.cidade_label = QLabel("Cidade:")
        self.cidade_label.setStyleSheet(label_style)
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(input_style)
        
        cidade_layout = QFormLayout()
        cidade_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cidade_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cidade_layout.addRow(self.cidade_label, self.cidade_input)
        
        # Campo Estado (novo)
        self.estado_label = QLabel("Estado (UF):")
        self.estado_label.setStyleSheet(label_style)
        self.estado_input = QLineEdit()
        self.estado_input.setStyleSheet(input_style)
        self.estado_input.setMaxLength(2)
        
        estado_layout = QFormLayout()
        estado_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        estado_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        estado_layout.addRow(self.estado_label, self.estado_input)
        
        cidade_estado_layout.addLayout(cidade_layout)
        cidade_estado_layout.addLayout(estado_layout)
        
        # Botão Incluir
        incluir_layout = QHBoxLayout()
        incluir_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                font-weight: bold;
                padding: 12px 40px;
                font-size: 16px;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir.clicked.connect(self.salvar_pessoa)
        
        incluir_layout.addWidget(self.btn_incluir)
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(codigo_telefone_layout)
        main_layout.addLayout(nome_layout)
        main_layout.addLayout(tipo_data_layout)
        main_layout.addLayout(documento_layout)
        main_layout.addWidget(endereco_titulo)
        main_layout.addLayout(cep_layout)
        main_layout.addLayout(rua_layout)
        main_layout.addLayout(bairro_layout)
        main_layout.addLayout(cidade_estado_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(incluir_layout)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
        # Atualizar o tipo de documento com base no tipo de pessoa inicial
        self.atualizar_tipo_documento()
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Atenção", 
                "O módulo 'requests' não está disponível. As funcionalidades de consulta de CEP não funcionarão.")
            # Desabilitar botões de consulta
            self.btn_buscar_cep.setEnabled(False)
        
    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
    def atualizar_tipo_documento(self):
        """Atualiza o label e placeholder do campo de documento conforme o tipo de pessoa"""
        tipo_pessoa = self.tipo_combo.currentText()
        if tipo_pessoa == "Física":
            self.documento_label.setText("CPF:")
            self.documento_input.setPlaceholderText("000.000.000-00")
            # Limpar o campo se já tiver um CNPJ digitado
            texto = self.documento_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) > 11:
                self.documento_input.clear()
        else:
            self.documento_label.setText("CNPJ:")
            self.documento_input.setPlaceholderText("00.000.000/0001-00")
            # Limpar o campo se já tiver um CPF digitado
            texto = self.documento_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) <= 11 and len(''.join(filter(str.isdigit, texto))) > 0:
                self.documento_input.clear()
    
    def formatar_telefone(self, texto):
        """Formata o telefone para (XX) XXXXX-XXXX"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 11 dígitos
        if len(texto_limpo) > 11:
            texto_limpo = texto_limpo[:11]
        
        # Formatar o telefone
        if len(texto_limpo) == 0:
            texto_formatado = ""
        elif len(texto_limpo) <= 2:
            texto_formatado = f"({texto_limpo}"
        elif len(texto_limpo) <= 7:
            texto_formatado = f"({texto_limpo[:2]}) {texto_limpo[2:]}"
        else:
            texto_formatado = f"({texto_limpo[:2]}) {texto_limpo[2:7]}-{texto_limpo[7:]}"
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Bloqueia sinais para evitar recursão
            self.telefone_input.blockSignals(True)
            self.telefone_input.setText(texto_formatado)
            
            # Posiciona o cursor com base apenas no número de dígitos
            if len(texto_limpo) == 0:
                nova_pos = 0
            elif len(texto_limpo) == 1:
                nova_pos = 2  # Após o primeiro dígito no formato "(1"
            elif len(texto_limpo) == 2:
                nova_pos = 3  # Após o DDD no formato "(12"
            elif len(texto_limpo) <= 7:
                nova_pos = 5 + len(texto_limpo) - 2  # Posição na parte central do telefone
            else:
                nova_pos = 11 + len(texto_limpo) - 7  # Posição após o hífen
            
            # Define a nova posição do cursor
            self.telefone_input.setCursorPosition(nova_pos)
            self.telefone_input.blockSignals(False)
    
    def formatar_documento(self, texto):
        """Formata o CNPJ/CPF durante a digitação"""
        # Implementação completa de formatação de documento
        pass
        
    def formatar_cep(self, texto):
        """Formata o CEP durante a digitação"""
        # Implementação completa de formatação de CEP
        pass
        
    def buscar_endereco_por_cep(self):
        """Busca o endereço pelo CEP usando a API ViaCEP"""
        # Esta função depende do módulo requests
        # Implementação completa de busca de CEP
        pass
    
    def salvar_pessoa(self):
        """Salva os dados da pessoa na tabela da tela de cadastro"""
        nome = self.nome_input.text()
        documento = self.documento_input.text() if hasattr(self, 'documento_input') else ""
        tipo_pessoa = self.tipo_combo.currentText()
        codigo = self.codigo_input.text()  # Obtém o código se estiver preenchido
        
        # Validação básica para o nome
        if not nome:
            self.mostrar_mensagem("Campos obrigatórios", "Por favor, informe pelo menos o nome da pessoa.", QMessageBox.Warning)
            return
        
        # Verificar acesso à tabela
        if not self.cadastro_tela or not hasattr(self.cadastro_tela, 'table'):
            self.mostrar_mensagem("Erro", "Não foi possível acessar a tabela de pessoas.", QMessageBox.Critical)
            return
        
        # Verificar se é uma atualização ou novo cadastro
        if self.btn_incluir.text() == "Atualizar" and codigo:
            # Modo de atualização - procurar o item na tabela pelo código
            encontrado = False
            for row in range(self.cadastro_tela.table.rowCount()):
                if self.cadastro_tela.table.item(row, 0).text() == codigo:
                    # Atualizar os dados na tabela
                    self.cadastro_tela.table.setItem(row, 1, QTableWidgetItem(nome))
                    self.cadastro_tela.table.setItem(row, 2, QTableWidgetItem(tipo_pessoa))
                    
                    # Mensagem de sucesso
                    self.mostrar_mensagem("Sucesso", f"Pessoa atualizada com sucesso!\nNome: {nome}\nTipo: {tipo_pessoa}")
                    
                    encontrado = True
                    break
            
            if not encontrado:
                self.mostrar_mensagem("Erro", "Pessoa não encontrada para atualização.", QMessageBox.Warning)
                return
        else:
            # Gerar código para nova pessoa
            ultimo_codigo = 0
            if self.cadastro_tela.table.rowCount() > 0:
                for row in range(self.cadastro_tela.table.rowCount()):
                    codigo = int(self.cadastro_tela.table.item(row, 0).text())
                    if codigo > ultimo_codigo:
                        ultimo_codigo = codigo
            
            novo_codigo = ultimo_codigo + 1
            
            # Adicionar à tabela
            row_position = self.cadastro_tela.table.rowCount()
            self.cadastro_tela.table.insertRow(row_position)
            self.cadastro_tela.table.setItem(row_position, 0, QTableWidgetItem(str(novo_codigo)))
            self.cadastro_tela.table.setItem(row_position, 1, QTableWidgetItem(nome))
            self.cadastro_tela.table.setItem(row_position, 2, QTableWidgetItem(tipo_pessoa))
            
            # Mensagem de sucesso
            self.mostrar_mensagem("Sucesso", f"Pessoa cadastrada com sucesso!\nNome: {nome}\nCódigo: {novo_codigo}")
        
        # Fechar a janela em ambos os casos
        if self.janela_parent:
            self.janela_parent.close()
''')
        except Exception as e:
            print(f"Erro ao criar arquivo formulario_pessoa.py: {str(e)}")
    
    def cadastrar_pessoa(self):
        """Abre o formulário para cadastro de pessoa"""
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'form_window') and self.form_window.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
            self.form_window.activateWindow()
            self.form_window.raise_()
            return
        
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
    
    # Substituir o método alterar_pessoa em cadastro_pessoa.py

    def alterar_pessoa(self):
        """Abre o formulário para alterar os dados da pessoa selecionada"""
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Seleção necessária", 
                                "Por favor, selecione uma pessoa para alterar",
                                QMessageBox.Warning)
            return
        
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'form_window') and self.form_window.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
            self.form_window.activateWindow()
            self.form_window.raise_()
            return
        
        # Buscar dados da pessoa no banco de dados
        try:
            from base.banco import buscar_pessoa_por_id
            
            # Buscar dados completos da pessoa
            pessoa = buscar_pessoa_por_id(int(codigo))
            if not pessoa:
                self.mostrar_mensagem("Erro", f"Pessoa com código {codigo} não encontrada", QMessageBox.Warning)
                return
                
            # Carregar FormularioPessoa
            FormularioPessoa = self.load_formulario_pessoa()
            if FormularioPessoa is None:
                return
            
            # Criar uma nova janela para o formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Alterar Cadastro de Pessoa")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("""
                background-color: #043b57;
                QMessageBox {
                    background-color: #043b57;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QMessageBox QPushButton {
                    background-color: #fffff0;
                    color: black;
                    border: 1px solid #cccccc;
                    min-width: 80px;
                    min-height: 25px;
                    padding: 3px;
                    font-size: 13px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #e6e6e6;
                }
            """)
            
            # Criar e definir o widget do formulário
            form_widget = FormularioPessoa(self, self.form_window)
            self.form_window.setCentralWidget(form_widget)
            
            # Preencher o formulário com os dados da pessoa
            form_widget.preencher_formulario_do_banco(int(codigo))
            
            # Mostrar a janela
            self.form_window.show()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao buscar dados da pessoa: {e}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()  # Imprime o stack trace completo para depuração
    
    def excluir_pessoa(self):
        """Exclui uma pessoa do banco de dados"""
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
        
        try:
            from base.banco import excluir_pessoa
            
            # Excluir a pessoa do banco
            excluir_pessoa(int(codigo))
            
            # Limpar apenas o campo código que existe nesta classe
            self.codigo_input.clear()
            
            # Recarregar a tabela
            self.carregar_pessoas()
            
            self.mostrar_mensagem("Sucesso", f"Pessoa com código {codigo} excluída com sucesso!")
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao excluir pessoa: {e}", QMessageBox.Critical)


# Classe para executar o módulo como script principal
class CadastroPessoaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Pessoa")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #043b57;")
        
        cadastro_widget = CadastroPessoa()
        self.setCentralWidget(cadastro_widget)

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CadastroPessoaWindow()
    window.show()
    sys.exit(app.exec_())