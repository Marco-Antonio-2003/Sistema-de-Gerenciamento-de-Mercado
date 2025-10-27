#produtos.py
import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QMessageBox, QStyle, QToolButton, QGridLayout)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

# Importar o módulo banco.py da pasta base
try:
    from base.banco import (verificar_tabela_produtos, listar_produtos, 
                           buscar_produto_por_id, buscar_produto_por_codigo,
                           criar_produto, atualizar_produto, excluir_produto,
                           buscar_produtos_por_filtro)
except ImportError as e:
    print(f"Erro ao importar funções do banco: {e}")
    # Mostrar mensagem de erro
    QMessageBox.critical(None, "Erro de importação", 
                        f"Não foi possível importar o módulo banco.py da pasta base: {e}")

# Funções para gerenciamento de estoque
def atualizar_estoque_apos_venda(codigo_produto, quantidade_vendida):
    """
    Atualiza o estoque de um produto após uma venda
    
    Args:
        codigo_produto (str): Código do produto vendido
        quantidade_vendida (float): Quantidade vendida
        
    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário
        dict: Informações sobre o estoque após a atualização, incluindo avisos se necessário
    """
    try:
        from base.banco import buscar_produto_por_codigo, execute_query
        
        # Buscar o produto pelo código
        produto = buscar_produto_por_codigo(codigo_produto)
        
        if not produto:
            raise Exception(f"Produto com código {codigo_produto} não encontrado")
        
        # Obter o estoque atual e calcular o novo estoque
        id_produto = produto[0]
        estoque_atual = produto[8] or 0  # Índice 8 é QUANTIDADE_ESTOQUE
        
        if estoque_atual < quantidade_vendida:
            raise Exception(f"Estoque insuficiente. Disponível: {estoque_atual}, Solicitado: {quantidade_vendida}")
        
        novo_estoque = estoque_atual - quantidade_vendida
        
        # Atualizar o estoque do produto
        query = """
        UPDATE PRODUTOS
        SET QUANTIDADE_ESTOQUE = ?
        WHERE ID = ?
        """
        
        execute_query(query, (novo_estoque, id_produto))
        
        # Verificar se o estoque está baixo
        resultado = {
            "sucesso": True,
            "produto": produto[2],  # Nome do produto
            "estoque_anterior": estoque_atual,
            "estoque_atual": novo_estoque,
            "estoque_baixo": False,
            "mensagem": "Estoque atualizado com sucesso."
        }
        
        # Definir limites para estoque baixo (pode ajustar conforme necessário)
        limite_estoque_baixo = 5  # Exemplo: avisar quando estoque for menor que 5
        
        if novo_estoque <= limite_estoque_baixo:
            resultado["estoque_baixo"] = True
            resultado["mensagem"] = f"ATENÇÃO: Estoque baixo para o produto {produto[2]}. Restam apenas {novo_estoque} unidades. É necessário repor!"
            
            # Registrar o alerta de estoque baixo
            registrar_alerta_estoque_baixo(produto[0], produto[2], novo_estoque)
        
        return resultado
    
    except Exception as e:
        print(f"Erro ao atualizar estoque: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao atualizar estoque: {str(e)}"
        }

def registrar_alerta_estoque_baixo(id_produto, nome_produto, estoque_atual):
    """
    Registra um alerta de estoque baixo (pode ser adaptado para
    salvar em uma tabela de alertas, enviar e-mail, etc.)
    
    Args:
        id_produto (int): ID do produto
        nome_produto (str): Nome do produto
        estoque_atual (float): Quantidade atual em estoque
    """
    # Esta é uma implementação simples que apenas imprime o alerta no console
    # Você pode expandir para salvar em um log ou tabela, enviar e-mail, etc.
    print(f"[ALERTA] Estoque baixo: Produto {nome_produto} (ID: {id_produto}) - Restam apenas {estoque_atual} unidades.")

def verificar_produtos_estoque_baixo(limite=5):
    """
    Verifica todos os produtos com estoque baixo
    
    Args:
        limite (int): Limite para considerar estoque baixo
        
    Returns:
        list: Lista de produtos com estoque baixo
    """
    try:
        from base.banco import execute_query
        
        query = """
        SELECT ID, CODIGO, NOME, QUANTIDADE_ESTOQUE
        FROM PRODUTOS
        WHERE QUANTIDADE_ESTOQUE <= ?
        ORDER BY QUANTIDADE_ESTOQUE
        """
        
        result = execute_query(query, (limite,))
        
        # Formatar os resultados
        produtos_estoque_baixo = []
        for produto in result:
            produtos_estoque_baixo.append({
                "id": produto[0],
                "codigo": produto[1],
                "nome": produto[2],
                "estoque": produto[3]
            })
        
        return produtos_estoque_baixo
        
    except Exception as e:
        print(f"Erro ao verificar produtos com estoque baixo: {e}")
        return []

