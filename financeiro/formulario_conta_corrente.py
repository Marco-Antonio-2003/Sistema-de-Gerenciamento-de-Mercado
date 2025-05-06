import os
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFormLayout, 
                            QWidget, QMessageBox, QGridLayout, QCheckBox,
                            QComboBox, QTabWidget)
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from geral.formulario_empresa import FormularioEmpresa

# Importar formulário de empresa
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from geral.formulario_empresa import FormularioEmpresa

# Importar funções do banco.py para operações com o banco de dados Firebird
from base.banco import (execute_query, criar_conta_corrente, atualizar_conta_corrente,
                       buscar_conta_corrente_por_id, buscar_conta_corrente_por_codigo,
                       listar_empresas)

class FormularioContaCorrente(QDialog):
    def __init__(self, parent=None, main_window=None, id_conta=None, codigo="", descricao="", 
                agencia="", numero_conta="", empresa="", saldo="0.00", caixa_pdv=False, modo_edicao=False):
        super().__init__(parent)
        self.parent = parent
        self.main_window = main_window
        self.modo_edicao = modo_edicao
        self.codigo_original = codigo
        self.id_conta = id_conta  # Adicionado para armazenar ID da conta quando em modo de edição
        self.initUI(codigo, descricao, agencia, numero_conta, empresa, saldo, caixa_pdv)
        
    def initUI(self, codigo, descricao, agencia, numero_conta, empresa, saldo, caixa_pdv):
        # Configuração da janela
        self.setWindowTitle("Incluindo Registro")
        self.setMinimumWidth(560)
        self.setMinimumHeight(270)
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Criar um widget para o conteúdo principal
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Tab widget (apenas com a aba "Geral")
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #cccccc;
                background-color: #003353;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: black;
                padding: 5px 10px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #0078d7;
            }
        """)
        
        # Aba "Geral"
        tab_geral = QWidget()
        tab_geral.setStyleSheet("background-color: #003353;")
        tab_layout = QVBoxLayout(tab_geral)
        
        # Estilo para inputs
        input_style = """
            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 12px;
                min-height: 20px;
                color: black;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
            }
        """
        
        # Layout para campos Código, Descrição e checkbox CAIXA PDV
        top_grid = QGridLayout()
        top_grid.setVerticalSpacing(8)
        top_grid.setHorizontalSpacing(10)
        
        # Código
        codigo_label = QLabel("Código")
        codigo_label.setStyleSheet("color: white;")
        top_grid.addWidget(codigo_label, 0, 0)
        
        self.codigo_edit = QLineEdit(codigo)
        self.codigo_edit.setStyleSheet(input_style)
        self.codigo_edit.setFixedWidth(60)
        self.codigo_edit.setReadOnly(True)  # Tornar o campo somente leitura
        if not self.modo_edicao:
            # Gerar novo código baseado no próximo ID
            try:
                query = "SELECT COALESCE(MAX(ID), 0) + 1 FROM CONTAS_CORRENTES"
                resultado = execute_query(query)
                next_id = resultado[0][0] if resultado and resultado[0][0] else 1
                self.codigo_edit.setText(str(next_id))
            except Exception as e:
                print(f"Erro ao gerar código: {e}")
                self.codigo_edit.setText("1")
        top_grid.addWidget(self.codigo_edit, 0, 1)
        
        # Descrição
        descricao_label = QLabel("Descrição")
        descricao_label.setStyleSheet("color: white;")
        top_grid.addWidget(descricao_label, 0, 2)
        
        self.descricao_edit = QLineEdit(descricao)
        self.descricao_edit.setStyleSheet(input_style)
        self.descricao_edit.setMinimumWidth(300)
        top_grid.addWidget(self.descricao_edit, 0, 3)
        
        # Checkbox CAIXA PDV (à direita)
        self.caixa_pdv_check = QCheckBox("Utilizar esta conta como CAIXA PDV")
        self.caixa_pdv_check.setStyleSheet("color: white;")
        self.caixa_pdv_check.setChecked(caixa_pdv)
        top_grid.addWidget(self.caixa_pdv_check, 0, 4)
        
        tab_layout.addLayout(top_grid)
        
        # Linha 2: Agência e Número da Conta
        middle_grid = QGridLayout()
        middle_grid.setVerticalSpacing(8)
        middle_grid.setHorizontalSpacing(10)
        
        # Agência
        agencia_label = QLabel("Agência")
        agencia_label.setStyleSheet("color: white;")
        middle_grid.addWidget(agencia_label, 0, 0)
        
        self.agencia_edit = QLineEdit(agencia)
        self.agencia_edit.setStyleSheet(input_style)
        self.agencia_edit.setMinimumWidth(120)
        middle_grid.addWidget(self.agencia_edit, 0, 1)
        
        # Número da Conta
        conta_label = QLabel("Número da Conta")
        conta_label.setStyleSheet("color: white;")
        middle_grid.addWidget(conta_label, 0, 2)
        
        self.numero_conta_edit = QLineEdit(numero_conta)
        self.numero_conta_edit.setStyleSheet(input_style)
        self.numero_conta_edit.setMinimumWidth(120)
        middle_grid.addWidget(self.numero_conta_edit, 0, 3)
        
        # Saldo
        saldo_label = QLabel("Saldo")
        saldo_label.setStyleSheet("color: white;")
        middle_grid.addWidget(saldo_label, 0, 4)
        
        self.saldo_edit = QLineEdit(saldo)
        self.saldo_edit.setStyleSheet(input_style)
        self.saldo_edit.setMinimumWidth(120)
        
        # Configurar validador para permitir valores decimais
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        validator.setDecimals(2)
        self.saldo_edit.setValidator(validator)
        
        middle_grid.addWidget(self.saldo_edit, 0, 5)
        
        tab_layout.addLayout(middle_grid)
        
        # Linha 3: Empresa (removida a parte de Moeda)
        bottom_grid = QGridLayout()
        bottom_grid.setVerticalSpacing(8)
        bottom_grid.setHorizontalSpacing(10)
        
        # Empresa
        empresa_label = QLabel("Empresa")
        empresa_label.setStyleSheet("color: white;")
        bottom_grid.addWidget(empresa_label, 0, 0)
        
        # Layout para combobox de empresa e botão adicional
        empresa_layout = QHBoxLayout()
        
        # Criar um combobox editável para empresas
        self.empresa_combo = QComboBox()
        self.empresa_combo.setEditable(True)  # Permitir edição
        self.empresa_combo.setStyleSheet(input_style)
        self.empresa_combo.setMinimumWidth(350)
        
        # Carregar dados de empresas do banco de dados
        self.carregar_empresas()
        
        # Se estamos em modo de edição e já temos uma empresa, definir como texto atual
        if self.modo_edicao and empresa:
            index = self.empresa_combo.findText(empresa)
            if index >= 0:
                self.empresa_combo.setCurrentIndex(index)
            else:
                self.empresa_combo.setEditText(empresa)
        
        empresa_layout.addWidget(self.empresa_combo)
        
        # # Botão de busca de empresa
        # btn_buscar_empresa = QPushButton("")
        # btn_buscar_empresa.clicked.connect(self.abrir_formulario_empresa)

        # btn_buscar_empresa.setStyleSheet("""
        #     QPushButton {
        #         background-color: #00e676;
        #         color: black;
        #         padding: 3px;
        #         border: none;
        #         border-radius: 3px;
        #         font-size: 12px;
        #         font-weight: bold;
        #         min-width: 20px;
        #         max-width: 20px;
        #     }
        #     QPushButton:hover {
        #         background-color: #00c853;
        #     }
        # """)
        # # Conectar o botão à função que abre o formulário de empresa
        # btn_buscar_empresa.clicked.connect(self.abrir_formulario_empresa)
        # empresa_layout.addWidget(btn_buscar_empresa)
        
        # Adicionar layout de empresa ao grid
        bottom_grid.addLayout(empresa_layout, 0, 1, 1, 5)  # Span para ocupar todo o espaço
        
        tab_layout.addLayout(bottom_grid)
        
        # Adicionar espaço expansível para preencher o restante da aba
        tab_layout.addStretch(1)
        
        # Adicionar a aba ao tab widget
        tab_widget.addTab(tab_geral, "Geral")
        
        # Adicionar o tab widget ao layout principal
        content_layout.addWidget(tab_widget)
        
        # Adicionar o widget de conteúdo ao layout principal
        main_layout.addWidget(content_widget)
        
        # Botões de ação (Gravar e Cancelar) em uma linha horizontal no rodapé
        btn_layout = QHBoxLayout()
        
        # Espaço expansível à esquerda
        btn_layout.addStretch(1)
        
        # Botão Gravar
        self.btn_salvar = QPushButton("Gravar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: black;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00b248;
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar_conta)
        btn_layout.addWidget(self.btn_salvar)
        
        # Espaço entre botões
        btn_layout.addSpacing(10)
        
        # Botão Cancelar
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)
        
        main_layout.addLayout(btn_layout)
    
    def abrir_formulario_empresa(self):
        """Abre o formulário de cadastro de empresa"""
        try:
            # Instanciar o formulário de empresa
            formulario = FormularioEmpresa(self)
            
            # Exibir o formulário como um diálogo modal
            if formulario.exec_() == QDialog.Accepted:
                # Recarregar a lista de empresas para atualizar o combobox
                self.carregar_empresas()
                
        except Exception as e:
            print(f"Erro ao abrir formulário de empresa: {e}")
            self.mostrar_erro(f"Não foi possível abrir o formulário de empresa: {str(e)}")
    
    def carregar_empresas(self):
        """Carrega a lista de empresas do banco de dados"""
        try:
            # Obter lista de empresas do banco de dados
            empresas = listar_empresas()
            
            if empresas:
                # Limpar itens atuais
                self.empresa_combo.clear()
                
                # Adicionar empresas
                for empresa in empresas:
                    # Adicionar no formato "ID - NOME_EMPRESA"
                    self.empresa_combo.addItem(f"{empresa[0]} - {empresa[1]}")
                    
                # Adicionar "1 MB SISTEMA" como exemplo se não estiver na lista
                if self.empresa_combo.findText("1 MB SISTEMA", Qt.MatchContains) == -1:
                    self.empresa_combo.addItem("1 MB SISTEMA")
        except Exception as e:
            print(f"Erro ao carregar empresas: {e}")
            # Adicionar "1 MB SISTEMA" como exemplo se ocorrer erro
            self.empresa_combo.clear()
            self.empresa_combo.addItem("1 MB SISTEMA")
    
    def salvar_conta(self):
        """Salva os dados da conta corrente no banco de dados Firebird"""
        try:
            # Validar formulário
            codigo = self.codigo_edit.text().strip()
            descricao = self.descricao_edit.text().strip()
            agencia = self.agencia_edit.text().strip()
            numero_conta = self.numero_conta_edit.text().strip()
            
            # Extrair apenas o texto da empresa (removendo ID se presente)
            empresa_texto = self.empresa_combo.currentText().strip()
            if " - " in empresa_texto and empresa_texto[0].isdigit():
                # Formato "ID - NOME", extrair apenas NOME
                empresa = empresa_texto.split(" - ", 1)[1]
            else:
                empresa = empresa_texto
                
            saldo_text = self.saldo_edit.text().strip().replace(',', '.')
            caixa_pdv = self.caixa_pdv_check.isChecked()
            
            # Validações
            if not descricao:
                self.mostrar_erro("A descrição da conta é obrigatória.")
                return
            
            if not empresa:
                self.mostrar_erro("A empresa é obrigatória.")
                return
            
            # Converter saldo para float
            try:
                saldo = float(saldo_text) if saldo_text else 0.0
            except ValueError:
                self.mostrar_erro("O valor do saldo é inválido.")
                return
            
            # Converter caixa_pdv para 'S' ou 'N'
            caixa_pdv_valor = 'S' if caixa_pdv else 'N'
            
            # Salvar no banco de dados
            if self.modo_edicao and self.id_conta:
                # Modo de edição: atualizar conta existente
                atualizar_conta_corrente(
                    self.id_conta,
                    codigo,
                    descricao,
                    agencia,  # Banco
                    empresa,  # Descrição do banco
                    caixa_pdv_valor,
                    agencia,
                    numero_conta,
                    saldo
                )
                mensagem = f"Conta corrente alterada com sucesso!"
            else:
                # Modo de inclusão: criar nova conta com o código já gerado
                criar_conta_corrente(
                    codigo,
                    descricao,
                    agencia,  # Banco
                    empresa,  # Descrição do banco
                    caixa_pdv_valor,
                    agencia,
                    numero_conta,
                    saldo
                )
                mensagem = f"Conta corrente cadastrada com sucesso!"
            
            # Mensagem de sucesso
            self.mostrar_sucesso(mensagem)
            
            # Atualizar a tabela na tela principal
            if self.parent and hasattr(self.parent, 'carregar_dados_db'):
                self.parent.carregar_dados_db()
            
            # Fechar a janela
            self.accept()
            
        except Exception as e:
            # Em caso de erro com o banco de dados
            self.mostrar_erro(f"Erro ao salvar conta corrente: {str(e)}")
    
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
    
    def mostrar_sucesso(self, mensagem):
        """Exibe uma mensagem de sucesso"""
        msg_box = QMessageBox(
            QMessageBox.Information,
            "Sucesso",
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

# Para testar o formulário individualmente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = FormularioContaCorrente()
    dialog.show()
    sys.exit(app.exec_())