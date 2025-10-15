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
                            'inscricao_estadual': '',
                            'cnae': dados.get('atividade_principal', [{}])[0].get('code', '') if dados.get('atividade_principal') else '',
                            'cnea_sec': ''
                        }
                        
                        self.consulta_concluida.emit(resultado)
                        return
                
                except (requests.RequestException, json.JSONDecodeError) as e:
                    continue
            
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
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(5)
        
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
                padding: 5px 8px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        self.btn_voltar.clicked.connect(self.voltar)
        
        # Título
        titulo = QLabel("Consulta CNPJ")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 5px;")
        titulo.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.btn_voltar)
        header_layout.addWidget(titulo, 1)
        
        main_layout.addLayout(header_layout)
        
        # Estilo para os labels
        label_style = "QLabel { color: white; font-size: 12px; font-weight: bold; }"
        
        # Estilo para os inputs
        input_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 3px;
                font-size: 12px;
                min-height: 18px;
                max-height: 24px;
                border-radius: 3px;
            }
        """
        
        # Campo CNPJ
        cnpj_layout = QHBoxLayout()
        cnpj_layout.setSpacing(5)
        
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
                padding: 4px 12px;
                font-size: 12px;
                border-radius: 3px;
                min-width: 100px;
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
        form_esquerda.setVerticalSpacing(3)
        form_esquerda.setHorizontalSpacing(5)
        
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
        form_direita.setVerticalSpacing(3)
        form_direita.setHorizontalSpacing(5)
        
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
        
        # Botões "Incluir como Cliente" e "Incluir como Fornecedor"
        self.btn_incluir_cliente = QPushButton("Incluir como um novo Cliente")
        self.btn_incluir_cliente.setStyleSheet("""
            QPushButton {
                background-color: #01fd9a;
                color: black;
                border: none;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir_cliente.clicked.connect(self.incluir_como_cliente)
        
        self.btn_incluir_fornecedor = QPushButton("Incluir como um novo Fornecedor")
        self.btn_incluir_fornecedor.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        self.btn_incluir_fornecedor.clicked.connect(self.incluir_como_fornecedor)
        
        # Layout horizontal para os botões
        opcoes_inclusion_btns = QHBoxLayout()
        opcoes_inclusion_btns.setAlignment(Qt.AlignCenter)
        opcoes_inclusion_btns.setSpacing(10)
        opcoes_inclusion_btns.addWidget(self.btn_incluir_cliente)
        opcoes_inclusion_btns.addWidget(self.btn_incluir_fornecedor)
        
        main_layout.addLayout(opcoes_inclusion_btns)
        
        # Definir estilo do widget principal
        self.setStyleSheet("background-color: #043b57;")
        
        # Verificar e avisar se o módulo requests não estiver disponível
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Atenção", 
                "O módulo 'requests' não está disponível. A consulta de CNPJ não será possível.")
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
        texto_limpo = ''.join(filter(str.isdigit, texto))
        
        if len(texto_limpo) > 14:
            texto_limpo = texto_limpo[:14]
        
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
        
        if texto_formatado != texto:
            self.cnpj_input.blockSignals(True)
            self.cnpj_input.setText(texto_formatado)
            
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
            
            self.cnpj_input.setCursorPosition(nova_pos)
            self.cnpj_input.blockSignals(False)
    
    def consultar_cnpj(self):
        """Consulta os dados do CNPJ"""
        if not REQUESTS_AVAILABLE:
            QMessageBox.warning(self, "Funcionalidade indisponível", 
                               "A consulta de CNPJ requer o módulo 'requests' que não está disponível.")
            return
            
        cnpj = ''.join(filter(str.isdigit, self.cnpj_input.text()))
        
        if len(cnpj) != 14:
            msg = QMessageBox(self)
            msg.setWindowTitle("CNPJ Inválido")
            msg.setText("Por favor, digite um CNPJ válido.")
            msg.setStyleSheet("background-color: white;")
            msg.exec_()
            return
        
        if not self.validar_cnpj(cnpj):
            msg = QMessageBox(self)
            msg.setWindowTitle("CNPJ Inválido")
            msg.setText("O CNPJ digitado não é válido.")
            msg.setStyleSheet("background-color: white;")
            msg.exec_()
            return
        
        self.btn_consultar.setEnabled(False)
        self.btn_consultar.setText("Consultando...")
        
        campos = [
            'nome_input', 'tipo_empresa_input', 'fantasia_input', 'abertura_input', 
            'numero_input', 'complemento_input', 'bairro_input', 'cidade_input', 
            'uf_input', 'cep_input', 'situacao_input', 'telefone_input', 
            'email_input', 'inscricao_estadual_input', 'cnae_input', 'cnea_sec_input'
        ]
        
        for campo in campos:
            getattr(self, campo).clear()
        
        self.thread_consulta = CNPJConsultaThread(cnpj)
        self.thread_consulta.consulta_concluida.connect(self.processar_resultado_consulta)
        self.thread_consulta.erro_consulta.connect(self.processar_erro_consulta)
        self.thread_consulta.start()
    
    def processar_resultado_consulta(self, dados):
        """Processa o resultado da consulta de CNPJ"""
        self.btn_consultar.setEnabled(True)
        self.btn_consultar.setText("Consultar")
        
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
        self.btn_consultar.setEnabled(True)
        self.btn_consultar.setText("Consultar")
        
        QMessageBox.warning(self, "Erro na Consulta", mensagem)
    
    def validar_cnpj(self, cnpj):
        """Valida o formato do CNPJ"""
        if len(set(cnpj)) == 1:
            return False
        
        def calcular_digito(cnpj, peso):
            soma = sum(int(d) * p for d, p in zip(cnpj, peso))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        digitos = list(map(int, cnpj))
        
        dv1 = calcular_digito(cnpj[:12], peso1)
        
        if dv1 != digitos[12]:
            return False
        
        dv2 = calcular_digito(cnpj[:13], peso2)
        
        return dv2 == digitos[13]
    
    def incluir_como_cliente(self):
        """
        Inclui os dados consultados do CNPJ como uma nova pessoa no banco de dados
        """
        if not self.nome_input.text():
            QMessageBox.warning(self, "Dados incompletos", 
                            "Por favor, consulte um CNPJ antes de incluir os dados.")
            return
        
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from base.banco import criar_pessoa
            
            nome = self.nome_input.text()
            tipo_pessoa = "Jurídica"
            documento = self.cnpj_input.text()
            telefone = self.telefone_input.text()
            cep = self.cep_input.text() or ""
            complemento = self.complemento_input.text() or ""
            numero = self.numero_input.text() or ""
            
            rua = ""
            if complemento or numero:
                if complemento and numero:
                    rua = f"{complemento}, {numero}"
                elif complemento:
                    rua = complemento
                else:
                    rua = f"Número: {numero}"
            
            bairro = self.bairro_input.text() or ""
            cidade = self.cidade_input.text() or ""
            estado = self.uf_input.text() or ""
            
            from datetime import datetime
            data_cadastro = datetime.now().strftime("%d/%m/%Y")
            
            observacao = f"CNPJ consultado automaticamente. "
            
            info_add = []
            if self.situacao_input.text():
                info_add.append(f"Situação: {self.situacao_input.text()}")
            if self.fantasia_input.text():
                info_add.append(f"Nome Fantasia: {self.fantasia_input.text()}")
            if self.email_input.text():
                info_add.append(f"Email: {self.email_input.text()}")
            if self.cnae_input.text():
                info_add.append(f"CNAE: {self.cnae_input.text()}")
            if self.inscricao_estadual_input.text():
                info_add.append(f"Inscrição Estadual: {self.inscricao_estadual_input.text()}")
            if self.abertura_input.text():
                info_add.append(f"Data de Abertura: {self.abertura_input.text()}")
            
            observacao += ". ".join(info_add)
            
            novo_id = criar_pessoa(
                nome, 
                tipo_pessoa, 
                documento, 
                telefone, 
                data_cadastro,
                cep, 
                rua, 
                bairro, 
                cidade, 
                estado, 
                observacao
            )
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Inclusão")
            msg.setText(f"Empresa cadastrada com sucesso como Cliente!\n\nCódigo: {novo_id}\nNome: {nome}")
            msg.setStyleSheet("background-color: white;")
            msg.exec_()
            
            if self.cadastro_tela and hasattr(self.cadastro_tela, 'carregar_pessoas'):
                self.cadastro_tela.carregar_pessoas()
            
            if self.janela_parent:
                self.janela_parent.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao incluir os dados: {str(e)}")
            import traceback
            traceback.print_exc()

    def incluir_como_fornecedor(self):
        """
        Inclui os dados consultados do CNPJ como um novo fornecedor no banco de dados
        """
        if not self.nome_input.text():
            QMessageBox.warning(self, "Dados incompletos", 
                            "Por favor, consulte um CNPJ antes de incluir os dados.")
            return
        
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from base.banco import criar_fornecedor
            
            nome = self.nome_input.text()
            fantasia = self.fantasia_input.text() or ""
            cnpj = self.cnpj_input.text()
            
            # Determinar tipo de fornecedor baseado no tipo de empresa
            tipo_empresa = self.tipo_empresa_input.text()
            if "Fabricante" in tipo_empresa or "Indústria" in tipo_empresa:
                tipo = "Fabricante"
            elif "Distribuidor" in tipo_empresa:
                tipo = "Distribuidor"
            elif "Atacado" in tipo_empresa or "Atacadista" in tipo_empresa:
                tipo = "Atacadista"
            else:
                tipo = "Distribuidor"  # Padrão
            
            cep = self.cep_input.text() or ""
            complemento = self.complemento_input.text() or ""
            numero = self.numero_input.text() or ""
            
            # Usar RUA em vez de ENDERECO (conforme a tabela)
            rua = ""
            if complemento or numero:
                if complemento and numero:
                    rua = f"{complemento}, {numero}"
                elif complemento:
                    rua = complemento
                else:
                    rua = f"Número: {numero}"
            
            bairro = self.bairro_input.text() or ""
            cidade = self.cidade_input.text() or ""
            estado = self.uf_input.text() or ""  # Usar ESTADO em vez de UF
            
            from datetime import datetime
            data_cadastro = datetime.now().strftime("%d/%m/%Y")
            
            # CORREÇÃO: Chamar criar_fornecedor com a assinatura correta
            # A função espera: (codigo, nome, fantasia, tipo, cnpj, data_cadastro, cep, rua, bairro, cidade, estado)
            # O código será gerado automaticamente pela função, então passamos string vazia
            novo_id = criar_fornecedor(
                "",  # codigo (será gerado automaticamente)
                nome,
                fantasia,
                tipo,
                cnpj,
                data_cadastro,
                cep,
                rua,
                bairro,
                cidade,
                estado
            )
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Inclusão")
            msg.setText(f"Empresa cadastrada com sucesso como Fornecedor!\n\nCódigo: {novo_id}\nNome: {nome}")
            msg.setStyleSheet("background-color: white;")
            msg.exec_()
            
            if self.cadastro_tela and hasattr(self.cadastro_tela, 'carregar_fornecedores'):
                self.cadastro_tela.carregar_fornecedores()
            
            if self.janela_parent:
                self.janela_parent.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao incluir o fornecedor: {str(e)}")
            import traceback
            traceback.print_exc()


class ConsultaCNPJWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Consulta CNPJ")
        self.setGeometry(100, 100, 800, 480)
        self.setStyleSheet("background-color: #043b57;")
        
        form_widget = ConsultaCNPJForm(janela_parent=self)
        self.setCentralWidget(form_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConsultaCNPJWindow()
    window.show()
    sys.exit(app.exec_())