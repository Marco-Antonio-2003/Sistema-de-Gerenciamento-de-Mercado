import sys
import os
import importlib.util
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QComboBox, QMessageBox, QListWidget, QListWidgetItem, 
    QSplitter, QFrame
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


class CustomMessageBox(QMessageBox):
    """Classe personalizada para QMessageBox com cores customizadas"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilo para os botões do MessageBox
        self.setStyleSheet("""
            QMessageBox {
                background-color: #043b57;
                color: white;
            }
            QLabel {
                color: white;
                background-color: #043b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: 1px solid #007ab3;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)


class UnidadeMedidaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unidade de Medida")
        self.setGeometry(100, 100, 800, 600)  # Aumentei a altura para acomodar a lista
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

        # # btn_cadastrar = QPushButton("Cadastrar")
        # # carregar ícone se existir
        # try:
        #     icon_path = os.path.join(os.path.dirname(__file__), "ico-img", "add.png")
        #     if os.path.exists(icon_path):
        #         btn_cadastrar.setIcon(QIcon(icon_path))
        # except Exception:
        #     pass
        # btn_cadastrar.setStyleSheet("""
        #     QPushButton {
        #         background-color: #005079; color: white; border: none;
        #         padding: 10px 20px; font-size: 14px; border-radius: 4px;
        #     }
        #     QPushButton:hover { background-color: #003d5c; }
        # """)
        # btn_cadastrar.clicked.connect(self.cadastrar)
        # header_layout.addWidget(btn_cadastrar)

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

        # Nome da Medida (campo de texto em vez de ComboBox)
        nome_layout = QVBoxLayout()
        nome_label = QLabel("Nome da Medida:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        
        # Substituir ComboBox por QLineEdit
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 1px solid #cccccc;
                padding: 10px; font-size: 14px; border-radius: 4px;
                color: black;
            }
        """)
        
        nome_layout.addWidget(nome_label)
        nome_layout.addWidget(self.nome_input)
        fields_layout.addLayout(nome_layout, 1)

        main_layout.addLayout(fields_layout)

        # Botões de ação (Alterar, Excluir)
        actions_layout = QHBoxLayout()
        actions_layout.addStretch(1)

        btn_alterar = QPushButton("Alterar")
        btn_alterar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0; color: black; border: 1px solid #cccccc;
                padding: 10px 20px; font-size: 14px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #e6e6d9; }
        """)
        btn_alterar.clicked.connect(self.alterar)
        actions_layout.addWidget(btn_alterar)

        actions_layout.addSpacing(20)

        btn_excluir = QPushButton("Excluir")
        btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0; color: black; border: 1px solid #cccccc;
                padding: 10px 20px; font-size: 14px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #e6e6d9; }
        """)
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

        # Adicionar um título para a lista de unidades
        lista_label = QLabel("Unidades de Medida Cadastradas:")
        lista_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(lista_label)

        # Adicionar uma lista para mostrar as unidades cadastradas
        self.lista_unidades = QListWidget()
        self.lista_unidades.setStyleSheet("""
            QListWidget {
                background-color: #fffff0; border: 1px solid #cccccc;
                font-size: 14px; border-radius: 4px; color: black;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #043b57;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e6e6e6;
            }
        """)
        self.lista_unidades.itemClicked.connect(self.selecionar_unidade)
        
        # Carregar os dados na lista
        self.carregar_unidades()
        
        main_layout.addWidget(self.lista_unidades)

    def carregar_unidades(self):
        """Carrega as unidades na lista"""
        self.lista_unidades.clear()
        for unidade in self.unidades_data:
            item_text = f"{unidade['codigo']} - {unidade['descricao']}"
            item = QListWidgetItem(item_text)
            self.lista_unidades.addItem(item)

    def selecionar_unidade(self, item):
        """Preenche os campos quando um item é selecionado na lista"""
        texto = item.text()
        partes = texto.split(" - ", 1)
        if len(partes) == 2:
            codigo = partes[0]
            descricao = partes[1]
            self.codigo_input.setText(codigo)
            self.nome_input.setText(descricao)

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
                            QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CustomMessageBox(QMessageBox):
    """Classe personalizada para QMessageBox com cores customizadas"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilo para os botões do MessageBox
        self.setStyleSheet("""
            QMessageBox {
                background-color: #043b57;
                color: white;
            }
            QLabel {
                color: white;
                background-color: #043b57;
            }
            QPushButton {
                background-color: #005079;
                color: white;
                border: 1px solid #007ab3;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)

class FormularioUnidade(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Cadastro de Unidade de Medida")
        self.setMinimumSize(500, 300)
        self.setStyleSheet("background-color: #043b57;")
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        titulo = QLabel("Cadastro de Unidade de Medida")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        form_layout = QVBoxLayout()
        
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setFixedWidth(100)
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
        form_layout.addLayout(codigo_layout)
        
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome da Medida:")
        nome_label.setFixedWidth(100)
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 1px solid #cccccc;
                padding: 10px; font-size: 14px; border-radius: 4px;
                color: black;
            }
        """)
        nome_layout.addWidget(nome_label)
        nome_layout.addWidget(self.nome_input)
        form_layout.addLayout(nome_layout)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0; color: black; border: 1px solid #cccccc;
                padding: 10px 20px; font-size: 14px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #e6e6d9; }
        """)
        self.btn_cancelar.clicked.connect(self.voltar)
        
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d; color: black; border: none;
                padding: 10px 20px; font-size: 14px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #00e088; }
        """)
        self.btn_salvar.clicked.connect(self.salvar)
        
        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addWidget(self.btn_salvar)
        main_layout.addLayout(buttons_layout)
    
    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        msg = CustomMessageBox(self)
        msg.setIcon(tipo)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.exec_()
    
    def voltar(self):
        """Fecha a janela e volta para a tela anterior"""
        if self.parent and hasattr(self.parent, 'form_window'):
            self.parent.form_window.close()
        else:
            self.close()
    
    def salvar(self):
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!", QMessageBox.Warning)
            return
            
        # Verificar se o código já existe
        if self.parent and hasattr(self.parent, 'unidades_data'):
            # Verificar duplicidade
            for unidade in self.parent.unidades_data:
                if unidade["codigo"] == codigo:
                    self.mostrar_mensagem("Atenção", "Este código já está em uso!", QMessageBox.Warning)
                    return
            
            # Adicionar a nova unidade
            nova_unidade = {
                "codigo": codigo,
                "descricao": nome
            }
            self.parent.unidades_data.append(nova_unidade)
            self.parent.carregar_unidades()
            
        self.mostrar_mensagem("Sucesso", "Unidade de medida salva com sucesso!")
        self.voltar()

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
        nome = self.nome_input.text()
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!", QMessageBox.Warning)
            return
            
        # Verificar se o código existe
        unidade_encontrada = False
        for i, unidade in enumerate(self.unidades_data):
            if unidade["codigo"] == codigo:
                # Atualizar a unidade
                self.unidades_data[i]["descricao"] = nome
                unidade_encontrada = True
                # Atualizar a lista
                self.carregar_unidades()
                self.mostrar_mensagem("Sucesso", "Unidade de medida alterada com sucesso!")
                break
        
        if not unidade_encontrada:
            self.mostrar_mensagem("Atenção", "Unidade não encontrada.", QMessageBox.Warning)

    def excluir(self):
        codigo = self.codigo_input.text()
        if not codigo:
            self.mostrar_mensagem("Atenção", "Selecione uma unidade para excluir!", QMessageBox.Warning)
            return

        # Criar uma caixa de diálogo de confirmação personalizada com estilo
        msg_box = CustomMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmar Exclusão")
        msg_box.setText(f"Deseja realmente excluir a unidade de medida '{codigo}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        resp = msg_box.exec_()
        
        if resp == QMessageBox.Yes:
            # Remover a unidade da lista
            for i, unidade in enumerate(self.unidades_data):
                if unidade["codigo"] == codigo:
                    del self.unidades_data[i]
                    # Atualizar a lista
                    self.carregar_unidades()
                    break
                    
            self.codigo_input.clear()
            self.nome_input.clear()
            self.mostrar_mensagem("Sucesso", "Unidade de medida excluída com sucesso!")

    def incluir(self):
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos!", QMessageBox.Warning)
            return
            
        # Verificar se o código já existe
        for unidade in self.unidades_data:
            if unidade["codigo"] == codigo:
                self.mostrar_mensagem("Atenção", "Este código já está em uso!", QMessageBox.Warning)
                return
        
        # Adicionar a nova unidade
        nova_unidade = {
            "codigo": codigo,
            "descricao": nome
        }
        self.unidades_data.append(nova_unidade)
        
        # Atualizar a lista
        self.carregar_unidades()
        
        self.codigo_input.clear()
        self.nome_input.clear()
        self.mostrar_mensagem("Sucesso", "Unidade de medida incluída com sucesso!")

    def mostrar_mensagem(self, titulo, texto, tipo=QMessageBox.Information):
        msg = CustomMessageBox(self)
        msg.setIcon(tipo)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnidadeMedidaWindow()
    window.show()
    sys.exit(app.exec_())