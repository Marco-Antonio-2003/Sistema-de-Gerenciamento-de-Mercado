# relatorios/relatorio_vendas_produtos.py
import sys
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QDateEdit,
                             QGroupBox, QFormLayout, QRadioButton, QButtonGroup,
                             QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QDate, QDateTime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# Importar funções do banco de dados
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from base.banco import (get_connection, execute_query, verificar_tabela_vendas_produtos,
                        listar_produtos, listar_grupos, obter_vendas_por_periodo)


class GraficoVendas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor('#043b57')
        self.axes.set_facecolor('#043b57')
        
        # Configurar estilo do gráfico para fundo escuro
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white') 
        self.axes.spines['right'].set_color('white')
        self.axes.spines['left'].set_color('white')
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.yaxis.label.set_color('white')
        self.axes.xaxis.label.set_color('white')
        self.axes.title.set_color('white')
        
        super(GraficoVendas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Dados iniciais
        self.atualizar_grafico([])
    
    def atualizar_grafico(self, dados_venda):
        """
        Atualiza o gráfico com os dados de venda
        
        dados_venda: lista de dicionários no formato:
        [{'produto': 'Nome do Produto', 'quantidade': 10, 'data': '2025-04-28'}, ...]
        """
        self.axes.clear()
        
        # Verificar se há dados
        if not dados_venda:
            self.axes.text(0.5, 0.5, 'Nenhum dado disponível', 
                          horizontalalignment='center',
                          verticalalignment='center',
                          transform=self.axes.transAxes,
                          color='white', fontsize=12)
            self.draw()
            return
        
        # Processar dados para o gráfico (agrupa por produto)
        produtos = {}
        for venda in dados_venda:
            produto = venda['produto']
            if produto in produtos:
                produtos[produto] += venda['quantidade']
            else:
                produtos[produto] = venda['quantidade']
        
        # Criar gráfico de barras
        nomes = list(produtos.keys())
        valores = list(produtos.values())
        
        # Limitar a 10 produtos para melhor visualização
        if len(nomes) > 10:
            indices_ordenados = sorted(range(len(valores)), key=lambda i: valores[i], reverse=True)[:10]
            nomes = [nomes[i] for i in indices_ordenados]
            valores = [valores[i] for i in indices_ordenados]
            self.axes.set_title('Top 10 Produtos Vendidos', color='white')
        else:
            self.axes.set_title('Produtos Vendidos', color='white')
        
        # Criar barras com cores gradientes
        barras = self.axes.bar(nomes, valores, color=plt.cm.viridis(np.linspace(0, 1, len(nomes))))
        
        # Configurar eixos e rótulos
        self.axes.set_ylabel('Quantidade Vendida', color='white')
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
        
        # Definir tamanho mínimo da janela
        self.setMinimumSize(900, 600)
        
        # Para garantir que a janela seja aberta com esse tamanho
        self.resize(900, 600)
        
        # Verificar e criar a tabela de vendas se necessário
        verificar_tabela_vendas_produtos()
        
        self.initUI()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#043b57"))
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
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: white;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
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
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: white;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
        """)
        
        data_final_label = QLabel("Data Final:")
        data_final_label.setStyleSheet(form_label_style)
        filtros_layout.addRow(data_final_label, self.data_final)
        
        # Categoria (Grupo)
        self.categoria_combo = QComboBox()
        categorias = ["Todas as Categorias"]  # Buscar do banco
        categorias.extend(self.carregar_categorias())
        self.categoria_combo.addItems(categorias)
        self.categoria_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #043b57;
                border: 1px solid white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: white;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #043b57;
                selection-background-color: #0078d7;
                selection-color: white;
            }
        """)
        
        categoria_label = QLabel("Categoria:")
        categoria_label.setStyleSheet(form_label_style)
        filtros_layout.addRow(categoria_label, self.categoria_combo)
        
        # Botão gerar relatório
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
            QPushButton:pressed {
                background-color: #005f9e;
            }
        """)
        self.btn_gerar.clicked.connect(self.gerar_relatorio)
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
            QPushButton:pressed {
                background-color: #2d682f;
            }
        """)
        self.btn_exportar.clicked.connect(self.exportar_relatorio)
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
        content_layout.addWidget(self.tabela, 3)  # Proporção 3:2
        
        # Gráfico de vendas
        self.grafico = GraficoVendas(self, width=6, height=4, dpi=80)
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
        
        # Conectar sinais
        self.grupo_periodo.buttonClicked.connect(self.atualizar_periodo)
        
        # Gerar relatório inicial
        self.gerar_relatorio()
    
    def carregar_categorias(self):
        """Carrega as categorias (grupos) do banco de dados"""
        try:
            grupos = listar_grupos()
            return grupos
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
            return []
    
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
    
    def gerar_relatorio(self):
        """Gera o relatório com base nos filtros selecionados"""
        try:
            # Obter datas do filtro
            data_inicial = self.data_inicial.date().toString("yyyy-MM-dd")
            data_final = self.data_final.date().toString("yyyy-MM-dd")
            
            # Obter categoria selecionada
            categoria = self.categoria_combo.currentText()
            if categoria == "Todas as Categorias":
                categoria = None
                
            # Buscar dados no banco
            self.dados_filtrados = obter_vendas_por_periodo(data_inicial, data_final, categoria)
            
            # Limpar e preencher a tabela
            self.tabela.setRowCount(0)
            
            # Variáveis para cálculo de totais
            total_vendas = 0
            total_produtos = 0
            
            # Preencher a tabela com os dados
            for i, venda in enumerate(self.dados_filtrados):
                self.tabela.insertRow(i)
                
                # Configurar células da tabela
                self.tabela.setItem(i, 0, QTableWidgetItem(venda["produto"]))
                self.tabela.setItem(i, 1, QTableWidgetItem(venda["categoria"]))
                
                # Formatar data - CORREÇÃO AQUI
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
            
            # Atualizar rótulos de resumo
            self.total_vendas_label.setText(f"Total de Vendas: R$ {total_vendas:.2f}".replace('.', ','))
            self.total_produtos_label.setText(f"Produtos Vendidos: {total_produtos}")
            
            # Atualizar gráfico
            self.grafico.atualizar_grafico(self.dados_filtrados)
            
            # Exibir mensagem se não houver dados
            if not self.dados_filtrados:
                self.mostrar_mensagem("Sem Dados", 
                                    "Não foram encontrados dados para o período e categoria selecionados.")
        
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_mensagem("Erro", f"Ocorreu um erro ao gerar o relatório: {str(e)}")
            
            # Limpar dados
            self.dados_filtrados = []
            self.tabela.setRowCount(0)
            self.total_vendas_label.setText("Total de Vendas: R$ 0,00")
            self.total_produtos_label.setText("Produtos Vendidos: 0")
            self.grafico.atualizar_grafico([])
    
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
                with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                    # Cabeçalho
                    arquivo.write("Produto,Categoria,Data,Quantidade,Valor Total\n")
                    
                    # Dados
                    for venda in self.dados_filtrados:
                        # Formatar a data
                        data = venda['data']
                        if isinstance(data, str) and "-" in data:
                            partes = data.split("-")
                            if len(partes) == 3:
                                data = f"{partes[2]}/{partes[1]}/{partes[0]}"
                        
                        linha = f"{venda['produto']},{venda['categoria']},{data},"
                        linha += f"{venda['quantidade']},{venda['valor_total']:.2f}\n"
                        arquivo.write(linha)
                
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
            QPushButton:hover {
                background-color: #0078d7;
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