import sys
import os
import importlib.util
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QComboBox, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


class UnidadeMedidaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unidade de Medida")
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: #043b57;")

        # Widget central
        self.unidade_medida_widget = UnidadeMedida(self)
        self.setCentralWidget(self.unidade_medida_widget)

        print("Iniciando UnidadeMedidaWindow")


class UnidadeMedida(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.unidades_data = [
            {"codigo": "UN", "descricao": "Unidade (un)"},
            {"codigo": "KG", "descricao": "Quilograma (kg)"},
            {"codigo": "G", "descricao": "Grama (g)"},
            {"codigo": "L", "descricao": "Litro (L)"},
            {"codigo": "ML", "descricao": "Mililitro (mL)"},
            {"codigo": "PCT", "descricao": "Pacote (pct)"},
            {"codigo": "CX", "descricao": "Caixa (cx)"},
            {"codigo": "BDJ", "descricao": "Bandeja (bdj)"},
            {"codigo": "DZ", "descricao": "Dúzia (dz)"},
            {"codigo": "FD", "descricao": "Fardo (fd)"},
            {"codigo": "GF", "descricao": "Garrafa (gf)"}
        ]
        self.form_window = None  # referência à janela de formulário
        self.initUI()

    def create_palette(self):
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#043b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.setAutoFillBackground(True)
        self.setPalette(self.create_palette())

        # Cabeçalho
        header_layout = QHBoxLayout()
        btn_voltar = QPushButton("Voltar")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079; color: white; border: none;
                padding: 10px 20px; font-size: 14px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #003d5c; }
        """)
        btn_voltar.clicked.connect(self.voltar)
        header_layout.addWidget(btn_voltar)

        titulo = QLabel("Unidade de Medida")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)

        btn_cadastrar = QPushButton("Cadastrar")
        # carregar ícone se existir
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "ico-img", "add.png")
            if os.path.exists(icon_path):
                btn_cadastrar.setIcon(QIcon(icon_path))
        except Exception:
            pass
        btn_cadastrar.setStyleSheet("""
            QPushButton {
                background-color: #005079; color: white; border: none;
                padding: 10px 20px; font-size: 14px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #003d5c; }
        """)
        btn_cadastrar.clicked.connect(self.cadastrar)
        header_layout.addWidget(btn_cadastrar)

        main_layout.addLayout(header_layout)

        # Campos de entrada
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(20)

        # Código
        codigo_layout = QVBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 1px solid #cccccc;
                padding: 10px; font-size: 14px; border-radius: 4px;
                color: black;
            }
        """)
        codigo_layout.addWidget(codigo_label)
        codigo_layout.addWidget(self.codigo_input)
        fields_layout.addLayout(codigo_layout)

        # Nome da Medida
        nome_layout = QVBoxLayout()
        nome_label = QLabel("Nome da Medida:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        self.nome_combo = QComboBox()
        self.nome_combo.setStyleSheet("""
            QComboBox {
                background-color: white; border: 1px solid #cccccc;
                padding: 10px; font-size: 14px; border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: white; color: black;
                selection-background-color: #e6e6e6;
            }
        """)
        # adicionar opções
        self.nome_combo.addItem("Selecione uma unidade")
        for u in self.unidades_data:
            self.nome_combo.addItem(u["descricao"])
        nome_layout.addWidget(nome_label)
        nome_layout.addWidget(self.nome_combo)
        fields_layout.addLayout(nome_layout, 1)

        main_layout.addLayout(fields_layout)

        # Botões de ação (Alterar, Excluir)
        actions_layout = QHBoxLayout()
        actions_layout.addStretch(1)

        btn_alterar = QPushButton("Alterar")
        btn_alterar.clicked.connect(self.alterar)
        actions_layout.addWidget(btn_alterar)

        actions_layout.addSpacing(20)

        btn_excluir = QPushButton("Excluir")
        btn_excluir.clicked.connect(self.excluir)
        actions_layout.addWidget(btn_excluir)

        actions_layout.addStretch(1)
        main_layout.addLayout(actions_layout)

        # Botão Incluir
        btn_incluir = QPushButton("Incluir")
        btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d; color: black; border: none;
                padding: 15px 0; font-size: 16px; border-radius: 4px;
                margin: 0 100px;
            }
            QPushButton:hover { background-color: #00e088; }
        """)
        btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(btn_incluir)

        main_layout.addStretch()

    def load_formulario_unidade(self):
        """
        Carrega dinamicamente o módulo formulario_unidade.py
        """
        try:
            from formulario_unidade import FormularioUnidade
            return FormularioUnidade
        except ImportError:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            module_path = os.path.join(script_dir, "formulario_unidade.py")
            if not os.path.exists(module_path):
                self.criar_formulario_unidade_padrao(module_path)
            spec = importlib.util.spec_from_file_location("formulario_unidade", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, "FormularioUnidade", None)

    def criar_formulario_unidade_padrao(self, filepath):
        """Cria um arquivo formulario_unidade.py básico se não existir"""
        template = '''import sys
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
'''
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

    def cadastrar(self):
        if self.form_window and self.form_window.isVisible():
            self.form_window.activateWindow()
            return

        FormularioUnidade = self.load_formulario_unidade()
        if FormularioUnidade is None:
            self.mostrar_mensagem("Erro", "Não foi possível carregar o formulário", QMessageBox.Critical)
            return

        self.form_window = QMainWindow()
        self.form_window.setWindowTitle("Cadastro de Unidade de Medida")
        self.form_window.setGeometry(100, 100, 600, 400)
        self.form_window.setStyleSheet("background-color: #043b57;")
        formulario_widget = FormularioUnidade(self)
        self.form_window.setCentralWidget(formulario_widget)
        self.form_window.show()

    def voltar(self):
        if self.parent_window:
            self.parent_window.close()

    def alterar(self):
        codigo = self.codigo_input.text()
        nome = self.nome_combo.currentText()
        if not codigo or nome == "Selecione uma unidade":
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!")
            return
        self.mostrar_mensagem("Sucesso", "Unidade de medida alterada com sucesso!")

    def excluir(self):
        codigo = self.codigo_input.text()
        if not codigo:
            self.mostrar_mensagem("Atenção", "Selecione uma unidade para excluir!")
            return

        resp = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Deseja realmente excluir a unidade de medida '{codigo}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.codigo_input.clear()
            self.nome_combo.setCurrentIndex(0)
            self.mostrar_mensagem("Sucesso", "Unidade de medida excluída com sucesso!")

    def incluir(self):
        codigo = self.codigo_input.text()
        nome = self.nome_combo.currentText()
        if not codigo or nome == "Selecione uma unidade":
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!")
            return
        self.codigo_input.clear()
        self.nome_combo.setCurrentIndex(0)
        self.mostrar_mensagem("Sucesso", "Unidade de medida incluída com sucesso!")

    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        msg = QMessageBox(self)
        msg.setIcon(tipo)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnidadeMedidaWindow()
    window.show()
    sys.exit(app.exec_())
