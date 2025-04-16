#formulario_produtos.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QDateEdit, QComboBox, QMessageBox, QStyle, QSpinBox,
                             QToolButton, QListWidget, QInputDialog, QDialog)

from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate, QTimer

# Importar as funções do banco de dados
try:
    from base.banco import (criar_produto, atualizar_produto, 
                           buscar_produto_por_codigo, buscar_produto_por_id,
                           buscar_produto_por_barras, execute_query)
except ImportError as e:
    print(f"Erro ao importar funções do banco: {e}")
    # Mostrar mensagem de erro
    QMessageBox.critical(None, "Erro de importação", 
                         f"Não foi possível importar o módulo banco.py da pasta base: {e}")

# Importar a classe LeitorCodigoBarras
# Coloque esta classe em um arquivo separado e importe-a, ou a defina diretamente aqui
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

class LeitorCodigoBarras(QLineEdit):
    """
    Classe personalizada para campo de código de barras com suporte a leitores de código de barras.
    Detecta automaticamente quando um código é escaneado por um leitor físico.
    """
    codigo_lido = pyqtSignal(str)  # Sinal emitido quando um código de barras é lido com sucesso
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Tempo limite para considerar uma sequência como leitura de código de barras
        # A maioria dos leitores de código de barras envia caracteres muito rapidamente
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.finalizar_leitura)
        
        # Buffer para acumular caracteres durante a leitura
        self.buffer = ""
        
        # Tempo máximo entre caracteres para considerar como parte do mesmo código (ms)
        self.tempo_entre_caracteres = 50
        
        # Indicador se estamos em modo de leitura
        self.lendo_codigo = False
        
        # Flag para evitar processamento duplicado
        self.codigo_processado = False
        
        # Conectar ao evento de texto alterado para detectar entrada
        self.textChanged.connect(self.on_text_changed)
        
        # Estilo padrão para o campo
        self.estilo_normal = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
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
            self.codigo_processado = False
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
        if self.lendo_codigo and self.buffer and not self.codigo_processado:
            # Marcar como processado para evitar duplicação
            self.codigo_processado = True
            
            # Emitir o sinal com o código lido
            self.codigo_lido.emit(self.buffer)
            
            # Reseta o estado de leitura
            self.lendo_codigo = False
            
            # Deixar o campo com fundo verde por um momento para indicar sucesso
            self.setStyleSheet("""
                QLineEdit {
                    background-color: #c8f7c8;
                    border: 1px solid #00cc00;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 4px;
                    color: black;
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
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        
    def focusOutEvent(self, event):
        """Sobrescreve o evento de perda de foco"""
        super().focusOutEvent(event)
        # Restaurar estilo normal quando o campo perde o foco
        self.setStyleSheet(self.estilo_normal)


class FormularioProdutos(QWidget):
    def __init__(self, parent=None, modo_alteracao=False):
        super().__init__(parent)
        self.parent = parent
        self.produto_original = None  # Armazenar referência ao produto original
        self.modo_alteracao = modo_alteracao  # Novo flag para indicar modo de alteração
        self.initUI()
        
        # Carregar o próximo código disponível no modo de inclusão
        if not self.produto_original and not self.modo_alteracao:
            self.carregar_proximo_codigo()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#043b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
    
    def carregar_proximo_codigo(self):
        """Carrega o próximo código disponível do banco de dados"""
        try:
            # Query para encontrar o próximo código disponível
            query = """
            SELECT COALESCE(MAX(CAST(CODIGO AS INTEGER)), 0) + 1 FROM PRODUTOS
            """
            result = execute_query(query)
            
            if result and len(result) > 0 and result[0][0]:
                proximo_codigo = str(result[0][0])
                self.codigo_input.setText(proximo_codigo)
            else:
                # Se não houver produtos, começar com o código 1
                self.codigo_input.setText("1")
                
        except Exception as e:
            print(f"Erro ao carregar próximo código: {str(e)}")
            # Em caso de erro, definir código padrão
            self.codigo_input.setText("1")
    
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
        
        titulo = QLabel("Cadastro de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)
        
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Estilos
        label_style = "color: white; font-size: 14px;"
        # Correção específica para o estilo dos ComboBoxes
        

        combobox_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down { 
                border: none; 
            }
            QComboBox:hover { 
                border: 1px solid #0078d7; 
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QComboBox QListView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
                border: 1px solid #cccccc;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
                border: 1px solid #cccccc;
            }
            QComboBox QAbstractItemView::item {
                background-color: white;
                color: black;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """

        # Para garantir que o estilo seja aplicado, certifique-se de aplicar este estilo 
        # tanto no FormularioProdutos quanto no GerenciadorItensDialog
        lineedit_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QLineEdit:focus { border: 1px solid #0078d7; }
        """
        readonly_lineedit_style = """
            QLineEdit {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: #505050;
            }
        """
        spinbox_style = """
            QSpinBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QSpinBox:focus { border: 1px solid #0078d7; }
        """
        
        # Linha 1: Código e Nome
        linha1 = QHBoxLayout()
        linha1.setSpacing(20)
        
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet(label_style)
        codigo_layout.addWidget(codigo_label)
        self.codigo_input = QLineEdit()
        self.codigo_input.setReadOnly(True)
        self.codigo_input.setStyleSheet(readonly_lineedit_style)
        codigo_layout.addWidget(self.codigo_input)
        linha1.addLayout(codigo_layout)
        
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet(label_style)
        nome_layout.addWidget(nome_label)
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        nome_layout.addWidget(self.nome_input)
        linha1.addLayout(nome_layout, 1)
        
        main_layout.addLayout(linha1)
        
        # Linha 2: Código de Barras e Grupo
        linha2 = QHBoxLayout()
        linha2.setSpacing(20)
        
        # Código de Barras
        barras_v = QVBoxLayout()
        barras_h = QHBoxLayout()
        barras_label = QLabel("Código de Barras:")
        barras_label.setStyleSheet(label_style)
        barras_h.addWidget(barras_label)
        self.barras_input = LeitorCodigoBarras()
        barras_h.addWidget(self.barras_input, 1)
        btn_scan = QToolButton()
        btn_scan.setText("Scan")
        btn_scan.setStyleSheet("""
            QToolButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
            }
            QToolButton:hover { background-color: #003d5c; }
        """)
        btn_scan.clicked.connect(self.focar_scanner)
        barras_h.addWidget(btn_scan)
        barras_v.addLayout(barras_h)
        self.scan_info_label = QLabel("Escaneie ou digite o código de barras do produto")
        self.scan_info_label.setStyleSheet("color: #90CAF9; font-size: 12px; font-style: italic;")
        barras_v.addWidget(self.scan_info_label)
        linha2.addLayout(barras_v, 1)
        
        # Grupo
        grupo_layout = QHBoxLayout()
        grupo_layout.setSpacing(5)
        grupo_layout.setContentsMargins(0, 0, 0, 0)
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet(label_style)
        grupo_layout.addWidget(grupo_label)
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(combobox_style)
        try:
            from base.banco import listar_grupos
            items = listar_grupos() or []
            self.grupo_combo.addItem("Selecione um grupo")
            for g in sorted(items):
                self.grupo_combo.addItem(g)
        except:
            self.grupo_combo.addItems(["Selecione um grupo","Alimentos","Bebidas","Limpeza","Higiene","Hortifruti","Eletrônicos","Vestuário","Outros"])
        btn_gg = QToolButton()
        btn_gg.setText("+")
        btn_gg.setToolTip("Gerenciar grupos")
        btn_gg.setStyleSheet("""
            QToolButton { background-color: #00c853; color: white; border: none; padding: 4px 8px; border-radius: 4px; }
            QToolButton:hover { background-color: #009624; }
        """)
        btn_gg.clicked.connect(self.abrir_gerenciador_grupos)
        grupo_layout.addWidget(self.grupo_combo)
        grupo_layout.addWidget(btn_gg)
        linha2.addLayout(grupo_layout)
        
        main_layout.addLayout(linha2)
        
        # Linha 3: Marca e preços
        linha3 = QHBoxLayout()
        linha3.setSpacing(20)
        
        marca_layout = QHBoxLayout()
        marca_layout.setSpacing(5)
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet(label_style)
        marca_layout.addWidget(marca_label)
        self.marca_combo = QComboBox()
        self.marca_combo.setStyleSheet(combobox_style)
        try:
            from base.banco import listar_marcas
            items = listar_marcas() or []
            self.marca_combo.addItem("Selecione uma marca")
            for m in sorted(items):
                self.marca_combo.addItem(m)
        except:
            self.marca_combo.addItems(["Selecione uma marca","Nestlé","Unilever","Coca-Cola"])
        btn_gm = QToolButton()
        btn_gm.setText("+")
        btn_gm.setToolTip("Gerenciar marcas")
        btn_gm.setStyleSheet("""
            QToolButton { background-color: #00c853; color: white; border: none; padding: 4px 8px; border-radius: 4px; }
            QToolButton:hover { background-color: #009624; }
        """)
        btn_gm.clicked.connect(self.abrir_gerenciador_marcas)
        marca_layout.addWidget(self.marca_combo)
        marca_layout.addWidget(btn_gm)
        linha3.addLayout(marca_layout, 1)
        
        # Preço de Venda
        pv_layout = QHBoxLayout()
        pv_label = QLabel("Preço de venda:")
        pv_label.setStyleSheet(label_style)
        pv_layout.addWidget(pv_label)
        self.preco_venda_input = QLineEdit()
        self.preco_venda_input.setStyleSheet(lineedit_style)
        pv_layout.addWidget(self.preco_venda_input)
        linha3.addLayout(pv_layout)
        
        # Preço de Compra
        pc_layout = QHBoxLayout()
        pc_label = QLabel("Preço de Compra:")
        pc_label.setStyleSheet(label_style)
        pc_layout.addWidget(pc_label)
        self.preco_compra_input = QLineEdit()
        self.preco_compra_input.setStyleSheet(lineedit_style)
        pc_layout.addWidget(self.preco_compra_input)
        linha3.addLayout(pc_layout)
        
        main_layout.addLayout(linha3)
        
        # Linha 4: Data e estoque
        linha4 = QHBoxLayout()
        linha4.setSpacing(20)
        
        data_layout = QHBoxLayout()
        data_label = QLabel("Data de Cadastro:")
        data_label.setStyleSheet(label_style)
        data_layout.addWidget(data_label)
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setStyleSheet("""
            QDateEdit { background-color: white; border: 1px solid #cccccc; padding: 10px; border-radius: 4px; }
            QDateEdit:hover { border: 1px solid #0078d7; }
        """)
        data_layout.addWidget(self.data_input)
        linha4.addLayout(data_layout)
        
        estoque_layout = QHBoxLayout()
        estoque_layout.setSpacing(5)
        estoque_label = QLabel("Quant. Estoque:")
        estoque_label.setStyleSheet(label_style)
        estoque_layout.addWidget(estoque_label)
        self.estoque_input = QSpinBox()
        self.estoque_input.setRange(0, 99999)
        self.estoque_input.setStyleSheet(spinbox_style)
        estoque_layout.addWidget(self.estoque_input)
        linha4.addLayout(estoque_layout)
        
        main_layout.addLayout(linha4)
        
        # Botão Incluir
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 15px 0;
                font-size: 16px;
                border-radius: 4px;
                margin: 20px 100px 0;
            }
            QPushButton:hover { background-color: #00e088; }
        """)
        self.btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(self.btn_incluir)
        
        main_layout.addStretch()


    def abrir_gerenciador_marcas(self):
        """Abre o gerenciador de marcas de forma segura"""
        try:
            # Criar e mostrar o diálogo
            dialog = GerenciadorItensDialog(self, tipo="marca")
            dialog.setWindowModality(Qt.ApplicationModal)  # Bloqueia a janela principal
            dialog.show()
        except Exception as e:
            print(f"Erro ao abrir gerenciador de marcas: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao abrir gerenciador de marcas: {str(e)}")

    def abrir_gerenciador_grupos(self):
        """Abre o gerenciador de grupos de forma segura"""
        try:
            # Criar e mostrar o diálogo
            dialog = GerenciadorItensDialog(self, tipo="grupo")
            dialog.setWindowModality(Qt.ApplicationModal)  # Bloqueia a janela principal
            dialog.show()
        except Exception as e:
            print(f"Erro ao abrir gerenciador de grupos: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao abrir gerenciador de grupos: {str(e)}")

    def focar_scanner(self):
        """Dá foco ao campo de código de barras para facilitar a leitura"""
        self.barras_input.setFocus()
        self.scan_info_label.setText("Pronto para escanear! Aproxime o leitor do código de barras.")
        self.scan_info_label.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold;")
        
        # Resetar a mensagem após 3 segundos se nenhum código for lido
        QTimer.singleShot(3000, self.resetar_mensagem_scanner)
    
    def resetar_mensagem_scanner(self):
        """Reseta a mensagem informativa após o tempo definido"""
        self.scan_info_label.setText("Escaneie ou digite o código de barras do produto")
        self.scan_info_label.setStyleSheet("color: #90CAF9; font-size: 12px; font-style: italic;")
    
    def codigo_barras_lido(self, codigo):
        """Manipula o evento de leitura de código de barras completa"""
        # Verificar se o atributo modo_alteracao existe antes de usá-lo
        modo_alteracao = getattr(self, 'modo_alteracao', False)
        
        # Evitar processamento se estiver no modo de alteração
        if modo_alteracao:
            return
            
        self.scan_info_label.setText(f"Código de barras lido com sucesso: {codigo}")
        self.scan_info_label.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold;")
        
        # Buscar produto pelo código de barras se já existir
        self.buscar_produto_por_barras(codigo)
        
        # Resetar a mensagem após 3 segundos
        QTimer.singleShot(3000, self.resetar_mensagem_scanner)
    
    def buscar_produto_por_barras(self, codigo_barras):
        """Busca um produto pelo código de barras"""
        try:
            # Verificar se o atributo modo_alteracao existe antes de usá-lo
            modo_alteracao = getattr(self, 'modo_alteracao', False)
            
            # Se já estivermos em modo de alteração, não perguntar novamente
            if modo_alteracao:
                return
                
            # Verificar se já existe um produto com este código de barras
            produto = buscar_produto_por_barras(codigo_barras)
            
            if produto:
                # Produto encontrado, perguntar ao usuário se deseja carregá-lo
                # Criar uma caixa de mensagem personalizada com estilo
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setWindowTitle("Produto Encontrado")
                msg_box.setText(f'O produto "{produto["nome"]}" com este código de barras já existe. Deseja carregá-lo?')
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.Yes)
                
                # Personalizar os botões para Sim e Não
                btn_sim = msg_box.button(QMessageBox.Yes)
                btn_sim.setText("Sim")
                btn_nao = msg_box.button(QMessageBox.No)
                btn_nao.setText("Não")
                
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
                reply = msg_box.exec_()
                
                if reply == QMessageBox.Yes:
                    # Carregar o produto encontrado para edição
                    self.set_produto_original(produto)
                    # Preencher os campos com os dados do produto
                    self.preencher_campos_produto(produto)
                    # Mudar o botão para Atualizar
                    self.btn_incluir.setText("Atualizar")
        
        except Exception as e:
            print(f"Erro ao buscar produto por código de barras: {str(e)}")
            # Se a função não existir ou ocorrer um erro, apenas ignorar
            pass
    
    def set_produto_original(self, produto):
        """Define o produto original para modo de edição"""
        if isinstance(produto, dict):
            self.produto_original = produto
            
            # Se estamos no modo de edição, preencher o campo código com o código do produto
            if "codigo" in produto:
                self.codigo_input.setText(str(produto["codigo"]))
    
    def preencher_campos_produto(self, produto):
        """Preenche os campos com os dados do produto"""
        # Esta função pode ser chamada quando um produto é encontrado pelo código de barras
        if isinstance(produto, dict):
            # Preencher os campos com os dados do produto
            if "codigo" in produto:
                self.codigo_input.setText(str(produto["codigo"]))
            if "nome" in produto:
                self.nome_input.setText(produto["nome"])
            if "barras" in produto:
                self.barras_input.setText(produto["barras"])
            if "marca" in produto:
                # Encontrar o índice da marca no combobox
                index = self.marca_combo.findText(produto["marca"])
                if index >= 0:
                    self.marca_combo.setCurrentIndex(index)
            if "grupo" in produto:
                # Encontrar o índice do grupo no combobox
                index = self.grupo_combo.findText(produto["grupo"])
                if index >= 0:
                    self.grupo_combo.setCurrentIndex(index)
            if "preco_venda" in produto:
                self.preco_venda_input.setText(str(produto["preco_venda"]))
            if "preco_compra" in produto:
                self.preco_compra_input.setText(str(produto["preco_compra"]))
            if "estoque" in produto:
                self.estoque_input.setValue(int(produto["estoque"]))
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual
        if hasattr(self, 'parent_widget') and self.parent_widget and hasattr(self.parent_widget, 'form_window'):
            self.parent_widget.form_window.close()
        else:
            # Se não encontrar a janela pai, tenta fechar a janela atual
            parent_window = self.window()
            if parent_window and parent_window != self:
                parent_window.close()
            else:
                print("Voltar para a tela de produtos")
    
    def incluir(self):
        """Inclui um novo produto ou salva alterações no banco de dados"""
        # Validar campos obrigatórios
        codigo = self.codigo_input.text().strip()
        nome = self.nome_input.text().strip()
        grupo = self.grupo_combo.currentText() if self.grupo_combo.currentIndex() > 0 else ""
        unidade = self.unidade_combo.currentText() if self.unidade_combo.currentIndex() > 0 else ""
        preco_venda = self.preco_venda_input.text().strip()
        barras = self.barras_input.text().strip()
        marca = self.marca_combo.currentText() if self.marca_combo.currentIndex() > 0 else ""
        preco_compra = self.preco_compra_input.text().strip()
        quantidade_estoque = self.estoque_input.value()  # Obtém o valor do campo de estoque
        
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Preencha pelo menos o código e o nome do produto!")
            return
        
        # Verificar se é uma alteração (botão com texto "Atualizar")
        eh_alteracao = self.btn_incluir.text() == "Atualizar"
        
        # Converter preços para float
        preco_venda_float = 0.0
        try:
            preco_venda_float = float(preco_venda.replace(',', '.')) if preco_venda else 0.0
        except ValueError:
            self.mostrar_mensagem("Erro", "Formato de preço de venda inválido. Use apenas números e vírgula.")
            return
            
        preco_compra_float = 0.0
        try:
            preco_compra_float = float(preco_compra.replace(',', '.')) if preco_compra else 0.0
        except ValueError:
            self.mostrar_mensagem("Erro", "Formato de preço de compra inválido. Use apenas números e vírgula.")
            return

        try:
            if eh_alteracao:
                # Modo de alteração - atualizar produto existente no banco de dados
                if self.produto_original and "id" in self.produto_original:
                    # Usar o ID do produto original para atualização
                    id_produto = self.produto_original["id"]
                    
                    # Atualizar produto no banco de dados
                    resultado = atualizar_produto(
                        id_produto, codigo, nome, barras, marca, grupo,
                        preco_compra_float, preco_venda_float, quantidade_estoque
                    )
                    
                    if resultado:
                        # Se a atualização foi bem-sucedida
                        self.mostrar_mensagem("Sucesso", "Produto alterado com sucesso!")
                        
                        # Atualizar a tabela na tela principal
                        if hasattr(self.parent_widget, 'carregar_produtos'):
                            self.parent_widget.carregar_produtos()
                        
                        # Voltar para a tela anterior
                        self.voltar()
                    else:
                        self.mostrar_mensagem("Erro", "Erro ao atualizar o produto no banco de dados.")
                else:
                    self.mostrar_mensagem("Erro", "Produto original não encontrado para atualização.")
            else:
                # Modo de inclusão - criar novo produto no banco de dados
                
                # Não precisamos verificar se o código existe, pois agora é gerado automaticamente
                # e é somente leitura, garantindo que será único
                
                # Inserir no banco de dados
                resultado = criar_produto(
                    codigo, nome, barras, marca, grupo,
                    preco_compra_float, preco_venda_float, quantidade_estoque
                )
                
                if resultado:
                    # Se a criação foi bem-sucedida
                    self.mostrar_mensagem("Sucesso", "Produto cadastrado com sucesso!")
                    
                    # Atualizar a tabela na tela principal
                    if hasattr(self.parent_widget, 'carregar_produtos'):
                        self.parent_widget.carregar_produtos()
                    
                    # Limpar os campos para novo cadastro
                    self.nome_input.clear()
                    self.barras_input.clear()
                    self.marca_combo.setCurrentIndex(0)
                    self.preco_venda_input.clear()
                    self.preco_compra_input.clear()
                    self.grupo_combo.setCurrentIndex(0)
                    self.unidade_combo.setCurrentIndex(0)
                    self.estoque_input.setValue(0)  # Limpar campo de estoque
                    
                    # Atualizar o código para o próximo disponível
                    self.carregar_proximo_codigo()
                else:
                    self.mostrar_mensagem("Erro", "Erro ao cadastrar o produto no banco de dados.")
                    
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao salvar produto: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem personalizada"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        
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
        
        # Traduzir botões padrão para português
        for button in msg_box.buttons():
            if msg_box.buttonRole(button) == QMessageBox.AcceptRole:
                button.setText("OK")
            elif msg_box.buttonRole(button) == QMessageBox.RejectRole:
                button.setText("Cancelar")
        
        return msg_box.exec_()

# Adicione as novas classes para gerenciar marcas e grupos
# Coloque este código no início do arquivo formulario_produtos.py, após os imports

# A correção está na classe GerenciadorItensDialog

# A correção está na classe GerenciadorItensDialog

# A correção está na classe GerenciadorItensDialog

class GerenciadorItensDialog(QWidget):
    """Diálogo para gerenciar itens (marcas ou grupos)"""
    def __init__(self, parent=None, tipo="marca"):
        super().__init__(parent, Qt.Window)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.parent = parent
        self.tipo = tipo  # "marca" ou "grupo"
        self.item_selecionado = None
        self.items = []
        
        # Título e tamanho
        self.setWindowTitle(f"Gerenciar {self.tipo.title()}s")
        self.setGeometry(300, 300, 450, 400)
        self.setStyleSheet("background-color: #043b57;")
        
        # Carrega antes de construir a UI
        self.carregar_itens()
        self.initUI()
    
    def carregar_itens(self):
        """Carrega os itens do banco de dados"""
        try:
            if self.tipo == "marca":
                from base.banco import listar_marcas
                self.items = listar_marcas() or []
            else:
                from base.banco import listar_grupos
                self.items = listar_grupos() or []
        except Exception as e:
            print(f"Erro ao listar {self.tipo}s: {e}")
            # valores padrão
            self.items = ["Nestlé", "Unilever", "Procter & Gamble", "Coca-Cola"] \
                if self.tipo=="marca" else ["Alimentos","Bebidas","Limpeza","Higiene"]
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel(f"Gerenciar {self.tipo.title()}s")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Adicionar novo item
        add_layout = QHBoxLayout()
        self.novo_item_input = QLineEdit()
        self.novo_item_input.setPlaceholderText(f"Digite um novo {self.tipo}")
        self.novo_item_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
        """)
        add_layout.addWidget(self.novo_item_input)
        btn_adicionar = QPushButton("Adicionar")
        btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #00c853;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #009624; }
        """)
        btn_adicionar.clicked.connect(self.adicionar_item)
        add_layout.addWidget(btn_adicionar)
        layout.addLayout(add_layout)
        
        # Lista de itens
        label_lista = QLabel(f"Lista de {self.tipo}s cadastrados:")
        label_lista.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(label_lista)
        self.lista_itens = QListWidget()
        self.lista_itens.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
                color: black;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eaeaea;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.preencher_lista()
        self.lista_itens.itemClicked.connect(self.selecionar_item)
        layout.addWidget(self.lista_itens, 1)
        
        # Botões Editar / Excluir
        botoes_layout = QHBoxLayout()
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setEnabled(False)
        self.btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #0b7dda; }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_editar.clicked.connect(self.editar_item)
        botoes_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setEnabled(False)
        self.btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir_item)
        botoes_layout.addWidget(self.btn_excluir)
        layout.addLayout(botoes_layout)
        
        # Botão Fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 14px;
                border-radius: 4px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #003d5c; }
        """)
        btn_fechar.clicked.connect(self.close)
        layout.addWidget(btn_fechar)
    
    def preencher_lista(self):
        self.lista_itens.clear()
        for item in sorted(self.items):
            self.lista_itens.addItem(item)
    
    def selecionar_item(self, item):
        self.item_selecionado = item.text()
        self.btn_editar.setEnabled(True)
        self.btn_excluir.setEnabled(True)
    
    def adicionar_item(self):
        texto = self.novo_item_input.text().strip()
        if not texto:
            QMessageBox.warning(self, "Atenção", f"Digite o nome do {self.tipo}.")
            return
        if texto in self.items:
            QMessageBox.warning(self, "Atenção", f"Este {self.tipo} já existe.")
            return
        try:
            if self.tipo == "marca":
                from base.banco import adicionar_marca
                adicionar_marca(texto)
            else:
                from base.banco import adicionar_grupo
                adicionar_grupo(texto)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao adicionar: {e}")
            return
        self.items.append(texto)
        self.preencher_lista()
        self.novo_item_input.clear()
        self.atualizar_combobox_pai()  # Chamada corrigida
        # Mensagem de sucesso com estilo personalizado
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Sucesso")
        msg_box.setText(f"{self.tipo.title()} adicionado!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        
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
        
        # Traduzir botão para português
        btn_ok = msg_box.button(QMessageBox.Ok)
        btn_ok.setText("OK")
        
        msg_box.exec_()
    
    def editar_item(self):
        if not self.item_selecionado:
            return
        
        # Usar QInputDialog personalizado
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Editar")
        dialog.setLabelText(f"Novo nome para '{self.item_selecionado}':")
        dialog.setTextValue(self.item_selecionado)
        
        # Aplicar estilo personalizado
        dialog.setStyleSheet("""
            QInputDialog { 
                background-color: #043b57;
            }
            QLabel { 
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
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
        
        # Traduzir botões
        for button in dialog.findChildren(QPushButton):
            if button.text() == "OK":
                button.setText("OK")
            elif button.text() == "Cancel":
                button.setText("Cancelar")
                
        ok = dialog.exec_()
        novo = dialog.textValue().strip()
        
        if not (ok and novo):
            return
            
        if novo in self.items and novo != self.item_selecionado:
            QMessageBox.warning(self, "Atenção", f"Este {self.tipo} já existe.")
            return
        try:
            if self.tipo == "marca":
                from base.banco import atualizar_marca
                atualizar_marca(self.item_selecionado, novo)
            else:
                from base.banco import atualizar_grupo
                atualizar_grupo(self.item_selecionado, novo)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao editar: {e}")
            return
        idx = self.items.index(self.item_selecionado)
        self.items[idx] = novo
        self.preencher_lista()
        self.atualizar_combobox_pai()  # Chamada corrigida
        # Mensagem de sucesso com estilo personalizado
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Sucesso")
        msg_box.setText(f"{self.tipo.title()} atualizado!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        
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
        
        # Traduzir botão para português
        btn_ok = msg_box.button(QMessageBox.Ok)
        btn_ok.setText("OK")
        
        msg_box.exec_()
    
    def excluir_item(self):
        if not self.item_selecionado:
            return
            
        # Criar uma caixa de mensagem personalizada com estilo
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar")
        msg_box.setText(f"Excluir '{self.item_selecionado}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Personalizar os botões para Sim e Não
        btn_sim = msg_box.button(QMessageBox.Yes)
        btn_sim.setText("Sim")
        btn_nao = msg_box.button(QMessageBox.No)
        btn_nao.setText("Não")
        
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
        resp = msg_box.exec_()
            
        if resp != QMessageBox.Yes:
            return
        try:
            if self.tipo == "marca":
                from base.banco import excluir_marca
                excluir_marca(self.item_selecionado)
            else:
                from base.banco import excluir_grupo
                excluir_grupo(self.item_selecionado)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")
            return
        self.items.remove(self.item_selecionado)
        self.preencher_lista()
        self.item_selecionado = None
        self.btn_editar.setEnabled(False)
        self.btn_excluir.setEnabled(False)
        self.atualizar_combobox_pai()  # Chamada corrigida
        # Mensagem de sucesso com estilo personalizado
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Sucesso")
        msg_box.setText(f"{self.tipo.title()} excluído!")
        msg_box.setStandardButtons(QMessageBox.Ok)
        
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
        
        # Traduzir botão para português
        btn_ok = msg_box.button(QMessageBox.Ok)
        btn_ok.setText("OK")
        
        msg_box.exec_()

    
    def atualizar_combobox_pai(self):
        """Atualiza o combobox no formulário principal de forma segura"""
        if not self.parent:
            return
        
        try:    
            # Determinar qual combobox atualizar com base no tipo
            combobox = None
            texto_padrao = ""
            
            if self.tipo == "marca":
                if hasattr(self.parent, 'marca_combo'):
                    combobox = self.parent.marca_combo
                    texto_padrao = "Selecione uma marca"
            else:  # grupo
                if hasattr(self.parent, 'grupo_combo'):
                    combobox = self.parent.grupo_combo
                    texto_padrao = "Selecione um grupo"
            
            # Verificar se o combobox foi encontrado
            if combobox is not None:
                # Salvar o item selecionado atualmente
                try:
                    indice_atual = combobox.currentIndex()
                    texto_atual = combobox.currentText()
                    
                    # Limpar e preencher novamente
                    combobox.clear()
                    combobox.addItem(texto_padrao)
                    
                    for item in sorted(self.items):  # Ordenar alfabeticamente
                        combobox.addItem(item)
                    
                    # Tentar restaurar a seleção anterior
                    if texto_atual != texto_padrao and texto_atual in self.items:
                        indice = combobox.findText(texto_atual)
                        if indice >= 0:
                            combobox.setCurrentIndex(indice)
                    else:
                        combobox.setCurrentIndex(0)  # Selecionar o item padrão
                except Exception as e:
                    print(f"Erro ao atualizar combobox: {e}")
        except Exception as e:
            print(f"Erro ao atualizar combobox pai: {e}")
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        """Exibe uma caixa de mensagem personalizada"""
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        
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
        
        # Traduzir botões padrão para português
        for button in msg_box.buttons():
            if msg_box.buttonRole(button) == QMessageBox.AcceptRole:
                button.setText("OK")
            elif msg_box.buttonRole(button) == QMessageBox.RejectRole:
                button.setText("Cancelar")
        
        return msg_box.exec_()
    
# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Cadastro de Produtos")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    formulario_produtos_widget = FormularioProdutos(window)
    window.setCentralWidget(formulario_produtos_widget)
    
    window.show()
    sys.exit(app.exec_())