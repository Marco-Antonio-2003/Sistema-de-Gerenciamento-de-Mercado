#ver_baixados.py
import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView, QFrame, QStyle, QDateEdit, QMessageBox, 
                           QSizePolicy, QComboBox)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QDate
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funções do banco
from base.banco import (verificar_tabela_recebimentos_clientes, filtrar_recebimentos,
                       listar_recebimentos_baixados, listar_clientes, execute_query)

JANELA_LARGURA = 800
JANELA_ALTURA = 600

# Classe principal para visualização de recebimentos baixados
class VerBaixadosWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        
        # Verificar se a tabela existe
        self.verificar_tabela()
        
        self.initUI()
        self.setMinimumSize(JANELA_LARGURA, JANELA_ALTURA)
    
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
        
        # Título
        titulo = QLabel("Recebimentos Baixados")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar
        spacer = QWidget()
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
        
        # Estilo para QDateEdit
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
            QDateEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Estilo para ComboBox
        combobox_style = """
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                min-height: 25px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: url(ico-img/down-arrow.png);
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #003b57;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
        """
        
        # Layout principal para os campos de entrada
        campos_layout = QHBoxLayout()
        
        # Layout esquerdo para código e cliente
        left_layout = QVBoxLayout()
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 16px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        codigo_layout.addWidget(self.codigo_input)
        
        left_layout.addLayout(codigo_layout)
        
        # Campo Cliente (substituído por ComboBox)
        cliente_layout = QHBoxLayout()
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        cliente_layout.addWidget(cliente_label)
        
        # Novo ComboBox para clientes
        self.cliente_input = QComboBox()
        self.cliente_input.setStyleSheet(combobox_style)
        self.cliente_input.setEditable(True)  # Permite digitação para busca rápida
        self.cliente_input.setMaxVisibleItems(10)
        self.carregar_clientes()  # Carrega a lista de clientes
        cliente_layout.addWidget(self.cliente_input, 1)
        
        left_layout.addLayout(cliente_layout)
        
        campos_layout.addLayout(left_layout)
        
        # Layout direito para datas
        right_layout = QVBoxLayout()
        
        # Data de Entrada (para filtrar por data de pagamento)
        data_entrada_layout = QHBoxLayout()
        data_entrada_label = QLabel("Data Inicial:")
        data_entrada_label.setStyleSheet("color: white; font-size: 16px;")
        data_entrada_layout.addWidget(data_entrada_label)
        
        self.data_entrada_input = QDateEdit(QDate.currentDate().addMonths(-6))  # Padrão: 6 meses atrás
        self.data_entrada_input.setCalendarPopup(True)
        self.data_entrada_input.setStyleSheet(dateedit_style)
        
        # Adicionar ícone de calendário
        try:
            calendar_icon = QIcon("ico-img/calendar-outline.svg")
            self.data_entrada_input.setCalendarPopupEnabled(True)
            self.data_entrada_input.calendarWidget().setWindowIcon(calendar_icon)
        except Exception as e:
            print(f"Erro ao carregar ícone de calendário: {e}")
        
        data_entrada_layout.addWidget(self.data_entrada_input)
        
        right_layout.addLayout(data_entrada_layout)
        
        # Data de Saída
        data_saida_layout = QHBoxLayout()
        data_saida_label = QLabel("Data Final:")
        data_saida_label.setStyleSheet("color: white; font-size: 16px;")
        data_saida_layout.addWidget(data_saida_label)
        
        self.data_saida_input = QDateEdit(QDate.currentDate())
        self.data_saida_input.setCalendarPopup(True)
        self.data_saida_input.setStyleSheet(dateedit_style)
        
        # Adicionar ícone de calendário
        try:
            self.data_saida_input.setCalendarPopupEnabled(True)
            self.data_saida_input.calendarWidget().setWindowIcon(calendar_icon)
        except Exception as e:
            print(f"Erro ao carregar ícone de calendário: {e}")
        
        data_saida_layout.addWidget(self.data_saida_input)
        
        right_layout.addLayout(data_saida_layout)
        
        campos_layout.addLayout(right_layout)
        
        main_layout.addLayout(campos_layout)
        
        # Layout para botões Filtrar e Limpar
        botoes_filtro_layout = QHBoxLayout()
        
        # Botão Filtrar
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 13px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #3a80d2;
            }
        """)
        btn_filtrar.clicked.connect(self.filtrar_recebimentos)
        botoes_filtro_layout.addWidget(btn_filtrar)
        
        # Botão Limpar
        btn_limpar = QPushButton("Limpar")
        btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #cccccc;
                padding: 8px 15px;
                font-size: 13px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #0078d7;
            }
        """)
        btn_limpar.clicked.connect(self.limpar_filtros)
        botoes_filtro_layout.addWidget(btn_limpar)
        
        # Botão Voltar (para fechar a tela)
        btn_voltar = QPushButton("Voltar")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 13px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_voltar.clicked.connect(self.voltar)
        botoes_filtro_layout.addWidget(btn_voltar)
        
        # Adicionar espaço para alinhar à esquerda
        botoes_filtro_layout.addStretch()
        
        main_layout.addLayout(botoes_filtro_layout)
        
        # Adicionar aviso sobre duplo clique
        aviso_label = QLabel("Clique duas vezes para ver detalhes do pagamento")
        aviso_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-style: italic;
                margin-top: 10px;
                margin-bottom: 5px;
            }
        """)
        aviso_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(aviso_label)
        
        # Tabela de recebimentos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["Código", "Cliente", "Data Venc.", "Data Baixa", "Total", "Status"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #f5f5dc;
                gridline-color: #003b57;
                border: 1px solid #003b57;
                border-radius: 0px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #dddddd;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #003b57;
                color: white;
                padding: 5px;
                border: 1px solid #003b57;
                font-weight: bold;
            }
        """)
        
        # Configurar duplo clique na tabela
        self.tabela.doubleClicked.connect(self.mostrar_detalhes_pagamento)
        
        main_layout.addWidget(self.tabela)
        
        # Carregar recebimentos baixados do banco de dados
        self.carregar_recebimentos_baixados()
    
    def carregar_clientes(self):
        """Carrega a lista de clientes no ComboBox"""
        try:
            # Limpar ComboBox
            self.cliente_input.clear()
            
            # Adicionar item padrão
            self.cliente_input.addItem("Selecione um cliente")
            
            # Carregar clientes do banco de dados
            clientes = listar_clientes()
            
            # Adicionar ao ComboBox
            for id_cliente, nome in clientes:
                self.cliente_input.addItem(nome)
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            # Adicionar alguns clientes de exemplo como fallback
            self.cliente_input.clear()
            self.cliente_input.addItem("Selecione um cliente")
            self.cliente_input.addItem("Cliente Exemplo 1")
            self.cliente_input.addItem("Cliente Exemplo 2")
    
    def limpar_filtros(self):
        """Limpa todos os campos de filtro"""
        self.codigo_input.clear()
        self.cliente_input.setCurrentIndex(0)  # Voltar para "Selecione um cliente"
        self.data_entrada_input.setDate(QDate.currentDate().addMonths(-6))
        self.data_saida_input.setDate(QDate.currentDate())
        
        # Recarregar todos os recebimentos baixados
        self.carregar_recebimentos_baixados()
    
    def carregar_recebimentos_baixados(self):
        """Carrega recebimentos baixados do banco de dados"""
        try:
            print("Iniciando carregamento de recebimentos baixados...")
            
            # Obter os recebimentos baixados
            recebimentos = listar_recebimentos_baixados()
            
            # Limpar tabela
            self.tabela.setRowCount(0)
            
            # Se não houver recebimentos
            if not recebimentos or len(recebimentos) == 0:
                print("Nenhum recebimento baixado encontrado no banco de dados")
                return
            
            print(f"Encontrados {len(recebimentos)} recebimentos baixados")
            
            # Preencher a tabela
            row = 0
            for recebimento in recebimentos:
                # Verificar estrutura do registro para debug
                print(f"Processando recebimento: {recebimento}")
                
                # Extrair dados - garantir que temos acesso seguro aos campos
                if len(recebimento) < 8:
                    print(f"ATENÇÃO: Recebimento com estrutura incompleta: {recebimento}")
                    continue
                    
                id_recebimento = recebimento[0]
                codigo = recebimento[1] if recebimento[1] else ""
                cliente = recebimento[2] if recebimento[2] else ""
                
                # Tratar vencimento - garantir conversão correta
                vencimento_formatado = ""
                try:
                    vencimento = recebimento[4]
                    if vencimento:
                        from datetime import datetime
                        if isinstance(vencimento, str):
                            vencimento = datetime.strptime(vencimento, '%Y-%m-%d').date()
                        vencimento_formatado = vencimento.strftime("%d/%m/%Y")
                except Exception as e:
                    print(f"Erro ao formatar vencimento: {e}")
                    vencimento_formatado = str(recebimento[4]) if recebimento[4] else ""
                
                # Tratar data recebimento - garantir conversão correta
                data_recebimento_formatado = ""
                try:
                    data_recebimento = recebimento[6]
                    if data_recebimento:
                        from datetime import datetime
                        if isinstance(data_recebimento, str):
                            data_recebimento = datetime.strptime(data_recebimento, '%Y-%m-%d').date()
                        data_recebimento_formatado = data_recebimento.strftime("%d/%m/%Y")
                except Exception as e:
                    print(f"Erro ao formatar data recebimento: {e}")
                    data_recebimento_formatado = str(recebimento[6]) if recebimento[6] else ""
                
                # Formatar valor
                try:
                    valor = float(recebimento[5]) if recebimento[5] is not None else 0.0
                    valor_formatado = f"R$ {valor:.2f}".replace('.', ',')
                except:
                    valor_formatado = "R$ 0,00"
                
                # Status
                status = recebimento[7] if recebimento[7] else "Recebido"
                
                # Adicionar linha na tabela
                self.tabela.insertRow(row)
                self.tabela.setItem(row, 0, QTableWidgetItem(codigo))  # Código
                self.tabela.setItem(row, 1, QTableWidgetItem(cliente))  # Cliente
                self.tabela.setItem(row, 2, QTableWidgetItem(vencimento_formatado))  # Data Vencimento
                self.tabela.setItem(row, 3, QTableWidgetItem(data_recebimento_formatado))  # Data Baixa
                self.tabela.setItem(row, 4, QTableWidgetItem(valor_formatado))  # Valor
                self.tabela.setItem(row, 5, QTableWidgetItem(status))  # Status
                
                # Aplicar cores às linhas
                cor_linha = QColor("#f5f5dc") if row % 2 == 0 else QColor("#FFFFFF")
                
                for col in range(6):
                    item = self.tabela.item(row, col)
                    item.setBackground(cor_linha)
                    
                    # Destacar cliente em azul
                    if col == 1:
                        item.setForeground(QColor("#0000FF"))
                    
                    # Destacar valor em verde (pago)
                    if col == 4:
                        item.setForeground(QColor("#008000"))
                    
                    # Destacar status em verde
                    if col == 5:
                        item.setForeground(QColor("#008000"))
                
                row += 1
                
            print(f"Carregados {row} recebimentos na tabela")
        except Exception as e:
            print(f"Erro ao carregar recebimentos baixados: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_mensagem("Erro", f"Erro ao carregar recebimentos: {str(e)}")
    
    def filtrar_recebimentos(self):
        """Filtra recebimentos baixados com base nos critérios de busca"""
        try:
            # Obter valores dos filtros
            codigo = self.codigo_input.text().strip()
            
            # Obter o cliente do ComboBox, apenas se não for o item "Selecione um cliente"
            cliente = ""
            if self.cliente_input.currentIndex() > 0:
                cliente = self.cliente_input.currentText().strip()
            # Se for texto digitado manualmente, usar esse texto
            elif self.cliente_input.currentText() != "Selecione um cliente":
                cliente = self.cliente_input.currentText().strip()
            
            # Converter as datas do formato QDate para date do Python
            data_inicio = self.data_entrada_input.date().toPyDate() if self.data_entrada_input.date() else None
            data_fim = self.data_saida_input.date().toPyDate() if self.data_saida_input.date() else None
            
            print(f"Aplicando filtros: Código='{codigo}', Cliente='{cliente}', Data Início={data_inicio}, Data Fim={data_fim}")
            
            # Se nenhum filtro foi informado, carrega todos os recebimentos baixados
            if not codigo and not cliente and not data_inicio and not data_fim:
                self.carregar_recebimentos_baixados()
                return
            
            # DIAGNÓSTICO: Se houver um nome de cliente, executar verificação antes
            if cliente:
                print(f"\n----- EXECUTANDO DIAGNÓSTICO PARA CLIENTE '{cliente}' -----")
                try:
                    from base.banco import verificar_registros_cliente
                    verificar_registros_cliente(cliente)
                except Exception as e:
                    print(f"Erro ao executar diagnóstico: {e}")
            
            # Buscar recebimentos com os filtros (status="Recebido")
            # Vamos tentar buscar SEM especificar o status para diagnóstico
            from base.banco import filtrar_recebimentos
            recebimentos = filtrar_recebimentos(
                codigo=codigo, 
                cliente=cliente, 
                data_inicio=data_inicio, 
                data_fim=data_fim
                # Removendo o filtro de status para verificação
                # status="Recebido"
            )
            
            # Limpar tabela
            self.tabela.setRowCount(0)
            
            # Se não houver resultados
            if not recebimentos or len(recebimentos) == 0:
                # DIAGNÓSTICO: verificar a tabela para este cliente
                if cliente:
                    try:
                        from base.banco import execute_query
                        query = "SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES WHERE UPPER(CLIENTE) LIKE UPPER(?)"
                        result = execute_query(query, (f"%{cliente}%",))
                        total = result[0][0] if result and len(result) > 0 else 0
                        
                        if total > 0:
                            self.mostrar_mensagem("Informação", 
                                f"Foram encontrados {total} registros para o cliente '{cliente}', "
                                f"mas nenhum com status 'Recebido'. Verifique o status dos registros.")
                        else:
                            self.mostrar_mensagem("Informação", 
                                f"Nenhum registro encontrado para o cliente '{cliente}'. "
                                f"Verifique se o nome está correto.")
                    except Exception as e:
                        print(f"Erro no diagnóstico: {e}")
                        self.mostrar_mensagem("Informação", "Nenhum recebimento baixado encontrado com os filtros informados.")
                else:
                    self.mostrar_mensagem("Informação", "Nenhum recebimento baixado encontrado com os filtros informados.")
                return
            
            print(f"Encontrados {len(recebimentos)} registros - filtrando apenas status 'Recebido'")
            
            # Filtrar apenas os registros com status 'Recebido'
            recebimentos_recebidos = [r for r in recebimentos if r[7] == 'Recebido']
            
            if not recebimentos_recebidos:
                self.mostrar_mensagem("Informação", 
                    f"Foram encontrados {len(recebimentos)} registros, mas nenhum com status 'Recebido'. "
                    f"Verifique o campo STATUS no banco de dados.")
                return
                
            print(f"Registros com status 'Recebido': {len(recebimentos_recebidos)}")
            
            # Preencher a tabela com os resultados filtrados
            row = 0
            for recebimento in recebimentos_recebidos:
                try:
                    # Extrair dados
                    id_recebimento = recebimento[0]
                    codigo_completo = recebimento[1] if recebimento[1] else ""
                    cliente_nome = recebimento[2] if recebimento[2] else ""
                    
                    # Formatar datas
                    vencimento_formatado = ""
                    if recebimento[4]:  # Vencimento
                        try:
                            from datetime import datetime
                            vencimento = recebimento[4]
                            if isinstance(vencimento, str):
                                vencimento = datetime.strptime(vencimento, '%Y-%m-%d').date()
                            vencimento_formatado = vencimento.strftime("%d/%m/%Y")
                        except Exception as e:
                            print(f"Erro ao formatar vencimento: {e}")
                            vencimento_formatado = str(recebimento[4])
                    
                    data_recebimento_formatado = ""
                    if recebimento[6]:  # Data recebimento
                        try:
                            from datetime import datetime
                            data_recebimento = recebimento[6]
                            if isinstance(data_recebimento, str):
                                data_recebimento = datetime.strptime(data_recebimento, '%Y-%m-%d').date()
                            data_recebimento_formatado = data_recebimento.strftime("%d/%m/%Y")
                        except Exception as e:
                            print(f"Erro ao formatar data recebimento: {e}")
                            data_recebimento_formatado = str(recebimento[6])
                    
                    # Formatar valor
                    try:
                        valor = float(recebimento[5]) if recebimento[5] is not None else 0.0
                        valor_formatado = f"R$ {valor:.2f}".replace('.', ',')
                    except Exception as e:
                        print(f"Erro ao formatar valor: {e}")
                        valor_formatado = "R$ 0,00"
                    
                    # Status
                    status = recebimento[7] if recebimento[7] else "Recebido"
                    
                    # Adicionar linha na tabela
                    self.tabela.insertRow(row)
                    self.tabela.setItem(row, 0, QTableWidgetItem(str(codigo_completo)))
                    self.tabela.setItem(row, 1, QTableWidgetItem(str(cliente_nome)))
                    self.tabela.setItem(row, 2, QTableWidgetItem(vencimento_formatado))
                    self.tabela.setItem(row, 3, QTableWidgetItem(data_recebimento_formatado))
                    self.tabela.setItem(row, 4, QTableWidgetItem(valor_formatado))
                    self.tabela.setItem(row, 5, QTableWidgetItem(str(status)))
                    
                    # Aplicar cores alternadas às linhas
                    cor_linha = QColor("#f5f5dc") if row % 2 == 0 else QColor("#FFFFFF")
                    
                    for col in range(6):
                        item = self.tabela.item(row, col)
                        item.setBackground(cor_linha)
                        
                        # Destacar cliente em azul
                        if col == 1:
                            item.setForeground(QColor("#0000FF"))
                        
                        # Destacar valor em verde (pago)
                        if col == 4:
                            item.setForeground(QColor("#008000"))
                        
                        # Destacar status em verde
                        if col == 5:
                            item.setForeground(QColor("#008000"))
                    
                    row += 1
                except Exception as e:
                    print(f"Erro ao processar recebimento {recebimento}: {e}")
                    continue
                    
        except Exception as e:
            print(f"ERRO na função filtrar_recebimentos: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_mensagem("Erro", f"Erro ao filtrar recebimentos: {str(e)}")
            
    def voltar(self):
        """Ação do botão voltar"""
        if self.janela_parent:
            self.janela_parent.close()
        else:
            self.close()
    
    def mostrar_detalhes_pagamento(self):
        """Exibe os detalhes completos do pagamento selecionado"""
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            return
        
        # Obter a linha selecionada
        row = self.tabela.currentRow()
        codigo = self.tabela.item(row, 0).text()
        cliente = self.tabela.item(row, 1).text()
        data_venc = self.tabela.item(row, 2).text()
        data_baixa = self.tabela.item(row, 3).text()
        valor = self.tabela.item(row, 4).text()
        status = self.tabela.item(row, 5).text()
        
        # Buscar informações detalhadas no banco de dados
        try:
            # Importar funções necessárias
            from base.banco import buscar_historico_pagamentos
            
            # Vamos supor que exista uma função para buscar o histórico de pagamentos
            historico = buscar_historico_pagamentos(codigo)
            
            # Preparar texto com detalhes
            detalhes = f"<html><body style='font-family: Arial; background-color: white;'>"
            detalhes += f"<h2 style='color: #003b57;'>Detalhes do Pagamento</h2>"
            detalhes += f"<p><b>Código:</b> {codigo}</p>"
            detalhes += f"<p><b>Cliente:</b> {cliente}</p>"
            detalhes += f"<p><b>Data de Vencimento:</b> {data_venc}</p>"
            detalhes += f"<p><b>Data de Baixa:</b> {data_baixa}</p>"
            detalhes += f"<p><b>Valor:</b> {valor}</p>"
            detalhes += f"<p><b>Status:</b> <span style='color: green;'>{status}</span></p>"
            
            # Adicionar histórico de pagamentos, se existir
            if historico and len(historico) > 0:
                detalhes += f"<h3 style='color: #003b57;'>Histórico de Pagamentos</h3>"
                detalhes += "<table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>"
                detalhes += "<tr style='background-color: #003b57; color: white;'><th>Data</th><th>Valor</th><th>Observação</th></tr>"
                
                for item in historico:
                    data_pgto = item[0].strftime("%d/%m/%Y") if item[0] else "-"
                    valor_pgto = f"R$ {item[1]:.2f}".replace('.', ',')
                    obs = item[2] if item[2] else "-"
                    
                    detalhes += f"<tr><td>{data_pgto}</td><td>{valor_pgto}</td><td>{obs}</td></tr>"
                
                detalhes += "</table>"
            else:
                detalhes += "<p><i>Não há histórico detalhado de pagamentos disponível.</i></p>"
            
            detalhes += "</body></html>"
            
            # Exibir mensagem com detalhes
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(f"Detalhes do Pagamento - {cliente}")
            msg_box.setText(detalhes)
            msg_box.setStyleSheet("""
                QMessageBox { 
                    background-color: white;
                    min-width: 500px;
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
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao buscar detalhes do pagamento: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Sucesso" in titulo:
            msg_box.setIcon(QMessageBox.Information)
        elif "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
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
    window.setWindowTitle("Sistema - Recebimentos Baixados")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    baixados_widget = VerBaixadosWindow(window)  # Passa a janela como parent
    window.setCentralWidget(baixados_widget)
    
    window.show()
    sys.exit(app.exec_())