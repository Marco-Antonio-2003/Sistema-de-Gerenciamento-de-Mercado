import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QCheckBox, QDialog,
                             QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

class ClasseFinanceira(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho com título
        header_layout = QHBoxLayout()
        
        # Botão Voltar
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_voltar.setMinimumWidth(70)
        self.btn_voltar.clicked.connect(self.voltar)
        header_layout.addWidget(self.btn_voltar)
        
        # Título
        title_label = QLabel("Classe Financeira")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-left: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label, 1)  # 1 = stretch factor
        
        # Adicionar espaço à direita para balancear o botão voltar
        spacer = QWidget()
        spacer.setMinimumWidth(70)
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Formulário de filtros
        filtros_frame = QFrame()
        filtros_frame.setFrameShape(QFrame.StyledPanel)
        filtros_frame.setStyleSheet("""
            QFrame {
                background-color: #003353;
                border: 1px solid #00253e;
                border-radius: 5px;
            }
        """)
        
        filtros_layout = QHBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(15, 15, 15, 15)
        filtros_layout.setSpacing(10)
        
        # Código
        codigo_label = QLabel("Código:")
        codigo_label.setFont(QFont("Arial", 11))
        codigo_label.setStyleSheet("color: white;")
        filtros_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 12px;
                min-height: 18px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        self.codigo_input.setFixedWidth(100)
        filtros_layout.addWidget(self.codigo_input)
        
        # Espaço entre código e descrição
        filtros_layout.addSpacing(20)
        
        # Descrição
        descricao_label = QLabel("Descrição:")
        descricao_label.setFont(QFont("Arial", 11))
        descricao_label.setStyleSheet("color: white;")
        filtros_layout.addWidget(descricao_label)
        
        self.descricao_input = QLineEdit()
        self.descricao_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 12px;
                min-height: 18px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        self.descricao_input.setMinimumWidth(250)
        filtros_layout.addWidget(self.descricao_input)
        
        main_layout.addWidget(filtros_frame)
        
        # Tabela de classes financeiras
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Código", "Descrição"])
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #cccccc;
            }
        """)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffff0;
                alternate-background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Ajustar largura das colunas
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        self.table.itemClicked.connect(self.selecionar_linha)
        
        main_layout.addWidget(self.table)
        
        # Botões de controle
        btn_control_layout = QHBoxLayout()
        btn_control_layout.addStretch(1)  # Adiciona espaço elástico à esquerda
        
        # Botão Alterar
        self.btn_alterar = QPushButton("Alterar")
        self.btn_alterar.setIcon(QIcon("ico-img/pencil-outline.svg"))
        self.btn_alterar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 6px 12px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_alterar.clicked.connect(self.alterar_classe)
        btn_control_layout.addWidget(self.btn_alterar)
        
        # Espaçamento entre botões
        btn_control_layout.addSpacing(10)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setIcon(QIcon("ico-img/trash-outline.svg"))
        self.btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 6px 12px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir_classe)
        btn_control_layout.addWidget(self.btn_excluir)
        
        # Espaçamento entre botões
        btn_control_layout.addSpacing(10)
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setIcon(QIcon("ico-img/plus-circle-outline.svg"))
        self.btn_cadastrar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 6px 12px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_cadastrar.clicked.connect(self.cadastrar_classe)
        btn_control_layout.addWidget(self.btn_cadastrar)
        
        main_layout.addLayout(btn_control_layout)
        
        # Carregar dados de teste
        self.carregar_dados_teste()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #003353; }")
        
    def carregar_dados_teste(self):
        # Dados de exemplo para a tabela
        dados = [
            ("001", "DESPESAS OPERACIONAIS"),
            ("002", "DESPESAS ADMINISTRATIVAS"),
            ("003", "RECEITAS"),
            ("004", "INVESTIMENTOS")
        ]
        
        self.table.setRowCount(len(dados))
        
        for row, (codigo, descricao) in enumerate(dados):
            self.table.setItem(row, 0, QTableWidgetItem(codigo))
            self.table.setItem(row, 1, QTableWidgetItem(descricao))
    
    def selecionar_linha(self, item):
        # Implementar ações quando uma linha é selecionada
        row = item.row()
        codigo = self.table.item(row, 0).text()
        descricao = self.table.item(row, 1).text()
        
        # Preencher os campos de filtro com os dados da linha selecionada
        self.codigo_input.setText(codigo)
        self.descricao_input.setText(descricao)
        
    def voltar(self):
        """Fecha a tela atual quando o botão voltar for clicado"""
        self.window().close()
    
    def cadastrar_classe(self):
        """Abre o formulário para cadastrar nova classe financeira"""
        dialog = FormularioClasseFinanceira(self)
        result = dialog.exec_()
        
        # Se o diálogo foi aceito (usuário clicou em Incluir/Salvar)
        if result == QDialog.Accepted:
            # Obter os dados do formulário e adicionar à tabela
            codigo = dialog.codigo_edit.text().strip()
            descricao = dialog.descricao_edit.text().strip()
            
            # Adicionar nova linha na tabela
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(codigo))
            self.table.setItem(row_position, 1, QTableWidgetItem(descricao))
    
    def alterar_classe(self):
        """Abre o formulário para alterar classe financeira selecionada"""
        row = self.table.currentRow()
        if row >= 0:
            codigo = self.table.item(row, 0).text()
            descricao = self.table.item(row, 1).text()
            
            dialog = FormularioClasseFinanceira(self, codigo=codigo, descricao=descricao, modo_edicao=True)
            result = dialog.exec_()
            
            # Se o diálogo foi aceito (usuário clicou em Salvar)
            if result == QDialog.Accepted:
                # Obter os dados atualizados do formulário
                novo_codigo = dialog.codigo_edit.text().strip()
                nova_descricao = dialog.descricao_edit.text().strip()
                
                # Atualizar a linha na tabela
                self.table.setItem(row, 0, QTableWidgetItem(novo_codigo))
                self.table.setItem(row, 1, QTableWidgetItem(nova_descricao))
        else:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "Seleção necessária", 
                "Por favor, selecione uma classe para alterar.",
                QMessageBox.Ok,
                self
            )
            
            # Aplicar estilo com texto branco
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #003353;
                }
                QMessageBox QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
            
            # Obter o botão OK e aplicar estilo diretamente nele
            ok_button = msg_box.button(QMessageBox.Ok)
            if ok_button:
                ok_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 70px;
                        min-height: 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            msg_box.exec_()
    
    def excluir_classe(self):
        """Exclui a classe financeira selecionada após confirmação"""
        row = self.table.currentRow()
        if row >= 0:
            codigo = self.table.item(row, 0).text()
            descricao = self.table.item(row, 1).text()
            
            # Configurar caixa de mensagem de confirmação com estilo
            msg_box = QMessageBox(
                QMessageBox.Question,
                "Confirmar exclusão", 
                f"Deseja realmente excluir a classe {codigo} - {descricao}?",
                QMessageBox.Yes | QMessageBox.No,
                self
            )
            
            # Aplicar estilo com texto branco
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #003353;
                }
                QMessageBox QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
            
            # Estilizar botões
            yes_button = msg_box.button(QMessageBox.Yes)
            if yes_button:
                yes_button.setText("Sim")
                yes_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 70px;
                        min-height: 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            no_button = msg_box.button(QMessageBox.No)
            if no_button:
                no_button.setText("Não")
                no_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 70px;
                        min-height: 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            confirmacao = msg_box.exec_()
            
            if confirmacao == QMessageBox.Yes:
                self.table.removeRow(row)
                
                # Mensagem de sucesso
                success_box = QMessageBox(
                    QMessageBox.Information,
                    "Exclusão concluída", 
                    f"A classe {codigo} foi excluída com sucesso.",
                    QMessageBox.Ok,
                    self
                )
                
                # Aplicar estilo com texto branco
                success_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #003353;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-weight: bold;
                    }
                """)
                
                # Obter o botão OK e aplicar estilo diretamente nele
                ok_button = success_box.button(QMessageBox.Ok)
                if ok_button:
                    ok_button.setStyleSheet("""
                        QPushButton {
                            color: white;
                            background-color: #004465;
                            border: none;
                            border-radius: 3px;
                            min-width: 70px;
                            min-height: 20px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #00354f;
                        }
                        QPushButton:pressed {
                            background-color: #0078d7;
                        }
                    """)
                
                success_box.exec_()
        else:
            # Mensagem de aviso quando nenhuma linha está selecionada
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "Seleção necessária", 
                "Por favor, selecione uma classe para excluir.",
                QMessageBox.Ok,
                self
            )
            
            # Aplicar estilo com texto branco
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #003353;
                }
                QMessageBox QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
            
            # Obter o botão OK e aplicar estilo diretamente nele
            ok_button = msg_box.button(QMessageBox.Ok)
            if ok_button:
                ok_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 70px;
                        min-height: 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            msg_box.exec_()


