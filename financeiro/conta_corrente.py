import sys
import os
import importlib.util
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QMessageBox, QStyle, QComboBox, QCheckBox, QDialog,
                             QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

# Função para importar a classe FormularioContaCorrente de forma dinâmica
def importar_formulario_conta_corrente():
    try:
        # Tente importar normalmente
        from formulario_conta_corrente import FormularioContaCorrente
        return FormularioContaCorrente
    except ImportError:
        try:
            # Se falhar, importe dinamicamente do arquivo no mesmo diretório
            current_dir = os.path.dirname(os.path.abspath(__file__))
            module_path = os.path.join(current_dir, 'formulario_conta_corrente.py')
            
            if not os.path.exists(module_path):
                print(f"Arquivo 'formulario_conta_corrente.py' não encontrado em: {current_dir}")
                return None
                
            spec = importlib.util.spec_from_file_location("formulario_conta_corrente", module_path)
            formulario_conta_corrente_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(formulario_conta_corrente_module)
            
            return formulario_conta_corrente_module.FormularioContaCorrente
        except Exception as e:
            print(f"Erro ao importar 'formulario_conta_corrente.py': {e}")
            return None

class ContaCorrenteWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho com título centralizado (sem botão voltar)
        header_layout = QHBoxLayout()
        
        # Título centralizado
        title_label = QLabel("Contas Correntes")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
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
        
        filtros_layout = QVBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(15, 15, 15, 15)
        filtros_layout.setSpacing(10)
        
        # Linha superior com Código e Descrição
        filtro_superior = QHBoxLayout()
        
        # Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setFont(QFont("Arial", 12))
        codigo_label.setStyleSheet("color: white;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.codigo_input.setFixedWidth(100)
        codigo_layout.addWidget(self.codigo_input)
        filtro_superior.addLayout(codigo_layout)
        
        # Espaço entre código e descrição
        filtro_superior.addSpacing(20)
        
        # Descrição
        descricao_layout = QHBoxLayout()
        descricao_label = QLabel("Descrição:")
        descricao_label.setFont(QFont("Arial", 12))
        descricao_label.setStyleSheet("color: white;")
        descricao_layout.addWidget(descricao_label)
        
        self.descricao_input = QLineEdit()
        self.descricao_input.setStyleSheet("""
            QLineEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.descricao_input.setMinimumWidth(300)
        descricao_layout.addWidget(self.descricao_input)
        filtro_superior.addLayout(descricao_layout)
        
        # Botões de filtro e limpar
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 5px 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_filtrar.clicked.connect(self.filtrar)
        filtro_superior.addWidget(self.btn_filtrar)
        
        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 5px 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_limpar.clicked.connect(self.limpar_filtros)
        filtro_superior.addWidget(self.btn_limpar)
        
        filtros_layout.addLayout(filtro_superior)
        main_layout.addWidget(filtros_frame)
        
        # Tabela de contas correntes
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Conta", "Descrição", "Banco", "Descrição", "Caixa PDV"])
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
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
                padding: 6px;
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
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        self.table.itemClicked.connect(self.selecionar_linha)
        
        main_layout.addWidget(self.table)
        
        # Botões de controle
        btn_control_layout = QHBoxLayout()
        
        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("+ Cadastrar")
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
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_cadastrar.clicked.connect(self.cadastrar_conta)
        btn_control_layout.addWidget(self.btn_cadastrar)
        
        # Botão Alterar
        self.btn_alterar = QPushButton("✎ Alterar")
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
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_alterar.clicked.connect(self.alterar_conta)
        btn_control_layout.addWidget(self.btn_alterar)
        
        # Botão Excluir
        self.btn_excluir = QPushButton("✖ Excluir")
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
            QPushButton:pressed {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.btn_excluir.clicked.connect(self.excluir_conta)
        btn_control_layout.addWidget(self.btn_excluir)
        
        main_layout.addLayout(btn_control_layout)
        
        # Carregar dados de teste
        self.carregar_dados_teste()
        
        # Aplicar estilo ao fundo
        self.setStyleSheet("QWidget { background-color: #043b57; }")
        
    def carregar_dados_teste(self):
        # Dados de exemplo conforme a imagem
        dados = [
            ("002", "CAIXA", "1", "LOCAL", True),
            ("001", "CARTEIRA", "1", "LOCAL", True)
        ]
        
        self.table.setRowCount(len(dados))
        
        for row, (conta, descricao, banco, banco_desc, caixa_pdv) in enumerate(dados):
            self.table.setItem(row, 0, QTableWidgetItem(conta))
            self.table.setItem(row, 1, QTableWidgetItem(descricao))
            self.table.setItem(row, 2, QTableWidgetItem(banco))
            self.table.setItem(row, 3, QTableWidgetItem(banco_desc))
            
            # Para a coluna Caixa PDV, criar uma célula com um checkbox
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.Checked if caixa_pdv else Qt.Unchecked)
            self.table.setItem(row, 4, checkbox_item)
            
            # Colorir a linha conforme selecionada (primeira linha azul clara)
            if row == 0:
                for col in range(5):
                    self.table.item(row, col).setBackground(Qt.lightGray)
    
    def selecionar_linha(self, item):
        # Implementar ações quando uma linha é selecionada
        row = item.row()
        conta = self.table.item(row, 0).text()
        descricao = self.table.item(row, 1).text()
        # Preencher os campos de filtro com os dados da linha selecionada
        self.codigo_input.setText(conta)
        self.descricao_input.setText(descricao)
    
    # Método voltar foi removido
    
    def filtrar(self):
        """Filtra os dados da tabela com base nos critérios de filtro"""
        codigo = self.codigo_input.text().strip().lower()
        descricao = self.descricao_input.text().strip().lower()
        
        # Mostrar/esconder linhas com base nos filtros
        for row in range(self.table.rowCount()):
            row_codigo = self.table.item(row, 0).text().lower()
            row_descricao = self.table.item(row, 1).text().lower()
            
            mostrar = True
            if codigo and codigo not in row_codigo:
                mostrar = False
            if descricao and descricao not in row_descricao:
                mostrar = False
                
            self.table.setRowHidden(row, not mostrar)
    
    def limpar_filtros(self):
        """Limpa os campos de filtro e mostra todas as linhas"""
        self.codigo_input.clear()
        self.descricao_input.clear()
        
        # Mostrar todas as linhas
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)
    
    def cadastrar_conta(self):
        """Abre o formulário para cadastrar nova conta corrente"""
        try:
            # Importar a classe FormularioContaCorrente dinamicamente
            FormularioContaCorrente = importar_formulario_conta_corrente()
            
            if FormularioContaCorrente is None:
                # Se não conseguir importar, exibe mensagem de erro
                msg_box = QMessageBox(
                    QMessageBox.Warning,
                    "Arquivo não encontrado",
                    "O arquivo 'formulario_conta_corrente.py' não foi encontrado.",
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
                            min-width: 80px;
                            min-height: 25px;
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
                return
            
            # Criar uma nova janela para o formulário
            self.form_window = QMainWindow()
            self.form_window.setWindowTitle("Cadastro de Conta Corrente")
            self.form_window.setGeometry(100, 100, 600, 400)
            self.form_window.setStyleSheet("background-color: #043b57;")
            
            # Criar e definir o widget do formulário
            form_widget = FormularioContaCorrente(self, self.form_window)
            self.form_window.setCentralWidget(form_widget)
            
            # Mostrar a janela
            self.form_window.show()
            
        except Exception as e:
            # Se ocorrer qualquer erro, exibe uma mensagem
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "Erro",
                f"Ocorreu um erro ao abrir o formulário: {str(e)}",
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
                        min-width: 80px;
                        min-height: 25px;
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
    
    def alterar_conta(self):
        """Abre o formulário para alterar conta selecionada"""
        row = self.table.currentRow()
        if row >= 0:
            conta = self.table.item(row, 0).text()
            descricao = self.table.item(row, 1).text()
            banco = self.table.item(row, 2).text()
            banco_desc = self.table.item(row, 3).text()
            caixa_pdv = self.table.item(row, 4).checkState() == Qt.Checked
            
            try:
                # Importar a classe FormularioContaCorrente dinamicamente
                FormularioContaCorrente = importar_formulario_conta_corrente()
                
                if FormularioContaCorrente is None:
                    # Se não conseguir importar, exibe mensagem de erro
                    msg_box = QMessageBox(
                        QMessageBox.Warning,
                        "Arquivo não encontrado",
                        "O arquivo 'formulario_conta_corrente.py' não foi encontrado.",
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
                                min-width: 80px;
                                min-height: 25px;
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
                    return
                
                # Criar uma nova janela para o formulário
                self.form_window = QMainWindow()
                self.form_window.setWindowTitle("Alteração de Conta Corrente")
                self.form_window.setGeometry(100, 100, 600, 400)
                self.form_window.setStyleSheet("background-color: #043b57;")
                
                # Criar e definir o widget do formulário, passando os dados da conta
                form_widget = FormularioContaCorrente(
                    self, 
                    self.form_window, 
                    codigo=conta,
                    descricao=descricao,
                    agencia=banco,
                    numero_conta="",
                    empresa=banco_desc,
                    saldo="0.00",
                    modo_edicao=True
                )
                self.form_window.setCentralWidget(form_widget)
                
                # Mostrar a janela
                self.form_window.show()
                
            except Exception as e:
                # Se ocorrer qualquer erro, exibe uma mensagem
                msg_box = QMessageBox(
                    QMessageBox.Warning,
                    "Erro",
                    f"Ocorreu um erro ao abrir o formulário: {str(e)}",
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
                            min-width: 80px;
                            min-height: 25px;
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
        else:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "Seleção necessária", 
                "Por favor, selecione uma conta para alterar.",
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
                        min-width: 80px;
                        min-height: 25px;
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
    
    def excluir_conta(self):
        """Exclui a conta selecionada após confirmação"""
        row = self.table.currentRow()
        if row >= 0:
            conta = self.table.item(row, 0).text()
            descricao = self.table.item(row, 1).text()
            
            # Configurar caixa de mensagem de confirmação com estilo
            msg_box = QMessageBox(
                QMessageBox.Question,
                "Confirmar exclusão", 
                f"Deseja realmente excluir a conta {conta} - {descricao}?",
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
                        min-width: 80px;
                        min-height: 25px;
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
                        min-width: 80px;
                        min-height: 25px;
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
                    f"A conta {conta} foi excluída com sucesso.",
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
                            min-width: 80px;
                            min-height: 25px;
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
                "Por favor, selecione uma conta para excluir.",
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
                        min-width: 80px;
                        min-height: 25px;
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
    window.setWindowTitle("Contas Correntes")
    window.setGeometry(100, 100, 800, 500)
    window.setStyleSheet("QMainWindow { background-color: #043b57; }")
    
    contas_correntes = ContaCorrenteWindow()
    window.setCentralWidget(contas_correntes)
    window.show()
    sys.exit(app.exec_())
    