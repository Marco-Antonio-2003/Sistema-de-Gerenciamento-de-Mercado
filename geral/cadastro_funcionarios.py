import sys
import os
# Adicionar o diretório raiz ao caminho de busca
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
                             QFrame, QFormLayout, QStyle, QGridLayout)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

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

class CadastroFuncionario(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Inicializar banco de dados
        self.inicializar_bd()
        self.initUI()

    def inicializar_bd(self):
        """Inicializa a tabela de funcionários no banco de dados"""
        try:
            from base.banco import verificar_tabela_funcionarios
            verificar_tabela_funcionarios()
        except Exception as e:
            self.mostrar_mensagem(
                "Erro", 
                f"Erro ao inicializar tabela de funcionários: {e}", 
                QMessageBox.Critical
            )
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título da tela
        title_label = QLabel("Cadastro de Funcionário")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Área de pesquisa (adicionado seguindo o modelo de pessoas)
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #043b57;")
        search_layout = QVBoxLayout(search_frame)
        
        # Estilos
        label_style = "color: white; font-size: 14px;"
        
        # Grid de pesquisa
        search_grid = QGridLayout()
        search_grid.setColumnStretch(1, 1)  # Coluna do campo de texto se expande
        search_grid.setColumnStretch(3, 1)  # Coluna do campo de texto se expande
        
        # Campo de pesquisa por código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet(label_style)
        self.codigo_search = ComboBoxEditavel()
        self.codigo_search.setPlaceholderText("Digite o código")
        search_grid.addWidget(codigo_label, 0, 0)
        search_grid.addWidget(self.codigo_search, 0, 1)
        
        # Campo de pesquisa por nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet(label_style)
        self.nome_search = ComboBoxEditavel()
        self.nome_search.setPlaceholderText("Digite o nome do funcionário")
        search_grid.addWidget(nome_label, 0, 2)
        search_grid.addWidget(self.nome_search, 0, 3)
        
        # Campo de pesquisa por telefone
        telefone_label = QLabel("Telefone:")
        telefone_label.setStyleSheet(label_style)
        self.telefone_search = ComboBoxEditavel()
        self.telefone_search.setPlaceholderText("Digite o telefone")
        search_grid.addWidget(telefone_label, 1, 0)
        search_grid.addWidget(self.telefone_search, 1, 1)
        
        # Campo de pesquisa por tipo de vendedor
        tipo_label = QLabel("Tipo de Vendedor:")
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
        self.tipo_search.addItems(["Todos", "Interno", "Externo", "Representante"])
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
        self.btn_cadastrar.clicked.connect(self.abrir_formulario_funcionario)
        
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
        self.btn_alterar.clicked.connect(self.alterar_funcionario)
        
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
        self.btn_excluir.clicked.connect(self.excluir_funcionario)
        
        # Adicionar à direita
        botoes_direita = QHBoxLayout()
        botoes_direita.addWidget(self.btn_cadastrar)
        botoes_direita.addWidget(self.btn_alterar)
        botoes_direita.addWidget(self.btn_excluir)
        
        botoes_layout.addLayout(codigo_layout)
        botoes_layout.addLayout(botoes_direita)
        
        main_layout.addLayout(botoes_layout)
        
        # Tabela de funcionários
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Adicionado coluna para telefone
        self.table.setHorizontalHeaderLabels(["Código", "Nome", "Tipo de Vendedor", "Telefone"])
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
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table.itemClicked.connect(self.selecionar_funcionario)

        self.table.itemDoubleClicked.connect(self.abrir_alteracao_por_duplo_clique)
        
        main_layout.addWidget(self.table, 1)  # Dar maior prioridade de espaço para a tabela
        
        # Carregar dados do banco de dados
        self.carregar_funcionarios()
        
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")
    
    def abrir_alteracao_por_duplo_clique(self, item):
        """
        Abre o formulário de alteração ao dar um duplo clique em uma linha da tabela.
        """
        # Pega a linha do item que recebeu o duplo clique
        row = item.row()
        
        # Pega o código do funcionário da primeira coluna (índice 0)
        codigo_do_funcionario = self.table.item(row, 0).text()
        
        # Preenche o campo de texto 'codigo_input', que a sua função 'alterar_funcionario' já utiliza
        self.codigo_input.setText(codigo_do_funcionario)
        
        # Simplesmente chama a função de alterar que já existe
        self.alterar_funcionario()

    def formatar_telefone(self, texto):
        """Formata o telefone para (XX) XXXXX-XXXX"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 11 dígitos
        if len(texto_limpo) > 11:
            texto_limpo = texto_limpo[:11]
        
        # Formatar telefone: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        if len(texto_limpo) <= 2:
            texto_formatado = '(' + texto_limpo
        elif len(texto_limpo) <= 6:
            texto_formatado = '(' + texto_limpo[:2] + ') ' + texto_limpo[2:]
        elif len(texto_limpo) <= 10:
            texto_formatado = '(' + texto_limpo[:2] + ') ' + texto_limpo[2:6] + '-' + texto_limpo[6:]
        else:
            texto_formatado = '(' + texto_limpo[:2] + ') ' + texto_limpo[2:7] + '-' + texto_limpo[7:]
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            self.telefone_input.blockSignals(True)
            self.telefone_input.setText(texto_formatado)
            
            # Posicionar o cursor no final
            self.telefone_input.setCursorPosition(len(texto_formatado))
            self.telefone_input.blockSignals(False)
    
    def selecionar_funcionario(self, item):
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
    
    # Métodos de pesquisa e limpeza de filtros (adicionados seguindo o modelo de pessoas)
    def pesquisar(self):
        """Pesquisa funcionários com base nos filtros selecionados"""
        codigo = self.codigo_search.currentText().strip()
        nome = self.nome_search.currentText().strip()
        telefone = self.telefone_search.currentText().strip()
        tipo = self.tipo_search.currentText()
        
        try:
            # Limpar tabela para os novos resultados
            self.table.setRowCount(0)
            
            # Construir consulta SQL base
            query = """
            SELECT ID, NOME, TIPO_VENDEDOR, TELEFONE
            FROM FUNCIONARIOS
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
                
            if telefone:
                # Remover caracteres não numéricos para busca
                telefone_limpo = ''.join(filter(str.isdigit, telefone))
                if telefone_limpo:
                    query += " AND TELEFONE LIKE ?"
                    params.append(f"%{telefone_limpo}%")
            
            # Filtrar pelo tipo de vendedor
            if tipo != "Todos":
                query += " AND TIPO_VENDEDOR = ?"
                params.append(tipo)
            
            # Adicionar ordenação
            query += " ORDER BY ID"
            
            # Executar a consulta
            from base.banco import execute_query
            funcionarios = execute_query(query, tuple(params) if params else None)
            
            # Verificar se encontrou resultados
            if funcionarios and len(funcionarios) > 0:
                # Preencher a tabela com os resultados
                self.table.setRowCount(len(funcionarios))
                
                for row, (id_funcionario, nome, tipo_vendedor, telefone) in enumerate(funcionarios):
                    self.table.setItem(row, 0, QTableWidgetItem(str(id_funcionario)))
                    self.table.setItem(row, 1, QTableWidgetItem(nome))
                    self.table.setItem(row, 2, QTableWidgetItem(tipo_vendedor))
                    
                    # Adicionar telefone se disponível
                    if telefone:
                        self.table.setItem(row, 3, QTableWidgetItem(telefone))
                    else:
                        self.table.setItem(row, 3, QTableWidgetItem(""))
            else:
                # Mensagem quando nenhum funcionário corresponde aos filtros
                self.mostrar_mensagem("Aviso", "Nenhum funcionário encontrado com os filtros selecionados.")
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao pesquisar funcionários: {str(e)}", QMessageBox.Critical)

    def limpar_filtros(self):
        """Limpa todos os campos de pesquisa e carrega todos os funcionários novamente"""
        self.codigo_search.setCurrentIndex(-1)
        self.codigo_search.clearEditText()
        
        self.nome_search.setCurrentIndex(-1)
        self.nome_search.clearEditText()
        
        self.telefone_search.setCurrentIndex(-1)
        self.telefone_search.clearEditText()
        
        self.tipo_search.setCurrentIndex(0)  # "Todos"
        
        # Recarregar todos os funcionários
        self.carregar_funcionarios()
        
    def excluir_funcionario(self):
        """Exclui um funcionário do banco de dados"""
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Seleção necessária", 
                                "Por favor, selecione um funcionário para excluir", 
                                QMessageBox.Warning)
            return
            
        # Confirmar exclusão
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar exclusão")
        msg_box.setText(f"Deseja realmente excluir o funcionário de código {codigo}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
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
        resposta = msg_box.exec_()
        
        if resposta == QMessageBox.No:
            return
        
        try:
            # Busca a linha pelo código
            encontrado = False
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).text() == codigo:
                    nome = self.table.item(row, 1).text()
                    self.table.removeRow(row)
                    
                    # Excluir do banco de dados
                    try:
                        from base.banco import excluir_funcionario
                        excluir_funcionario(int(codigo))
                    except Exception as e:
                        print(f"Aviso: Não foi possível excluir do banco de dados: {e}")
                    
                    # Limpar o campo de código
                    self.codigo_input.clear()
                    
                    self.mostrar_mensagem("Sucesso", f"Funcionário {nome} (código: {codigo}) excluído com sucesso!")
                    encontrado = True
                    break
            
            if not encontrado:
                self.mostrar_mensagem("Não encontrado", 
                                    f"Funcionário com código {codigo} não encontrado", 
                                    QMessageBox.Warning)
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao excluir funcionário: {e}", QMessageBox.Critical)

    def carregar_funcionarios(self):
        """Carrega os funcionários do banco de dados na tabela"""
        try:
            from base.banco import listar_funcionarios
            funcionarios = listar_funcionarios()
            
            # Limpar tabela atual
            self.table.setRowCount(0)
            
            # Conjuntos para armazenar valores únicos
            codigos = set()
            nomes = set()
            telefones = set()
            
            # Adicionar funcionários na tabela
            if funcionarios:
                self.table.setRowCount(len(funcionarios))
                
                for row, (id_funcionario, nome, tipo_vendedor, telefone) in enumerate(funcionarios):
                    # Adicionar à tabela
                    self.table.setItem(row, 0, QTableWidgetItem(str(id_funcionario)))
                    self.table.setItem(row, 1, QTableWidgetItem(nome))
                    self.table.setItem(row, 2, QTableWidgetItem(tipo_vendedor))
                    
                    # Adicionar telefone se disponível
                    if telefone:
                        self.table.setItem(row, 3, QTableWidgetItem(telefone))
                    else:
                        self.table.setItem(row, 3, QTableWidgetItem(""))
                    
                    # Adicionar aos conjuntos para os ComboBoxes
                    codigos.add(str(id_funcionario))
                    if nome:
                        nomes.add(nome)
                    if telefone:
                        telefones.add(telefone)
                
                # Preencher os ComboBoxes com valores únicos
                self.codigo_search.clear()
                self.nome_search.clear()
                self.telefone_search.clear()
                
                self.codigo_search.addItems(sorted(codigos))
                self.nome_search.addItems(sorted(nomes))
                self.telefone_search.addItems(sorted(telefones))
                    
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao carregar funcionários: {e}", QMessageBox.Critical)
    
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
    
    def load_formulario_funcionario(self):
        """Carrega dinamicamente o módulo FormularioFuncionario"""
        try:
            # Tente primeiro com importação direta (para ambiente de desenvolvimento)
            try:
                # Importação direta usando o módulo
                from geral.formulario_funcionario import FormularioFuncionario
                print("Importação direta de FormularioFuncionario bem-sucedida")
                return FormularioFuncionario
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_funcionario.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_funcionario.py")
                
                # Se o arquivo não existir, vamos criar um básico
                if not os.path.exists(module_path):
                    self.criar_formulario_funcionario_padrao(module_path)
                
                # Carregar o módulo dinamicamente
                module_name = "formulario_funcionario"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Não foi possível carregar o módulo {module_name}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Retornar a classe FormularioFuncionario
                if hasattr(module, "FormularioFuncionario"):
                    return getattr(module, "FormularioFuncionario")
                else:
                    raise ImportError(f"A classe FormularioFuncionario não foi encontrada no módulo {module_name}")
        except Exception as e:
            print(f"Erro ao carregar FormularioFuncionario: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}", QMessageBox.Critical)
            return None
    
    def criar_formulario_funcionario_padrao(self, filepath):
        """Cria um arquivo formulario_funcionario.py básico se não existir"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''#formulario_funcionario.py
import sys
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

class FormularioFuncionario(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None, dados_funcionario=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela  # Referência para a tela de cadastro
        self.janela_parent = janela_parent  # Referência para a janela que contém este widget
        self.dados_funcionario = dados_funcionario  # Dados do funcionário para edição
        self.initUI()
        
        # Se tiver dados para edição, preencher o formulário
        if self.dados_funcionario:
            self.preencher_formulario()
        
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
        titulo = QLabel("Cadastro de Funcionário")
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
                selection-background-color: #043b57;
                selection-color: white;
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
        self.tipo_combo.addItems(["Física", "Jurídica"])  # Inverter a ordem dos itens
        self.tipo_combo.setCurrentIndex(0)  # Agora aponta para "Física"

        self.tipo_combo.currentIndexChanged.connect(self.atualizar_tipo_documento)
        
        tipo_layout = QFormLayout()
        tipo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tipo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tipo_layout.addRow(self.tipo_label, self.tipo_combo)
        
        # Campo Tipo de Vendedor
        self.tipo_vendedor_label = QLabel("Tipo de Vendedor:")
        self.tipo_vendedor_label.setStyleSheet(label_style)
        self.tipo_vendedor_combo = QComboBox()
        self.tipo_vendedor_combo.setStyleSheet(combo_style)
        self.tipo_vendedor_combo.setFixedWidth(200)
        self.tipo_vendedor_combo.addItems(["Interno", "Externo", "Representante"])
        
        tipo_vendedor_layout = QFormLayout()
        tipo_vendedor_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tipo_vendedor_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tipo_vendedor_layout.addRow(self.tipo_vendedor_label, self.tipo_vendedor_combo)
        
        tipo_data_layout.addLayout(tipo_layout)
        tipo_data_layout.addLayout(tipo_vendedor_layout)
        
        # Campo Data de Cadastro
        self.data_label = QLabel("Data de Cadastro:")
        self.data_label.setStyleSheet(label_style)
        self.data_input = QDateEdit()
        self.data_input.setStyleSheet(date_style)  # Estilo específico para DateEdit
        self.data_input.setFixedWidth(150)  # Largura fixa reduzida
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        
        # Mostrar botão do calendário com texto
        try:
            self.data_input.calendarWidget().setAutoFillBackground(True)
        except:
            pass
        
        data_layout = QFormLayout()
        data_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        data_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        data_layout.addRow(self.data_label, self.data_input)
        
        # Campo CPF
        self.cpf_label = QLabel("CPF:")  # Começa com CPF por padrão
        self.cpf_label.setStyleSheet(label_style)
        self.cpf_input = QLineEdit()
        self.cpf_input.setStyleSheet(input_style)
        self.cpf_input.setFixedWidth(250)  # Largura fixa reduzida
        self.cpf_input.textChanged.connect(self.formatar_cpf)
        self.cpf_input.setPlaceholderText("000.000.000-00")  # Placeholder para CPF
        
        cpf_layout = QFormLayout()
        cpf_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cpf_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cpf_layout.addRow(self.cpf_label, self.cpf_input)
        
        # Campo Sexo (novo campo visto na imagem)
        self.sexo_label = QLabel("Sexo:")
        self.sexo_label.setStyleSheet(label_style)
        self.sexo_combo = QComboBox()
        self.sexo_combo.setStyleSheet(combo_style)
        self.sexo_combo.setFixedWidth(150)
        self.sexo_combo.addItems(["Masculino", "Feminino", "Outro"])
        
        sexo_layout = QFormLayout()
        sexo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sexo_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        sexo_layout.addRow(self.sexo_label, self.sexo_combo)
        
        # Adicionar sexo ao layout do CPF para ficar lado a lado
        sexo_cpf_layout = QHBoxLayout()
        sexo_cpf_layout.addLayout(cpf_layout)
        sexo_cpf_layout.addLayout(sexo_layout)
        
        # Título do Endereço
        endereco_titulo = QLabel("Endereço")
        endereco_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        endereco_titulo.setStyleSheet("color: white; margin-top: 20px;")
        endereco_titulo.setAlignment(Qt.AlignCenter)
        
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
        
        # Campo CEP
        self.cep_label = QLabel("CEP:")
        self.cep_label.setStyleSheet(label_style)
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet(input_style)
        self.cep_input.setFixedWidth(150)
        self.cep_input.textChanged.connect(self.formatar_cep)
        self.cep_input.setPlaceholderText("00000-000")
        
        cep_layout = QFormLayout()
        cep_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cep_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cep_layout.addRow(self.cep_label, self.cep_input)
        
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
        
        # Layout para CEP e botão de busca
        cep_busca_layout = QHBoxLayout()
        cep_busca_layout.addLayout(cep_layout)
        cep_busca_layout.addWidget(self.btn_buscar_cep)
        cep_busca_layout.addStretch()
        
        # Campo Cidade
        self.cidade_label = QLabel("Cidade:")
        self.cidade_label.setStyleSheet(label_style)
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(input_style)
        
        cidade_layout = QFormLayout()
        cidade_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cidade_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cidade_layout.addRow(self.cidade_label, self.cidade_input)
        
        # Botão Salvar (renomeado de "Incluir" para "Salvar" quando em modo de edição)
        botao_salvar_texto = "Salvar" if self.dados_funcionario else "Incluir"
        
        incluir_layout = QHBoxLayout()
        incluir_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_incluir = QPushButton(botao_salvar_texto)
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
        self.btn_incluir.clicked.connect(self.salvar_funcionario)
        
        incluir_layout.addWidget(self.btn_incluir)
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(codigo_telefone_layout)
        main_layout.addLayout(nome_layout)
        main_layout.addLayout(tipo_data_layout)
        main_layout.addLayout(data_layout)
        main_layout.addLayout(sexo_cpf_layout)
        main_layout.addWidget(endereco_titulo)
        main_layout.addLayout(rua_layout)
        main_layout.addLayout(bairro_layout)
        main_layout.addLayout(cep_busca_layout)
        main_layout.addLayout(cidade_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(incluir_layout)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Atenção", 
                "O módulo 'requests' não está disponível. As funcionalidades de consulta de CEP não funcionarão.")
            # Desabilitar botões de consulta
            self.btn_buscar_cep.setEnabled(False)
                        
        self.atualizar_tipo_documento()
    
    def preencher_formulario(self):
        """Preenche o formulário com os dados do funcionário para edição"""
        if not self.dados_funcionario:
            return
            
        # Preencher dados do funcionário
        self.codigo_input.setText(self.dados_funcionario.get('codigo', ''))
        self.nome_input.setText(self.dados_funcionario.get('nome', ''))
        self.telefone_input.setText(self.dados_funcionario.get('telefone', ''))
        
        # Tipo de vendedor
        tipo_vendedor = self.dados_funcionario.get('tipo_vendedor', 'Interno')
        index = 0  # Padrão: Interno
        if tipo_vendedor == "Externo":
            index = 1
        elif tipo_vendedor == "Representante":
            index = 2
        self.tipo_vendedor_combo.setCurrentIndex(index)
        
        # Cidade (se disponível)
        self.cidade_input.setText(self.dados_funcionario.get('cidade', ''))
    
    def preencher_formulario_do_banco(self, codigo):
        """Preenche o formulário com dados do funcionário a partir do banco de dados"""
        try:
            from base.banco import buscar_funcionario_por_id
            funcionario = buscar_funcionario_por_id(codigo)
            
            if funcionario:
                id_funcionario, nome, tipo_vendedor, telefone = funcionario[0]
                
                # Preencher dados básicos
                self.codigo_input.setText(str(id_funcionario))
                self.nome_input.setText(nome)
                self.telefone_input.setText(telefone or "")
                
                # Tipo de vendedor
                index = 0  # Padrão: Interno
                if tipo_vendedor == "Externo":
                    index = 1
                elif tipo_vendedor == "Representante":
                    index = 2
                self.tipo_vendedor_combo.setCurrentIndex(index)
                
                # Alterar texto do botão para "Salvar"
                self.btn_incluir.setText("Salvar")
            else:
                QMessageBox.warning(self, "Aviso", f"Funcionário com código {codigo} não encontrado.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados do funcionário: {str(e)}")
            
    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
    def atualizar_tipo_documento(self):
        """Atualiza o label e placeholder do campo de documento conforme o tipo de pessoa"""
        tipo_pessoa = self.tipo_combo.currentText()
        print("Tipo de Pessoa selecionado:", tipo_pessoa)  # Linha de depuração
        if tipo_pessoa == "Jurídica":
            self.cpf_label.setText("CNPJ:")
            self.cpf_input.setPlaceholderText("00.000.000/0001-00")
            texto = self.cpf_input.text()
            if texto and len(''.join(filter(str.isdigit, texto))) <= 11 and len(''.join(filter(str.isdigit, texto))) > 0:
                self.cpf_input.clear()
        else:
            self.cpf_label.setText("CPF:")
            self.cpf_input.setPlaceholderText("000.000.000-00")
                        
    # Também modifique o método formatar_cpf() para corrigir a verificação:

    def formatar_cpf(self, texto):
        """Formata o CPF ou CNPJ durante a digitação"""
        # Verificar o tipo de documento atual
        tipo_documento = self.cpf_label.text()
        if tipo_documento == "CNPJ:" or tipo_documento == "CNPJ":
            self.formatar_cnpj_texto(texto)
        else:
            self.formatar_cpf_texto(texto)

    # Adicione esta linha no final do método initUI(), antes do bloco de verificação do módulo requests
    self.atualizar_tipo_documento()
    
    def formatar_telefone(self, texto):
        """Formata o telefone para (XX) XXXXX-XXXX"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 11 dígitos
        if len(texto_limpo) > 11:
            texto_limpo = texto_limpo[:11]
        
        # Formatar telefone: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        if len(texto_limpo) <= 2:
            texto_formatado = '(' + texto_limpo
        elif len(texto_limpo) <= 6:
            texto_formatado = '(' + texto_limpo[:2] + ') ' + texto_limpo[2:]
        elif len(texto_limpo) <= 10:
            texto_formatado = '(' + texto_limpo[:2] + ') ' + texto_limpo[2:6] + '-' + texto_limpo[6:]
        else:
            texto_formatado = '(' + texto_limpo[:2] + ') ' + texto_limpo[2:7] + '-' + texto_limpo[7:]
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            self.telefone_input.blockSignals(True)
            self.telefone_input.setText(texto_formatado)
            
            # Posicionar o cursor no final
            self.telefone_input.setCursorPosition(len(texto_formatado))
            self.telefone_input.blockSignals(False)
    
    def formatar_cpf_texto(self, texto):
        """Formata o texto como CPF: 000.000.000-00"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 11 dígitos
        if len(texto_limpo) > 11:
            texto_limpo = texto_limpo[:11]
        
        # Formatar CPF: 000.000.000-00
        if len(texto_limpo) <= 3:
            texto_formatado = texto_limpo
        elif len(texto_limpo) <= 6:
            texto_formatado = texto_limpo[:3] + '.' + texto_limpo[3:]
        elif len(texto_limpo) <= 9:
            texto_formatado = texto_limpo[:3] + '.' + texto_limpo[3:6] + '.' + texto_limpo[6:]
        else:
            texto_formatado = texto_limpo[:3] + '.' + texto_limpo[3:6] + '.' + texto_limpo[6:9] + '-' + texto_limpo[9:]
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            self.cpf_input.blockSignals(True)
            self.cpf_input.setText(texto_formatado)
            
            # Posicionar o cursor no final
            self.cpf_input.setCursorPosition(len(texto_formatado))
            self.cpf_input.blockSignals(False)
    
    def formatar_cnpj_texto(self, texto):
        """Formata o texto como CNPJ: 00.000.000/0001-00"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 14 dígitos
        if len(texto_limpo) > 14:
            texto_limpo = texto_limpo[:14]
        
        # Formatar CNPJ: 00.000.000/0001-00
        if len(texto_limpo) <= 2:
            texto_formatado = texto_limpo
        elif len(texto_limpo) <= 5:
            texto_formatado = texto_limpo[:2] + '.' + texto_limpo[2:]
        elif len(texto_limpo) <= 8:
            texto_formatado = texto_limpo[:2] + '.' + texto_limpo[2:5] + '.' + texto_limpo[5:]
        elif len(texto_limpo) <= 12:
            texto_formatado = texto_limpo[:2] + '.' + texto_limpo[2:5] + '.' + texto_limpo[5:8] + '/' + texto_limpo[8:]
        else:
            texto_formatado = texto_limpo[:2] + '.' + texto_limpo[2:5] + '.' + texto_limpo[5:8] + '/' + texto_limpo[8:12] + '-' + texto_limpo[12:]
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            self.cpf_input.blockSignals(True)
            self.cpf_input.setText(texto_formatado)
            
            # Posicionar o cursor no final
            self.cpf_input.setCursorPosition(len(texto_formatado))
            self.cpf_input.blockSignals(False)
    
    def formatar_cep(self, texto):
        """Formata o CEP durante a digitação e busca endereço quando completo"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 8 dígitos
        if len(texto_limpo) > 8:
            texto_limpo = texto_limpo[:8]
        
        # Formatar CEP: 00000-000
        if len(texto_limpo) <= 5:
            texto_formatado = texto_limpo
        else:
            texto_formatado = texto_limpo[:5] + '-' + texto_limpo[5:]
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            self.cep_input.blockSignals(True)
            self.cep_input.setText(texto_formatado)
            
            # Posicionar o cursor no final
            self.cep_input.setCursorPosition(len(texto_formatado))
            self.cep_input.blockSignals(False)
        
        # Se o CEP estiver completo, buscar o endereço automaticamente
        if len(texto_limpo) == 8 and REQUESTS_AVAILABLE:
            self.buscar_endereco_por_cep()
    
    def buscar_endereco_por_cep(self):
        """Busca o endereço pelo CEP usando a API ViaCEP"""
        # Verificar se o módulo requests está disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Funcionalidade indisponível", 
                               "A consulta de CEP requer o módulo 'requests' que não está disponível.")
            return
            
        # Obter o CEP removendo caracteres não numéricos
        cep = ''.join(filter(str.isdigit, self.cep_input.text()))
        
        # Verificar se o CEP tem 8 dígitos
        # Verificar se o CEP tem 8 dígitos
        if len(cep) != 8:
            QMessageBox.warning(self, "CEP inválido", 
                               "O CEP deve conter 8 dígitos numéricos.")
            return
        
        try:
            # Consultar o CEP na API ViaCEP
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url, timeout=5)
            
            # Verificar se a resposta foi bem-sucedida
            if response.status_code == 200:
                dados = response.json()
                
                # Verificar se o CEP foi encontrado
                if "erro" in dados and dados["erro"]:
                    QMessageBox.warning(self, "CEP não encontrado", 
                                       "O CEP informado não foi encontrado.")
                    return
                
                # Preencher os campos com os dados obtidos
                self.rua_input.setText(dados.get("logradouro", ""))
                self.bairro_input.setText(dados.get("bairro", ""))
                self.cidade_input.setText(dados.get("localidade", ""))
                
                # Exibir mensagem de sucesso
                QMessageBox.information(self, "Sucesso", 
                                      "Endereço encontrado e preenchido com sucesso!")
            else:
                QMessageBox.warning(self, "Erro na consulta", 
                                   f"Erro ao consultar o CEP: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", 
                               f"Erro ao consultar o CEP: {str(e)}")
    
    def validar_cpf(self, cpf):
        """Valida o CPF informado"""
        # Remover caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verificar se o CPF tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verificar se o CPF contém todos os dígitos iguais
        if len(set(cpf)) == 1:
            return False
        
        # Calcular o primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        # Verificar o primeiro dígito verificador
        if dv1 != int(cpf[9]):
            return False
        
        # Calcular o segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        # Verificar o segundo dígito verificador
        return dv2 == int(cpf[10])
    
    def salvar_funcionario(self):
        """Salva os dados do funcionário na tabela da tela de cadastro"""
        # Obter os dados do formulário
        nome = self.nome_input.text()
        telefone = self.telefone_input.text()
        tipo_vendedor = self.tipo_vendedor_combo.currentText()
        cidade = self.cidade_input.text()
        
        # Validação básica para os campos obrigatórios
        if not nome:
            QMessageBox.warning(self, "Campos obrigatórios", 
                               "Por favor, informe o nome do funcionário.")
            self.nome_input.setFocus()
            return
        
        # Validar o CPF se for pessoa física
        if self.tipo_combo.currentText() == "Física":
            cpf = self.cpf_input.text()
            if not cpf or not self.validar_cpf(cpf):
                QMessageBox.warning(self, "CPF inválido", 
                                   "Por favor, informe um CPF válido.")
                self.cpf_input.setFocus()
                return
        
        # Código para salvar na tabela principal
        if self.cadastro_tela and hasattr(self.cadastro_tela, 'table'):
            # Se é uma edição, localiza o item na tabela
            modo_edicao = False
            row_position = -1
            
            if self.codigo_input.text():
                codigo = self.codigo_input.text()
                for row in range(self.cadastro_tela.table.rowCount()):
                    if self.cadastro_tela.table.item(row, 0).text() == codigo:
                        row_position = row
                        modo_edicao = True
                        break
            
            # Se não for edição, adicionar nova linha
            if not modo_edicao:
                # Gerar código
                novo_codigo = 1
                if self.cadastro_tela.table.rowCount() > 0:
                    ultimo_codigo = 0
                    for row in range(self.cadastro_tela.table.rowCount()):
                        codigo_atual = int(self.cadastro_tela.table.item(row, 0).text())
                        if codigo_atual > ultimo_codigo:
                            ultimo_codigo = codigo_atual
                    novo_codigo = ultimo_codigo + 1
                
                row_position = self.cadastro_tela.table.rowCount()
                self.cadastro_tela.table.insertRow(row_position)
                self.cadastro_tela.table.setItem(row_position, 0, QTableWidgetItem(str(novo_codigo)))
            
            # Atualizar ou adicionar dados à tabela
            self.cadastro_tela.table.setItem(row_position, 1, QTableWidgetItem(nome))
            self.cadastro_tela.table.setItem(row_position, 2, QTableWidgetItem(tipo_vendedor))
            
            # Adicionar telefone se a coluna existir
            if self.cadastro_tela.table.columnCount() > 3:
                self.cadastro_tela.table.setItem(row_position, 3, QTableWidgetItem(telefone))
            
            # Mensagem de sucesso
            acao = "alterado" if modo_edicao else "cadastrado"
            codigo_exibir = self.codigo_input.text() if modo_edicao else str(novo_codigo)
            
            QMessageBox.information(self, "Sucesso", 
                                   f"Funcionário {acao} com sucesso!\nNome: {nome}\nCódigo: {codigo_exibir}")
            
            # Fechar a janela
            if self.janela_parent:
                self.janela_parent.close()
        else:
            # Caso não tenha referência à tabela principal
            QMessageBox.information(self, "Teste", 
                                   "Funcionário seria cadastrado com os seguintes dados:\n" +
                                   f"Nome: {nome}\n" +
                                   f"Telefone: {telefone}\n" +
                                   f"Tipo de pessoa: {self.tipo_combo.currentText()}\n" +
                                   f"Tipo de vendedor: {tipo_vendedor}\n" +
                                   f"Data de cadastro: {self.data_input.date().toString('dd/MM/yyyy')}")
''')
        except Exception as e:
            print(f"Erro ao criar arquivo formulario_funcionario.py: {str(e)}")
    
    def abrir_formulario_funcionario(self):
        """Abre o formulário para cadastro de funcionário"""
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'janela_formulario') and self.janela_formulario.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.janela_formulario.setWindowState(self.janela_formulario.windowState() & ~Qt.WindowMinimized)
            self.janela_formulario.activateWindow()
            self.janela_formulario.raise_()
            return
        
        # Carregar dinamicamente a classe FormularioFuncionario
        FormularioFuncionario = self.load_formulario_funcionario()
        if not FormularioFuncionario:
            return
            
        # Criar uma nova janela para o formulário
        self.janela_formulario = QMainWindow()
        self.janela_formulario.setWindowTitle("Formulário de Cadastro de Funcionário")
        self.janela_formulario.setGeometry(150, 150, 800, 600)
        self.janela_formulario.setStyleSheet("background-color: #043b57;")
        
        # Criar o widget do formulário e passá-lo como widget central da janela
        formulario = FormularioFuncionario(cadastro_tela=self, janela_parent=self.janela_formulario)
        self.janela_formulario.setCentralWidget(formulario)
        
        # Limpar o campo de código para garantir um novo cadastro
        self.codigo_input.clear()
        
        # Exibir a janela
        self.janela_formulario.show()
    
    def alterar_funcionario(self):
        """Abre o formulário para alterar os dados do funcionário selecionado"""
        codigo = self.codigo_input.text()
        
        if not codigo:
            self.mostrar_mensagem("Seleção necessária", 
                                "Por favor, selecione um funcionário para alterar",
                                QMessageBox.Warning)
            return
        
        # Verificar se já existe uma janela de formulário aberta
        if hasattr(self, 'janela_formulario') and self.janela_formulario.isVisible():
            # Se existir, apenas ativá-la em vez de criar uma nova
            self.janela_formulario.setWindowState(self.janela_formulario.windowState() & ~Qt.WindowMinimized)
            self.janela_formulario.activateWindow()
            self.janela_formulario.raise_()
            return
        
        # Buscar dados do funcionário no banco de dados ou da tabela
        try:
            # Obter dados da linha selecionada na tabela
            row = -1
            for i in range(self.table.rowCount()):
                if self.table.item(i, 0).text() == codigo:
                    row = i
                    break
                    
            if row == -1:
                self.mostrar_mensagem("Erro", f"Funcionário com código {codigo} não encontrado", QMessageBox.Warning)
                return
                
            # Obter dados da linha
            nome = self.table.item(row, 1).text()
            tipo_vendedor = self.table.item(row, 2).text()
            telefone = self.table.item(row, 3).text() if self.table.columnCount() > 3 else ""
            
            # Preparar dados para o formulário
            dados_funcionario = {
                'codigo': codigo,
                'nome': nome,
                'tipo_vendedor': tipo_vendedor,
                'telefone': telefone
            }
            
            # Carregar FormularioFuncionario
            FormularioFuncionario = self.load_formulario_funcionario()
            if FormularioFuncionario is None:
                return
            
            # Criar uma nova janela para o formulário
            self.janela_formulario = QMainWindow()
            self.janela_formulario.setWindowTitle("Alterar Cadastro de Funcionário")
            self.janela_formulario.setGeometry(150, 150, 800, 600)
            self.janela_formulario.setStyleSheet("background-color: #043b57;")
            
            # Criar o widget do formulário com os dados do funcionário
            formulario = FormularioFuncionario(
                cadastro_tela=self, 
                janela_parent=self.janela_formulario,
                dados_funcionario=dados_funcionario
            )
            self.janela_formulario.setCentralWidget(formulario)
            
            # Mostrar a janela
            self.janela_formulario.show()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Falha ao buscar dados do funcionário: {e}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()  # Imprime o stack trace completo para depuração


# Classe para executar o módulo como script principal
class CadastroFuncionariosWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Cadastro de Funcionários")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: #043b57;")
        
        cadastro_widget = CadastroFuncionario()
        self.setCentralWidget(cadastro_widget)

# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CadastroFuncionariosWindow()
    window.show()
    sys.exit(app.exec_())