import sys
# Importação condicional do requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
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
        # Verificar se o módulo requests está disponível
        if not REQUESTS_AVAILABLE:
            self.erro_consulta.emit("O módulo 'requests' não está disponível. A consulta de CNPJ não é possível.")
            return
            
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
        # Layout principal com margens reduzidas
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)  # Reduzido o espaço vertical
        main_layout.setSpacing(5)  # Espaçamento reduzido entre elementos
        
        # Botão de voltar e título em linha horizontal
        header_layout = QHBoxLayout()
        
        # Botão de voltar
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setFixedWidth(80)
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 5px 8px;  /* Padding reduzido */
                font-size: 13px;   /* Fonte reduzida */
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        # Conectar o botão voltar ao método voltar
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Título
        titulo = QLabel("Consulta CNPJ")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))  # Fonte reduzida
        titulo.setStyleSheet("color: white; margin-bottom: 5px;")  # Margem reduzida
        titulo.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.btn_voltar)
        header_layout.addWidget(titulo, 1)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para os labels - tamanho da fonte reduzido
        label_style = "QLabel { color: white; font-size: 12px; font-weight: bold; }"
        
        # Estilo para os inputs - menor altura
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 3px;  /* Padding reduzido */
                font-size: 12px;  /* Fonte reduzida */
                min-height: 18px;  /* Altura mínima reduzida */
                max-height: 24px;  /* Altura máxima reduzida */
                border-radius: 3px;
            }
        """
        
        # Campo CNPJ
        cnpj_layout = QHBoxLayout()
        cnpj_layout.setSpacing(5)  # Espaçamento reduzido
        
        self.cnpj_label = QLabel("Digite o CNPJ:")
        self.cnpj_label.setStyleSheet(label_style)
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setStyleSheet(input_style)
        self.cnpj_input.setPlaceholderText("00.000.000/0001-00")
        self.cnpj_input.textChanged.connect(self.formatar_cnpj)
        
        # Botão Consultar com tamanho reduzido
        self.btn_consultar = QPushButton("Consultar")
        self.btn_consultar.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                font-weight: bold;
                padding: 4px 12px;  /* Padding reduzido */
                font-size: 12px;  /* Fonte reduzida */
                border-radius: 3px;
                min-width: 100px;  /* Largura mínima reduzida */
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
        
        # Campos de informação organizados em duas colunas
        campos_esquerda = [
            ("Nome:", "nome_input"),
            ("Tipo de Empresa:", "tipo_empresa_input"),
            ("Fantasia:", "fantasia_input"),
            ("Abertura:", "abertura_input"),
            ("Número:", "numero_input"),
            ("Complemento:", "complemento_input"),
            ("Bairro:", "bairro_input"),
            ("Cidade:", "cidade_input")
        ]
        
        campos_direita = [
            ("UF:", "uf_input"),
            ("CEP:", "cep_input"),
            ("Situação:", "situacao_input"),
            ("Telefone:", "telefone_input"),
            ("Email:", "email_input"),
            ("Ins. Estadual:", "inscricao_estadual_input"),
            ("CNAE:", "cnae_input"),
            ("CNEA Sec:", "cnea_sec_input")
        ]
        
        # Layout para as duas colunas
        duas_colunas_layout = QHBoxLayout()
        
        # Layout de formulário para a coluna esquerda
        form_esquerda = QFormLayout()
        form_esquerda.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_esquerda.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_esquerda.setVerticalSpacing(3)  # Espaçamento vertical reduzido
        form_esquerda.setHorizontalSpacing(5)  # Espaçamento horizontal reduzido
        
        for label_text, attr_name in campos_esquerda:
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            input_field = QLineEdit()
            input_field.setStyleSheet(input_style)
            input_field.setReadOnly(True)
            setattr(self, attr_name, input_field)
            form_esquerda.addRow(label, input_field)
        
        # Layout de formulário para a coluna direita
        form_direita = QFormLayout()
        form_direita.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_direita.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_direita.setVerticalSpacing(3)  # Espaçamento vertical reduzido
        form_direita.setHorizontalSpacing(5)  # Espaçamento horizontal reduzido
        
        for label_text, attr_name in campos_direita:
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            input_field = QLineEdit()
            input_field.setStyleSheet(input_style)
            input_field.setReadOnly(True)
            setattr(self, attr_name, input_field)
            form_direita.addRow(label, input_field)
        
        duas_colunas_layout.addLayout(form_esquerda)
        duas_colunas_layout.addLayout(form_direita)
        
        main_layout.addLayout(duas_colunas_layout)
        
        # Botão "Incluir" com tamanho reduzido
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                padding: 4px 12px;  /* Padding reduzido */
                font-size: 12px;  /* Fonte reduzida */
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir.clicked.connect(self.incluir_registro)
        
        # Grupo de opções de inclusão com layout compacto
        opcoes_inclusion_btns = QHBoxLayout()
        opcoes_inclusion_btns.setAlignment(Qt.AlignCenter)
        opcoes_inclusion_btns.addWidget(self.btn_incluir)
        
        main_layout.addLayout(opcoes_inclusion_btns)
        
        # Grupo de botões de rádio em layout horizontal com espaçamento reduzido
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(10)  # Espaçamento reduzido
        radio_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_group = QButtonGroup()
        
        self.radio_cliente = QRadioButton("Incluir como Cliente")
        self.radio_cliente.setStyleSheet("color: white; font-size: 12px;")  # Fonte reduzida
        self.radio_fornecedor = QRadioButton("Como Fornecedor")
        self.radio_fornecedor.setStyleSheet("color: white; font-size: 12px;")  # Fonte reduzida
        
        self.btn_group.addButton(self.radio_cliente)
        self.btn_group.addButton(self.radio_fornecedor)
        
        radio_layout.addWidget(self.radio_cliente)
        radio_layout.addWidget(self.radio_fornecedor)
        
        main_layout.addLayout(radio_layout)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Atenção", 
                "O módulo 'requests' não está disponível. A consulta de CNPJ não será possível.")
            # Desabilitar botão de consulta
            self.btn_consultar.setEnabled(False)
            self.btn_consultar.setStyleSheet("""
                QPushButton {
                    background-color: #888888;
                    color: #dddddd;
                    border: none;
                    font-weight: bold;
                    padding: 4px 12px;
                    font-size: 12px;
                    border-radius: 3px;
                    min-width: 100px;
                }
            """)

    def voltar(self):
        """Volta para a tela anterior fechando esta janela"""
        if self.janela_parent:
            self.janela_parent.close()
        elif isinstance(self.parent(), QMainWindow):
            self.parent().close()

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
        # Verificar se o módulo requests está disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Funcionalidade indisponível", 
                               "A consulta de CNPJ requer o módulo 'requests' que não está disponível.")
            return
            
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


class ConsultaCNPJWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Consulta CNPJ")
        self.setGeometry(100, 100, 800, 480)  # Altura reduzida de 600 para 480
        self.setStyleSheet("background-color: #043b57;")
        
        form_widget = ConsultaCNPJForm(janela_parent=self)
        self.setCentralWidget(form_widget)


# Para testar a tela individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConsultaCNPJWindow()
    window.show()
    sys.exit(app.exec_())