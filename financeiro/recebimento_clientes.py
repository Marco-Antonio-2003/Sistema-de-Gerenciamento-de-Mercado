#recebimento_clientes.py
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
from financeiro.ver_baixados import VerBaixadosWindow
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financeiro.formulario_recebimento_clientes import FormularioRecebimentoClientes

# Importar funções do banco
from base.banco import (verificar_tabela_recebimentos_clientes, filtrar_recebimentos,
                       listar_recebimentos_pendentes, excluir_recebimento, listar_clientes, execute_query)

JANELA_LARGURA = 800
JANELA_ALTURA = 600

# Agora definimos a classe principal de recebimento de clientes
class RecebimentoClientesWindow(QWidget):
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
        titulo = QLabel("Recebimento de Clientes")
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
        
        # Data de Entrada
        data_entrada_layout = QHBoxLayout()
        data_entrada_label = QLabel("Data de Entrada")
        data_entrada_label.setStyleSheet("color: white; font-size: 16px;")
        data_entrada_layout.addWidget(data_entrada_label)
        
        self.data_entrada_input = QDateEdit(QDate.currentDate())
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
        data_saida_label = QLabel("Data de Saída")
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
        
        # Botão Filtrar (menor)
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
        
        # Botão Limpar (novo)
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
        
        # Adicionar espaço para alinhar à esquerda
        botoes_filtro_layout.addStretch()
        
        main_layout.addLayout(botoes_filtro_layout)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        
        # Botão Excluir
        btn_excluir = QPushButton("Excluir")
        try:
            # Ícone de lixeira
            btn_excluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except:
            pass
        btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                border: 1px solid #cccccc;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
                border: 1px solid #0078d7;
            }
        """)
        btn_excluir.clicked.connect(self.excluir)
        acoes_layout.addWidget(btn_excluir)
        
        # botao ver baixa 
        btn_ver_baixados = QPushButton("Ver Baixados")
        try:
            # Ícone de verificação
            btn_ver_baixados.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        except:
            pass
        btn_ver_baixados.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_ver_baixados.clicked.connect(self.abrir_tela_baixados)
        acoes_layout.addWidget(btn_ver_baixados)

        # Adicionar um espaçador para empurrar os botões para a esquerda
        acoes_layout.addStretch()

        main_layout.addLayout(acoes_layout)
        # Adicionar um espaçador para empurrar o botão para a esquerda
        acoes_layout.addStretch()
        
        main_layout.addLayout(acoes_layout)
        
        # Adicionar aviso sobre duplo clique
        aviso_label = QLabel("Clique duas vezes para cadastrar a baixa do cliente")
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
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Código", "Cliente", "Data", "Num. parcelas", "Vr. Pago"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
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
        self.tabela.doubleClicked.connect(self.abrir_formulario_baixa)
        
        main_layout.addWidget(self.tabela)
        
        # Carregar recebimentos do banco de dados
        self.carregar_recebimentos()
    
    def abrir_tela_baixados(self):
        """Abre a janela para visualização de recebimentos baixados"""
        try:
            # Criar uma nova janela
            self.janela_baixados = QMainWindow()
            self.janela_baixados.setWindowTitle("Recebimentos Baixados")
            self.janela_baixados.setGeometry(100, 100, 1000, 600)
            self.janela_baixados.setStyleSheet("background-color: #003b57;")
            
            # Instanciar o widget de recebimentos baixados
            baixados_widget = VerBaixadosWindow(janela_parent=self.janela_baixados)
            
            self.janela_baixados.setCentralWidget(baixados_widget)
            
            # Mostrar a janela
            self.janela_baixados.show()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Não foi possível abrir a tela de recebimentos baixados: {str(e)}")

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
        self.data_entrada_input.setDate(QDate.currentDate())
        self.data_saida_input.setDate(QDate.currentDate())
        
        # Recarregar todos os recebimentos
        self.carregar_recebimentos()
    
    def carregar_recebimentos(self):
        """Carrega recebimentos do banco de dados com agrupamento por cliente e código"""
        try:
            # Buscar todos os recebimentos pendentes
            recebimentos = listar_recebimentos_pendentes()
            
            # Limpar tabela
            self.tabela.setRowCount(0)
            
            # Se não houver recebimentos, não fazer nada
            if not recebimentos:
                return
            
            # Dicionário para armazenar os recebimentos por código base
            recebimentos_por_codigo = {}
            
            # Primeiro passo: organizar os recebimentos por código base
            for recebimento in recebimentos:
                id_recebimento = recebimento[0]
                codigo_completo = recebimento[1]
                cliente = recebimento[2]
                vencimento = recebimento[4]
                valor = recebimento[5]  # Este é o valor atual no banco
                
                # Extrair o código base (sem a parte da parcela)
                codigo_base = codigo_completo.split('-')[0] if '-' in codigo_completo else codigo_completo
                
                # Chave para agrupar: código base + cliente
                chave = (codigo_base, cliente)
                
                # Adicionar ao dicionário
                if chave not in recebimentos_por_codigo:
                    recebimentos_por_codigo[chave] = []
                
                recebimentos_por_codigo[chave].append(recebimento)
            
            # Segundo passo: para cada grupo, encontrar a parcela mais baixa
            row = 0
            for chave, lista_recebimentos in recebimentos_por_codigo.items():
                # Ordenar por número de parcela (crescente)
                lista_ordenada = sorted(lista_recebimentos, key=self.extrair_numero_parcela)
                
                # Pegar o primeiro recebimento (menor parcela)
                recebimento = lista_ordenada[0]
                
                # Extrair dados
                codigo_completo = recebimento[1]
                cliente = recebimento[2]
                vencimento = recebimento[4]
                valor = recebimento[5]  # Usar o valor do banco
                
                # Extrair informações de parcela
                parcela_atual, total_parcelas = self.extrair_info_parcela(codigo_completo)
                
                # Formatar data
                data_formatada = vencimento.strftime("%d/%m/%y") if vencimento else ""
                
                # Formatar parcelas
                parcelas_formatado = f"{parcela_atual}/{total_parcelas}"
                
                # Formatar valor
                valor_formatado = f"R$ {valor:.2f}".replace('.', ',')
                
                # Adicionar linha na tabela
                self.tabela.insertRow(row)
                self.tabela.setItem(row, 0, QTableWidgetItem(chave[0]))  # Código base
                self.tabela.setItem(row, 1, QTableWidgetItem(cliente))  # Cliente
                self.tabela.setItem(row, 2, QTableWidgetItem(data_formatada))  # Data
                self.tabela.setItem(row, 3, QTableWidgetItem(parcelas_formatado))  # Parcelas
                self.tabela.setItem(row, 4, QTableWidgetItem(valor_formatado))  # Valor
                
                # Aplicar cores alternadas às linhas
                cor_linha = QColor("#f5f5dc") if row % 2 == 0 else QColor("#FFFFFF")
                
                for col in range(5):
                    item = self.tabela.item(row, col)
                    item.setBackground(cor_linha)
                    
                    # Destacar cliente em azul
                    if col == 1:
                        item.setForeground(QColor("#0000FF"))
                    
                    # Destacar valor em vermelho
                    if col == 4:
                        item.setForeground(QColor("#FF0000"))
                
                row += 1
                
        except Exception as e:
            print(f"Erro ao carregar recebimentos: {e}")
            self.carregar_dados_exemplo()
        
    def extrair_numero_parcela(self, recebimento):
        """Extrai o número da parcela do código completo"""
        codigo_completo = recebimento[1]
        
        # Valor padrão
        parcela = 1
        
        # Extrair número da parcela
        if '-' in codigo_completo and '/' in codigo_completo:
            try:
                parte_parcela = codigo_completo.split('-')[1]
                parcela = int(parte_parcela.split('/')[0])
            except (IndexError, ValueError):
                parcela = 1
        
        return parcela

    def extrair_info_parcela(self, codigo_completo):
        """Extrai o número da parcela atual e total de parcelas"""
        parcela_atual = 1
        total_parcelas = 1
        
        if '-' in codigo_completo and '/' in codigo_completo:
            try:
                parte_parcela = codigo_completo.split('-')[1]
                partes = parte_parcela.split('/')
                parcela_atual = int(partes[0])
                total_parcelas = int(partes[1])
            except (IndexError, ValueError):
                pass
        
        return parcela_atual, total_parcelas



    
    def filtrar_recebimentos(self):
        """Filtra recebimentos com base nos critérios de busca"""
        try:
            # Obter valores dos filtros
            codigo = self.codigo_input.text().strip()
            cliente = self.cliente_input.currentText() if self.cliente_input.currentIndex() > 0 else ""
            
            # Converter as datas do formato QDate para date do Python
            data_inicio = self.data_entrada_input.date().toPyDate() if self.data_entrada_input.date() else None
            data_fim = self.data_saida_input.date().toPyDate() if self.data_saida_input.date() else None
            
            # Se nenhum filtro foi informado, carrega todos os recebimentos
            if not codigo and not cliente and not data_inicio and not data_fim:
                self.carregar_recebimentos()
                return
            
            # Buscar recebimentos com os filtros
            recebimentos = filtrar_recebimentos(
                codigo=codigo, 
                cliente=cliente, 
                data_inicio=data_inicio, 
                data_fim=data_fim,
                status="Pendente"
            )
            
            # Limpar tabela
            self.tabela.setRowCount(0)
            
            # Se não houver resultados
            if not recebimentos:
                self.mostrar_mensagem("Informação", "Nenhum recebimento encontrado com os filtros informados.")
                return
            
            # Dicionário para agrupar por cliente e código
            clientes_codigos = {}
            
            # Processar os dados
            for recebimento in recebimentos:
                id_recebimento = recebimento[0]
                codigo_completo = recebimento[1]
                cliente = recebimento[2]
                vencimento = recebimento[3]
                valor = recebimento[4]
                
                # Extrair o código base e informação de parcelas
                codigo_base = codigo_completo
                parcela_atual = "1"
                total_parcelas = "1"
                
                if "-" in codigo_completo and "/" in codigo_completo:
                    partes = codigo_completo.split("-")
                    codigo_base = partes[0].strip()  # Número base do código
                    info_parcelas = partes[1].strip()  # Informação de parcelas (X/Y)
                    
                    # Extrair o número da parcela atual e total de parcelas
                    if "/" in info_parcelas:
                        numeros = info_parcelas.split("/")
                        parcela_atual = numeros[0]
                        total_parcelas = numeros[1]
                
                # Chave para agrupar cliente e código
                chave = (cliente, codigo_base)
                
                # Formatar data de vencimento
                vencimento_formatado = ""
                if vencimento:
                    vencimento_formatado = vencimento.strftime("%d/%m/%y")
                
                # Adicionar ao dicionário
                if chave not in clientes_codigos:
                    clientes_codigos[chave] = {
                        'cliente': cliente,
                        'codigo': codigo_base,
                        'data': vencimento_formatado,  # Usamos a data da primeira parcela
                        'valor': valor,  # Usamos o valor da primeira parcela
                        'total_parcelas': total_parcelas,
                        'parcelas_atuais': [parcela_atual]  # Lista com as parcelas atuais
                    }
                else:
                    # Adicionar parcela à lista de parcelas
                    clientes_codigos[chave]['parcelas_atuais'].append(parcela_atual)
            
            # Preencher a tabela agrupada
            row = 0
            for chave, dados in clientes_codigos.items():
                # Adicionar nova linha
                self.tabela.insertRow(row)
                
                # Calcular número de parcelas no formato "X/Y"
                # MODIFICADO: Usar min em vez de max para pegar a primeira parcela (1/6) em vez da última (6/6)
                parcela_atual = min(map(int, dados['parcelas_atuais']))
                parcelas_formatado = f"{parcela_atual}/{dados['total_parcelas']}"
                
                # Formatar valor com R$ e duas casas decimais
                valor_formatado = f"R$ {dados['valor']:.2f}".replace('.', ',')
                
                # Inserir dados
                self.tabela.setItem(row, 0, QTableWidgetItem(dados['codigo']))  # Código
                self.tabela.setItem(row, 1, QTableWidgetItem(dados['cliente']))  # Cliente
                self.tabela.setItem(row, 2, QTableWidgetItem(dados['data']))  # Data
                self.tabela.setItem(row, 3, QTableWidgetItem(parcelas_formatado))  # Parcelas
                self.tabela.setItem(row, 4, QTableWidgetItem(valor_formatado))  # Valor
                
                # Aplicar cores alternadas às linhas
                cor_linha = QColor("#f5f5dc") if row % 2 == 0 else QColor("#FFFFFF")
                
                for col in range(5):
                    item = self.tabela.item(row, col)
                    item.setBackground(cor_linha)
                    
                    # Destacar cliente em azul
                    if col == 1:
                        item.setForeground(QColor("#0000FF"))
                    
                    # Destacar valor em vermelho
                    if col == 4:
                        item.setForeground(QColor("#FF0000"))
                
                row += 1
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao filtrar recebimentos: {str(e)}")

    
    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo na tabela para visualização de teste"""
        # Dados de exemplo que correspondem exatamente às imagens
        dados_imagem1 = [
            ("1", "Cliente 1", "20/05/25", "2/4", "R$ 100,00"),
            ("2", "Cliente 2", "20/05/25", "2/2", "R$ 20,50")
        ]
        
        # Usar os dados da imagem 1 (com R$ e formatação decimal)
        dados = dados_imagem1
        
        self.tabela.setRowCount(len(dados))
        for row, (codigo, cliente, data, parcelas, valor) in enumerate(dados):
            self.tabela.setItem(row, 0, QTableWidgetItem(codigo))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente))
            self.tabela.setItem(row, 2, QTableWidgetItem(data))
            self.tabela.setItem(row, 3, QTableWidgetItem(parcelas))
            self.tabela.setItem(row, 4, QTableWidgetItem(valor))
            
            # Aplicar cores alternadas às linhas
            cor_linha = QColor("#f5f5dc") if row % 2 == 0 else QColor("#FFFFFF")
            
            for col in range(5):
                item = self.tabela.item(row, col)
                item.setBackground(cor_linha)
                
                # Destacar cliente em azul
                if col == 1:
                    item.setForeground(QColor("#0000FF"))
                
                # Destacar valor em vermelho
                if col == 4:
                    item.setForeground(QColor("#FF0000"))
    
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
    
    def excluir(self):
        """Ação do botão excluir"""
        selected_items = self.tabela.selectedItems()
        if not selected_items:
            self.mostrar_mensagem("Atenção", "Selecione um recebimento para excluir!")
            return
        
        # Obter a linha selecionada
        row = self.tabela.currentRow()
        codigo = self.tabela.item(row, 0).text()
        cliente = self.tabela.item(row, 1).text()
        
        # Mostrar mensagem de confirmação
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle("Confirmação")
        msgBox.setText(f"Deseja realmente excluir o recebimento do cliente {cliente}?")
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
        
        if resposta == QMessageBox.Yes:
            try:
                # Importar funções necessárias
                from base.banco import execute_query, excluir_recebimento
                
                # Mostrar debug para identificar o problema
                print(f"Tentando excluir: Código={codigo}, Cliente={cliente}")
                
                # Buscar IDs de todos os possíveis recebimentos relacionados
                query = """
                SELECT ID FROM RECEBIMENTOS_CLIENTES
                WHERE (CODIGO = ? OR CODIGO LIKE ? OR CODIGO LIKE ?)
                """
                
                # Parâmetros para busca ampla
                codigo_base = codigo.split('-')[0] if '-' in codigo else codigo
                params = (codigo, f"{codigo_base}-%", f"{codigo}-%")
                
                print(f"Buscando com: código exato={codigo}, base1={f'{codigo_base}-%'}, base2={f'{codigo}-%'}")
                
                # Executar a busca
                resultado = execute_query(query, params)
                
                if resultado and len(resultado) > 0:
                    print(f"Encontrados {len(resultado)} registros para excluir")
                    
                    # Para cada ID encontrado, excluir o registro
                    for reg in resultado:
                        id_recebimento = reg[0]
                        print(f"Excluindo recebimento ID: {id_recebimento}")
                        excluir_recebimento(id_recebimento)
                    
                    # Remover da tabela visual
                    self.tabela.removeRow(row)
                    self.mostrar_mensagem("Sucesso", "Recebimento excluído com sucesso!")
                    
                    # Recarregar a tabela para garantir sincronização
                    print("Recarregando tabela...")
                    self.carregar_recebimentos()
                else:
                    # Se não encontrou pelo método acima, tenta uma busca mais agressiva
                    print("Tentando busca alternativa por cliente...")
                    query = """
                    SELECT ID FROM RECEBIMENTOS_CLIENTES
                    WHERE CLIENTE = ? AND (CODIGO LIKE ? OR CODIGO = ?)
                    """
                    
                    params = (cliente, f"%{codigo_base}%", codigo)
                    resultado = execute_query(query, params)
                    
                    if resultado and len(resultado) > 0:
                        print(f"Busca alternativa encontrou {len(resultado)} registros")
                        for reg in resultado:
                            id_recebimento = reg[0]
                            print(f"Excluindo recebimento ID: {id_recebimento}")
                            excluir_recebimento(id_recebimento)
                        
                        self.tabela.removeRow(row)
                        self.mostrar_mensagem("Sucesso", "Recebimento excluído com sucesso!")
                        self.carregar_recebimentos()
                    else:
                        self.mostrar_mensagem("Erro", f"Não foi possível encontrar o recebimento com código {codigo}")
                        print(f"Nenhum registro encontrado para código={codigo}, cliente={cliente}")
                    
            except Exception as e:
                self.mostrar_mensagem("Erro", f"Erro ao excluir recebimento: {str(e)}")
                print(f"Exceção durante exclusão: {str(e)}")
    
    def abrir_formulario_baixa(self):
        """Abrir formulário para baixa quando houver duplo clique na tabela"""
        print("Abrindo formulário para baixa de recebimento")
        
        # Obter a linha selecionada
        row = self.tabela.currentRow()
        if row < 0:
            return
            
        # Obter dados da linha selecionada
        codigo = self.tabela.item(row, 0).text()
        cliente = self.tabela.item(row, 1).text()
        data = self.tabela.item(row, 2).text()
        parcelas = self.tabela.item(row, 3).text()
        valor = self.tabela.item(row, 4).text()
        
        try:
            # Criar uma nova janela
            self.janela_formulario = QMainWindow()
            self.janela_formulario.setWindowTitle(f"Baixa de Recebimento - {cliente}")
            self.janela_formulario.setGeometry(100, 100, 1000, 600)
            self.janela_formulario.setStyleSheet("background-color: #003b57;")
            
            # Instanciar o formulário de recebimento de clientes
            formulario_widget = FormularioRecebimentoClientes(
                janela_parent=self.janela_formulario,
                modo_baixa=True,
                dados_baixa={
                    'codigo': codigo,
                    'cliente': cliente,
                    'data': data,
                    'parcelas': parcelas,
                    'valor': valor
                }
            )
            
            # Conectar um callback para atualizar a tabela quando o formulário for fechado
            formulario_widget.callback_atualizacao = self.carregar_recebimentos
            
            self.janela_formulario.setCentralWidget(formulario_widget)
            
            # Mostrar a janela
            self.janela_formulario.show()
            
            # Conectar sinal de fechamento da janela para atualizar a tabela
            self.janela_formulario.destroyed.connect(self.carregar_recebimentos)
            
            # Adicionar também um sinal de fechamento alternativo
            def on_close():
                self.carregar_recebimentos()
                self.janela_formulario.deleteLater()
            
            self.janela_formulario.closeEvent = lambda event: on_close()
            
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Não foi possível abrir o formulário: {str(e)}")
    
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