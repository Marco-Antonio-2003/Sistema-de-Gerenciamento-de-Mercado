# formulario_conta_corrente.py
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFormLayout, 
                            QWidget, QMessageBox, QGridLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FormularioContaCorrente(QDialog):
    def __init__(self, parent=None, main_window=None, codigo="", descricao="", 
                agencia="", numero_conta="", empresa="", saldo="0.00", modo_edicao=False):
        super().__init__(parent)
        self.parent = parent
        self.main_window = main_window
        self.modo_edicao = modo_edicao
        self.codigo_original = codigo
        self.initUI(codigo, descricao, agencia, numero_conta, empresa, saldo)
        
    def initUI(self, codigo, descricao, agencia, numero_conta, empresa, saldo):
        # Configuração da janela
        self.setWindowTitle("Cadastro de Conta Corrente")
        self.setMinimumWidth(500)  # Reduzido de 550
        self.setMinimumHeight(250)  # Reduzido de 300
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)  # Reduzido de 20, 20, 20, 20
        main_layout.setSpacing(10)  # Reduzido de 15
        
        # Cabeçalho com botão voltar e título
        header_layout = QHBoxLayout()
        
        # Botão Voltar com texto
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 5px 10px;  /* Reduzido de 8px 15px */
                border: none;
                border-radius: 4px;  /* Reduzido de 5px */
                font-size: 12px;  /* Reduzido de 14px */
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_voltar.setFixedWidth(60)  # Reduzido de 80
        self.btn_voltar.clicked.connect(self.reject)
        header_layout.addWidget(self.btn_voltar)
        
        # Título
        title_label = QLabel("Cadastro de Conta Correntes")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))  # Reduzido de 18
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label, 1)  # 1 = stretch factor
        
        # Adicionar espaço à direita para balancear o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(60)  # Reduzido de 80
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para inputs - mais compacto
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;  /* Reduzido de 5px */
                padding: 3px 6px;  /* Reduzido de 8px */
                font-size: 12px;  /* Reduzido de 14px */
                min-height: 18px;  /* Reduzido de 25px */
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;  /* Reduzido de 2px */
            }
        """
        
        # Grid layout para os campos
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(10)  # Reduzido de 15
        grid_layout.setHorizontalSpacing(10)  # Reduzido de 15
        
        # Primeira linha - Código
        codigo_label = QLabel("Código:")
        codigo_label.setFont(QFont("Arial", 11))  # Reduzido de 12
        codigo_label.setStyleSheet("color: white;")
        grid_layout.addWidget(codigo_label, 0, 0)
        
        self.codigo_edit = QLineEdit(codigo)
        self.codigo_edit.setStyleSheet(input_style)
        self.codigo_edit.setFixedWidth(120)  # Reduzido de 140
        grid_layout.addWidget(self.codigo_edit, 0, 1)
        
        # Descrição (na mesma linha que código, mas começa na coluna 2)
        descricao_label = QLabel("Descrição:")
        descricao_label.setFont(QFont("Arial", 11))  # Reduzido de 12
        descricao_label.setStyleSheet("color: white;")
        grid_layout.addWidget(descricao_label, 0, 2)
        
        self.descricao_edit = QLineEdit(descricao)
        self.descricao_edit.setStyleSheet(input_style)
        self.descricao_edit.setMinimumWidth(200)  # Reduzido de 250
        grid_layout.addWidget(self.descricao_edit, 0, 3)
        
        # Segunda linha - Agência
        agencia_label = QLabel("Agencia:")
        agencia_label.setFont(QFont("Arial", 11))  # Reduzido de 12
        agencia_label.setStyleSheet("color: white;")
        grid_layout.addWidget(agencia_label, 1, 0)
        
        self.agencia_edit = QLineEdit(agencia)
        self.agencia_edit.setStyleSheet(input_style)
        self.agencia_edit.setMinimumWidth(120)  # Reduzido de 200
        grid_layout.addWidget(self.agencia_edit, 1, 1)
        
        # Número da conta (na mesma linha que agência)
        numero_conta_label = QLabel("Numero da conta")
        numero_conta_label.setFont(QFont("Arial", 11))  # Reduzido de 12
        numero_conta_label.setStyleSheet("color: white;")
        grid_layout.addWidget(numero_conta_label, 1, 2)
        
        self.numero_conta_edit = QLineEdit(numero_conta)
        self.numero_conta_edit.setStyleSheet(input_style)
        self.numero_conta_edit.setFixedWidth(120)  # Reduzido de 150
        grid_layout.addWidget(self.numero_conta_edit, 1, 3)
        
        # Terceira linha - Empresa
        empresa_label = QLabel("Empresa:")
        empresa_label.setFont(QFont("Arial", 11))  # Reduzido de 12
        empresa_label.setStyleSheet("color: white;")
        grid_layout.addWidget(empresa_label, 2, 0)
        
        self.empresa_edit = QLineEdit(empresa)
        self.empresa_edit.setStyleSheet(input_style)
        self.empresa_edit.setMinimumWidth(120)  # Reduzido de 200
        grid_layout.addWidget(self.empresa_edit, 2, 1)
        
        # Saldo (na mesma linha que empresa)
        saldo_label = QLabel("Saldo:")
        saldo_label.setFont(QFont("Arial", 11))  # Reduzido de 12
        saldo_label.setStyleSheet("color: white;")
        grid_layout.addWidget(saldo_label, 2, 2)
        
        self.saldo_edit = QLineEdit(saldo)
        self.saldo_edit.setStyleSheet(input_style)
        self.saldo_edit.setFixedWidth(120)  # Reduzido de 150
        grid_layout.addWidget(self.saldo_edit, 2, 3)
        
        main_layout.addLayout(grid_layout)
        
        # Botão de Incluir/Salvar
        self.btn_salvar = QPushButton("Incluir" if not self.modo_edicao else "Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: black;
                padding: 6px 12px;  /* Reduzido de 10px 15px */
                border: none;
                border-radius: 4px;  /* Reduzido de 5px */
                font-size: 12px;  /* Reduzido de 14px */
                min-width: 100px;  /* Reduzido de 120px */
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00b248;
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar_conta)
        
        # Layout do botão centralizado
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addStretch(1)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch(1)  # Adiciona espaço extra no final
    
    def salvar_conta(self):
        """Salva os dados da conta corrente"""
        # Validar formulário
        codigo = self.codigo_edit.text().strip()
        descricao = self.descricao_edit.text().strip()
        agencia = self.agencia_edit.text().strip()
        numero_conta = self.numero_conta_edit.text().strip()
        empresa = self.empresa_edit.text().strip()
        saldo = self.saldo_edit.text().strip()
        
        # Validações
        if not codigo:
            self.mostrar_erro("O código da conta é obrigatório.")
            return
            
        if not descricao:
            self.mostrar_erro("A descrição da conta é obrigatória.")
            return
            
        if not agencia:
            self.mostrar_erro("A agência é obrigatória.")
            return
            
        if not numero_conta:
            self.mostrar_erro("O número da conta é obrigatório.")
            return
            
        if not empresa:
            self.mostrar_erro("A empresa é obrigatória.")
            return
            
        if not saldo:
            self.mostrar_erro("O saldo é obrigatório.")
            return
        
        # Aqui você implementaria o código para salvar os dados no banco de dados
        # Por enquanto, vamos apenas simular que salvou e atualizar a tabela
        
        # Mensagem de sucesso
        acao = "alterada" if self.modo_edicao else "cadastrada"
        msg_box = QMessageBox(
            QMessageBox.Information,
            "Sucesso",
            f"Conta corrente {codigo} - {descricao} {acao} com sucesso!",
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
                    min-width: 70px;  /* Reduzido de 80px */
                    min-height: 20px;  /* Reduzido de 25px */
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
                    min-width: 70px;  /* Reduzido de 80px */
                    min-height: 20px;  /* Reduzido de 25px */
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

# Para testar o formulário individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = FormularioContaCorrente()
    dialog.show()
    sys.exit(app.exec_())