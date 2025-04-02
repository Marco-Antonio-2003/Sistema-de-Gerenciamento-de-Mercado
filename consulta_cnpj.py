import sys
import requests
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QFormLayout, QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import re

class CNPJConsultaThread(QThread):
    """Thread para realizar consulta de CNPJ em segundo plano"""
    consulta_concluida = pyqtSignal(dict)
    erro_consulta = pyqtSignal(str)
    
    def __init__(self, cnpj):
        super().__init__()
        self.cnpj = cnpj

    def run(self):
        try:
            # Método de consulta mais robusto
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }

            # Tentativa com múltiplas APIs de consulta de CNPJ
            apis = [
                f'https://www.receitaws.com.br/v1/cnpj/{self.cnpj}',
                f'https://brasilapi.com.br/api/cnpj/v1/{self.cnpj}'
            ]

            for url in apis:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        
                        # Padronizar os dados
                        resultado = {
                            'nome': dados.get('nome', '') or dados.get('razao_social', ''),
                            'fantasia': dados.get('fantasia', ''),
                            'abertura': dados.get('abertura', ''),
                            'situacao': dados.get('situacao', ''),
                            'tipo_empresa': dados.get('tipo', ''),
                            'cnpj': self.cnpj,
                            'telefone': dados.get('telefone', ''),
                            'email': dados.get('email', ''),
                            'bairro': dados.get('bairro', ''),
                            'cidade': dados.get('municipio', ''),
                            'uf': dados.get('uf', ''),
                            'cep': dados.get('cep', '').replace('.', ''),
                            'numero': dados.get('numero', ''),
                            'complemento': dados.get('complemento', ''),
                            'inscricao_estadual': '',  # Pode não estar disponível
                            'cnae': dados.get('atividade_principal', [{}])[0].get('code', '') if dados.get('atividade_principal') else '',
                            'cnea_sec': ''  # Pode não estar disponível
                        }
                        
                        self.consulta_concluida.emit(resultado)
                        return
                
                except (requests.RequestException, json.JSONDecodeError) as e:
                    # Continua para próxima API se uma falhar
                    continue
            
            # Se todas as APIs falharem
            self.erro_consulta.emit("Não foi possível consultar o CNPJ. Verifique o número ou sua conexão.")
        
        except Exception as e:
            self.erro_consulta.emit(f"Erro inesperado: {str(e)}")

