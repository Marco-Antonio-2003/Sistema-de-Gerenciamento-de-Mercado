import sys
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QDateEdit, QMessageBox, 
                           QSizePolicy, QCheckBox, QGroupBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QDate

# Importar funções do banco
from base.banco import (criar_recebimento, get_connection, verificar_tabela_recebimentos_clientes, 
                       listar_recebimentos_pendentes, buscar_recebimento_por_id, 
                       dar_baixa_recebimento, buscar_recebimento_por_codigo, verificar_e_corrigir_tabela_recebimentos   )
from decimal import Decimal

JANELA_LARGURA = 600
JANELA_ALTURA = 600

# Formulário de recebimento
class FormularioRecebimentoClientes(QWidget):
    def __init__(self, janela_parent=None, modo_baixa=False, dados_baixa=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.modo_baixa = modo_baixa
        self.dados_baixa = dados_baixa
        self.callback_atualizacao = None  # Adicionar esta linha
        
        # Verificar se a tabela existe
        self.verificar_tabela()
        
        self.initUI()
        
    def verificar_tabela(self):
        """Verifica se a tabela existe e cria se necessário"""
        try:
            verificar_tabela_recebimentos_clientes()
        except Exception as e:
            print(f"Erro ao verificar tabela: {e}")
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
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
        
        # Título diferente dependendo do modo
        titulo_texto = "Baixa de Recebimento" if self.modo_baixa else "Recebimento de Clientes"
        titulo = QLabel(titulo_texto)
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
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
        
        # Layout para informações principais
        info_group = QGroupBox("Informações do Recebimento")
        info_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #4a90e2;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        info_layout = QVBoxLayout()
        
        # Layout para Código e Cliente
        dados_layout = QHBoxLayout()
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 16px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        self.codigo_input.setFixedWidth(200)
        codigo_layout.addWidget(self.codigo_input)
        
        dados_layout.addLayout(codigo_layout)
        
        # Espaçamento
        dados_layout.addSpacing(30)
        
        # Campo Cliente
        cliente_layout = QHBoxLayout()
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        cliente_layout.addWidget(cliente_label)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setStyleSheet(lineedit_style)
        cliente_layout.addWidget(self.cliente_input, 1)  # 1 para expandir
        
        dados_layout.addLayout(cliente_layout, 1)  # 1 para expandir
        
        info_layout.addLayout(dados_layout)
        
        # Layout para parcelas e valor
        valores_layout = QHBoxLayout()
        
        # Campo Parcelas
        parcelas_layout = QHBoxLayout()
        parcelas_label = QLabel("Parcela:")
        parcelas_label.setStyleSheet("color: white; font-size: 16px;")
        parcelas_layout.addWidget(parcelas_label)
        
        self.parcelas_input = QLineEdit()
        self.parcelas_input.setStyleSheet(lineedit_style)
        self.parcelas_input.setFixedWidth(100)
        self.parcelas_input.setReadOnly(True)  # Apenas informativo
        parcelas_layout.addWidget(self.parcelas_input)
        
        valores_layout.addLayout(parcelas_layout)
        
        # Espaçamento
        valores_layout.addSpacing(30)
        
        # Campo Valor Total
        valor_total_layout = QHBoxLayout()
        valor_total_label = QLabel("Valor Total:")
        valor_total_label.setStyleSheet("color: white; font-size: 16px;")
        valor_total_layout.addWidget(valor_total_label)
        
        self.valor_total_input = QLineEdit()
        self.valor_total_input.setStyleSheet(lineedit_style)
        self.valor_total_input.setFixedWidth(200)
        self.valor_total_input.setReadOnly(True)  # Apenas informativo
        valor_total_layout.addWidget(self.valor_total_input)
        
        valores_layout.addLayout(valor_total_layout)
        
        # Espaçamento
        valores_layout.addStretch(1)
        
        info_layout.addLayout(valores_layout)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Grupo para baixa
        baixa_group = QGroupBox("Informações da Baixa")
        baixa_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #4a90e2;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        baixa_layout = QVBoxLayout()  # Mudado para VBoxLayout para acomodar o texto explicativo
        
        # Layout horizontal para campos
        campos_baixa_layout = QHBoxLayout()
        
        # Campo para Valor a Pagar
        valor_baixa_layout = QHBoxLayout()
        valor_baixa_label = QLabel("Valor a Pagar:")
        valor_baixa_label.setStyleSheet("color: white; font-size: 16px;")
        valor_baixa_layout.addWidget(valor_baixa_label)
        
        self.valor_baixa_input = QLineEdit()
        self.valor_baixa_input.setStyleSheet(lineedit_style)
        self.valor_baixa_input.setFixedWidth(200)
        valor_baixa_layout.addWidget(self.valor_baixa_input)
        
        campos_baixa_layout.addLayout(valor_baixa_layout)
        
        # Espaçamento
        campos_baixa_layout.addSpacing(30)
        
        # Opção para pagamento parcial
        pagamento_parcial_layout = QHBoxLayout()
        pagamento_parcial_label = QLabel("Pagamento Parcial:")
        pagamento_parcial_label.setStyleSheet("color: white; font-size: 16px;")
        pagamento_parcial_layout.addWidget(pagamento_parcial_label)
        
        self.pagamento_parcial_check = QCheckBox()
        self.pagamento_parcial_check.setStyleSheet("QCheckBox { color: white; }")
        pagamento_parcial_layout.addWidget(self.pagamento_parcial_check)
        
        campos_baixa_layout.addLayout(pagamento_parcial_layout)
        campos_baixa_layout.addStretch(1)
        
        baixa_layout.addLayout(campos_baixa_layout)
        
        # Texto explicativo sobre pagamento parcial
        explicacao_label = QLabel(
            "O pagamento parcial permite registrar um pagamento incompleto. "
            "O sistema criará automaticamente um novo recebimento com o valor restante."
        )
        explicacao_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 12px;
                font-weight: normal;
                margin-top: 5px;
                margin-left: 5px;
            }
        """)
        explicacao_label.setWordWrap(True)
        baixa_layout.addWidget(explicacao_label)
        
        baixa_group.setLayout(baixa_layout)
        main_layout.addWidget(baixa_group)
        
        # Espaçamento
        baixa_layout.addStretch(1)
        
        baixa_group.setLayout(baixa_layout)
        main_layout.addWidget(baixa_group)
        
        # Tabela de títulos pendentes
        if not self.modo_baixa:
            self.tabela = QTableWidget()
            self.tabela.setColumnCount(5)
            self.tabela.setHorizontalHeaderLabels(["ID", "Código", "Cliente", "Vencimento", "Valor"])
            self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            self.tabela.verticalHeader().setVisible(False)
            self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tabela.setStyleSheet("""
                QTableWidget {
                    background-color: #fffff0;
                    gridline-color: #cccccc;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
                QTableWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #eeeeee;
                }
                QTableWidget::item:selected {
                    background-color: #0078d7;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    padding: 5px;
                    border: 1px solid #cccccc;
                    font-weight: bold;
                }
            """)
            
            # Esconder a coluna ID (mas mantê-la para referência interna)
            self.tabela.setColumnHidden(0, True)
            
            main_layout.addWidget(self.tabela)
            
            # Conectar evento de seleção de linha na tabela
            self.tabela.itemClicked.connect(self.selecionar_item)
        else:
            # No modo de baixa, adicionar um espaço vazio no lugar da tabela
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            main_layout.addWidget(spacer)
        
        # Layout do rodapé com botão Salvar
        rodape_layout = QHBoxLayout()
        
        # Espaçamento
        rodape_layout.addStretch()
        
        # Botão Salvar
        btn_salvar_texto = "Registrar Baixa" if self.modo_baixa else "Salvar"
        btn_salvar = QPushButton(btn_salvar_texto)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #00E676;
                color: black;
                border: none;
                padding: 15px 20px;
                font-size: 16px;
                border-radius: 4px;
                text-align: center;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #00C853;
            }
        """)
        btn_salvar.clicked.connect(self.salvar)
        rodape_layout.addWidget(btn_salvar)
        
        main_layout.addLayout(rodape_layout)
        
        # Inicializar dados
        if not self.modo_baixa:
            # Carregar dados do banco de dados para o modo normal
            self.carregar_recebimentos_pendentes()
        elif self.dados_baixa:
            # Preencher campos com os dados fornecidos para o modo de baixa
            self.preencher_dados_baixa()
    
    def preencher_dados_baixa(self):
        """Preenche os campos com os dados passados para baixa"""
        try:
            if self.dados_baixa:
                # Preencher código e cliente
                codigo = self.dados_baixa.get('codigo', '')
                self.codigo_input.setText(codigo)
                self.cliente_input.setText(self.dados_baixa.get('cliente', ''))
                
                # Preencher parcelas
                parcelas = self.dados_baixa.get('parcelas', '')
                self.parcelas_input.setText(parcelas)
                
                # Preencher valor total
                valor = self.dados_baixa.get('valor', '')
                self.valor_total_input.setText(valor)
                
                # Preencher valor de baixa (remover R$ se presente)
                valor_baixa = valor
                if valor_baixa and valor_baixa.startswith('R$ '):
                    valor_baixa = valor_baixa[3:]
                self.valor_baixa_input.setText(valor_baixa)
                
                # Desabilitar edição dos campos informativos
                self.codigo_input.setEnabled(False)
                self.cliente_input.setEnabled(False)
                self.valor_total_input.setEnabled(False)
                self.parcelas_input.setEnabled(False)
        except Exception as e:
            print(f"Erro ao preencher dados de baixa: {e}")
    
    def carregar_recebimentos_pendentes(self):
        """Carrega os recebimentos pendentes do banco de dados"""
        try:
            # Buscar os recebimentos pendentes
            recebimentos = listar_recebimentos_pendentes()
            
            # Limpar a tabela
            self.tabela.setRowCount(0)
            
            # Se não houver recebimentos, não fazer nada
            if not recebimentos:
                return
                
            # Adicionar os recebimentos à tabela
            self.tabela.setRowCount(len(recebimentos))
            for row, recebimento in enumerate(recebimentos):
                id_recebimento = recebimento[0]
                codigo = recebimento[1]
                cliente = recebimento[2]
                vencimento = recebimento[4]  # VENCIMENTO é a 5ª coluna (índice 4)
                valor = recebimento[5]  # VALOR é a 6ª coluna (índice 5)
                
                # Formatação da data
                vencimento_formatado = ""
                if vencimento:
                    vencimento_formatado = vencimento.strftime("%d/%m/%Y")
                
                # Formatação do valor
                valor_formatado = f"R$ {valor:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")
                
                # Inserir na tabela
                self.tabela.setItem(row, 0, QTableWidgetItem(str(id_recebimento)))
                self.tabela.setItem(row, 1, QTableWidgetItem(codigo))
                self.tabela.setItem(row, 2, QTableWidgetItem(cliente))
                self.tabela.setItem(row, 3, QTableWidgetItem(vencimento_formatado))
                self.tabela.setItem(row, 4, QTableWidgetItem(valor_formatado))
                
        except Exception as e:
            print(f"Erro ao carregar recebimentos: {e}")
            # Em caso de falha, carrega dados de exemplo
            self.carregar_dados_exemplo()
    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela (fallback)"""
        dados = [
            ("1", "001", "Empresa ABC Ltda", "01/04/2025", "R$ 5.000,00"),
            ("2", "002", "João Silva", "02/04/2025", "R$ 1.200,00"),
            ("3", "003", "Distribuidora XYZ", "03/04/2025", "R$ 3.500,00"),
            ("4", "004", "Ana Souza", "04/04/2025", "R$ 750,00"),
            ("5", "005", "Mercado Central", "05/04/2025", "R$ 2.100,00")
        ]
        
        self.tabela.setRowCount(len(dados))
        for row, (id_rec, codigo, cliente, vencimento, valor) in enumerate(dados):
            self.tabela.setItem(row, 0, QTableWidgetItem(id_rec))
            self.tabela.setItem(row, 1, QTableWidgetItem(codigo))
            self.tabela.setItem(row, 2, QTableWidgetItem(cliente))
            self.tabela.setItem(row, 3, QTableWidgetItem(vencimento))
            self.tabela.setItem(row, 4, QTableWidgetItem(valor))
    
    def selecionar_item(self, item):
        """Quando um item da tabela é selecionado, preenche os campos"""
        row = item.row()
        
        # Preencher os campos com os dados da linha selecionada
        self.codigo_input.setText(self.tabela.item(row, 1).text())
        self.cliente_input.setText(self.tabela.item(row, 2).text())
        self.valor_total_input.setText(self.tabela.item(row, 4).text())
        self.valor_baixa_input.setText(self.tabela.item(row, 4).text().replace("R$ ", ""))
        
        # Extrair informações de parcelas do código
        codigo = self.tabela.item(row, 1).text()
        parcelas = "1/1"  # Valor padrão
        
        try:
            # Buscar o recebimento no banco para verificar parcelas
            recebimento = buscar_recebimento_por_codigo(codigo)
            if recebimento:
                codigo_completo = recebimento[1]  # Código completo do banco
                
                # Extrair informações de parcelas se estiverem no formato código-X/Y
                if "-" in codigo_completo and "/" in codigo_completo:
                    partes = codigo_completo.split("-")
                    parcelas = partes[-1]  # Parte que contém X/Y
        except Exception as e:
            print(f"Erro ao extrair informações de parcelas: {e}")
            
        self.parcelas_input.setText(parcelas)
    
    def voltar(self):
        """Ação do botão voltar"""
        # Se a janela foi criada a partir de outra janela (tem um parent)
        if self.janela_parent:
            # Verifica se o parent é um QMainWindow
            if isinstance(self.janela_parent, QMainWindow):
                self.janela_parent.close()
            # Se o parent for um widget dentro de uma aplicação
            else:
                # Verifica se há uma janela principal ativa
                main_window = QApplication.activeWindow()
                if main_window:
                    main_window.close()
                    
        # Se estiver sendo executado como aplicação principal (sem parent)
        else:
            # Encerra a aplicação
            QApplication.instance().quit()
    
    def salvar(self):
        """Ação do botão salvar/registrar baixa"""
        # Verificar se todos os campos obrigatórios foram preenchidos
        if not self.codigo_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o código!")
            return
        
        if not self.cliente_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o cliente!")
            return
        
        if not self.valor_baixa_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o valor a pagar!")
            return
        
        # Obter os valores dos campos
        codigo = self.codigo_input.text()
        cliente = self.cliente_input.text()
        
        # Verificar o modo de operação
        if self.modo_baixa:
            # Modo de baixa - usar os dados fornecidos
            self.processar_baixa()
        else:
            # Modo normal - verificar se um item foi selecionado na tabela
            if self.tabela.selectedItems():
                self.processar_baixa()
            else:
                self.mostrar_mensagem("Atenção", "Selecione um título na tabela para dar baixa!")
    
    def processar_baixa(self):
        """Processa a baixa do recebimento"""
        try:
            # Obter ID do recebimento
            if self.modo_baixa:
                # Buscar o ID pelo código e cliente
                codigo = self.codigo_input.text()
                cliente = self.cliente_input.text()
                
                # Definir o código completo com parcelas
                # Se já tem "-" no código, usar ele mesmo
                # Se não tem, tentar extrair da informação de parcelas
                if "-" in codigo:
                    codigo_completo = codigo
                else:
                    parcelas_texto = self.parcelas_input.text()
                    if "/" in parcelas_texto:
                        codigo_completo = f"{codigo}-{parcelas_texto}"
                    else:
                        codigo_completo = codigo
                
                # Buscar o recebimento no banco
                from base.banco import execute_query
                
                # Primeiro, tentar buscar pelo código exato
                query = """
                SELECT ID, CODIGO, VALOR, VENCIMENTO, STATUS 
                FROM RECEBIMENTOS_CLIENTES
                WHERE CLIENTE = ? AND CODIGO = ?
                AND STATUS = 'Pendente'
                """
                resultados = execute_query(query, (cliente, codigo_completo))
                
                # Se não encontrou, tentar com o código base
                if not resultados:
                    query = """
                    SELECT ID, CODIGO, VALOR, VENCIMENTO, STATUS 
                    FROM RECEBIMENTOS_CLIENTES
                    WHERE CLIENTE = ? AND CODIGO = ?
                    AND STATUS = 'Pendente'
                    """
                    resultados = execute_query(query, (cliente, codigo))
                
                # Se ainda não encontrou, tentar buscar com LIKE
                if not resultados:
                    query = """
                    SELECT ID, CODIGO, VALOR, VENCIMENTO, STATUS 
                    FROM RECEBIMENTOS_CLIENTES
                    WHERE CLIENTE = ? AND CODIGO LIKE ?
                    AND STATUS = 'Pendente'
                    ORDER BY CODIGO
                    """
                    resultados = execute_query(query, (cliente, f"{codigo}-%"))
                
                if not resultados:
                    self.mostrar_mensagem("Erro", f"Recebimento não encontrado ou já foi baixado!\nCódigo procurado: {codigo_completo}")
                    return
                
                # Pegar o recebimento específico
                id_recebimento = resultados[0][0]
                codigo_completo = resultados[0][1]
                
            else:
                # Obter o ID da linha selecionada na tabela
                row = self.tabela.currentRow()
                id_recebimento = int(self.tabela.item(row, 0).text())
            
            # Obter dados do recebimento
            recebimento = buscar_recebimento_por_id(id_recebimento)
            if not recebimento:
                self.mostrar_mensagem("Erro", "Recebimento não encontrado no banco de dados!")
                return
            
            # Verificar se o recebimento já foi baixado
            status = recebimento[7]  # Posição 7 é o status
            if status == 'Recebido':
                self.mostrar_mensagem("Erro", "Este recebimento já foi baixado!")
                return
            
            codigo_completo = recebimento[1]
            cliente_nome = recebimento[2]
            cliente_id = recebimento[3]
            vencimento = recebimento[4]
            valor_atual = recebimento[5]  # Valor atual
            
            # Garantir que valor_atual é um Decimal
            if not isinstance(valor_atual, Decimal):
                valor_atual = Decimal(str(valor_atual))
            
            # Extrair informações de parcelas
            codigo_base = self.codigo_input.text()     # ex: "001"
            parcelas_texto = self.parcelas_input.text()   # ex: "5/6"
            try:
                parcela_atual, total_parcelas = map(int, parcelas_texto.split("/"))
            except ValueError:
                parcela_atual, total_parcelas = 1, 1
            
            # Converter o valor de baixa para Decimal
            valor_baixa_texto = self.valor_baixa_input.text()
            valor_baixa_texto = valor_baixa_texto.replace("R$ ", "").replace(".", "").replace(",", ".")
            valor_baixa = Decimal(valor_baixa_texto)
            
            # Verificar se o valor da baixa é válido
            if valor_baixa <= 0:
                self.mostrar_mensagem("Atenção", "O valor da baixa deve ser maior que zero!")
                return
            
            # Verificar se é um pagamento parcial
            pagamento_parcial = self.pagamento_parcial_check.isChecked()
            
            # Data atual para o pagamento
            data_atual = datetime.now().date()
            
            # Mostrar mensagem de confirmação
            mensagem = f"Confirma a baixa do título do cliente {cliente_nome}?"
            if pagamento_parcial:
                mensagem += f"\n\nAtenção: Esta é uma baixa parcial."
                mensagem += f"\nValor atual: R$ {valor_atual:.2f}"
                mensagem += f"\nValor a pagar: R$ {valor_baixa:.2f}"
                mensagem += f"\nValor restante: R$ {valor_atual - valor_baixa:.2f}"
            
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowTitle("Confirmação")
            msgBox.setText(mensagem)
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setStyleSheet("""
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
            resposta = msgBox.exec_()
            
            if resposta != QMessageBox.Yes:
                return
            
            # Processar a baixa conforme o caso
            try:
                if pagamento_parcial:
                    # Baixa parcial - usar Decimal para o cálculo
                    valor_restante = valor_atual - valor_baixa
                    
                    print(f"DEBUG: Valor atual: {float(valor_atual)}, Pagamento: {float(valor_baixa)}, Restante: {float(valor_restante)}")
                    
                    if valor_restante <= 0:
                        # Se o valor restante é zero ou negativo, considera quitado
                        dar_baixa_recebimento(id_recebimento, float(valor_baixa), data_atual)
                        self.mostrar_mensagem("Sucesso", "Baixa completa registrada com sucesso!")
                    else:
                        # MODIFICAÇÃO AQUI: Verificar se o código já tem um sufixo de pagamento parcial
                        if "-" in codigo_completo and codigo_completo.endswith("-1"):
                            # Se já é um pagamento parcial (termina com -1), atualizar este registro
                            # em vez de criar um novo
                            
                            # Atualizar o valor do recebimento atual
                            from base.banco import execute_query
                            query_update = """
                            UPDATE RECEBIMENTOS_CLIENTES
                            SET VALOR = ?
                            WHERE ID = ?
                            """
                            execute_query(query_update, (float(valor_restante), id_recebimento))
                            
                            # Dar baixa no valor parcial em um registro separado
                            dar_baixa_recebimento(id_recebimento, float(valor_baixa), data_atual, criar_novo=False)
                            
                            self.mostrar_mensagem("Sucesso", 
                                                f"Baixa parcial registrada! Valor restante de R$ {valor_restante:.2f} " +
                                                f"mantido na parcela {parcela_atual}/{total_parcelas}.")
                        else:
                            # Primeiro pagamento parcial - criar novo recebimento
                            novo_codigo = f"{codigo_base}-{parcela_atual}/{total_parcelas}"
                            
                            # Criar o novo recebimento antes de dar baixa no atual
                            novo_id = criar_recebimento(
                                codigo=novo_codigo,
                                cliente=cliente_nome,
                                cliente_id=cliente_id,
                                vencimento=vencimento,
                                valor=float(valor_restante),  # Valor restante
                                valor_original=float(valor_atual)  # MANTER valor original
                            )
                            # Depois: dar baixa no valor parcial
                            dar_baixa_recebimento(id_recebimento, float(valor_baixa), data_atual)
                            
                            self.mostrar_mensagem("Sucesso", 
                                                f"Baixa parcial registrada! Valor restante de R$ {valor_restante:.2f} " +
                                                f"mantido na parcela {parcela_atual}/{total_parcelas}.")
                else:
                    # Baixa completa
                    dar_baixa_recebimento(id_recebimento, float(valor_baixa), data_atual)
                    
                    # Buscar quantas parcelas ainda restam
                    from base.banco import execute_query
                    query = """
                    SELECT COUNT(*) 
                    FROM RECEBIMENTOS_CLIENTES
                    WHERE CLIENTE = ? AND CODIGO LIKE ? AND STATUS = 'Pendente'
                    AND ID != ?
                    """
                    resultado = execute_query(query, (cliente_nome, f"{codigo_base}-%", id_recebimento))
                    parcelas_restantes = resultado[0][0] if resultado else 0
                    
                    if parcelas_restantes > 0:
                        parcelas_restantes_total = total_parcelas - parcela_atual
                        self.mostrar_mensagem("Sucesso", 
                                            f"Parcela {parcela_atual}/{total_parcelas} quitada com sucesso! " +
                                            f"Restam {parcelas_restantes_total} parcelas.")
                    else:
                        self.mostrar_mensagem("Sucesso", "Todas as parcelas foram quitadas com sucesso!")
                
                # Chamar o callback de atualização se existir
                if hasattr(self, 'callback_atualizacao') and self.callback_atualizacao:
                    self.callback_atualizacao()
                
                # IMPORTANTE: Forçar a atualização da tabela principal
                if hasattr(self, 'janela_parent') and hasattr(self.janela_parent, 'carregar_recebimentos'):
                    self.janela_parent.carregar_recebimentos()
                
                # Fechar formulário após a baixa
                if self.janela_parent:
                    self.janela_parent.close()
                    
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Erro ao processar baixa: {str(e)}")
                # Log detalhado para depuração
                print(f"ERRO DETALHADO: {e}")
                return  # Sair imediatamente após o erro
                
        except ValueError:
            self.mostrar_mensagem("Erro", "Valor inválido! Use apenas números, pontos e vírgulas.")
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao processar baixa: {str(e)}")


    def gerar_codigo_recebimento_unico():
        """
        Gera um código único para novo recebimento baseado em timestamp e sequência
        """
        try:
            conn = None
            cursor = None
            try:
                # Obter conexão
                conn = get_connection()
                cursor = conn.cursor()
                
                # Obter timestamp atual + sequência
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                
                # Obter uma sequência para o dia atual
                cursor.execute("""
                SELECT COUNT(*) + 1 FROM RECEBIMENTOS_CLIENTES 
                WHERE CAST(ID AS VARCHAR(20)) LIKE ?
                """, (f"{timestamp[:8]}%",))
                
                sequencia = cursor.fetchone()[0]
                
                # Formar o código único: AAAAMMDD-XXX onde XXX é sequência do dia
                codigo_unico = f"{timestamp[:8]}-{sequencia:03d}"
                
                return codigo_unico
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        except Exception as e:
            print(f"Erro ao gerar código único: {e}")
            # Fallback - usar timestamp completo se ocorrer erro
            return f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Sucesso" in titulo:
            msg_box.setIcon(QMessageBox.Information)
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