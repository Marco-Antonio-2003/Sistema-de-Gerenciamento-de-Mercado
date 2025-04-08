import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize


class Estoque(QWidget):
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
        titulo = QLabel("Estoque")
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
        
        # Estilo para QComboBox
        combobox_style = """
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
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #0078d7;
                selection-color: white;
            }
        """
        
        # Primeira linha: Código e Nome
        linha1_layout = QHBoxLayout()
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 16px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setFixedWidth(200)
        codigo_layout.addWidget(self.codigo_input)
        
        linha1_layout.addLayout(codigo_layout)
        
        # Espaçamento
        linha1_layout.addSpacing(30)
        
        # Campo Nome
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 16px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        nome_layout.addWidget(self.nome_input, 1)  # 1 para expandir
        
        linha1_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha: Marca e Grupo
        linha2_layout = QHBoxLayout()
        
        # Campo Marca
        marca_layout = QHBoxLayout()
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet("color: white; font-size: 16px;")
        marca_layout.addWidget(marca_label)
        
        self.marca_input = QLineEdit()
        self.marca_input.setStyleSheet(lineedit_style)
        marca_layout.addWidget(self.marca_input, 1)  # 1 para expandir
        
        linha2_layout.addLayout(marca_layout)
        
        # Espaçamento
        linha2_layout.addSpacing(30)
        
        # Campo Grupo
        grupo_layout = QHBoxLayout()
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet("color: white; font-size: 16px;")
        grupo_layout.addWidget(grupo_label)
        
        self.grupo_input = QComboBox()
        self.grupo_input.addItems(["Selecione um grupo", "Alimentos", "Bebidas", "Limpeza", "Higiene", "Eletrônicos", "Vestuário", "Outros"])
        self.grupo_input.setStyleSheet(combobox_style)
        grupo_layout.addWidget(self.grupo_input, 1)  # 1 para expandir
        
        linha2_layout.addLayout(grupo_layout)
        
        main_layout.addLayout(linha2_layout)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(15)
        
        # Estilo para os botões
        btn_style = """
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
                border: 1px solid #0078d7;
            }
        """
        
        # Botão Alterar
        btn_alterar = QPushButton("Alterar")
        try:
            btn_alterar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        except:
            pass
        btn_alterar.setStyleSheet(btn_style)
        btn_alterar.clicked.connect(self.alterar)
        acoes_layout.addWidget(btn_alterar)
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        try:
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet(btn_style)
        btn_excluir.clicked.connect(self.excluir)
        acoes_layout.addWidget(btn_excluir)
        
        # Botão Cadastrar
        btn_cadastrar = QPushButton("Cadastrar")
        try:
            btn_cadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        except:
            pass
        btn_cadastrar.setStyleSheet(btn_style)
        btn_cadastrar.clicked.connect(self.cadastrar)
        acoes_layout.addWidget(btn_cadastrar)
        
        main_layout.addLayout(acoes_layout)
        
        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Código", "Cliente", "Quant. Estoque", "Grupo", "Marca"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
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
        
        # Adicionar alguns dados de exemplo na tabela
        self.carregar_dados_exemplo()
        
        # Conectar evento de seleção de linha na tabela
        self.tabela.itemClicked.connect(self.selecionar_item)
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela"""
        dados = [
            ("001", "Notebook Dell", "10", "Eletrônicos", "Dell"),
            ("002", "Smartphone Galaxy", "15", "Eletrônicos", "Samsung"),
            ("003", "Camiseta Polo", "25", "Vestuário", "Lacoste"),
            ("004", "Sabão em Pó", "30", "Limpeza", "OMO"),
            ("005", "Refrigerante Cola", "50", "Bebidas", "Coca-Cola")
        ]
        
        self.tabela.setRowCount(len(dados))
        for row, (codigo, nome, quantidade, grupo, marca) in enumerate(dados):
            self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(quantidade))
            self.tabela.setItem(row, 3, QTableWidgetItem(grupo))
            self.tabela.setItem(row, 4, QTableWidgetItem(marca))
    
    def selecionar_item(self, item):
        """Quando um item da tabela é selecionado, preenche os campos"""
        row = item.row()
        
        # Preencher os campos com os dados da linha selecionada
        self.codigo_input.setText(self.tabela.item(row, 0).text())
        self.nome_input.setText(self.tabela.item(row, 1).text())
        
        # Definir o grupo
        grupo_selecionado = self.tabela.item(row, 3).text()
        index = self.grupo_input.findText(grupo_selecionado)
        if index >= 0:
            self.grupo_input.setCurrentIndex(index)
        
        # Definir a marca
        self.marca_input.setText(self.tabela.item(row, 4).text())
    
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
    
    def alterar(self):
        """Ação do botão alterar"""
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um produto para alterar!")
            return
        
        # Obter a linha selecionada
        row = self.tabela.currentRow()
        
        # Validar campos
        if not self.codigo_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o código!")
            return
        
        if not self.nome_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o nome!")
            return
        
        if not self.marca_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe a marca!")
            return
        
        if self.grupo_input.currentIndex() == 0:
            self.mostrar_mensagem("Atenção", "Por favor, selecione um grupo!")
            return
        
        # Atualizar dados na tabela
        self.tabela.item(row, 0).setText(self.codigo_input.text())
        self.tabela.item(row, 1).setText(self.nome_input.text())
        self.tabela.item(row, 3).setText(self.grupo_input.currentText())
        self.tabela.item(row, 4).setText(self.marca_input.text())
        
        self.mostrar_mensagem("Sucesso", "Produto alterado com sucesso!")
        
        # Limpar os campos
        self.limpar_campos()
    
    def excluir(self):
        """Ação do botão excluir"""
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um produto para excluir!")
            return
        
        # Obter a linha selecionada
        row = self.tabela.currentRow()
        codigo = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        
        # Confirmar exclusão
        from PyQt5.QtWidgets import QMessageBox
        confirma = QMessageBox()
        confirma.setIcon(QMessageBox.Question)
        confirma.setWindowTitle("Confirmar Exclusão")
        confirma.setText(f"Deseja realmente excluir o produto {codigo} - {nome}?")
        confirma.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirma.setStyleSheet("""
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
        
        resposta = confirma.exec_()
        
        if resposta == QMessageBox.Yes:
            # Remover a linha da tabela
            self.tabela.removeRow(row)
            self.mostrar_mensagem("Sucesso", "Produto excluído com sucesso!")
            
            # Limpar os campos
            self.limpar_campos()
    
    def cadastrar(self):
        """Ação do botão cadastrar"""
        # Validar campos
        if not self.codigo_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o código!")
            return
        
        if not self.nome_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o nome!")
            return
        
        if not self.marca_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe a marca!")
            return
        
        if self.grupo_input.currentIndex() == 0:
            self.mostrar_mensagem("Atenção", "Por favor, selecione um grupo!")
            return
        
        # Verificar se o código já existe
        for row in range(self.tabela.rowCount()):
            if self.tabela.item(row, 0).text() == self.codigo_input.text():
                self.mostrar_mensagem("Atenção", "Este código de produto já existe!")
                return
        
        # Adicionar nova linha na tabela
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)
        
        # Criar itens para a nova linha
        self.tabela.setItem(row, 0, QTableWidgetItem(self.codigo_input.text()))
        self.tabela.setItem(row, 1, QTableWidgetItem(self.nome_input.text()))
        self.tabela.setItem(row, 2, QTableWidgetItem("0"))  # Quantidade inicial
        self.tabela.setItem(row, 3, QTableWidgetItem(self.grupo_input.currentText()))
        self.tabela.setItem(row, 4, QTableWidgetItem(self.marca_input.text()))
        
        self.mostrar_mensagem("Sucesso", "Produto cadastrado com sucesso!")
        
        # Limpar os campos
        self.limpar_campos()
    
    def limpar_campos(self):
        """Limpa os campos do formulário"""
        self.codigo_input.clear()
        self.nome_input.clear()
        self.marca_input.clear()
        self.grupo_input.setCurrentIndex(0)
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        from PyQt5.QtWidgets import QMessageBox
        
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
    window.setWindowTitle("Sistema - Estoque")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    estoque_widget = Estoque(window)  # Passa a janela como parent
    window.setCentralWidget(estoque_widget)
    
    window.show()
    sys.exit(app.exec_())