def registrar_venda_produto(data, codigo_produto, produto, categoria, quantidade, 
                           valor_unitario, valor_total, cliente=None, vendedor=None):
    """
    Registra uma venda de produto e atualiza o estoque
    
    Args:
        data (str): Data da venda no formato YYYY-MM-DD
        codigo_produto (str): Código do produto
        produto (str): Nome do produto
        categoria (str): Categoria/grupo do produto
        quantidade (float): Quantidade vendida
        valor_unitario (float): Valor unitário
        valor_total (float): Valor total
        cliente (str, optional): Nome do cliente
        vendedor (str, optional): Nome do vendedor
        
    Returns:
        dict: Resultado da operação incluindo ID da venda e informações de estoque
    """
    try:
        from base.banco import execute_query
        
        # Inserir a venda
        query = """
        INSERT INTO VENDAS_PRODUTOS (
            DATA, CODIGO_PRODUTO, PRODUTO, CATEGORIA, QUANTIDADE,
            VALOR_UNITARIO, VALOR_TOTAL, CLIENTE, VENDEDOR
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        execute_query(query, (
            data, codigo_produto, produto, categoria, quantidade,
            valor_unitario, valor_total, cliente, vendedor
        ))
        
        # Obter o ID da venda recém-registrada
        query_id = "SELECT MAX(ID) FROM VENDAS_PRODUTOS"
        result = execute_query(query_id)
        
        id_venda = None
        if result and len(result) > 0 and result[0][0]:
            id_venda = result[0][0]
        
        # Atualizar o estoque do produto
        resultado_estoque = atualizar_estoque_apos_venda(codigo_produto, quantidade)
        
        # Retornar um resultado completo
        return {
            "id_venda": id_venda,
            "sucesso": resultado_estoque["sucesso"],
            "mensagem": resultado_estoque["mensagem"],
            "estoque_baixo": resultado_estoque.get("estoque_baixo", False)
        }
        
    except Exception as e:
        print(f"Erro ao registrar venda: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao registrar venda: {str(e)}"
        }

# Classe LeitorCodigoBarras - para detectar automaticamente leituras de código de barras
class LeitorCodigoBarras(QLineEdit):
    """
    Classe personalizada para campo de código de barras com suporte a leitores de código de barras.
    Detecta automaticamente quando um código é escaneado por um leitor físico.
    """
    codigo_lido = pyqtSignal(str)  # Sinal emitido quando um código de barras é lido com sucesso
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Tempo limite para considerar uma sequência como leitura de código de barras
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.finalizar_leitura)
        
        # Buffer para acumular caracteres durante a leitura
        self.buffer = ""
        
        # Tempo máximo entre caracteres para considerar como parte do mesmo código (ms)
        self.tempo_entre_caracteres = 50
        
        # Indicador se estamos em modo de leitura
        self.lendo_codigo = False
        
        # Conectar ao evento de texto alterado para detectar entrada
        self.textChanged.connect(self.on_text_changed)
        
        # Estilo padrão para o campo
        self.estilo_normal = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 25px;
                max-height: 25px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        self.setStyleSheet(self.estilo_normal)
        
        # Definir placeholder text
        self.setPlaceholderText("Digite ou escaneie o código de barras")
    
    def on_text_changed(self, texto):
        """Chamado quando o texto do campo é alterado"""
        # Se a mudança foi muito rápida, provavelmente é de um scanner
        if not self.lendo_codigo:
            self.lendo_codigo = True
            self.buffer = texto
        else:
            self.buffer = texto
        
        # Reiniciar o timer - se nenhum caractere for recebido dentro do tempo limite,
        # consideramos a leitura completa
        self.timer.start(self.tempo_entre_caracteres)
    
    def keyPressEvent(self, event):
        """Sobrescreve o método de tecla pressionada para detectar Enter/Return"""
        # Muitos leitores de código de barras terminam a leitura com Enter
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.finalizar_leitura()
            # Não propagar o Enter para evitar que o formulário seja submetido
            event.accept()
            return
        
        # Para todas as outras teclas, comportamento normal
        super().keyPressEvent(event)
    
    def finalizar_leitura(self):
        """Finaliza a leitura do código de barras e emite o sinal"""
        if self.lendo_codigo and self.buffer:
            # Emitir o sinal com o código lido
            self.codigo_lido.emit(self.buffer)
            
            # Reseta o estado de leitura
            self.lendo_codigo = False
            
            # Deixar o campo com fundo verde por um momento para indicar sucesso
            self.setStyleSheet("""
                QLineEdit {
                    background-color: #c8f7c8;
                    border: 1px solid #00cc00;
                    padding: 5px;
                    font-size: 14px;
                    border-radius: 4px;
                    color: black;
                    min-height: 25px;
                    max-height: 25px;
                }
            """)
            
            # Voltar ao estilo normal após 1 segundo
            QTimer.singleShot(1000, self.restaurar_estilo)
    
    def restaurar_estilo(self):
        """Restaura o estilo normal do campo após a leitura"""
        self.setStyleSheet(self.estilo_normal)
    
    def focusInEvent(self, event):
        """Sobrescreve o evento de foco para visual feedback"""
        super().focusInEvent(event)
        # Destacar quando o campo recebe foco para indicar que está pronto para leitura
        self.setStyleSheet("""
            QLineEdit {
                background-color: #f0f8ff;  /* Azul bem claro */
                border: 2px solid #0078d7;
                padding: 5px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 25px;
                max-height: 25px;
            }
        """)
        
    def focusOutEvent(self, event):
        """Sobrescreve o evento de perda de foco"""
        super().focusOutEvent(event)
        # Restaurar estilo normal quando o campo perde o foco
        self.setStyleSheet(self.estilo_normal)


class Produtos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Flag para controlar quando os sinais de edição são bloqueados
        self._sinais_bloqueados = False
        
        # Verificar se a tabela de produtos existe no banco
        try:
            verificar_tabela_produtos()
        except Exception as e:
            print(f"Erro ao verificar tabela de produtos: {str(e)}")
        
        self.initUI()
        
        # Verificar estoque baixo ao iniciar
        self.verificar_estoque_inicial()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#043b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
        
    def initUI(self):
        # Layout principal com menos margem vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 15)  # Reduzir margem superior
        main_layout.setSpacing(8)  # Reduzir espaçamento entre elementos
        
        # Fundo para todo o aplicativo
        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())
        
        # Layout para o título centralizado (sem botão voltar)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remover margens extras
        
        # Título centralizado com menos altura
        titulo = QLabel("Produtos")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Estilos compactos para os widgets
        combobox_style = """
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
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
            }
        """
        
        lineedit_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 25px;
                max-height: 25px;
            }
        """
        
        # Criar layout de grid para campos de pesquisa (mais compacto)
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)  # Espaçamento vertical menor
        grid_layout.setHorizontalSpacing(10)
        
        # Estilo para labels - garantindo que sejam brancos
        label_style = "color: white; font-size: 13px;"
        
        # Linha 0: Código e Nome
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet(label_style)
        grid_layout.addWidget(codigo_label, 0, 0)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setPlaceholderText("Digite o código")
        grid_layout.addWidget(self.codigo_input, 0, 1)
        
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet(label_style)
        grid_layout.addWidget(nome_label, 0, 2)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        self.nome_input.setPlaceholderText("Digite o nome do produto")
        grid_layout.addWidget(self.nome_input, 0, 3)
        
        # Linha 1: Código de Barras, Grupo e Marca
        barras_label = QLabel("Cód. Barras:")
        barras_label.setStyleSheet(label_style)
        grid_layout.addWidget(barras_label, 1, 0)
        
        # Layout para código de barras com botão de scan
        barras_layout = QHBoxLayout()
        barras_layout.setSpacing(5)
        barras_layout.setContentsMargins(0, 0, 0, 0)
        
        self.barras_input = LeitorCodigoBarras()
        barras_layout.addWidget(self.barras_input)
        
        self.btn_scan = QToolButton()
        if os.path.exists("ico-img/barcode.svg"):
            self.btn_scan.setIcon(QIcon("ico-img/barcode.svg"))
        else:
            self.btn_scan.setText("Scan")
            
        self.btn_scan.setStyleSheet("""
            QToolButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 3px;
                font-size: 12px;
                border-radius: 3px;
                min-width: 25px;
                max-width: 25px;
                min-height: 25px;
                max-height: 25px;
            }
        """)
        self.btn_scan.setToolTip("Escanear código de barras")
        barras_layout.addWidget(self.btn_scan)
        
        grid_layout.addLayout(barras_layout, 1, 1)
        
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet(label_style)
        grid_layout.addWidget(grupo_label, 1, 2)
        
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(combobox_style)
        self.grupo_combo.addItem("Todos os grupos")
        self.grupo_combo.addItem("Alimentos")
        self.grupo_combo.addItem("Bebidas")
        self.grupo_combo.addItem("Limpeza")
        self.grupo_combo.addItem("Higiene")
        self.grupo_combo.addItem("Hortifruti")
        self.grupo_combo.addItem("Eletrônicos")
        self.grupo_combo.addItem("Vestuário")
        self.grupo_combo.addItem("Outros")
        grid_layout.addWidget(self.grupo_combo, 1, 3)
        
        # Linha 2: Marca e botões de ação
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet(label_style)
        grid_layout.addWidget(marca_label, 2, 0)
        
        self.marca_combo = QComboBox()
        self.marca_combo.setStyleSheet(combobox_style)
        self.marca_combo.addItem("Todas as marcas")
        self.marca_combo.addItem("Nestlé")
        self.marca_combo.addItem("Unilever")
        self.marca_combo.addItem("Procter & Gamble")
        self.marca_combo.addItem("Coca-Cola")
        self.marca_combo.addItem("Camil")
        self.marca_combo.addItem("Dell")
        self.marca_combo.addItem("Samsung")
        self.marca_combo.addItem("Lacoste")
        self.marca_combo.addItem("OMO")
        grid_layout.addWidget(self.marca_combo, 2, 1)
        
        # Botões de pesquisa na mesma linha
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(8)
        
        # Botão de Pesquisar (mais compacto)
        self.btn_pesquisar = QPushButton("Pesquisar")
        self.btn_pesquisar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 5px 15px;
                font-size: 13px;
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
        botoes_layout.addWidget(self.btn_pesquisar)
        
        # Botão Limpar Filtros
        self.btn_limpar = QPushButton("Limpar Filtros")
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #717171;
                color: white;
                border: none;
                padding: 5px 15px;
                font-size: 13px;
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
        botoes_layout.addWidget(self.btn_limpar)
        
        grid_layout.addLayout(botoes_layout, 2, 2, 1, 2)  # Span sobre 2 colunas
        
        # Adicionar mensagem informativa abaixo do código de barras (muito compacta)
        self.scan_info_label = QLabel("Escaneie para pesquisar")
        self.scan_info_label.setStyleSheet("color: #90CAF9; font-size: 11px; font-style: italic; padding: 0; margin: 0;")
        grid_layout.addWidget(self.scan_info_label, 3, 1)
        
        # Adicionar o grid_layout ao layout principal
        main_layout.addLayout(grid_layout)
        
        # Linha horizontal compacta que separa a área de pesquisa da tabela
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
        
        # Layout para botões de ação (Alterar, Excluir, Cadastrar) mais compacto
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(8)
        acoes_layout.setContentsMargins(0, 0, 0, 0)
        
        # Estilo para os botões de ação (mais compactos)
        btn_action_style = """
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                padding: 5px 10px;
                font-size: 13px;
                border-radius: 4px;
                text-align: center;
                min-height: 25px;
                max-height: 25px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """
        
        # Botão Alterar
        self.btn_alterar = QPushButton("Alterar")
        try:
            self.btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        self.btn_alterar.setStyleSheet(btn_action_style)
        acoes_layout.addWidget(self.btn_alterar)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        try:
            self.btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        self.btn_excluir.setStyleSheet(btn_action_style)
        acoes_layout.addWidget(self.btn_excluir)
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        try:
            self.btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        self.btn_cadastrar.setStyleSheet(btn_action_style)
        acoes_layout.addWidget(self.btn_cadastrar)
        
        # Botão para verificar produtos com estoque baixo
        self.btn_estoque_baixo = QPushButton("Verificar Estoque Baixo")
        try:
            self.btn_estoque_baixo.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
        except:
            pass
        self.btn_estoque_baixo.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: 1px solid #E69500;
                padding: 5px 10px;
                font-size: 13px;
                border-radius: 4px;
                text-align: center;
                min-height: 25px;
                max-height: 25px;
            }
            QPushButton:hover {
                background-color: #E69500;
            }
        """)
        acoes_layout.addWidget(self.btn_estoque_baixo)
        
        # Adicionar stretch para empurrar botões para a esquerda
        acoes_layout.addStretch(1)
        
        main_layout.addLayout(acoes_layout)
        
        # Tabela de Produtos
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                color: black;
            }
            QHeaderView::section {
                background-color: #fffff0;
                color: black;
                padding: 3px;
                border: 1px solid #cccccc;
                font-weight: bold;
                font-size: 13px;
                height: 25px;
            }
            QTableWidget::item {
                padding: 2px;
                font-size: 13px;
                height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Configurar tabela
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Marca", "Grupo", "Preço de Venda", "Quant. Estoque"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        
        # Importante: Desativar edição direta na tabela
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Definir altura menor para linhas da tabela
        self.tabela.verticalHeader().setDefaultSectionSize(25)
        
        # Carregar dados do banco
        self.carregar_produtos()
        
        # Dar mais espaço para a tabela (stretch factor 1)
        main_layout.addWidget(self.tabela, 1)
        
        # Conectar os sinais após criar todos os widgets
        self.conectar_sinais()
    
    def conectar_sinais(self):
        """
        Conecta apenas os sinais necessários - nenhum sinal de campo deve disparar pesquisa
        """
        # Botão de pesquisa - pesquisa apenas quando clicado explicitamente
        self.btn_pesquisar.clicked.connect(self.pesquisar)
        
        # Botões de ação
        self.btn_limpar.clicked.connect(self.limpar_filtros)
        self.btn_alterar.clicked.connect(self.alterar)
        self.btn_excluir.clicked.connect(self.excluir)
        self.btn_cadastrar.clicked.connect(self.cadastrar)
        self.btn_estoque_baixo.clicked.connect(self.verificar_estoque_baixo)
        
        # Leitor de código de barras - única exceção, este deve disparar pesquisa automática
        self.barras_input.codigo_lido.connect(self.pesquisar_por_codigo_barras)
        
        # Botão scan para o código de barras
        self.btn_scan.clicked.connect(self.focar_scanner)
        
        # Conectar a tabela a selecionar_item, que agora não dispara pesquisa
        self.tabela.itemSelectionChanged.connect(self.selecionar_item)
        
        # Configurar duplo clique na tabela para abrir o formulário de alteração
        self.tabela.doubleClicked.connect(self.alterar)
    
    def verificar_estoque_inicial(self):
        """Verifica produtos com estoque baixo ao iniciar o sistema"""
        produtos_baixo_estoque = verificar_produtos_estoque_baixo(limite=5)
        
        if produtos_baixo_estoque:
            mensagem = "Os seguintes produtos estão com estoque baixo:\n\n"
            for p in produtos_baixo_estoque:
                mensagem += f"• {p['nome']} (Código: {p['codigo']}) - Estoque: {p['estoque']} unidades\n"
            mensagem += "\nÉ necessário repor o estoque destes produtos!"
            
            self.mostrar_alerta("Alerta de Estoque Baixo", mensagem, QMessageBox.Warning)
    
    def verificar_estoque_baixo(self):
        """Verifica produtos com estoque baixo sob demanda"""
        produtos_baixo_estoque = verificar_produtos_estoque_baixo(limite=5)
        
        if produtos_baixo_estoque:
            mensagem = "Os seguintes produtos estão com estoque baixo:\n\n"
            for p in produtos_baixo_estoque:
                mensagem += f"• {p['nome']} (Código: {p['codigo']}) - Estoque: {p['estoque']} unidades\n"
            mensagem += "\nÉ necessário repor o estoque destes produtos!"
            
            self.mostrar_alerta("Alerta de Estoque Baixo", mensagem, QMessageBox.Warning)
        else:
            self.mostrar_mensagem("Estoque", "Todos os produtos estão com estoque adequado.")
    
    def mostrar_alerta(self, titulo, texto, icone=QMessageBox.Warning):
        """Exibe uma caixa de alerta personalizada"""
        msg_box = QMessageBox()
        msg_box.setIcon(icone)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #043b57;
            }
            QLabel { 
                color: white;
                background-color: #043b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        msg_box.exec_()
    
    def desconectar_sinais_temporariamente(self):
        """Desconecta sinais que poderiam disparar pesquisas automáticas"""
        try:
            # Em vez de apenas usar uma flag, vamos realmente bloquear os sinais
            self._sinais_bloqueados = True
            
            # Aqui precisamos garantir que alterações nos campos não disparem pesquisas
            # Usando blockSignals diretamente nos widgets
            self.codigo_input.blockSignals(True)
            self.nome_input.blockSignals(True)
            self.barras_input.blockSignals(True)
            self.grupo_combo.blockSignals(True)
            self.marca_combo.blockSignals(True)
        except Exception as e:
            print(f"Erro ao desconectar sinais: {e}")

    def reconectar_sinais(self):
        """Reconecta os sinais após operações críticas"""
        try:
            # Restaurar a recepção de sinais
            self._sinais_bloqueados = False
            
            # Desbloquear os sinais dos widgets
            self.codigo_input.blockSignals(False)
            self.nome_input.blockSignals(False)
            self.barras_input.blockSignals(False)
            self.grupo_combo.blockSignals(False)
            self.marca_combo.blockSignals(False)
        except Exception as e:
            print(f"Erro ao reconectar sinais: {e}")
    
    def focar_scanner(self):
        """Dá foco ao campo de código de barras para facilitar a leitura"""
        self.barras_input.setFocus()
        self.scan_info_label.setText("Pronto para escanear!")
        self.scan_info_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        
        # Resetar a mensagem após 3 segundos se nenhum código for lido
        QTimer.singleShot(3000, self.resetar_mensagem_scanner)
    
    def resetar_mensagem_scanner(self):
        """Reseta a mensagem informativa após o tempo definido"""
        self.scan_info_label.setText("Escaneie para pesquisar")
        self.scan_info_label.setStyleSheet("color: #90CAF9; font-size: 11px; font-style: italic;")
    
    def pesquisar_por_codigo_barras(self, codigo):
        """Pesquisa automaticamente quando um código de barras é lido"""
        self.scan_info_label.setText(f"Pesquisando: {codigo}")
        self.scan_info_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        
        # Limpar outros campos de pesquisa
        self.codigo_input.clear()
        self.nome_input.clear()
        self.grupo_combo.setCurrentIndex(0)
        self.marca_combo.setCurrentIndex(0)
        
        # Chamar a função de pesquisa
        self.pesquisar_produtos(codigo_barras=codigo)
        
        # Resetar a mensagem após alguns segundos
        QTimer.singleShot(3000, self.resetar_mensagem_scanner)
    
    def pesquisar(self):
        """Pesquisa produtos com base nos filtros selecionados"""
        # Não pesquisar se os sinais estiverem bloqueados
        if hasattr(self, '_sinais_bloqueados') and self._sinais_bloqueados:
            return
            
        codigo = self.codigo_input.text().strip()
        nome = self.nome_input.text().strip()
        codigo_barras = self.barras_input.text().strip()
        grupo = self.grupo_combo.currentText() if self.grupo_combo.currentIndex() > 0 else ""
        marca = self.marca_combo.currentText() if self.marca_combo.currentIndex() > 0 else ""
        
        # Se "Todos os grupos" estiver selecionado, define grupo como vazio para a pesquisa
        if grupo == "Todos os grupos":
            grupo = ""
            
        # Se "Todas as marcas" estiver selecionado, define marca como vazia para a pesquisa
        if marca == "Todas as marcas":
            marca = ""
        
        self.pesquisar_produtos(codigo, nome, codigo_barras, grupo, marca)
    
    def pesquisar_produtos(self, codigo="", nome="", codigo_barras="", grupo="", marca=""):
        """Realiza a pesquisa de produtos no banco de dados com base nos filtros fornecidos"""
        # Não pesquisar se os sinais estiverem bloqueados
        if hasattr(self, '_sinais_bloqueados') and self._sinais_bloqueados:
            return
            
        try:
            # Limpar tabela para os novos resultados
            self.tabela.setRowCount(0)
            
            # Consulta específica por código (prioridade mais alta)
            if codigo:
                produto = buscar_produto_por_codigo(codigo)
                if produto:
                    self.preencher_tabela_com_produtos([produto])
                else:
                    self.mostrar_mensagem("Aviso", f"Nenhum produto encontrado com o código {codigo}.")
                return
                
            # Se houver código de barras, pesquisar especificamente por ele
            if codigo_barras:
                # Implementar uma função no banco.py para buscar por código de barras
                # Por enquanto, vamos usar uma abordagem temporária
                try:
                    produtos = buscar_produtos_por_filtro(codigo_barras=codigo_barras)
                    if produtos and len(produtos) > 0:
                        self.preencher_tabela_com_produtos(produtos)
                    else:
                        self.mostrar_mensagem("Aviso", f"Nenhum produto encontrado com o código de barras {codigo_barras}.")
                except:
                    self.mostrar_mensagem("Erro", "Função de busca por código de barras não implementada.")
                return
            
            # Pesquisa com filtros combinados (nome, grupo, marca)
            produtos = buscar_produtos_por_filtro(nome=nome, grupo=grupo, marca=marca)
            
            if produtos and len(produtos) > 0:
                self.preencher_tabela_com_produtos(produtos)
            else:
                # Mensagem quando nenhum produto corresponde aos filtros
                self.mostrar_mensagem("Aviso", "Nenhum produto encontrado com os filtros selecionados.")
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao pesquisar produtos: {str(e)}", QMessageBox.Critical)
    
    def preencher_tabela_com_produtos(self, produtos):
        """Preenche a tabela com os produtos fornecidos"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Preencher tabela com os produtos
        for row, produto in enumerate(produtos):
            self.tabela.insertRow(row)
            
            # Índices: 0:ID, 1:CODIGO, 2:NOME, 3:CODIGO_BARRAS, 4:MARCA, 5:GRUPO,
            # 6:PRECO_CUSTO, 7:PRECO_VENDA, 8:QUANTIDADE_ESTOQUE
            id_produto = produto[0]
            codigo = produto[1]
            nome = produto[2]
            marca = produto[4] or ""
            grupo = produto[5] or ""
            preco_venda = produto[7] or 0
            quantidade_estoque = produto[8] or 0
            
            # Armazenar o ID do produto no item como dado (UserRole)
            codigo_item = QTableWidgetItem(str(codigo))
            codigo_item.setData(Qt.UserRole, id_produto)
            
            self.tabela.setItem(row, 0, codigo_item)
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(marca))
            self.tabela.setItem(row, 3, QTableWidgetItem(grupo))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"R$ {preco_venda:.2f}".replace('.', ',')))
            
            # Definir cor de fundo para quantidade de estoque baixo
            estoque_item = QTableWidgetItem(str(quantidade_estoque))
            if quantidade_estoque <= 5:  # Definir limite para estoque baixo
                estoque_item.setBackground(Qt.red)
                estoque_item.setForeground(Qt.white)
            self.tabela.setItem(row, 5, estoque_item)
    
    def limpar_filtros(self):
        """Limpa todos os campos de pesquisa e carrega todos os produtos novamente"""
        self.desconectar_sinais_temporariamente()
        
        self.codigo_input.clear()
        self.nome_input.clear()
        self.barras_input.clear()
        self.grupo_combo.setCurrentIndex(0)
        self.marca_combo.setCurrentIndex(0)
        
        self.reconectar_sinais()
        
        # Recarregar todos os produtos
        self.carregar_produtos()
    
    def carregar_produtos(self):
        """Carrega dados de produtos do banco de dados"""
        try:
            # Limpar tabela
            self.tabela.setRowCount(0)
            
            # Carregar produtos do banco de dados
            produtos = listar_produtos()
            
            # Se não existirem produtos no banco, mostrar mensagem
            if not produtos:
                self.mostrar_mensagem("Informação", "Não há produtos cadastrados.")
                return
            
            # Usar o método comum para preencher a tabela
            self.preencher_tabela_com_produtos(produtos)
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao carregar produtos: {str(e)}", QMessageBox.Critical)
    
    def selecionar_item(self):
        """Apenas preenche os campos quando uma linha é selecionada, sem realizar pesquisa"""
        try:
            selected_rows = self.tabela.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                
                # Obter ID do produto armazenado no item da primeira coluna
                id_produto = self.tabela.item(row, 0).data(Qt.UserRole)
                
                # Buscar dados completos do produto no banco usando o ID
                produto = buscar_produto_por_id(id_produto)
                
                if produto:
                    # Desconectar temporariamente qualquer sinal de alteração
                    self.desconectar_sinais_temporariamente()
                    
                    # Campos da tabela PRODUTOS:
                    # 0:ID, 1:CODIGO, 2:NOME, 3:CODIGO_BARRAS, 4:MARCA, 5:GRUPO,
                    # 6:PRECO_CUSTO, 7:PRECO_VENDA, 8:QUANTIDADE_ESTOQUE
                    self.codigo_input.setText(str(produto[1]))  # CODIGO
                    self.nome_input.setText(produto[2])         # NOME
                    
                    # Verificar se os dados existem antes de atribuir
                    codigo_barras = produto[3]
                    if codigo_barras:
                        self.barras_input.setText(codigo_barras)
                    else:
                        self.barras_input.setText("")
                    
                    # Selecionar a marca no combobox se existir
                    marca = produto[4]
                    if marca:
                        index = self.marca_combo.findText(marca)
                        if index >= 0:
                            self.marca_combo.setCurrentIndex(index)
                        else:
                            self.marca_combo.setCurrentIndex(0)
                    else:
                        self.marca_combo.setCurrentIndex(0)
                    
                    # Selecionar o grupo, se existir
                    grupo = produto[5]
                    if grupo:
                        index = self.grupo_combo.findText(grupo)
                        if index >= 0:
                            self.grupo_combo.setCurrentIndex(index)
                        else:
                            self.grupo_combo.setCurrentIndex(0)
                    else:
                        self.grupo_combo.setCurrentIndex(0)
                    
                    # Reconectar os sinais após preencher os campos
                    self.reconectar_sinais()
                else:
                    # Fallback para os dados da tabela
                    self.desconectar_sinais_temporariamente()
                    
                    self.codigo_input.setText(self.tabela.item(row, 0).text())
                    self.nome_input.setText(self.tabela.item(row, 1).text())
                    self.barras_input.setText("")
                    self.marca_combo.setCurrentIndex(0)
                    self.grupo_combo.setCurrentIndex(0)
                    
                    self.reconectar_sinais()
                    
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao selecionar produto: {str(e)}", QMessageBox.Critical)
    
    def alterar(self):
        """Abre o formulário para alterar os dados do produto selecionado"""
        try:    
            # Verificar se um produto foi selecionado
            selected_rows = self.tabela.selectionModel().selectedRows()
            if not selected_rows:
                self.mostrar_mensagem("Seleção necessária", 
                                    "Por favor, selecione um produto para alterar", 
                                    QMessageBox.Warning)
                return
                
            row = selected_rows[0].row()
            
            # Obter ID do produto armazenado no item da primeira coluna
            id_produto = self.tabela.item(row, 0).data(Qt.UserRole)
            
            # Buscar os dados completos do produto no banco
            produto_db = buscar_produto_por_id(id_produto)
            
            if not produto_db:
                self.mostrar_mensagem("Erro", 
                                    "Não foi possível encontrar os dados do produto selecionado", 
                                    QMessageBox.Critical)
                return
            
            # Criar um dicionário com os dados do produto para passar ao formulário
            dados_produto = {
                "id": produto_db[0],              # ID
                "codigo": produto_db[1],          # CODIGO
                "nome": produto_db[2],            # NOME
                "barras": produto_db[3],          # CODIGO_BARRAS
                "marca": produto_db[4],           # MARCA
                "grupo": produto_db[5],           # GRUPO
                "preco_compra": produto_db[6],    # PRECO_CUSTO
                "preco_venda": produto_db[7],     # PRECO_VENDA
                "estoque": produto_db[8]          # QUANTIDADE_ESTOQUE
            }
            
            # Verificar se já existe uma janela de formulário aberta
            if hasattr(self, 'form_window') and self.form_window.isVisible():
                # Se existir, fechá-la para abrir uma nova com os dados atualizados
                self.form_window.close()
            
            # Carregar dinamicamente a classe FormularioProdutos
            FormularioProdutos = self.load_formulario_produtos()
            if not FormularioProdutos:
                return
                
            # Criar uma nova janela para o formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Alterar Produto")
            self.form_window.setGeometry(150, 150, 800, 600)
            self.form_window.setStyleSheet("background-color: #043b57;")
            
            # Criar o widget do formulário, indicando que é modo de alteração
            formulario = FormularioProdutos(self, modo_alteracao=True)
            
            # Definir produto original e preencher os campos
            formulario.set_produto_original(dados_produto)
            formulario.preencher_campos_produto(dados_produto)
                
            # Alterar o texto do botão para "Atualizar"
            formulario.btn_incluir.setText("Atualizar")
            
            self.form_window.setCentralWidget(formulario)
            
            # Exibir a janela
            self.form_window.show()
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao abrir formulário de alteração: {str(e)}", QMessageBox.Critical)
            
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem personalizada"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #043b57;
            }
            QLabel { 
                color: white;
                background-color: #043b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        msg_box.exec_()
    
    def excluir(self):
        """Exclui um produto do banco de dados"""
        try:
            selected_rows = self.tabela.selectionModel().selectedRows()
            if not selected_rows:
                self.mostrar_mensagem("Atenção", "Selecione um produto para excluir!")
                return
                    
            row = selected_rows[0].row()
            
            # Obter o ID do produto para exclusão
            id_produto = self.tabela.item(row, 0).data(Qt.UserRole)
            nome = self.tabela.item(row, 1).text()
            
            # Criar uma mensagem de confirmação personalizada com estilo
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Confirmar exclusão")
            msg_box.setText(f"Deseja realmente excluir o produto '{nome}'?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            
            # Aplicar estilo personalizado
            msg_box.setStyleSheet("""
                QMessageBox { 
                    background-color: #043b57;
                }
                QLabel { 
                    color: white;
                    background-color: #043b57;
                }
                QPushButton {
                    background-color: #005079;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #003d5c;
                }
            """)
            
            # Obter resposta
            resposta = msg_box.exec_()
            
            if resposta == QMessageBox.No:
                return
            
            # Excluir o produto do banco de dados
            resultado = excluir_produto(id_produto)
            
            if resultado:
                # Atualizar a tabela removendo a linha
                self.tabela.removeRow(row)
                
                # Limpar os campos
                self.desconectar_sinais_temporariamente()
                
                self.codigo_input.clear()
                self.nome_input.clear()
                self.barras_input.clear()
                self.marca_combo.setCurrentIndex(0)
                self.grupo_combo.setCurrentIndex(0)
                
                self.reconectar_sinais()
                
                self.mostrar_mensagem("Sucesso", "Produto excluído com sucesso!")
            else:
                self.mostrar_mensagem("Erro", "Não foi possível excluir o produto.", QMessageBox.Critical)
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao excluir produto: {str(e)}", QMessageBox.Critical)
    
    def load_formulario_produtos(self):
        """
        Carrega dinamicamente o módulo formulario_produtos.py
        Isso permite que o arquivo seja encontrado mesmo quando compilado para .exe
        """
        try:
            # Tente primeiro com importação direta (para ambiente de desenvolvimento)
            try:
                # Importação direta usando o módulo
                from produtos_e_servicos.formulario_produtos import FormularioProdutos
                print("Importação direta de FormularioProdutos bem-sucedida")
                return FormularioProdutos
            except ImportError as e:
                print(f"Importação direta falhou: {str(e)}, tentando método alternativo...")
                
                # Caminho para o módulo formulario_produtos.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                module_path = os.path.join(script_dir, "formulario_produtos.py")
                
                # Se o arquivo não existir, vamos criar um básico
                if not os.path.exists(module_path):
                    self.criar_formulario_produtos_padrao(module_path)
                
                # Carregar o módulo dinamicamente
                module_name = "formulario_produtos"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Não foi possível carregar o módulo {module_name}")
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Retornar a classe FormularioProdutos
                if hasattr(module, "FormularioProdutos"):
                    return getattr(module, "FormularioProdutos")
                else:
                    raise ImportError(f"A classe FormularioProdutos não foi encontrada no módulo {module_name}")
        except Exception as e:
            print(f"Erro ao carregar FormularioProdutos: {str(e)}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar o formulário: {str(e)}", QMessageBox.Critical)
            return None
            
    def criar_formulario_produtos_padrao(self, filepath):
        """Cria um arquivo formulario_produtos.py básico se não existir"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('''\
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox, QFormLayout,
                             QDoubleSpinBox, QSpinBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Importar o módulo banco.py da pasta base
try:
    from base.banco import (criar_produto, atualizar_produto, buscar_produto_por_codigo)
except ImportError as e:
    print(f"Erro ao importar funções do banco: {e}")
    # Mostrar mensagem de erro
    QMessageBox.critical(None, "Erro de importação", 
                        f"Não foi possível importar o módulo banco.py da pasta base: {e}")

class FormularioProdutos(QWidget):
    def __init__(self, parent=None, api_url=None):
        super().__init__()
        self.parent = parent
        self.produto_original = None  # Para armazenar dados do produto em caso de alteração
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Cadastro de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; }"
        
        # Estilo para os inputs
        input_style = """
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
                min-height: 30px;
            }
        """
        
        # Campo Código
        self.codigo_label = QLabel("Código:")
        self.codigo_label.setStyleSheet(label_style)
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(input_style)
        form_layout.addRow(self.codigo_label, self.codigo_input)
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setStyleSheet(label_style)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(input_style)
        form_layout.addRow(self.nome_label, self.nome_input)
        
        # Campo Código de Barras
        self.barras_label = QLabel("Código de Barras:")
        self.barras_label.setStyleSheet(label_style)
        self.barras_input = QLineEdit()
        self.barras_input.setStyleSheet(input_style)
        form_layout.addRow(self.barras_label, self.barras_input)
        
        # Campo Marca
        self.marca_label = QLabel("Marca:")
        self.marca_label.setStyleSheet(label_style)
        self.marca_input = QLineEdit()
        self.marca_input.setStyleSheet(input_style)
        form_layout.addRow(self.marca_label, self.marca_input)
        
        # Campo Grupo
        self.grupo_label = QLabel("Grupo:")
        self.grupo_label.setStyleSheet(label_style)
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(input_style)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Alimentos")
        self.grupo_combo.addItem("Bebidas")
        self.grupo_combo.addItem("Limpeza")
        self.grupo_combo.addItem("Higiene")
        self.grupo_combo.addItem("Hortifruti")
        form_layout.addRow(self.grupo_label, self.grupo_combo)
        
        # Campo Preço de Custo
        self.preco_custo_label = QLabel("Preço de Custo:")
        self.preco_custo_label.setStyleSheet(label_style)
        self.preco_custo_input = QDoubleSpinBox()
        self.preco_custo_input.setStyleSheet(input_style)
        self.preco_custo_input.setRange(0.01, 99999.99)
        self.preco_custo_input.setDecimals(2)
        self.preco_custo_input.setSingleStep(0.10)
        self.preco_custo_input.setPrefix("R$ ")
        form_layout.addRow(self.preco_custo_label, self.preco_custo_input)
        
        # Campo Preço de Venda
        self.preco_venda_label = QLabel("Preço de Venda:")
        self.preco_venda_label.setStyleSheet(label_style)
        self.preco_venda_input = QDoubleSpinBox()
        self.preco_venda_input.setStyleSheet(input_style)
        self.preco_venda_input.setRange(0.01, 99999.99)
        self.preco_venda_input.setDecimals(2)
        self.preco_venda_input.setSingleStep(0.10)
        self.preco_venda_input.setPrefix("R$ ")
        form_layout.addRow(self.preco_venda_label, self.preco_venda_input)
        
        # Campo Estoque
        self.estoque_label = QLabel("Quantidade em Estoque:")
        self.estoque_label.setStyleSheet(label_style)
        self.estoque_input = QSpinBox()
        self.estoque_input.setStyleSheet(input_style)
        self.estoque_input.setRange(0, 99999)
        form_layout.addRow(self.estoque_label, self.estoque_input)
        
        main_layout.addLayout(form_layout)
        
        # Botões
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(15)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet(btn_style)
        self.btn_salvar.clicked.connect(self.salvar)
        
        botoes_layout.addWidget(self.btn_salvar)
        
        botoes_container = QHBoxLayout()
        botoes_container.addStretch()
        botoes_container.addLayout(botoes_layout)
        botoes_container.addStretch()
        
        main_layout.addLayout(botoes_container)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
    
    def set_produto_original(self, produto):
        """Define os dados originais do produto (para alteração)"""
        self.produto_original = produto
        
    def salvar(self):
        """Salva os dados do produto no banco de dados"""
        try:
            # Validação básica
            codigo = self.codigo_input.text().strip()
            nome = self.nome_input.text().strip()
            
            if not codigo:
                QMessageBox.warning(self, "Campos obrigatórios", "O campo Código é obrigatório.")
                self.codigo_input.setFocus()
                return
                
            if not nome:
                QMessageBox.warning(self, "Campos obrigatórios", "O campo Nome é obrigatório.")
                self.nome_input.setFocus()
                return
            
            # Capturar outros dados
            codigo_barras = self.barras_input.text().strip()
            marca = self.marca_input.text().strip()
            
            grupo = self.grupo_combo.currentText()
            if grupo == "Selecione um grupo":
                grupo = ""
                
            preco_custo = self.preco_custo_input.value()
            preco_venda = self.preco_venda_input.value()
            quantidade_estoque = self.estoque_input.value()
            
            # Verificar se é uma alteração ou inclusão
            if self.produto_original:
                # Alteração - usar o ID do produto original
                id_produto = self.produto_original["id"]
                
                try:
                    # Atualizar produto no banco
                    resultado = atualizar_produto(
                        id_produto, codigo, nome, codigo_barras, marca, grupo,
                        preco_custo, preco_venda, quantidade_estoque
                    )
                    
                    if resultado:
                        QMessageBox.information(self, "Sucesso", "Produto atualizado com sucesso!")
                        
                        # Atualizar a tabela na tela principal
                        if self.parent and hasattr(self.parent, 'carregar_produtos'):
                            self.parent.carregar_produtos()
                        
                        # Fechar o formulário
                        if self.parent and hasattr(self.parent, 'form_window'):
                            self.parent.form_window.close()
                    else:
                        QMessageBox.critical(self, "Erro", "Não foi possível atualizar o produto.")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao atualizar produto: {str(e)}")
            else:
                # Inclusão - novo produto
                try:
                    # Verificar se o código já existe
                    produto_existente = buscar_produto_por_codigo(codigo)
                    if produto_existente:
                        QMessageBox.warning(self, "Código duplicado", "Já existe um produto com este código.")
                        self.codigo_input.setFocus()
                        return
                    
                    # Criar novo produto no banco
                    resultado = criar_produto(
                        codigo, nome, codigo_barras, marca, grupo,
                        preco_custo, preco_venda, quantidade_estoque
                    )
                    
                    if resultado:
                        QMessageBox.information(self, "Sucesso", "Produto cadastrado com sucesso!")
                        
                        # Atualizar a tabela na tela principal
                        if self.parent and hasattr(self.parent, 'carregar_produtos'):
                            self.parent.carregar_produtos()
                        
                        # Fechar o formulário
                        if self.parent and hasattr(self.parent, 'form_window'):
                            self.parent.form_window.close()
                    else:
                        QMessageBox.critical(self, "Erro", "Não foi possível cadastrar o produto.")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao cadastrar produto: {str(e)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar dados: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormularioProdutos()
    window.show()
    sys.exit(app.exec_())
''')
        except Exception as e:
            print(f"Erro ao criar arquivo formulario_produtos.py: {str(e)}")
            
    def cadastrar(self):
        """Abre a tela de cadastro de produto"""
        try:
            # Verificar se já existe uma janela de formulário aberta
            if hasattr(self, 'form_window') and self.form_window.isVisible():
                # Se existir, apenas ativá-la em vez de criar uma nova
                self.form_window.setWindowState(self.form_window.windowState() & ~Qt.WindowMinimized)
                self.form_window.activateWindow()
                self.form_window.raise_()
                return
            
            # Carregar dinamicamente a classe FormularioProdutos
            FormularioProdutos = self.load_formulario_produtos()
            if FormularioProdutos is None:
                return
            
            # Criar uma nova janela para o formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Cadastro de Produtos")
            self.form_window.setGeometry(100, 100, 800, 600)
            self.form_window.setStyleSheet("background-color: #043b57;")
            
            # Configurar o widget central
            formulario_produtos_widget = FormularioProdutos(self)
            self.form_window.setCentralWidget(formulario_produtos_widget)
            
            # Mostrar a janela de formulário
            self.form_window.show()
        except AttributeError as e:
            self.mostrar_mensagem("Erro", f"Módulo de formulários carregado, mas há um problema com a classe: {str(e)}")
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao abrir o formulário: {str(e)}")


# A classe ProdutosWindow precisa estar presente para o sistema principal encontrá-la
class ProdutosWindow(QMainWindow):
    """Classe para gerenciar a janela de produtos quando executado como script principal"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Produtos")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #043b57;")
        
        # Configurando o widget central
        self.produtos_widget = Produtos(self)
        self.setCentralWidget(self.produtos_widget)


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProdutosWindow()
    window.show()
    sys.exit(app.exec_())