import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QDateEdit, QMessageBox, QFrame)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QDate


class FormularioPedidoVendas(QWidget):
    def __init__(self, janela_parent=None, num_pedido=None, cliente=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.num_pedido = num_pedido
        self.cliente = cliente
        self.initUI()
        
        # Se estiver alterando um pedido existente, preencher os campos
        if self.num_pedido and self.cliente:
            self.preencher_campos()
        
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
        titulo = QLabel("Cadastro de Pedido de vendas")
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
        
        # Estilo para DateEdit
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
                border: none;
            }
        """
        
        # Primeira linha - Número do Pedido e Cliente
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(10)
        
        # Campo Número do Pedido
        num_pedido_label = QLabel("Num. Pedido:")
        num_pedido_label.setStyleSheet("color: white; font-size: 16px;")
        linha1_layout.addWidget(num_pedido_label)
        
        self.num_pedido_input = QLineEdit()
        self.num_pedido_input.setStyleSheet(lineedit_style)
        self.num_pedido_input.setFixedWidth(150)
        if self.num_pedido:
            self.num_pedido_input.setText(self.num_pedido)
        linha1_layout.addWidget(self.num_pedido_input)
        
        # Campo Cliente
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        linha1_layout.addWidget(cliente_label)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setStyleSheet(lineedit_style)
        if self.cliente:
            self.cliente_input.setText(self.cliente)
        linha1_layout.addWidget(self.cliente_input, 1)
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha - Vendedor e Valor
        linha2_layout = QHBoxLayout()
        linha2_layout.setSpacing(10)
        
        # Campo Vendedor
        vendedor_label = QLabel("Vendedor:")
        vendedor_label.setStyleSheet("color: white; font-size: 16px;")
        linha2_layout.addWidget(vendedor_label)
        
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setStyleSheet(lineedit_style)
        linha2_layout.addWidget(self.vendedor_input, 1)
        
        # Campo Valor
        valor_label = QLabel("Valor:")
        valor_label.setStyleSheet("color: white; font-size: 16px;")
        linha2_layout.addWidget(valor_label)
        
        self.valor_input = QLineEdit()
        self.valor_input.setStyleSheet(lineedit_style)
        self.valor_input.setFixedWidth(150)
        linha2_layout.addWidget(self.valor_input)
        
        main_layout.addLayout(linha2_layout)
        
        # Terceira linha - Produto e Data
        linha3_layout = QHBoxLayout()
        linha3_layout.setSpacing(10)
        
        # Campo Produto
        produto_label = QLabel("Produto:")
        produto_label.setStyleSheet("color: white; font-size: 16px;")
        linha3_layout.addWidget(produto_label)
        
        self.produto_input = QLineEdit()
        self.produto_input.setStyleSheet(lineedit_style)
        linha3_layout.addWidget(self.produto_input, 1)
        
        # Campo Data
        data_label = QLabel("Data:")
        data_label.setStyleSheet("color: white; font-size: 16px;")
        linha3_layout.addWidget(data_label)
        
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setStyleSheet(dateedit_style)
        linha3_layout.addWidget(self.data_input)
        
        main_layout.addLayout(linha3_layout)
        
        # Botão Incluir
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
        # Aqui você pode implementar a lógica para buscar os dados completos
        # do pedido e preencher todos os campos. Por agora, vamos simular alguns dados
        self.vendedor_input.setText("Carlos")
        self.valor_input.setText("R$ 2.450,00")
        self.produto_input.setText("Produto XYZ")
        
        # Mudando o texto do botão para indicar alteração
        self.btn_incluir.setText("Alterar")
    
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
    
    def incluir(self):
        """Inclui ou altera um pedido"""
        # Validar campos obrigatórios
        num_pedido = self.num_pedido_input.text()
        cliente = self.cliente_input.text()
        vendedor = self.vendedor_input.text()
        valor = self.valor_input.text()
        produto = self.produto_input.text()
        
        if not num_pedido or not cliente or not vendedor or not valor or not produto:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos obrigatórios!")
            return
        
        # Aqui você implementaria a lógica para salvar os dados
        # Por agora, vamos apenas mostrar uma mensagem de sucesso
        
        # Verificar se é inclusão ou alteração
        if self.num_pedido:
            mensagem = "Pedido alterado com sucesso!"
        else:
            mensagem = "Pedido incluído com sucesso!"
        
        self.mostrar_mensagem("Sucesso", mensagem)
        
        # Fechar a janela após a inclusão/alteração
        if self.janela_parent:
            self.janela_parent.close()
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
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


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Cadastro de Pedido de Vendas")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    formulario_pedido_widget = FormularioPedidoVendas(window)  # Passa a janela como parent
    window.setCentralWidget(formulario_pedido_widget)
    
    window.show()
    sys.exit(app.exec_())