class ConsultaCNPJForm(QWidget):
    def __init__(self, cadastro_tela=None, janela_parent=None):
        super().__init__()
        self.cadastro_tela = cadastro_tela
        self.janela_parent = janela_parent
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        # Dentro do método initUI() da classe ConsultaCNPJForm, adicione após o layout de opções de inclusão:
        
        # Grupo de opções de inclusão (já existente)
        opcoes_inclusao_layout = QHBoxLayout()
        
        # # Grupo de botões de rádio
        # self.btn_group = QButtonGroup()
        
        # self.radio_cliente = QRadioButton("Incluir com novo Cliente")
        # self.radio_cliente.setStyleSheet("color: white;")
        # self.radio_fornecedor = QRadioButton("Como Fornecedor")
        # self.radio_fornecedor.setStyleSheet("color: white;")
        
        # self.btn_group.addButton(self.radio_cliente)
        # self.btn_group.addButton(self.radio_fornecedor)
        
        # opcoes_inclusao_layout.addWidget(self.radio_cliente)
        # opcoes_inclusao_layout.addWidget(self.radio_fornecedor)
        
        # main_layout.addLayout(opcoes_inclusao_layout)
        
       
        
        # Botão de voltar
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setFixedWidth(80)
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Título
        titulo_layout = QVBoxLayout()
        titulo = QLabel("Consulta CNPJ")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(titulo)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 14px; font-weight: bold; }"
        
        # Estilo para os inputs
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
        """
        
        # Campo CNPJ
        cnpj_layout = QHBoxLayout()
        
        self.cnpj_label = QLabel("Digite o CNPJ:")
        self.cnpj_label.setStyleSheet(label_style)
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setStyleSheet(input_style)
        self.cnpj_input.setPlaceholderText("00.000.000/0001-00")
        self.cnpj_input.textChanged.connect(self.formatar_cnpj)
        
        # Botão Consultar
        self.btn_consultar = QPushButton("Consultar")
        self.btn_consultar.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_consultar.clicked.connect(self.consultar_cnpj)
        
        cnpj_layout.addWidget(self.cnpj_label)
        cnpj_layout.addWidget(self.cnpj_input)
        cnpj_layout.addWidget(self.btn_consultar)
        
        main_layout.addLayout(cnpj_layout)
        
        # Campos de informação
        campos = [
            ("Nome:", "nome_input"),
            ("Tipo de Empresa:", "tipo_empresa_input"),
            ("Fantasia:", "fantasia_input"),
            ("Abertura:", "abertura_input"),
            ("Número:", "numero_input"),
            ("Complemento:", "complemento_input"),
            ("Bairro:", "bairro_input"),
            ("Cidade:", "cidade_input"),
            ("UF:", "uf_input"),
            ("CEP:", "cep_input"),
            ("Situação:", "situacao_input"),
            ("Telefone:", "telefone_input"),
            ("Email:", "email_input"),
            ("Ins. Estadual:", "inscricao_estadual_input"),
            ("CNAE:", "cnae_input"),
            ("CNEA Sec:", "cnea_sec_input")
        ]
        
        # Layout de formulário para os campos
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        for label_text, attr_name in campos:
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            input_field = QLineEdit()
            input_field.setStyleSheet(input_style)
            input_field.setReadOnly(True)
            setattr(self, attr_name, input_field)
            form_layout.addRow(label, input_field)
        
        main_layout.addLayout(form_layout)
        
        # Grupo de opções de inclusão
        opcoes_inclusao_layout = QHBoxLayout()
         # Botão "Incluir"
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir.clicked.connect(self.incluir_registro)
        main_layout.addWidget(self.btn_incluir)

        # Grupo de botões de rádio
        self.btn_group = QButtonGroup()
        
        self.radio_cliente = QRadioButton("Incluir com novo Cliente")
        self.radio_cliente.setStyleSheet("color: white;")
        self.radio_fornecedor = QRadioButton("Como Fornecedor")
        self.radio_fornecedor.setStyleSheet("color: white;")
        
        self.btn_group.addButton(self.radio_cliente)
        self.btn_group.addButton(self.radio_fornecedor)
        
        opcoes_inclusao_layout.addWidget(self.radio_cliente)
        opcoes_inclusao_layout.addWidget(self.radio_fornecedor)
        
        main_layout.addLayout(opcoes_inclusao_layout)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        

    # [Restante dos métodos mantidos iguais ao código anterior]
    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
    
    def incluir_registro(self):
        """
        Método para incluir os dados consultados no banco de dados.
        Atualmente, apenas exibe uma mensagem de sucesso.
        """
        # Aqui você pode adicionar a lógica para inserir os dados no banco de dados.
        # Exemplo: if self.radio_cliente.isChecked(): inserir_cliente() else: inserir_fornecedor()
        msg = QMessageBox(self)
        msg.setWindowTitle("Inclusão")
        msg.setText("Registro incluído com sucesso!")
        msg.setStyleSheet("background-color: white;")
        msg.exec_()


    def formatar_cnpj(self, texto):
        """Formata o CNPJ durante a digitação"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        # Limitar a 14 dígitos
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
            if len(texto_limpo) <= 2:
                nova_pos = len(texto_limpo)
            elif len(texto_limpo) <= 5:
                nova_pos = len(texto_limpo) + 1
            elif len(texto_limpo) <= 8:
                nova_pos = len(texto_limpo) + 2
            elif len(texto_limpo) <= 12:
                nova_pos = len(texto_limpo) + 3
            else:
                nova_pos = len(texto_limpo) + 4
            
            # Define a nova posição do cursor
            self.cnpj_input.setCursorPosition(nova_pos)
            self.cnpj_input.blockSignals(False)
    
    def consultar_cnpj(self):
        """Consulta os dados do CNPJ"""
        # Remover caracteres não numéricos
        cnpj = ''.join(filter(str.isdigit, self.cnpj_input.text()))
        
        # Validar CNPJ
        if len(cnpj) != 14:
            msg = QMessageBox(self)
            msg.setWindowTitle("CNPJ Inválido")
            msg.setText("Por favor, digite um CNPJ válido.")
            msg.setStyleSheet("background-color: white;")
            msg.exec_()

            return
        
        # Validar formato do CNPJ
        if not self.validar_cnpj(cnpj):
            msg = QMessageBox(self)
            msg.setWindowTitle("CNPJ Inválido")
            msg.setText("O CNPJ digitado não é válido.")
            msg.setStyleSheet("background-color: white;")
            msg.exec_()

            return
        
        # Desabilitar botão durante consulta
        self.btn_consultar.setEnabled(False)
        self.btn_consultar.setText("Consultando...")
        
        # Limpar campos anteriores
        campos = [
            'nome_input', 'tipo_empresa_input', 'fantasia_input', 'abertura_input', 
            'numero_input', 'complemento_input', 'bairro_input', 'cidade_input', 
            'uf_input', 'cep_input', 'situacao_input', 'telefone_input', 
            'email_input', 'inscricao_estadual_input', 'cnae_input', 'cnea_sec_input'
        ]
        
        for campo in campos:
            getattr(self, campo).clear()
        
        # Iniciar thread de consulta
        self.thread_consulta = CNPJConsultaThread(cnpj)
        self.thread_consulta.consulta_concluida.connect(self.processar_resultado_consulta)
        self.thread_consulta.erro_consulta.connect(self.processar_erro_consulta)
        self.thread_consulta.start()
    
    def processar_resultado_consulta(self, dados):
        """Processa o resultado da consulta de CNPJ"""
        # Reabilitar botão
        self.btn_consultar.setEnabled(True)
        self.btn_consultar.setText("Consultar")
        
        # Preencher os campos
        self.nome_input.setText(dados.get('nome', ''))
        self.tipo_empresa_input.setText(dados.get('tipo_empresa', ''))
        self.fantasia_input.setText(dados.get('fantasia', ''))
        self.abertura_input.setText(dados.get('abertura', ''))
        self.numero_input.setText(dados.get('numero', ''))
        self.complemento_input.setText(dados.get('complemento', ''))
        self.bairro_input.setText(dados.get('bairro', ''))
        self.cidade_input.setText(dados.get('cidade', ''))
        self.uf_input.setText(dados.get('uf', ''))
        self.cep_input.setText(dados.get('cep', ''))
        self.situacao_input.setText(dados.get('situacao', ''))
        self.telefone_input.setText(dados.get('telefone', ''))
        self.email_input.setText(dados.get('email', ''))
        self.inscricao_estadual_input.setText(dados.get('inscricao_estadual', ''))
        self.cnae_input.setText(dados.get('cnae', ''))
        self.cnea_sec_input.setText(dados.get('cnea_sec', ''))
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Sucesso")
        msg.setText("Dados do CNPJ consultados com sucesso!")
        msg.setStyleSheet("background-color: white;")
        msg.exec_()

    
    def processar_erro_consulta(self, mensagem):
        """Processa erros na consulta de CNPJ"""
        # Reabilitar botão
        self.btn_consultar.setEnabled(True)
        self.btn_consultar.setText("Consultar")
        
        QMessageBox.warning(self, "Erro na Consulta", mensagem)
    
    def validar_cnpj(self, cnpj):
        """Valida o formato do CNPJ"""
        # Verifica se o CNPJ tem 14 dígitos e não são todos iguais
        if len(set(cnpj)) == 1:
            return False
        
        # Calcula os dígitos verificadores
        def calcular_digito(cnpj, peso):
            soma = sum(int(d) * p for d, p in zip(cnpj, peso))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Pesos para o primeiro dígito verificador
        peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        # Pesos para o segundo dígito verificador
        peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        # Extrai os dígitos para verificação
        digitos = list(map(int, cnpj))
        
        # Calcula o primeiro dígito verificador
        dv1 = calcular_digito(cnpj[:12], peso1)
        
        # Verifica o primeiro dígito verificador
        if dv1 != digitos[12]:
            return False
        
        # Calcula o segundo dígito verificador
        dv2 = calcular_digito(cnpj[:13], peso2)
        
        # Verifica o segundo dígito verificador
        return dv2 == digitos[13]
    

# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Consulta CNPJ")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    form_widget = ConsultaCNPJForm()
    window.setCentralWidget(form_widget)
    
    window.show()
    sys.exit(app.exec_())