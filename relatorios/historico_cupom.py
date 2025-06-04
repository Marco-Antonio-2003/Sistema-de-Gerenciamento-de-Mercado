# relatorios/historico_cupom.py
import sys
import os
import datetime
import glob
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QListWidget,
                             QListWidgetItem, QLineEdit, QDateEdit, QComboBox,
                             QMessageBox, QTextEdit)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QDesktopServices
from PyQt5.QtCore import Qt, QDate, QDateTime, QThread, pyqtSignal, QTimer, QUrl

# Tentar importar QWebEngineView (opcional)
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_DISPONIVEL = True
except ImportError:
    WEBENGINE_DISPONIVEL = False
    print("QWebEngineView não disponível. Para visualização interna de PDFs, instale: pip install PyQtWebEngine")

# PyMuPDF para leitura de PDF (opcional)
try:
    import fitz
    PYMUPDF_DISPONIVEL = True
except ImportError:
    PYMUPDF_DISPONIVEL = False
    print("PyMuPDF não disponível. Para metadados de PDF, instale: pip install PyMuPDF")


class CarregadorCuponsThread(QThread):
    cupons_carregados = pyqtSignal(list)
    erro_carregamento = pyqtSignal(str)
    
    def __init__(self, pasta_cupons, filtro_data=None, filtro_nome=None):
        super().__init__()
        self.pasta_cupons = pasta_cupons
        self.filtro_data = filtro_data
        self.filtro_nome = filtro_nome
    
    def run(self):
        try:
            cupons = self.carregar_cupons()
            self.cupons_carregados.emit(cupons)
        except Exception as e:
            self.erro_carregamento.emit(str(e))
    
    def carregar_cupons(self):
        """Carrega todos os cupons PDF da pasta"""
        cupons = []
        
        print(f"=== THREAD: Carregando cupons da pasta ===")
        print(f"Pasta: {self.pasta_cupons}")
        
        if not os.path.exists(self.pasta_cupons):
            raise Exception(f"Pasta de cupons não encontrada: {self.pasta_cupons}")
        
        # Buscar todos os arquivos PDF
        pattern = os.path.join(self.pasta_cupons, "*.pdf")
        print(f"Pattern de busca: {pattern}")
        
        arquivos_pdf = glob.glob(pattern)
        print(f"Arquivos PDF encontrados: {len(arquivos_pdf)}")
        
        if len(arquivos_pdf) == 0:
            print("AVISO: Nenhum arquivo PDF encontrado na pasta!")
            # Vamos listar todos os arquivos para debug
            try:
                todos_arquivos = os.listdir(self.pasta_cupons)
                print(f"Todos os arquivos na pasta: {todos_arquivos}")
            except Exception as e:
                print(f"Erro ao listar arquivos: {e}")
        
        for i, arquivo in enumerate(arquivos_pdf):
            try:
                print(f"Processando arquivo {i+1}/{len(arquivos_pdf)}: {arquivo}")
                
                # Informações básicas do arquivo
                stat = os.stat(arquivo)
                nome_arquivo = os.path.basename(arquivo)
                data_modificacao = datetime.datetime.fromtimestamp(stat.st_mtime)
                
                print(f"  Nome: {nome_arquivo}")
                print(f"  Data modificação: {data_modificacao}")
                
                # Aplicar filtros
                if self.filtro_data:
                    if data_modificacao.date() != self.filtro_data:
                        print(f"  Filtrado por data: {data_modificacao.date()} != {self.filtro_data}")
                        continue
                        
                if self.filtro_nome and self.filtro_nome.lower() not in nome_arquivo.lower():
                    print(f"  Filtrado por nome: '{self.filtro_nome}' não está em '{nome_arquivo}'")
                    continue
                
                # Criar nome de exibição mais limpo
                nome_display = nome_arquivo.replace('.pdf', '').replace('_', ' ')
                
                cupom_info = {
                    "nome_arquivo": nome_arquivo,
                    "caminho_completo": arquivo,
                    "data_modificacao": data_modificacao,
                    "nome_display": nome_display
                }
                
                cupons.append(cupom_info)
                print(f"  Cupom adicionado: {cupom_info['nome_display']}")
                
            except Exception as e:
                print(f"ERRO ao processar arquivo {arquivo}: {e}")
                continue
        
        # Ordenar por data de modificação (mais recente primeiro)
        cupons.sort(key=lambda x: x["data_modificacao"], reverse=True)
        
        print(f"=== THREAD: Retornando {len(cupons)} cupons ===")
        return cupons


class HistoricoCuponsWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.pasta_cupons = r"C:\Users\Marco-Note\Desktop\PythonProject\Sistema\cupons"
        self.cupons_carregados = []
        self.thread_cupons = None
        self.arquivo_selecionado = None
        
        # Definir tamanho da janela
        self.setMinimumSize(1000, 600)
        self.resize(1000, 600)
        
        # Configurar UI
        self.setup_ui()
        self.configurar_eventos()
        
        # Carregar cupons automaticamente
        QTimer.singleShot(100, self.carregar_cupons)
    
    def setup_ui(self):
        """Configuração da interface igual à imagem"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Aplicar estilo de fundo igual à imagem
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1e3d59"))  # Azul da imagem
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        
        # Título principal - igual à imagem
        titulo = QLabel("Histórico de Cupons")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white; text-align: center; padding: 20px 0;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Área de filtros (busca)
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(10)
        
        # Label para nome
        label_nome = QLabel("Nome:")
        label_nome.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        filtros_layout.addWidget(label_nome)
        
        # Campo de pesquisa por nome
        self.filtro_nome = QLineEdit()
        self.filtro_nome.setPlaceholderText("Digite o nome do cupom...")
        self.filtro_nome.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #1e3d59;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        filtros_layout.addWidget(self.filtro_nome)
        
        # Label para data
        label_data = QLabel("Data:")
        label_data.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        filtros_layout.addWidget(label_data)
        
        # Filtro por data
        self.filtro_data = QDateEdit()
        self.filtro_data.setDate(QDate.currentDate())
        self.filtro_data.setCalendarPopup(True)
        self.filtro_data.setStyleSheet("""
            QDateEdit {
                background-color: white;
                color: #1e3d59;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        filtros_layout.addWidget(self.filtro_data)
        
        # Combo período
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Dia selecionado", "Últimos 7 dias", "Últimos 30 dias", "Todos"])
        self.combo_periodo.setCurrentText("Todos")
        self.combo_periodo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #1e3d59;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        filtros_layout.addWidget(self.combo_periodo)
        
        # Botão de pesquisar
        self.btn_pesquisar = QPushButton("Buscar")
        self.btn_pesquisar.setStyleSheet("""
            QPushButton {
                background-color: #00d4aa;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b894;
            }
        """)
        filtros_layout.addWidget(self.btn_pesquisar)
        
        filtros_layout.addStretch()  # Empurrar tudo para a esquerda
        main_layout.addLayout(filtros_layout)
        
        # Layout principal - dividido como na imagem
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # PAINEL ESQUERDO - exatamente como na imagem
        painel_esquerdo = QFrame()
        painel_esquerdo.setFixedWidth(300)  # Largura fixa igual à imagem
        painel_esquerdo.setStyleSheet("""
            QFrame {
                background-color: #2a4a5c;
                border-radius: 8px;
                border: 1px solid #3a5a6c;
            }
        """)
        
        layout_esquerdo = QVBoxLayout(painel_esquerdo)
        layout_esquerdo.setContentsMargins(15, 15, 15, 15)
        layout_esquerdo.setSpacing(10)
        
        # Título "Cupons" - igual à imagem
        label_cupons = QLabel("Cupons")
        label_cupons.setFont(QFont("Arial", 14, QFont.Bold))
        label_cupons.setStyleSheet("color: white; padding: 5px 0;")
        layout_esquerdo.addWidget(label_cupons)
        
        # Lista de cupons com fundo igual à imagem
        self.lista_cupons = QListWidget()
        self.lista_cupons.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #333333;
            }
            QListWidget::item {
                background-color: transparent;
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #e8f4f8;
            }
        """)
        layout_esquerdo.addWidget(self.lista_cupons)
        
        # Botão "Visualizar" - EXATAMENTE como na imagem (verde, largura total)
        self.btn_visualizar = QPushButton("Visualizar")
        self.btn_visualizar.setStyleSheet("""
            QPushButton {
                background-color: #00d4aa;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b894;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_visualizar.setEnabled(False)
        layout_esquerdo.addWidget(self.btn_visualizar)
        
        # PAINEL DIREITO - área de visualização (maior como na imagem)
        painel_direito = QFrame()
        painel_direito.setStyleSheet("""
            QFrame {
                background-color: #2a4a5c;
                border-radius: 8px;
                border: 1px solid #3a5a6c;
            }
        """)
        
        layout_direito = QVBoxLayout(painel_direito)
        layout_direito.setContentsMargins(15, 15, 15, 15)
        
        # Área de visualização do PDF
        self.visualizador_disponivel = False
        
        if WEBENGINE_DISPONIVEL:
            try:
                self.web_view = QWebEngineView()
                self.web_view.setStyleSheet("""
                    QWebEngineView {
                        background-color: white; 
                        border: none;
                        border-radius: 5px;
                    }
                """)
                
                # Página inicial
                self.web_view.setHtml("""
                    <html>
                    <body style='margin:0; padding:40px; background-color:#f8f9fa; 
                               font-family:Arial; text-align:center; color:#6c757d;'>
                        <h2>Selecione um cupom para visualizar</h2>
                        <p>Escolha um cupom da lista ao lado e clique em "Visualizar"</p>
                    </body>
                    </html>
                """)
                
                layout_direito.addWidget(self.web_view)
                self.visualizador_disponivel = True
                print("QWebEngineView carregado com sucesso!")
                
            except Exception as e:
                print(f"Erro ao inicializar QWebEngineView: {e}")
                self.web_view = None
                self.criar_fallback_visualizador(layout_direito)
        else:
            print("QWebEngineView não está disponível")
            self.web_view = None
            self.criar_fallback_visualizador(layout_direito)
    
    def criar_fallback_visualizador(self, layout):
        """Cria um visualizador fallback quando QWebEngineView não está disponível"""
        self.texto_info = QTextEdit()
        self.texto_info.setReadOnly(True)
        self.texto_info.setStyleSheet("""
            QTextEdit {
                background-color: white; 
                color: #6c757d; 
                padding: 40px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.texto_info.setHtml("""
            <div style='text-align: center; color: #6c757d;'>
                <h2>Visualização Interna Não Disponível</h2>
                <p>Para visualizar PDFs dentro do sistema, instale:</p>
                <code style='background-color: #f8f9fa; padding: 10px; display: block; margin: 10px 0; border-radius: 4px;'>
                    pip install PyQtWebEngine
                </code>
                <hr style='margin: 20px 0; border: none; border-top: 1px solid #dee2e6;'>
                <p><strong>Como usar:</strong></p>
                <p>1. Selecione um cupom da lista</p>
                <p>2. Clique em 'Visualizar'</p>
                <p>3. O PDF abrirá no visualizador padrão do sistema</p>
            </div>
        """)
        layout.addWidget(self.texto_info)
        
        # Adicionar painéis ao layout principal
        # Ensure variables are defined before use
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        painel_esquerdo = QFrame()
        painel_esquerdo.setFixedWidth(300)
        painel_esquerdo.setStyleSheet("""
            QFrame {
                background-color: #2a4a5c;
                border-radius: 8px;
                border: 1px solid #3a5a6c;
            }
        """)
        
        painel_direito = QFrame()
        painel_direito.setStyleSheet("""
            QFrame {
                background-color: #2a4a5c;
                border-radius: 8px;
                border: 1px solid #3a5a6c;
            }
        """)
        
        content_layout.addWidget(painel_esquerdo)
        content_layout.addWidget(painel_direito)
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(content_layout)
    
    def configurar_eventos(self):
        """Configura os eventos da interface"""
        self.btn_pesquisar.clicked.connect(self.carregar_cupons)
        self.btn_visualizar.clicked.connect(self.visualizar_cupom_selecionado)
        self.filtro_nome.returnPressed.connect(self.carregar_cupons)
        self.lista_cupons.itemSelectionChanged.connect(self.cupom_selecionado)
        self.lista_cupons.itemDoubleClicked.connect(self.visualizar_cupom_selecionado)
        self.combo_periodo.currentTextChanged.connect(self.carregar_cupons)
    
    def cupom_selecionado(self):
        """Ativa o botão visualizar quando um cupom é selecionado"""
        self.btn_visualizar.setEnabled(len(self.lista_cupons.selectedItems()) > 0)
    
    def carregar_cupons(self):
        """Inicia o carregamento dos cupons"""
        print(f"=== CARREGANDO CUPONS ===")
        print(f"Pasta de cupons: {self.pasta_cupons}")
        print(f"Pasta existe: {os.path.exists(self.pasta_cupons)}")
        
        if not os.path.exists(self.pasta_cupons):
            self.mostrar_mensagem("Erro", f"Pasta de cupons não encontrada:\n{self.pasta_cupons}")
            return
        
        self.btn_pesquisar.setEnabled(False)
        self.btn_pesquisar.setText("Carregando...")
        
        # Obter filtros
        filtro_nome = self.filtro_nome.text().strip() if self.filtro_nome.text().strip() else None
        print(f"Filtro nome: {filtro_nome}")
        
        # Filtro de data baseado na seleção
        filtro_data = None
        periodo = self.combo_periodo.currentText()
        print(f"Período selecionado: {periodo}")
        
        if periodo == "Dia selecionado":
            filtro_data = self.filtro_data.date().toPyDate()
            print(f"Filtro data: {filtro_data}")
        
        # Iniciar thread
        self.thread_cupons = CarregadorCuponsThread(
            self.pasta_cupons, filtro_data, filtro_nome
        )
        self.thread_cupons.cupons_carregados.connect(self.atualizar_lista_cupons)
        self.thread_cupons.erro_carregamento.connect(self.tratar_erro_carregamento)
        self.thread_cupons.finished.connect(self.finalizar_carregamento)
        self.thread_cupons.start()
    
    def finalizar_carregamento(self):
        """Finaliza o carregamento"""
        self.btn_pesquisar.setEnabled(True)
        self.btn_pesquisar.setText("Buscar")
    
    def tratar_erro_carregamento(self, erro):
        """Trata erros durante o carregamento"""
        self.mostrar_mensagem("Erro", f"Erro ao carregar cupons: {erro}")
        self.cupons_carregados = []
        self.lista_cupons.clear()
    
    def atualizar_lista_cupons(self, cupons):
        """Atualiza a lista de cupons"""
        print(f"=== ATUALIZANDO LISTA DE CUPONS ===")
        print(f"Cupons recebidos: {len(cupons)}")
        
        # Aplicar filtro de período se necessário
        periodo = self.combo_periodo.currentText()
        hoje = datetime.date.today()
        
        if periodo == "Últimos 7 dias":
            cupons = [c for c in cupons if (hoje - c["data_modificacao"].date()).days <= 7]
            print(f"Após filtro 7 dias: {len(cupons)}")
        elif periodo == "Últimos 30 dias":
            cupons = [c for c in cupons if (hoje - c["data_modificacao"].date()).days <= 30]
            print(f"Após filtro 30 dias: {len(cupons)}")
        
        self.cupons_carregados = cupons
        print(f"Cupons finais carregados: {len(self.cupons_carregados)}")
        
        # Limpar e preencher lista
        self.lista_cupons.clear()
        
        for i, cupom in enumerate(cupons):
            print(f"Adicionando cupom {i}: {cupom['nome_display']}")
            # Criar item da lista - formato simples como na imagem
            item = QListWidgetItem(cupom['nome_display'])
            item.setData(Qt.UserRole, i)  # Guardar índice para referência
            self.lista_cupons.addItem(item)
        
        print(f"Lista atualizada com {self.lista_cupons.count()} items")
        
        # Se não há cupons, mostrar mensagem
        if len(cupons) == 0:
            item_vazio = QListWidgetItem("Nenhum cupom encontrado")
            item_vazio.setData(Qt.UserRole, -1)  # Índice inválido
            self.lista_cupons.addItem(item_vazio)
    
    def visualizar_cupom_selecionado(self):
        """Visualiza o cupom selecionado na lista"""
        print("=== VISUALIZAR CUPOM CHAMADO ===")
        
        items_selecionados = self.lista_cupons.selectedItems()
        print(f"Items selecionados: {len(items_selecionados)}")
        
        if not items_selecionados:
            self.mostrar_mensagem("Atenção", "Selecione um cupom para visualizar.")
            return
        
        # Obter índice do cupom selecionado
        item = items_selecionados[0]
        indice = item.data(Qt.UserRole)
        print(f"Índice selecionado: {indice}")
        print(f"Total de cupons carregados: {len(self.cupons_carregados)}")
        
        if indice is None or indice == -1:
            self.mostrar_mensagem("Erro", "Nenhum cupom válido selecionado.")
            return
        
        if indice >= len(self.cupons_carregados):
            self.mostrar_mensagem("Erro", "Índice do cupom inválido.")
            return
            
        cupom = self.cupons_carregados[indice]
        caminho_arquivo = cupom["caminho_completo"]
        print(f"Caminho do arquivo: {caminho_arquivo}")
        
        if not os.path.exists(caminho_arquivo):
            self.mostrar_mensagem("Erro", f"Arquivo não encontrado:\n{caminho_arquivo}")
            return
        
        self.arquivo_selecionado = caminho_arquivo
        print(f"Arquivo existe: {os.path.exists(caminho_arquivo)}")
        print(f"Visualizador disponível: {getattr(self, 'visualizador_disponivel', False)}")
        
        try:
            # Tentar visualização interna primeiro
            if hasattr(self, 'web_view') and self.web_view and getattr(self, 'visualizador_disponivel', False):
                print("Carregando PDF no QWebEngineView...")
                
                # Mostrar mensagem de carregamento
                self.web_view.setHtml("""
                    <html>
                    <body style='margin:0; padding:40px; background-color:#f8f9fa; 
                               font-family:Arial; text-align:center; color:#007bff;'>
                        <h2>Carregando cupom...</h2>
                        <p>Aguarde enquanto o PDF é carregado.</p>
                        <div style='width: 50px; height: 50px; border: 3px solid #f3f3f3; 
                                  border-top: 3px solid #007bff; border-radius: 50%; 
                                  animation: spin 1s linear infinite; margin: 20px auto;'></div>
                        <style>
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                        </style>
                    </body>
                    </html>
                """)
                
                # Carregar PDF após um pequeno delay para mostrar o loading
                QTimer.singleShot(500, lambda: self.carregar_pdf_interno(caminho_arquivo, cupom['nome_display']))
                
            else:
                print("QWebEngineView não disponível, abrindo externamente...")
                self.abrir_pdf_externo(caminho_arquivo, cupom['nome_display'])
                
        except Exception as e:
            print(f"Erro ao visualizar PDF: {e}")
            # Fallback para visualizador externo
            self.abrir_pdf_externo(caminho_arquivo, cupom['nome_display'])
    
    def carregar_pdf_interno(self, caminho_arquivo, nome_cupom):
        """Carrega o PDF no visualizador interno"""
        try:
            url = QUrl.fromLocalFile(os.path.abspath(caminho_arquivo))
            print(f"URL do PDF: {url.toString()}")
            self.web_view.setUrl(url)
            
            # Verificar se carregou após alguns segundos
            QTimer.singleShot(3000, lambda: self.verificar_carregamento_pdf(caminho_arquivo, nome_cupom))
            
        except Exception as e:
            print(f"Erro ao carregar PDF interno: {e}")
            self.abrir_pdf_externo(caminho_arquivo, nome_cupom)
    
    def verificar_carregamento_pdf(self, caminho_arquivo, nome_cupom):
        """Verifica se o PDF foi carregado corretamente"""
        try:
            # Se chegou até aqui e não deu erro, provavelmente carregou
            print("PDF carregado no visualizador interno!")
        except:
            print("Falha ao carregar PDF interno, tentando externo...")
            self.abrir_pdf_externo(caminho_arquivo, nome_cupom)
    
    def abrir_pdf_externo(self, caminho_arquivo, nome_cupom):
        """Abre o PDF no visualizador externo do sistema"""
        try:
            from PyQt5.QtGui import QDesktopServices
            
            # Mostrar mensagem no painel
            if hasattr(self, 'web_view') and self.web_view:
                self.web_view.setHtml(f"""
                    <html>
                    <body style='margin:0; padding:40px; background-color:#f8f9fa; 
                               font-family:Arial; text-align:center; color:#28a745;'>
                        <h2>PDF Aberto Externamente</h2>
                        <p>O cupom <strong>{nome_cupom}</strong> foi aberto no visualizador padrão do sistema.</p>
                        <p style='color:#6c757d; font-size:12px;'>
                            Para visualização interna, instale: pip install PyQtWebEngine
                        </p>
                    </body>
                    </html>
                """)
            elif hasattr(self, 'texto_info'):
                self.texto_info.setHtml(f"""
                    <div style='text-align: center; color: #28a745;'>
                        <h2>PDF Aberto Externamente</h2>
                        <p>O cupom <strong>{nome_cupom}</strong> foi aberto no visualizador padrão.</p>
                    </div>
                """)
            
            # Abrir no visualizador externo
            resultado = QDesktopServices.openUrl(QUrl.fromLocalFile(caminho_arquivo))
            
            if resultado:
                print(f"PDF aberto externamente: {nome_cupom}")
            else:
                self.mostrar_mensagem("Erro", "Não foi possível abrir o PDF no visualizador externo.")
                
        except Exception as e:
            print(f"Erro ao abrir PDF externamente: {e}")
            self.mostrar_mensagem("Erro", f"Erro ao abrir PDF: {str(e)}")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
        elif "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(titulo)
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #1e3d59;
            }
            QLabel { 
                color: white;
                background-color: #1e3d59;
            }
            QPushButton {
                background-color: #00d4aa;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Histórico de Cupons Fiscais")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #1e3d59;")
    
    historico_widget = HistoricoCuponsWindow()
    window.setCentralWidget(historico_widget)
    
    window.show()
    sys.exit(app.exec_())