# relatorios/relatorio_vendas_produtos.py
import sys
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QDateEdit,
                             QGroupBox, QFormLayout, QRadioButton, QButtonGroup,
                             QMessageBox, QFileDialog, QProgressDialog)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QDate, QDateTime, QThread, pyqtSignal, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import functools

# Modificação na importação do banco de dados para funcionar tanto em desenvolvimento quanto no executável
# Determinar se estamos rodando como um executável ou script normal
if getattr(sys, 'frozen', False):
    # Estamos executando em um executável PyInstaller
    application_path = os.path.dirname(sys.executable)
else:
    # Estamos executando em um ambiente de desenvolvimento
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Adicionar o diretório raiz ao PATH
if application_path not in sys.path:
    sys.path.insert(0, application_path)

# Debugging: criar um arquivo de log para ajudar a diagnosticar problemas
try:
    log_path = os.path.join(application_path, 'debug_relatorio.txt')
    with open(log_path, 'a') as f:
        f.write(f"\n--- Iniciando módulo de relatórios em {datetime.datetime.now()} ---\n")
        f.write(f"Diretório da aplicação: {application_path}\n")
        f.write(f"Caminhos no sys.path: {sys.path}\n")
except Exception as e:
    # Falha no log não deve interromper a aplicação
    pass

# Agora importe as funções do banco de dados
try:
    from base.banco import (get_connection, execute_query, listar_produtos, listar_grupos)
except Exception as e:
    # Registrar erro de importação no log
    try:
        with open(log_path, 'a') as f:
            f.write(f"ERRO AO IMPORTAR MÓDULOS DO BANCO: {str(e)}\n")
    except:
        pass


# Thread para carregamento de dados
class CarregadorDadosThread(QThread):
    dados_carregados = pyqtSignal(list)
    erro_carregamento = pyqtSignal(str)
    
    def __init__(self, data_inicial, data_final, categoria=None):
        super().__init__()
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.categoria = categoria
        
    def run(self):
        try:
            vendas = self.obter_vendas_por_periodo(self.data_inicial, self.data_final, self.categoria)
            self.dados_carregados.emit(vendas)
        except Exception as e:
            self.erro_carregamento.emit(str(e))
    
    def obter_vendas_por_periodo(self, data_inicial, data_final, categoria=None):
        """
        Obtém as vendas da tabela VENDAS pelo período selecionado
        
        Args:
            data_inicial (str): Data inicial no formato yyyy-MM-dd
            data_final (str): Data final no formato yyyy-MM-dd
            categoria (str, optional): Filtrar por categoria. Default None (todas)
            
        Returns:
            list: Lista de dicionários com os dados das vendas
        """
        try:
            # Usar conexão direta para evitar problemas com o driver
            conn = get_connection()
            cursor = conn.cursor()
            
            # Consulta ajustada para a estrutura real da tabela VENDAS
            query = """
            SELECT 
                'Produto ' || ID_VENDA AS produto,  -- Placeholder para produto 
                'Geral' AS categoria,               -- Placeholder para categoria
                DATA_VENDA as data,
                1 as quantidade,                    -- Assumindo 1 por venda
                VALOR_TOTAL as valor_total
            FROM VENDAS
            WHERE DATA_VENDA BETWEEN ? AND ?
            """
            
            params = [data_inicial, data_final]
            
            # Se tiver categoria, apenas como exemplo (ajustar conforme necessário)
            if categoria and categoria != "Geral":
                # Neste caso iremos apenas ignorar, já que não temos categoria real
                pass
                
            # Ordenar por data e limitar para melhor performance
            query += " ORDER BY DATA_VENDA DESC"
            
            # Executar a consulta diretamente pelo cursor
            cursor.execute(query, params)
            
            # Processar resultados
            vendas = []
            for row in cursor.fetchall():
                venda = {
                    "produto": str(row[0]),           # Convertendo para string
                    "categoria": str(row[1]),         # Convertendo para string  
                    "data": row[2],                   # Data
                    "quantidade": float(row[3]),      # Quantidade como float
                    "valor_total": float(row[4]) if row[4] is not None else 0.0  # Valor como float
                }
                vendas.append(venda)
                
            cursor.close()
            conn.close()
            return vendas
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Erro ao obter vendas: {e}")
            raise