class FormularioClasseFinanceira(QDialog):
    def __init__(self, parent=None, codigo="", descricao="", modo_edicao=False):
        super().__init__(parent)
        self.parent = parent
        self.modo_edicao = modo_edicao
        self.codigo_original = codigo
        self.initUI(codigo, descricao)
        
    def initUI(self, codigo, descricao):
        # Configuração da janela
        self.setWindowTitle("Cadastro de Classe Financeira")
        self.setMinimumWidth(400)
        self.setMinimumHeight(180)
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Cabeçalho com botão voltar e título
        header_layout = QHBoxLayout()
        
        # Botão Voltar com texto
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_voltar.setFixedWidth(60)
        self.btn_voltar.clicked.connect(self.reject)
        header_layout.addWidget(self.btn_voltar)
        
        # Título
        title_label = QLabel("Cadastro de Classe Financeira")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label, 1)  # 1 = stretch factor
        
        # Adicionar espaço à direita para balancear o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(60)
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para inputs
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 12px;
                min-height: 18px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Form layout para os campos
        form_layout = QFormLayout()
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Código
        codigo_label = QLabel("Código:")
        codigo_label.setFont(QFont("Arial", 11))
        codigo_label.setStyleSheet("color: white;")
        
        self.codigo_edit = QLineEdit(codigo)
        self.codigo_edit.setStyleSheet(input_style)
        self.codigo_edit.setFixedWidth(100)
        form_layout.addRow(codigo_label, self.codigo_edit)
        
        # Descrição
        descricao_label = QLabel("Descrição:")
        descricao_label.setFont(QFont("Arial", 11))
        descricao_label.setStyleSheet("color: white;")
        
        self.descricao_edit = QLineEdit(descricao)
        self.descricao_edit.setStyleSheet(input_style)
        self.descricao_edit.setMinimumWidth(200)
        form_layout.addRow(descricao_label, self.descricao_edit)
        
        main_layout.addLayout(form_layout)
        
        # Botão de Incluir/Salvar
        self.btn_salvar = QPushButton("Incluir" if not self.modo_edicao else "Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: black;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00b248;
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar_classe)
        
        # Layout do botão centralizado
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addStretch(1)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch(1)  # Adiciona espaço extra no final
    
    def salvar_classe(self):
        """Salva os dados da classe financeira"""
        # Validar formulário
        codigo = self.codigo_edit.text().strip()
        descricao = self.descricao_edit.text().strip()
        
        # Validações
        if not codigo:
            self.mostrar_erro("O código da classe é obrigatório.")
            return
            
        if not descricao:
            self.mostrar_erro("A descrição da classe é obrigatória.")
            return
        
        # Mensagem de sucesso
        acao = "alterada" if self.modo_edicao else "cadastrada"
        msg_box = QMessageBox(
            QMessageBox.Information,
            "Sucesso",
            f"Classe financeira {codigo} - {descricao} {acao} com sucesso!",
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
            QMessageBox QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        # Obter o botão OK e aplicar estilo diretamente nele
        ok_button = msg_box.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #004465;
                    border: none;
                    border-radius: 3px;
                    min-width: 70px;
                    min-height: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00354f;
                }
                QPushButton:pressed {
                    background-color: #0078d7;
                }
            """)
        
        msg_box.exec_()
        
        # Fechar a janela
        self.accept()
        
    def mostrar_erro(self, mensagem):
        """Exibe uma mensagem de erro"""
        msg_box = QMessageBox(
            QMessageBox.Warning,
            "Erro",
            mensagem,
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #003353;
            }
            QMessageBox QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        # Obter o botão OK e aplicar estilo diretamente nele
        ok_button = msg_box.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #004465;
                    border: none;
                    border-radius: 3px;
                    min-width: 70px;
                    min-height: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00354f;
                }
                QPushButton:pressed {
                    background-color: #0078d7;
                }
            """)
        
        msg_box.exec_()

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Classe Financeira")
    window.setGeometry(100, 100, 700, 400)
    window.setStyleSheet("QMainWindow { background-color: #003353; }")
    
    classe_financeira = ClasseFinanceira()
    window.setCentralWidget(classe_financeira)
    
    window.show()
    sys.exit(app.exec_())