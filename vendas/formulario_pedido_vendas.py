import sys
import os
from datetime import datetime

# Corrigir a importação - garantindo que o módulo base seja encontrado
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QDateEdit, 
                           QMessageBox, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QDate

# Importar funções do banco de dados
try:
    from base.banco import (buscar_pedido_por_id, buscar_pedido_por_numero,
                      criar_pedido, atualizar_pedido, obter_vendedores_pedidos,
                      obter_clientes_pedidos, obter_cidades_pedidos,
                      listar_funcionarios, listar_pessoas, listar_produtos)
except ImportError as e:
    print(f"Erro ao importar funções do banco: {e}")
    # Se você está executando este arquivo diretamente para teste, pode querer comentar isso


# Classe para os ComboBox editáveis
class ComboBoxEditavel(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxEditavel, self).__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer().setCaseSensitivity(Qt.CaseInsensitive)
        
        # Estilo do ComboBox
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
                image: url(ico-img/arrow-down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #fffff0;
                selection-background-color: #0078d7;
                selection-color: white;
                border: 1px solid #cccccc;
            }
        """)


# Formulário de Pedido de Vendas
class FormularioPedidoVendas(QWidget):
    def __init__(self, janela_parent=None, num_pedido=None, cliente=None, tela_principal=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.num_pedido = num_pedido
        self.cliente = cliente
        self.pedido_id = None
        self.tela_principal = tela_principal  # Nova referência para a tela principal
        self.initUI()
        
        # Se estiver alterando um pedido existente, preencher os campos
        if self.num_pedido:
            self.preencher_campos()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
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
        titulo = QLabel("Cadastro de Pedido de vendas")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para DateEdit com ícone de calendário
        dateedit_style = """
            QDateEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QDateEdit:focus {
                border: 1px solid #0078d7;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QDateEdit::down-arrow {
                image: url(ico-img/calendar-outline.svg);
                width: 12px;
                height: 12px;
            }
        """
        
        # Primeira linha - Número do Pedido e Cliente
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(10)
        
        # Campo Número do Pedido
        num_pedido_label = QLabel("Num. Pedido:")
        num_pedido_label.setStyleSheet("color: white; font-size: 16px;")
        num_pedido_label.setFixedWidth(110)  # Fixar largura para alinhamento
        linha1_layout.addWidget(num_pedido_label)
        
        self.num_pedido_input = QLineEdit()
        self.num_pedido_input.setStyleSheet("""
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
        """)
        self.num_pedido_input.setFixedWidth(150)
        self.num_pedido_input.setReadOnly(True)  # Número do pedido é gerado automaticamente
        
        # Se for um novo pedido, gerar automaticamente
        if not self.num_pedido:
            try:
                from base.banco import gerar_numero_pedido
                self.num_pedido = gerar_numero_pedido()
            except Exception as e:
                print(f"Erro ao gerar número de pedido: {e}")
                self.num_pedido = "00000"
        
        self.num_pedido_input.setText(self.num_pedido)
        linha1_layout.addWidget(self.num_pedido_input)
        
        # Campo Cliente (ComboBox Editável)
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        cliente_label.setFixedWidth(60)  # Fixar largura para alinhamento
        linha1_layout.addWidget(cliente_label)
        
        self.cliente_input = ComboBoxEditavel()
        
        # Preencher com clientes existentes
        try:
            clientes = obter_clientes_pedidos()
            self.cliente_input.addItems(clientes)
            # Adicionar também clientes da tabela PESSOAS
            from base.banco import listar_pessoas
            pessoas = listar_pessoas()
            for pessoa in pessoas:
                if pessoa[1] not in clientes:  # Evitar duplicatas (índice 1 = nome)
                    self.cliente_input.addItem(pessoa[1])
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
        
        if self.cliente:
            # Definir o cliente atual
            index = self.cliente_input.findText(self.cliente)
            if index >= 0:
                self.cliente_input.setCurrentIndex(index)
            else:
                self.cliente_input.setCurrentText(self.cliente)
                
        linha1_layout.addWidget(self.cliente_input, 1)
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha - Vendedor e Valor
        linha2_layout = QHBoxLayout()
        linha2_layout.setSpacing(10)
        
        # Campo Vendedor (ComboBox Editável)
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        vendedor_label.setFixedWidth(110)  # Fixar largura para alinhamento
        linha2_layout.addWidget(vendedor_label)
        
        self.vendedor_input = ComboBoxEditavel()
        
        # Preencher com vendedores existentes
        try:
            # Obter vendedores de pedidos anteriores
            vendedores = obter_vendedores_pedidos()
            
            # Obter funcionários da tabela FUNCIONARIOS
            funcionarios = listar_funcionarios()
            
            # Combinar as listas, evitando duplicatas
            todos_vendedores = set(vendedores)
            for funcionario in funcionarios:
                todos_vendedores.add(funcionario[1])  # Nome do funcionário
            
            # Adicionar ao combobox
            self.vendedor_input.addItems(sorted(todos_vendedores))
        except Exception as e:
            print(f"Erro ao carregar vendedores: {e}")
        
        linha2_layout.addWidget(self.vendedor_input, 1)
        
        # Campo Valor
        valor_label = QLabel("Valor:")
        valor_label.setStyleSheet("color: white; font-size: 16px;")
        valor_label.setFixedWidth(60)  # Fixar largura para alinhamento
        linha2_layout.addWidget(valor_label)
        
        self.valor_input = QLineEdit()
        self.valor_input.setStyleSheet("""
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
        """)
        self.valor_input.setFixedWidth(150)
        self.valor_input.setPlaceholderText("0,00")
        linha2_layout.addWidget(self.valor_input)
        
        main_layout.addLayout(linha2_layout)
        
        # Terceira linha - Cidade e Produto
        linha3_layout = QHBoxLayout()
        linha3_layout.setSpacing(10)
        
        # Campo Cidade (ComboBox Editável)
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet("color: white; font-size: 16px;")
        cidade_label.setFixedWidth(110)  # Fixar largura para alinhamento
        linha3_layout.addWidget(cidade_label)
        
        self.cidade_input = ComboBoxEditavel()
        
        # Preencher com cidades existentes
        try:
            # Obter cidades de pedidos anteriores
            cidades_pedidos = obter_cidades_pedidos()
            
            # Obter cidades das pessoas cadastradas
            from base.banco import listar_pessoas
            pessoas = listar_pessoas()
            
            # Combinar as listas, evitando duplicatas
            todas_cidades = set(cidades_pedidos)
            for pessoa in pessoas:
                cidade = pessoa[9] if len(pessoa) > 9 else None  # Índice da cidade
                if cidade and cidade.strip():
                    todas_cidades.add(cidade)
            
            # Adicionar ao combobox
            self.cidade_input.addItems(sorted(todas_cidades))
        except Exception as e:
            print(f"Erro ao carregar cidades: {e}")
        
        linha3_layout.addWidget(self.cidade_input, 1)
        
        # Campo Produto (ComboBox Editável)
        produto_label = QLabel("Produto:")
        produto_label.setStyleSheet("color: white; font-size: 16px;")
        produto_label.setFixedWidth(60)  # Fixar largura para alinhamento
        linha3_layout.addWidget(produto_label)
        
        self.produto_input = ComboBoxEditavel()
        
        # Preencher com produtos existentes
        try:
            # Obter produtos do banco
            produtos = listar_produtos()
            produto_nomes = []
            for produto in produtos:
                produto_nomes.append(produto[2])  # Nome do produto (índice 2)
            self.produto_input.addItems(sorted(produto_nomes))
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
        
        linha3_layout.addWidget(self.produto_input, 1)
        
        main_layout.addLayout(linha3_layout)
        
        # Quarta linha - Data
        linha4_layout = QHBoxLayout()
        linha4_layout.setSpacing(10)
        
        # Campo Data
        data_label = QLabel("Data:")
        data_label.setStyleSheet("color: white; font-size: 16px;")
        data_label.setFixedWidth(110)  # Fixar largura para alinhamento
        linha4_layout.addWidget(data_label)
        
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setStyleSheet(dateedit_style)
        self.data_input.setFixedWidth(150)
        
        # Configurar calendário
        try:
            calendar = self.data_input.calendarWidget()
            calendar.setStyleSheet("""
                QCalendarWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QWidget {
                    background-color: #003b57;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    background-color: #003b57;
                    color: white;
                    selection-background-color: #005079;
                    selection-color: white;
                }
                QCalendarWidget QToolButton {
                    background-color: #003b57;
                    color: white;
                }
                QCalendarWidget QMenu {
                    background-color: #003b57;
                    color: white;
                }
            """)
        except:
            pass
            
        linha4_layout.addWidget(self.data_input)
        
        # Adicionar um espaço para alinhar com as outras linhas
        linha4_layout.addStretch(1)
        
        main_layout.addLayout(linha4_layout)
        
        # Botão Incluir (sempre "Incluir" como solicitado)
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 15px 0;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 20px 0;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
            QPushButton:pressed {
                background-color: #00cc7a;
            }
        """)
        self.btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(self.btn_incluir)
        
        # Adicionar espaço no final
        main_layout.addStretch()
    
    def preencher_campos(self):
        """Preenche os campos com os dados do pedido para alteração"""
        try:
            # Buscar dados do pedido pelo número
            pedido = buscar_pedido_por_numero(self.num_pedido)
            
            if pedido:
                self.pedido_id = pedido[0]  # Salvar o ID para atualização
                
                # Preencher campos com os dados do pedido
                # ID, NUMERO_PEDIDO, CLIENTE, CLIENTE_ID, VENDEDOR, VENDEDOR_ID, 
                # VALOR, PRODUTO, PRODUTO_ID, DATA_PEDIDO, CIDADE, STATUS, OBSERVACAO
                
                # Cliente (índice 2)
                cliente = pedido[2]
                index = self.cliente_input.findText(cliente)
                if index >= 0:
                    self.cliente_input.setCurrentIndex(index)
                else:
                    self.cliente_input.setCurrentText(cliente)
                
                # Vendedor (índice 4)
                vendedor = pedido[4]
                index = self.vendedor_input.findText(vendedor)
                if index >= 0:
                    self.vendedor_input.setCurrentIndex(index)
                else:
                    self.vendedor_input.setCurrentText(vendedor)
                
                # Valor (índice 6)
                valor = pedido[6]
                if valor is not None:
                    # Formatar como moeda
                    valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    self.valor_input.setText(valor_formatado)
                
                # Produto (índice 7)
                produto = pedido[7]
                if produto:
                    index = self.produto_input.findText(produto)
                    if index >= 0:
                        self.produto_input.setCurrentIndex(index)
                    else:
                        self.produto_input.setCurrentText(produto)
                
                # Data (índice 9)
                data_pedido = pedido[9]
                if data_pedido:
                    try:
                        # Converter data para QDate
                        if isinstance(data_pedido, str):
                            # Se for string, converter para QDate
                            data_parts = data_pedido.split('/')
                            qdate = QDate(int(data_parts[2]), int(data_parts[1]), int(data_parts[0]))
                        else:
                            # Se for datetime
                            qdate = QDate(data_pedido.year, data_pedido.month, data_pedido.day)
                        self.data_input.setDate(qdate)
                    except Exception as e:
                        print(f"Erro ao converter data: {e}")
                
                # Cidade (índice 10)
                cidade = pedido[10]
                if cidade:
                    index = self.cidade_input.findText(cidade)
                    if index >= 0:
                        self.cidade_input.setCurrentIndex(index)
                    else:
                        self.cidade_input.setCurrentText(cidade)
                
        except Exception as e:
            print(f"Erro ao preencher campos do pedido: {e}")
            self.mostrar_mensagem("Erro", f"Não foi possível carregar os dados do pedido: {str(e)}")
            
    def incluir(self):
        """Inclui ou altera um pedido"""
        # Obter os dados dos campos
        num_pedido = self.num_pedido_input.text()
        cliente = self.cliente_input.currentText()
        vendedor = self.vendedor_input.currentText()
        valor = self.valor_input.text()
        produto = self.produto_input.currentText()
        cidade = self.cidade_input.currentText()
        
        # Obter a data do pedido
        data_pedido = self.data_input.date().toString("dd/MM/yyyy")
        
        # Validar campos obrigatórios
        if not num_pedido or not cliente or not vendedor:
            self.mostrar_mensagem("Atenção", "Preencha os campos obrigatórios: Número do Pedido, Cliente e Vendedor!")
            return
        
        try:
            # Tratar o valor (remover formatação monetária)
            if valor:
                # Remover caracteres não numéricos e converter virgula para ponto
                valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
            
            if self.pedido_id:  # Alteração de pedido existente
                # Atualizar pedido
                try:
                    sucesso = atualizar_pedido(
                        self.pedido_id,
                        cliente=cliente,
                        vendedor=vendedor,
                        valor=valor,
                        produto=produto,
                        data_pedido=data_pedido,
                        cidade=cidade
                    )
                    
                    if sucesso:
                        mensagem = "Pedido alterado com sucesso!"
                    else:
                        mensagem = "Não foi possível alterar o pedido!"
                        self.mostrar_mensagem("Erro", mensagem)
                        return
                except Exception as e:
                    print(f"Erro detalhado ao atualizar pedido: {e}")
                    self.mostrar_mensagem("Erro", f"Não foi possível atualizar o pedido: {str(e)}")
                    return
            else:  # Criação de novo pedido
                # Criar novo pedido sem o parâmetro id
                try:
                    novo_numero_pedido = criar_pedido(
                        cliente=cliente,
                        cliente_id=None, 
                        vendedor=vendedor,
                        vendedor_id=None,
                        valor=valor,
                        produto=produto,
                        produto_id=None,
                        data_pedido=data_pedido,
                        cidade=cidade
                    )
                    
                    if novo_numero_pedido:
                        mensagem = f"Pedido {novo_numero_pedido} incluído com sucesso!"
                    else:
                        mensagem = "Não foi possível incluir o pedido!"
                        self.mostrar_mensagem("Erro", mensagem)
                        return
                except Exception as e:
                    print(f"Erro detalhado ao criar pedido: {e}")
                    self.mostrar_mensagem("Erro", f"Não foi possível incluir o pedido: {str(e)}")
                    return
            
            # Mostrar mensagem de sucesso
            self.mostrar_mensagem("Sucesso", mensagem)
            
            # Atualizar a tabela na tela principal diretamente
            if self.tela_principal is not None and hasattr(self.tela_principal, 'atualizar_apos_inclusao'):
                print("Chamando método atualizar_apos_inclusao")
                self.tela_principal.atualizar_apos_inclusao()
            else:
                print("Referência para tela principal não encontrada ou método não disponível")
            
            # Fechar a janela após a inclusão/alteração
            if self.janela_parent:
                self.janela_parent.close()
                
        except Exception as e:
            print(f"Erro ao salvar pedido: {e}")
            self.mostrar_mensagem("Erro", f"Não foi possível salvar o pedido: {str(e)}")
            
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
                background-color: #003b57;
            }
            QLabel { 
                color: white;
                background-color: #003b57;
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


# Para testar o formulário diretamente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Criar a janela principal
    window = QMainWindow()
    window.setWindowTitle("Cadastro de Pedido de vendas")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    # Criar o widget de formulário
    formulario_widget = FormularioPedidoVendas(window)
    window.setCentralWidget(formulario_widget)
    
    # Mostrar a janela
    window.show()
    
    # Iniciar o loop de eventos
    sys.exit(app.exec_())