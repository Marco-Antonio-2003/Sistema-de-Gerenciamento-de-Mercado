import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit,
                            QDateEdit, QComboBox, QMessageBox, QFrame, QStyle,
                            QFormLayout, QTableWidgetItem)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate

class FormularioFornecedores(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela
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
        titulo = QLabel("Cadastro de Fornecedores")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
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
        
        # Estilo comum para QComboBox
        combobox_style = """
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #0078d7;
                color: white;
            }
        """
        
        # Estilo comum para QDateEdit
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
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit:hover {
                border: 1px solid #0078d7;
            }
        """
        
        # Linha 1: Código e Nome
        linha1_layout = QHBoxLayout()
        
        # Campo Código
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        linha1_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setFixedWidth(100)  # Reduzida
        linha1_layout.addWidget(self.codigo_input)
        
        # Campo Nome
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        linha1_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        linha1_layout.addWidget(self.nome_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha1_layout)
        
        # Linha 2: Nome Fantasia e Tipo
        linha2_layout = QHBoxLayout()
        
        # Campo Nome Fantasia
        fantasia_label = QLabel("Nome Fantasia:")
        fantasia_label.setStyleSheet("color: white; font-size: 14px;")
        linha2_layout.addWidget(fantasia_label)
        
        self.fantasia_input = QLineEdit()
        self.fantasia_input.setStyleSheet(lineedit_style)
        linha2_layout.addWidget(self.fantasia_input, 1)  # 1 para expandir
        
        # Campo Tipo
        tipo_label = QLabel("Tipo:")
        tipo_label.setStyleSheet("color: white; font-size: 14px;")
        linha2_layout.addWidget(tipo_label)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.setStyleSheet(combobox_style)
        self.tipo_combo.addItem("Selecione um tipo")
        self.tipo_combo.addItem("Fabricante")
        self.tipo_combo.addItem("Distribuidor")
        self.tipo_combo.addItem("Atacadista")
        self.tipo_combo.addItem("Varejista")
        self.tipo_combo.addItem("Importador")
        self.tipo_combo.setFixedWidth(200)  # Reduzida
        linha2_layout.addWidget(self.tipo_combo)
        
        main_layout.addLayout(linha2_layout)
        
        # Linha 3: CNPJ e Data de Cadastro
        linha3_layout = QHBoxLayout()
        
        # Campo CNPJ
        cnpj_label = QLabel("CNPJ:")
        cnpj_label.setStyleSheet("color: white; font-size: 14px;")
        linha3_layout.addWidget(cnpj_label)
        
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setStyleSheet(lineedit_style)
        self.cnpj_input.setFixedWidth(180)  # Reduzida
        self.cnpj_input.textChanged.connect(self.formatar_cnpj)
        self.cnpj_input.setPlaceholderText("00.000.000/0001-00")
        linha3_layout.addWidget(self.cnpj_input)
        
        # Campo Data de Cadastro
        data_label = QLabel("Data de Cadastro:")
        data_label.setStyleSheet("color: white; font-size: 14px;")
        linha3_layout.addWidget(data_label)
        
        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        self.data_input.setStyleSheet(dateedit_style)
        self.data_input.setFixedWidth(130)  # Reduzida
        linha3_layout.addWidget(self.data_input)
        
        main_layout.addLayout(linha3_layout)
        
        # Título Endereço
        endereco_titulo = QLabel("Endereço")
        endereco_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        endereco_titulo.setStyleSheet("color: white;")
        endereco_titulo.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(endereco_titulo)
        
        # Linha 4: Rua
        linha4_layout = QHBoxLayout()
        
        # Campo Rua
        rua_label = QLabel("Rua:")
        rua_label.setStyleSheet("color: white; font-size: 14px;")
        linha4_layout.addWidget(rua_label)
        
        self.rua_input = QLineEdit()
        self.rua_input.setStyleSheet(lineedit_style)
        linha4_layout.addWidget(self.rua_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha4_layout)
        
        # Linha 5: Bairro
        linha5_layout = QHBoxLayout()
        
        # Campo Bairro
        bairro_label = QLabel("Bairro:")
        bairro_label.setStyleSheet("color: white; font-size: 14px;")
        linha5_layout.addWidget(bairro_label)
        
        self.bairro_input = QLineEdit()
        self.bairro_input.setStyleSheet(lineedit_style)
        linha5_layout.addWidget(self.bairro_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha5_layout)
        
        # Linha 6: CEP e Cidade
        linha6_layout = QHBoxLayout()
        
        # Linha 6: CEP e Cidade
        linha6_layout = QHBoxLayout()
        
        # Campo CEP
        cep_label = QLabel("CEP:")
        cep_label.setStyleSheet("color: white; font-size: 14px;")
        linha6_layout.addWidget(cep_label)
        
        cep_busca_layout = QHBoxLayout()
        cep_busca_layout.setSpacing(0)
        
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet(lineedit_style)
        self.cep_input.setFixedWidth(150)
        self.cep_input.setPlaceholderText("00000-000")
        self.cep_input.textChanged.connect(self.formatar_cep)
        cep_busca_layout.addWidget(self.cep_input)
        
        # Botão de busca para o CEP (lupa)
        btn_busca_cep = QPushButton()
        try:
            btn_busca_cep.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        except:
            pass
        btn_busca_cep.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                border-left: none;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        btn_busca_cep.clicked.connect(self.buscar_endereco_por_cep)
        cep_busca_layout.addWidget(btn_busca_cep)
        
        linha6_layout.addLayout(cep_busca_layout)
        
        # Campo Cidade
        cidade_label = QLabel("Cidade:")
        cidade_label.setStyleSheet("color: white; font-size: 14px;")
        linha6_layout.addWidget(cidade_label)
        
        self.cidade_input = QLineEdit()
        self.cidade_input.setStyleSheet(lineedit_style)
        linha6_layout.addWidget(self.cidade_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha6_layout)
        
        # Botão Incluir
        btn_incluir = QPushButton("Incluir")
        btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 15px 0;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 20px 100px 0;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
            QPushButton:pressed {
                background-color: #00cc7a;
            }
        """)
        btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(btn_incluir)
        
        # Adicionar espaço no final
        main_layout.addStretch()
    
    def buscar_endereco_por_cep(self):
        """Busca endereço baseado no CEP informado utilizando a API de CEP"""
        # Obter CEP, removendo caracteres não numéricos
        cep = ''.join(filter(str.isdigit, self.cep_input.text()))
        
        # Verificar se o CEP tem 8 dígitos
        if len(cep) != 8:
            self.mostrar_mensagem("Atenção", "Por favor, informe um CEP válido com 8 dígitos.")
            return
        
        try:
            # Fazer a requisição à API ViaCEP
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url)
            
            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se o CEP foi encontrado
                if "erro" not in data:
                    # Preencher os campos com os dados retornados
                    self.rua_input.setText(data.get("logradouro", ""))
                    self.bairro_input.setText(data.get("bairro", ""))
                    self.cidade_input.setText(data.get("localidade", ""))
                    return
            
            # Se chegou aqui, o CEP não foi encontrado ou houve erro
            self.mostrar_mensagem("Atenção", "CEP não encontrado ou inválido.")
        
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao buscar o CEP: {str(e)}")

    def formatar_cnpj(self, texto):
        """Formata o CNPJ durante a digitação"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 14 dígitos para CNPJ
        if len(texto_limpo) > 14:
            texto_limpo = texto_limpo[:14]
        
        # Formatar CNPJ: 00.000.000/0001-00
        if len(texto_limpo) <= 2:
            texto_formatado = texto_limpo
        elif len(texto_limpo) <= 5:
            texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:]}"
        elif len(texto_limpo) <= 8:
            texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:]}"
        elif len(texto_limpo) <= 12:
            texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:8]}/{texto_limpo[8:]}"
        else:
            texto_formatado = f"{texto_limpo[:2]}.{texto_limpo[2:5]}.{texto_limpo[5:8]}/{texto_limpo[8:12]}-{texto_limpo[12:]}"
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Bloqueia sinais para evitar recursão
            self.cnpj_input.blockSignals(True)
            self.cnpj_input.setText(texto_formatado)
            
            # Posicionamento direto do cursor para CNPJ baseado no número de dígitos
            if len(texto_limpo) == 0:
                nova_pos = 0
            elif len(texto_limpo) == 1:
                nova_pos = 1
            elif len(texto_limpo) == 2:
                nova_pos = 2
            elif len(texto_limpo) == 3:
                nova_pos = 4  # Após o primeiro ponto: "12.3"
            elif len(texto_limpo) == 4:
                nova_pos = 5
            elif len(texto_limpo) == 5:
                nova_pos = 6
            elif len(texto_limpo) == 6:
                nova_pos = 8  # Após o segundo ponto: "12.345.6"
            elif len(texto_limpo) == 7:
                nova_pos = 9
            elif len(texto_limpo) == 8:
                nova_pos = 10
            elif len(texto_limpo) == 9:
                nova_pos = 12  # Após a barra: "12.345.678/9"
            elif len(texto_limpo) == 10:
                nova_pos = 13
            elif len(texto_limpo) == 11:
                nova_pos = 14
            elif len(texto_limpo) == 12:
                nova_pos = 15
            elif len(texto_limpo) == 13:
                nova_pos = 17  # Após o hífen: "12.345.678/9012-3"
            else:  # len(texto_limpo) == 14
                nova_pos = 18
            
            # Define a nova posição do cursor
            self.cnpj_input.setCursorPosition(nova_pos)
            self.cnpj_input.blockSignals(False)
    
    def formatar_cep(self, texto):
        """Formata o CEP durante a digitação e busca endereço quando completo"""
        # Guarda a posição atual do cursor
        cursor_pos = self.cep_input.cursorPosition()
        
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 8 dígitos
        if len(texto_limpo) > 8:
            texto_limpo = texto_limpo[:8]
        
        # Formatar CEP: 00000-000
        if len(texto_limpo) <= 5:
            texto_formatado = texto_limpo
        else:
            texto_formatado = f"{texto_limpo[:5]}-{texto_limpo[5:]}"
        
        # Verifica se o texto realmente mudou para evitar loops
        if texto_formatado != texto:
            # Calcula quantos caracteres foram adicionados ou removidos
            dif_tamanho = len(texto_formatado) - len(texto)
            
            # Bloqueia sinais para evitar recursão
            self.cep_input.blockSignals(True)
            self.cep_input.setText(texto_formatado)
            
            # Ajuste especial para o hífen: se o usuário acabou de digitar o 5º dígito
            if len(texto_limpo) == 5 and len(''.join(filter(str.isdigit, texto))) == 5:
                # Posiciona o cursor depois do hífen
                nova_pos = 6
            else:
                # Ajusta a posição do cursor considerando a mudança de tamanho do texto
                nova_pos = cursor_pos + dif_tamanho
                # Garante que a posição está dentro dos limites do texto
                if nova_pos < 0:
                    nova_pos = 0
                elif nova_pos > len(texto_formatado):
                    nova_pos = len(texto_formatado)
            
            # Define a nova posição do cursor
            self.cep_input.setCursorPosition(nova_pos)
            self.cep_input.blockSignals(False)
        
        # Se o CEP estiver completo (8 dígitos), buscar endereço automaticamente
        if len(texto_limpo) == 8:
            self.buscar_endereco_por_cep()
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual 
        if self.janela_parent:
            self.janela_parent.close()
        else:
            # Caso esteja rodando independentemente
            print("Voltar para a tela de fornecedores")
    
    def incluir(self):
        """Inclui um novo fornecedor"""
        # Validar campos obrigatórios
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        fantasia = self.fantasia_input.text()
        tipo = self.tipo_combo.currentText()
        cnpj = self.cnpj_input.text()
        
        if not codigo or not nome or tipo == "Selecione um tipo" or not cnpj:
            self.mostrar_mensagem("Atenção", "Preencha todos os campos obrigatórios (Código, Nome, Tipo e CNPJ)!")
            return
        
        # Atualizar a tabela da tela de cadastro se estiver em modo de alteração
        if self.cadastro_tela and hasattr(self.cadastro_tela, 'tabela'):
            for row in range(self.cadastro_tela.tabela.rowCount()):
                if self.cadastro_tela.tabela.item(row, 0).text() == codigo:
                    # Atualizar linha existente
                    self.cadastro_tela.tabela.setItem(row, 1, QTableWidgetItem(nome))
                    self.cadastro_tela.tabela.setItem(row, 2, QTableWidgetItem(fantasia))
                    self.cadastro_tela.tabela.setItem(row, 3, QTableWidgetItem(tipo))
                    break
            else:
                # Adicionar nova linha
                row = self.cadastro_tela.tabela.rowCount()
                self.cadastro_tela.tabela.insertRow(row)
                self.cadastro_tela.tabela.setItem(row, 0, QTableWidgetItem(codigo))
                self.cadastro_tela.tabela.setItem(row, 1, QTableWidgetItem(nome))
                self.cadastro_tela.tabela.setItem(row, 2, QTableWidgetItem(fantasia))
                self.cadastro_tela.tabela.setItem(row, 3, QTableWidgetItem(tipo))
        
        # Limpar os campos após inclusão
        self.codigo_input.clear()
        self.nome_input.clear()
        self.fantasia_input.clear()
        self.cnpj_input.clear()
        self.rua_input.clear()
        self.bairro_input.clear()
        self.cep_input.clear()
        self.cidade_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.data_input.setDate(QDate.currentDate())
        
        self.mostrar_mensagem("Sucesso", "Fornecedor incluído com sucesso!")
        
        # Fechar a janela de formulário após a inclusão
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
    window.setWindowTitle("Cadastro de Fornecedores")
    window.setGeometry(100, 100, 700, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    formulario_fornecedores_widget = FormularioFornecedores()
    window.setCentralWidget(formulario_fornecedores_widget)
    
    window.show()
    sys.exit(app.exec_())