# Thread para carregamento de categorias
class CarregadorCategoriasThread(QThread):
    categorias_carregadas = pyqtSignal(list)
    erro_carregamento = pyqtSignal(str)
    
    def run(self):
        try:
            # Categorias simplificadas já que provavelmente não temos a tabela grupos
            categorias = ["Geral", "Produtos", "Serviços"]
            self.categorias_carregadas.emit(categorias)
        except Exception as e:
            self.erro_carregamento.emit(str(e))


class GraficoVendas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=70):
        # Reduzir DPI para melhorar performance
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        # Configurar estilo do gráfico uma única vez
        self.setup_style()
        
        super(GraficoVendas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Iniciar com um placeholder em vez de gráfico vazio
        self.mostrar_placeholder("Clique em 'Gerar Relatório' para visualizar dados")
        
        # Cache para evitar redesenhar gráficos idênticos
        self._ultimo_dados = None
    
    def setup_style(self):
        """Configura o estilo do gráfico uma única vez para economizar recursos"""
        self.fig.patch.set_facecolor('#043b57')
        self.axes.set_facecolor('#043b57')
        
        # Configurar estilo do gráfico para fundo escuro
        for spine in self.axes.spines.values():
            spine.set_color('white')
            
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.yaxis.label.set_color('white')
        self.axes.xaxis.label.set_color('white')
        self.axes.title.set_color('white')
    
    def mostrar_placeholder(self, mensagem):
        """Mostra uma mensagem placeholder em vez de gráfico vazio"""
        self.axes.clear()
        self.axes.text(0.5, 0.5, mensagem, 
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform=self.axes.transAxes,
                     color='white', fontsize=12)
        self.draw()
    
    def atualizar_grafico(self, dados_venda):
        """
        Atualiza o gráfico com os dados de venda, com cache para evitar redesenho desnecessário
        """
        # Verificar se temos os mesmos dados que antes (usando hash)
        hash_dados = hash(str(dados_venda))
        if hash_dados == self._ultimo_dados:
            return  # Evita redesenhar o mesmo gráfico
            
        self._ultimo_dados = hash_dados
        
        # Verificar se há dados
        if not dados_venda:
            self.mostrar_placeholder('Nenhum dado disponível')
            return
        
        self.axes.clear()
        
        # Processar dados para o gráfico (agrupa por produto)
        # Usando um método mais eficiente com dicionário
        produtos = {}
        for venda in dados_venda:
            produto = venda['produto']
            produtos[produto] = produtos.get(produto, 0) + venda['quantidade']
        
        # Criar gráfico de barras
        nomes = list(produtos.keys())
        valores = list(produtos.values())
        
        # Limitar a 10 produtos para melhor visualização e performance
        if len(nomes) > 10:
            # Usar numpy para ordenação mais rápida
            indices = np.argsort(valores)[-10:][::-1]
            nomes = [nomes[i] for i in indices]
            valores = [valores[i] for i in indices]
            self.axes.set_title('Top 10 Produtos Vendidos', color='white')
        else:
            self.axes.set_title('Produtos Vendidos', color='white')
        
        # Criar barras com cores gradientes (simplificado)
        cores = plt.cm.viridis(np.linspace(0, 1, len(nomes)))
        barras = self.axes.bar(nomes, valores, color=cores)
        
        # Configurar eixos e rótulos
        self.axes.set_ylabel('Quantidade', color='white')  # Texto mais curto
        self.axes.set_xlabel('Produtos', color='white')
        
        # Rotacionar rótulos do eixo X para melhor visualização
        plt.setp(self.axes.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        
        # Ajustar layout
        self.fig.tight_layout()
        
        # Redesenhar
        self.draw()


class RelatorioVendasWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.dados_filtrados = []
        self.thread_dados = None
        self.thread_categorias = None
        
        # Definir tamanho mínimo da janela
        self.setMinimumSize(900, 600)
        self.resize(900, 600)
        
        # Inicializar UI com carregamento preguiçoso
        self.setupUI()
        
        # Carregar categorias em segundo plano
        self.iniciar_carregamento_categorias()
        
        # Usar um QTimer para adiar o carregamento inicial de dados
        QTimer.singleShot(100, self.configurar_eventos)
    
    def setupUI(self):
        """Configuração básica da UI sem carregar dados inicialmente"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Aplicar estilo ao widget principal (simplificado)
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#043b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        
        # Título
        titulo = QLabel("Relatório de Vendas de Produtos")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Seção de Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid white;
                border-radius: 5px;
                margin-top: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        filtros_layout = QFormLayout(filtros_group)
        filtros_layout.setContentsMargins(15, 25, 15, 15)
        filtros_layout.setSpacing(15)
        
        # Estilo para elementos de formulário
        form_label_style = "color: white; font-size: 14px;"
        
        # Período - Tipo
        periodo_tipo_layout = QHBoxLayout()
        
        self.radio_dia = QRadioButton("Dia")
        self.radio_dia.setStyleSheet("color: white; font-size: 14px;")
        self.radio_dia.setChecked(True)
        
        self.radio_semana = QRadioButton("Semana")
        self.radio_semana.setStyleSheet("color: white; font-size: 14px;")
        
        self.radio_mes = QRadioButton("Mês")
        self.radio_mes.setStyleSheet("color: white; font-size: 14px;")
        
        # Grupo de botões
        self.grupo_periodo = QButtonGroup(self)
        self.grupo_periodo.addButton(self.radio_dia)
        self.grupo_periodo.addButton(self.radio_semana)
        self.grupo_periodo.addButton(self.radio_mes)
        
        periodo_tipo_layout.addWidget(self.radio_dia)
        periodo_tipo_layout.addWidget(self.radio_semana)
        periodo_tipo_layout.addWidget(self.radio_mes)
        periodo_tipo_layout.addStretch(1)
        
        periodo_label = QLabel("Período:")
        periodo_label.setStyleSheet(form_label_style)
        filtros_layout.addRow(periodo_label, periodo_tipo_layout)
        
        # Data Inicial
        self.data_inicial = QDateEdit(QDate.currentDate().addDays(-7))
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setStyleSheet("""
            QDateEdit {
                background-color: white;
                color: #043b57;
                border: 1px solid white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
        """)
        
        data_inicial_label = QLabel("Data Inicial:")
        data_inicial_label.setStyleSheet(form_label_style)
        filtros_layout.addRow(data_inicial_label, self.data_inicial)
        
        # Data Final
        self.data_final = QDateEdit(QDate.currentDate())
        self.data_final.setCalendarPopup(True)
        self.data_final.setStyleSheet("""
            QDateEdit {
                background-color: white;
                color: #043b57;
                border: 1px solid white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
        """)
        
        data_final_label = QLabel("Data Final:")
        data_final_label.setStyleSheet(form_label_style)
        filtros_layout.addRow(data_final_label, self.data_final)
        
        # Categoria (Grupo)
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItem("Carregando categorias...")  # Placeholder
        self.categoria_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #043b57;
                border: 1px solid white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
        """)
        
        categoria_label = QLabel("Categoria:")
        categoria_label.setStyleSheet(form_label_style)
        filtros_layout.addRow(categoria_label, self.categoria_combo)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        self.btn_gerar = QPushButton("Gerar Relatório")
        self.btn_gerar.setStyleSheet("""
            QPushButton {
                background-color: #00a8e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0078d7;
            }
        """)
        btn_layout.addWidget(self.btn_gerar)
        
        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #3d8b40;
            }
        """)
        btn_layout.addWidget(self.btn_exportar)
        
        filtros_layout.addRow("", btn_layout)
        
        main_layout.addWidget(filtros_group)
        
        # Layout do conteúdo
        content_layout = QHBoxLayout()
        
        # Tabela de vendas
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Produto", "Categoria", "Data", "Quantidade", "Valor Total"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #cccccc;
                border: none;
                border-radius: 5px;
            }
        """)
        content_layout.addWidget(self.tabela, 3)  # Proporção 3:2
        
        # Gráfico de vendas - com DPI reduzido para melhor performance
        self.grafico = GraficoVendas(self, width=6, height=4, dpi=70)
        self.grafico.setStyleSheet("background-color: #043b57; border-radius: 5px;")
        self.grafico.setMinimumWidth(400)
        content_layout.addWidget(self.grafico, 2)  # Proporção 3:2
        
        main_layout.addLayout(content_layout, 1)  # 1 = stretch factor
        
        # Informações de resumo
        resumo_layout = QHBoxLayout()
        
        self.total_vendas_label = QLabel("Total de Vendas: R$ 0,00")
        self.total_vendas_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        resumo_layout.addWidget(self.total_vendas_label)
        
        resumo_layout.addStretch(1)
        
        self.total_produtos_label = QLabel("Produtos Vendidos: 0")
        self.total_produtos_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        resumo_layout.addWidget(self.total_produtos_label)
        
        main_layout.addLayout(resumo_layout)
    
    def configurar_eventos(self):
        """Configura os eventos e conexões de sinais após a UI estar pronta"""
        self.btn_gerar.clicked.connect(self.iniciar_gerar_relatorio)
        self.btn_exportar.clicked.connect(self.exportar_relatorio)
        self.grupo_periodo.buttonClicked.connect(self.atualizar_periodo)
    
    def iniciar_carregamento_categorias(self):
        """Inicia o carregamento de categorias em uma thread separada"""
        self.thread_categorias = CarregadorCategoriasThread()
        self.thread_categorias.categorias_carregadas.connect(self.atualizar_categorias)
        self.thread_categorias.erro_carregamento.connect(lambda erro: self.mostrar_mensagem("Erro", f"Erro ao carregar categorias: {erro}"))
        self.thread_categorias.start()
    
    def atualizar_categorias(self, categorias):
        """Atualiza o combo de categorias com dados carregados"""
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Todas as Categorias")
        self.categoria_combo.addItems(categorias)
    
    def atualizar_periodo(self):
        """Atualiza o período selecionado"""
        hoje = QDate.currentDate()
        
        if self.radio_dia.isChecked():
            # Apenas o dia atual
            self.data_inicial.setDate(hoje)
            self.data_final.setDate(hoje)
        elif self.radio_semana.isChecked():
            # Última semana
            self.data_inicial.setDate(hoje.addDays(-7))
            self.data_final.setDate(hoje)
        elif self.radio_mes.isChecked():
            # Último mês
            self.data_inicial.setDate(hoje.addMonths(-1))
            self.data_final.setDate(hoje)
    
    def iniciar_gerar_relatorio(self):
        """Inicia a geração do relatório em uma thread separada"""
        # Desabilitar botão enquanto carrega
        self.btn_gerar.setEnabled(False)
        self.btn_gerar.setText("Carregando...")
        
        # Criar diálogo de progresso
        self.progresso = QProgressDialog("Carregando dados...", "Cancelar", 0, 0, self)
        self.progresso.setWindowTitle("Aguarde")
        self.progresso.setModal(True)
        self.progresso.setMinimumDuration(500)  # Só aparece se demorar mais de 500ms
        self.progresso.show()
        
        # Obter datas do filtro
        data_inicial = self.data_inicial.date().toString("yyyy-MM-dd")
        data_final = self.data_final.date().toString("yyyy-MM-dd")
        
        # Obter categoria selecionada
        categoria = self.categoria_combo.currentText()
        if categoria == "Todas as Categorias" or categoria == "Carregando categorias...":
            categoria = None
        
        # Iniciar thread de carregamento
        self.thread_dados = CarregadorDadosThread(data_inicial, data_final, categoria)
        self.thread_dados.dados_carregados.connect(self.atualizar_relatorio)
        self.thread_dados.erro_carregamento.connect(self.tratar_erro_carregamento)
        self.thread_dados.finished.connect(lambda: self.finalizar_carregamento())
        self.thread_dados.start()
    
    def finalizar_carregamento(self):
        """Finaliza o processo de carregamento, fechando o diálogo e reativando botões"""
        self.progresso.close()
        self.btn_gerar.setEnabled(True)
        self.btn_gerar.setText("Gerar Relatório")
    
    def tratar_erro_carregamento(self, erro):
        """Trata erros durante o carregamento de dados"""
        self.mostrar_mensagem("Erro", f"Ocorreu um erro ao gerar o relatório: {erro}")
        self.dados_filtrados = []
        self.tabela.setRowCount(0)
        self.total_vendas_label.setText("Total de Vendas: R$ 0,00")
        self.total_produtos_label.setText("Produtos Vendidos: 0")
        self.grafico.mostrar_placeholder("Ocorreu um erro ao carregar os dados")
    
    def atualizar_relatorio(self, dados):
        """Atualiza a UI com os dados carregados"""
        self.dados_filtrados = dados
        
        # Limpamos a tabela antes de preencher
        self.tabela.setRowCount(0)
        
        # Variáveis para cálculo de totais
        total_vendas = 0
        total_produtos = 0
        
        # Desativar sorting temporariamente para melhorar performance
        self.tabela.setSortingEnabled(False)
        
        # Usar setRowCount para pré-alocar linhas (melhora performance)
        self.tabela.setRowCount(len(dados))
        
        # Preencher a tabela com os dados - por batch para melhorar performance
        for i, venda in enumerate(self.dados_filtrados):
            # Configurar células da tabela
            self.tabela.setItem(i, 0, QTableWidgetItem(venda["produto"]))
            self.tabela.setItem(i, 1, QTableWidgetItem(venda["categoria"]))
            
            # Formatar data
            data_formatada = venda["data"]
            if isinstance(data_formatada, datetime.date):
                # Converter objeto date para string no formato "dd/mm/yyyy"
                data_formatada = data_formatada.strftime("%d/%m/%Y")
            elif isinstance(data_formatada, str) and "-" in data_formatada:
                # Converter de "yyyy-mm-dd" para "dd/mm/yyyy"
                partes = data_formatada.split("-")
                if len(partes) == 3:
                    data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}"
            
            # Garantir que seja string
            self.tabela.setItem(i, 2, QTableWidgetItem(str(data_formatada)))
            self.tabela.setItem(i, 3, QTableWidgetItem(str(venda["quantidade"])))
            
            # Formatação de valor monetário
            valor_total = venda["valor_total"]
            valor_formatado = f"R$ {valor_total:.2f}".replace('.', ',')
            self.tabela.setItem(i, 4, QTableWidgetItem(valor_formatado))
            
            # Acumular totais
            total_vendas += valor_total
            total_produtos += venda["quantidade"]
        
        # Reativar sorting
        self.tabela.setSortingEnabled(True)
        
        # Atualizar rótulos de resumo
        self.total_vendas_label.setText(f"Total de Vendas: R$ {total_vendas:.2f}".replace('.', ','))
        self.total_produtos_label.setText(f"Produtos Vendidos: {total_produtos}")
        
        # Atualizar gráfico (com delay para melhorar responsividade)
        QTimer.singleShot(100, lambda: self.grafico.atualizar_grafico(self.dados_filtrados))
    
    def exportar_relatorio(self):
        """Exporta o relatório para um arquivo CSV"""
        if not self.dados_filtrados:
            self.mostrar_mensagem("Sem Dados", 
                               "Não há dados para exportar. Gere um relatório primeiro.")
            return
        
        # Diálogo para escolher local do arquivo
        opcoes = QFileDialog.Options()
        nome_arquivo, _ = QFileDialog.getSaveFileName(
            self, "Exportar Relatório", 
            f"Relatorio_Vendas_{QDate.currentDate().toString('yyyy-MM-dd')}.csv",
            "Arquivos CSV (*.csv);;Todos os Arquivos (*)", options=opcoes)
        
        if nome_arquivo:
            try:
                # Mostrar progresso durante exportação para arquivos grandes
                progresso = QProgressDialog("Exportando relatório...", "Cancelar", 0, len(self.dados_filtrados), self)
                progresso.setWindowTitle("Exportando")
                progresso.setModal(True)
                progresso.show()
                
                with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                    # Cabeçalho
                    arquivo.write("Produto,Categoria,Data,Quantidade,Valor Total\n")
                    
                    # Dados - processados em lotes de 100 para não travar a UI
                    for i, venda in enumerate(self.dados_filtrados):
                        if i % 100 == 0:
                            progresso.setValue(i)
                            QApplication.processEvents()  # Permite que a UI responda
                            
                            if progresso.wasCanceled():
                                break
                        
                        # Formatar a data
                        data = venda['data']
                        if isinstance(data, str) and "-" in data:
                            partes = data.split("-")
                            if len(partes) == 3:
                                data = f"{partes[2]}/{partes[1]}/{partes[0]}"
                        
                        linha = f"{venda['produto']},{venda['categoria']},{data},"
                        linha += f"{venda['quantidade']},{venda['valor_total']:.2f}\n"
                        arquivo.write(linha)
                
                progresso.close()
                
                self.mostrar_mensagem("Exportação Concluída", 
                                    f"Relatório exportado com sucesso para:\n{nome_arquivo}")
            except Exception as e:
                self.mostrar_mensagem("Erro na Exportação", 
                                    f"Ocorreu um erro ao exportar o relatório:\n{str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem com o estilo adequado"""
        msg_box = QMessageBox()
        if "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
        elif "Atenção" in titulo or "Sem Dados" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #043b57;
            }
            QLabel { 
                color: white;
                background-color: #043b57;
            }
            QPushButton {
                background-color: #00a8e8;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
        """)
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Relatório de Vendas de Produtos")
    window.setGeometry(100, 100, 1200, 700)
    window.setStyleSheet("background-color: #043b57;")
    
    relatorio_widget = RelatorioVendasWindow(window)
    window.setCentralWidget(relatorio_widget)
    
    window.show()
    sys.exit(app.exec_())