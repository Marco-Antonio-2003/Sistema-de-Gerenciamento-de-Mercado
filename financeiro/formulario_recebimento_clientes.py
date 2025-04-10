#formulario_recebimento_clientes.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QMessageBox, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize


class FormularioRecebimentoClientes(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
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
        titulo = QLabel("Recebimento de Clientes")
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
        
        # Layout para Código e Cliente
        campos_layout = QHBoxLayout()
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 16px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setFixedWidth(200)
        codigo_layout.addWidget(self.codigo_input)
        
        campos_layout.addLayout(codigo_layout)
        
        # Espaçamento
        campos_layout.addSpacing(30)
        
        # Campo Cliente
        cliente_layout = QHBoxLayout()
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        cliente_layout.addWidget(cliente_label)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setStyleSheet(lineedit_style)
        cliente_layout.addWidget(self.cliente_input, 1)  # 1 para expandir
        
        campos_layout.addLayout(cliente_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(campos_layout)
        
        # Tabela de títulos pendentes
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Código", "Cliente", "Vencimento", "Vr. Pago"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                gridline-color: #cccccc;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        main_layout.addWidget(self.tabela)
        
        # Layout para Valor e botão Salvar
        rodape_layout = QHBoxLayout()
        
        # Campo Valor
        valor_layout = QHBoxLayout()
        valor_label = QLabel("Valor:")
        valor_label.setStyleSheet("color: white; font-size: 16px;")
        valor_layout.addWidget(valor_label)
        
        self.valor_input = QLineEdit()
        self.valor_input.setStyleSheet(lineedit_style)
        self.valor_input.setFixedWidth(200)
        valor_layout.addWidget(self.valor_input)
        
        rodape_layout.addLayout(valor_layout)
        
        # Espaçamento
        rodape_layout.addStretch()
        
        # Botão Salvar
        btn_salvar = QPushButton("Salvar")
        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00E676;
                color: black;
                border: none;
                padding: 15px 20px;
                font-size: 16px;
                border-radius: 4px;
                text-align: center;
                min-width: 500px;
            }
            QPushButton:hover {
                background-color: #00C853;
            }
        """)
        btn_salvar.clicked.connect(self.salvar)
        rodape_layout.addWidget(btn_salvar)
        
        main_layout.addLayout(rodape_layout)
        
        # Carregar dados de exemplo na tabela
        self.carregar_dados_exemplo()
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        dados = [
            ("001", "Empresa ABC Ltda", "01/04/2025", "R$ 5.000,00"),
            ("002", "João Silva", "02/04/2025", "R$ 1.200,00"),
            ("003", "Distribuidora XYZ", "03/04/2025", "R$ 3.500,00"),
            ("004", "Ana Souza", "04/04/2025", "R$ 750,00"),
            ("005", "Mercado Central", "05/04/2025", "R$ 2.100,00")
        ]
        
        self.tabela.setRowCount(len(dados))
        for row, (codigo, cliente, vencimento, valor) in enumerate(dados):
            self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente))
            self.tabela.setItem(row, 2, QTableWidgetItem(vencimento))
            self.tabela.setItem(row, 3, QTableWidgetItem(valor))
            
        # Conectar evento de seleção de linha na tabela
        self.tabela.itemClicked.connect(self.selecionar_item)
    
    def selecionar_item(self, item):
        """Quando um item da tabela é selecionado, preenche os campos"""
        row = item.row()
        
        # Preencher os campos com os dados da linha selecionada
        self.codigo_input.setText(self.tabela.item(row, 0).text())
        self.cliente_input.setText(self.tabela.item(row, 1).text())
        self.valor_input.setText(self.tabela.item(row, 3).text().replace("R$ ", ""))
    
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
    
    def salvar(self):
        """Ação do botão salvar"""
        # Verificar se todos os campos obrigatórios foram preenchidos
        if not self.codigo_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o código!")
            return
        
        if not self.cliente_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o cliente!")
            return
        
        if not self.valor_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o valor!")
            return
        
        # Verificar se algum item da tabela está selecionado
        if self.tabela.selectedItems():
            row = self.tabela.currentRow()
            
            # Mostrar mensagem de confirmação
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowTitle("Confirmação")
            msgBox.setText(f"Confirma a baixa do título do cliente {self.cliente_input.text()}?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setStyleSheet("""
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
            resposta = msgBox.exec_()
            
            if resposta == QMessageBox.Yes:
                # Remover o item da tabela (simulando a baixa)
                self.tabela.removeRow(row)
                
                # Enviar para a tela de recebimento de clientes
                try:
                    # Aqui simulamos o envio para a tela de recebimento
                    print(f"Título baixado: {self.codigo_input.text()} - {self.cliente_input.text()} - Valor: {self.valor_input.text()}")
                    
                    # Limpar os campos
                    self.codigo_input.clear()
                    self.cliente_input.clear()
                    self.valor_input.clear()
                    
                    # Mostrar mensagem de sucesso
                    self.mostrar_mensagem("Sucesso", "Baixa realizada com sucesso!")
                    
                    # Fechar o formulário após a baixa
                    if self.janela_parent:
                        self.janela_parent.close()
                except Exception as e:
                    self.mostrar_mensagem("Erro", f"Erro ao dar baixa: {str(e)}")
        else:
            self.mostrar_mensagem("Atenção", "Selecione um título na tabela para dar baixa!")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Sucesso" in titulo:
            msg_box.setIcon(QMessageBox.Information)
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
    window.setWindowTitle("Sistema - Recebimento de Clientes")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    recebimento_widget = FormularioRecebimentoClientes(window)  # Passa a janela como parent
    window.setCentralWidget(recebimento_widget)
    
    window.show()
    sys.exit(app.exec_())