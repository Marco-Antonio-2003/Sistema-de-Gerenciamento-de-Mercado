import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FormularioUnidade(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Unidade de Medida")
        self.setMinimumSize(500, 300)
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        titulo = QLabel("Cadastro de Unidade de Medida")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        form_layout = QVBoxLayout()
        
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setFixedWidth(100)
        self.codigo_input = QLineEdit()
        codigo_layout.addWidget(codigo_label)
        codigo_layout.addWidget(self.codigo_input)
        form_layout.addLayout(codigo_layout)
        
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome da Medida:")
        nome_label.setFixedWidth(100)
        self.nome_combo = QComboBox()
        unidades = ["Selecione uma unidade", "Quilograma (kg)", "Grama (g)", "Litro (L)",
                   "Mililitro (mL)", "Unidade (un)", "Pacote (pct)", "Caixa (cx)",
                   "Bandeja (bdj)", "Dúzia (dz)", "Fardo (fd)", "Garrafa (gf)"]
        for u in unidades:
            self.nome_combo.addItem(u)
        nome_layout.addWidget(nome_label)
        nome_layout.addWidget(self.nome_combo)
        form_layout.addLayout(nome_layout)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.close)
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar)
        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addWidget(self.btn_salvar)
        main_layout.addLayout(buttons_layout)
    
    def salvar(self):
        codigo = self.codigo_input.text()
        nome = self.nome_combo.currentText()
        if not codigo or nome == "Selecione uma unidade":
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos!")
            return
        QMessageBox.information(self, "Sucesso", "Unidade de medida salva com sucesso!")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FormularioUnidade()
    window.show()
    sys.exit(app.exec_())
