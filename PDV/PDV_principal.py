import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSpacerItem, QSizePolicy, QGridLayout, QToolButton,
    QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QCursor, QPainter
from PyQt5.QtCore import Qt, QDateTime, QTimer, QSize
from PyQt5.QtSvg import QSvgRenderer
try:
    # Importar os módulos do sistema
    from base.banco import buscar_produto_por_barras, buscar_produto_por_codigo
    # Importar a classe/função para listar vendas
    import Lista_vendas
    # Importar o módulo de cupom fiscal
    import cupom_fiscal
except ImportError as e:
    print(f"AVISO: Erro de importação: {e}")
    # Funções vazias para evitar erros
    def buscar_produto_por_barras(codigo): return None
    def buscar_produto_por_codigo(codigo): return None

try:
    # Tentativa de importação explícita do módulo cupom_fiscal
    import cupom_fiscal
    print("✅ Módulo cupom_fiscal importado com sucesso!")
    
    # Verificar se o método solicitar_tipo_cupom existe no módulo
    if hasattr(cupom_fiscal, 'solicitar_tipo_cupom'):
        print("✅ Método solicitar_tipo_cupom encontrado!")
    else:
        print("⚠️ ERRO: Método solicitar_tipo_cupom NÃO encontrado no módulo!")
        
except ImportError as e:
    print(f"⚠️ ERRO DE IMPORTAÇÃO: {e}")
    print("⚠️ O módulo cupom_fiscal.py não foi encontrado!")
    print("⚠️ Verifique se o arquivo cupom_fiscal.py está no mesmo diretório.")

class IconButton(QPushButton):
    """Botão customizado com ícone SVG embutido"""
    def __init__(self, svg_content, color="#FFFFFF", hover_color="#EEEEEE", size=24, parent=None):
        super().__init__(parent)
        self.svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')
        self.hover_svg = svg_content.replace('fill="currentColor"', f'fill="{hover_color}"')
        self.color = color
        self.hover_color = hover_color
        self.size = size
        self.setFixedSize(size, size)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFlat(True)
        self.update_icon()
        
    def update_icon(self, hover=False):
        svg = self.hover_svg if hover else self.svg_content
        renderer = QSvgRenderer(bytearray(svg, encoding='utf-8'))
        pixmap = QPixmap(self.size, self.size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(self.size, self.size))
    
    def enterEvent(self, event):
        self.update_icon(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.update_icon(False)
        super().leaveEvent(event)

# SVG ícones (podem ser substituídos por ícones mais adequados)
SVG_ICONS = {
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path></svg>',
    "list": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"></path></svg>',
    "edit": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"></path></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"></path></svg>',
    "barcode": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M2 2h2v20H2V2zm3 0h1v20H5V2zm2 0h3v20H7V2zm4 0h1v20h-1V2zm3 0h1v20h-1V2zm2 0h3v20h-3V2zm4 0h1v20h-1V2z"></path></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"></path></svg>',
    "minus": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19 13H5v-2h14v2z"></path></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"></path></svg>',
    "exit": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"></path></svg>',
    "minimize": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19 13H5v-2h14v2z"></path></svg>',
    "arrow_left": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"></path></svg>',
    "chevron_down": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5z"></path></svg>',
    "eye": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"></path></svg>',
    "history": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"></path></svg>'
}

class PDVWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema PDV")
        
        # Valores para desconto e acréscimo
        self.valor_desconto = 0.0
        self.valor_acrescimo = 0.0

        self.setWindowTitle("Sistema PDV")
        
        # Definir paleta de cores (baseada na imagem fornecida)
        self.colors = {
            "bg_main": "#FFFFFF",
            "header_bg": "#333333",
            "header_fg": "#FFFFFF",
            "sidebar_bg": "#FFFFFF",
            "button_pre_venda": "#00BCD4",  # Ciano
            "button_vendas": "#5E35B1",     # Roxo
            "button_sair": "#FF5252",       # Vermelho
            "button_minimizar": "#9E9E9E",  # Cinza
            "button_acoes": "#9E9E9E",      # Cinza
            "button_sidebar_1": "#F44336",  # Vermelho
            "button_sidebar_2": "#9C27B0",  # Roxo
            "button_sidebar_3": "#2196F3",  # Azul
            "button_minus": "#F44336",      # Vermelho
            "button_plus": "#00BCD4",       # Ciano
            "total_label": "#555555",
            "total_valor": "#333333",
            "troco_bg": "#E8EAF6",          # Azul claro
            "troco_fg": "#673AB7",          # Roxo
            "finalizar_bg": "#26A69A",      # Verde
            "finalizar_fg": "#FFFFFF",
            "table_header_bg": "#F5F5F5",
            "table_border": "#EEEEEE",
            "table_row_alt": "#F9F9F9"
        }

        # Aplicar estilo QSS
        self.setStyleSheet(self.get_stylesheet())

        # Widget Central e Layout Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Cabeçalho Superior ---
        header_widget = self.criar_cabecalho_superior()
        main_layout.addWidget(header_widget)

        # --- Corpo Principal (dividido) ---
        corpo_widget = QWidget()
        corpo_layout = QHBoxLayout(corpo_widget)
        corpo_layout.setContentsMargins(10, 5, 10, 10)
        corpo_layout.setSpacing(10)
        main_layout.addWidget(corpo_widget, 1) # Ocupa espaço restante

        # --- Área Esquerda ---
        area_esquerda_widget = self.criar_area_esquerda()
        corpo_layout.addWidget(area_esquerda_widget, 3) # Proporção 3

        # --- Área Direita (Sidebar) ---
        area_direita_widget = self.criar_area_direita()
        area_direita_widget.setObjectName("Sidebar") # Para estilização QSS
        corpo_layout.addWidget(area_direita_widget, 1) # Proporção 1

        # Iniciar relógio
        self.iniciar_relogio()
        
        # Conectar eventos
        self.entry_cod_barras.returnPressed.connect(self.processar_codigo_barras)
        self.entry_valor_recebido.textChanged.connect(self.calcular_troco)
        
        # Configurar para receber o foco e para tela cheia
        self.setFocusPolicy(Qt.StrongFocus)
        self.entry_cod_barras.setFocus()
        self.showFullScreen()

    def get_stylesheet(self):
        # Estilo QSS melhorado baseado na imagem
        return f"""
            QMainWindow {{ background-color: {self.colors['bg_main']}; }}
            QWidget {{ font-family: 'Segoe UI', Arial, sans-serif; }}
            QWidget#Header {{ 
                background-color: {self.colors['header_bg']}; 
                min-height: 40px;
            }}
            QWidget#Sidebar {{ 
                background-color: {self.colors['sidebar_bg']}; 
                border: 1px solid {self.colors['table_border']};
                border-radius: 5px;
            }}
            QLabel#ClockLabel {{ 
                color: {self.colors['header_fg']}; 
                padding: 5px 15px; 
                font-size: 16px; 
                font-weight: bold; 
            }}
            QPushButton#HeaderButton {{ 
                color: {self.colors['header_fg']}; 
                background-color: #555555; 
                border: none; 
                padding: 8px 15px; 
                font-size: 12px;
                border-radius: 3px;
                font-weight: normal;
            }}
            QPushButton#VendasButton {{ 
                background-color: {self.colors['button_vendas']}; 
                padding-left: 25px;
                padding-right: 25px;
            }}
            QPushButton#AcoesButton {{ background-color: {self.colors['button_acoes']}; }}
            QPushButton#SairButton {{ background-color: {self.colors['button_sair']}; }}
            QPushButton#MinimizeButton {{ 
                background-color: {self.colors['button_minimizar']}; 
                color: {self.colors['header_fg']};
                font-weight: bold;
                min-width: 40px;
                min-height: 30px;
                font-size: 16px;
                border-radius: 3px;
            }}
            QPushButton#ExitButton {{ 
                background-color: {self.colors['button_sair']}; 
                color: {self.colors['header_fg']};
                font-weight: bold;
                min-width: 40px;
                min-height: 30px;
                font-size: 16px;
                border-radius: 3px;
            }}
            QPushButton#HeaderButton:hover, QPushButton#MinimizeButton:hover {{ 
                background-color: #666666; 
            }}
            QPushButton#ExitButton:hover {{ background-color: #FF5555; }}
            
            QLabel {{ 
                font-size: 12px; 
                color: #333333; 
            }}
            QLineEdit, QComboBox {{ 
                padding: 8px; 
                border: 1px solid {self.colors['table_border']}; 
                border-radius: 3px; 
                font-size: 12px;
                background-color: #FFFFFF;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: {self.colors['table_border']};
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            QLineEdit:focus, QComboBox:focus {{ 
                border: 1px solid #2196F3; 
            }}
            QTableWidget {{ 
                border: 1px solid {self.colors['table_border']}; 
                gridline-color: {self.colors['table_border']};
                font-size: 12px;
                selection-background-color: #E3F2FD;
                selection-color: #000000;
                alternate-background-color: {self.colors['table_row_alt']};
                background-color: #FFFFFF;
            }}
            QHeaderView::section {{ 
                background-color: {self.colors['table_header_bg']}; 
                padding: 6px; 
                border: 1px solid {self.colors['table_border']}; 
                font-weight: bold; 
                font-size: 12px;
            }}
            QTableWidget::item {{ padding: 8px; }}
            
            QPushButton#SidebarButton1 {{ 
                background-color: {self.colors['button_sidebar_1']}; 
                color: white; 
                font-size: 18px; 
                font-weight: bold; 
                border: none; 
                border-radius: 3px; 
                padding: 10px; 
            }}
            QPushButton#SidebarButton2 {{ 
                background-color: {self.colors['button_sidebar_2']}; 
                color: white; 
                font-size: 18px; 
                font-weight: bold; 
                border: none; 
                border-radius: 3px; 
                padding: 10px; 
            }}
            QPushButton#SidebarButton3 {{ 
                background-color: {self.colors['button_sidebar_3']}; 
                color: white; 
                font-size: 18px; 
                font-weight: bold; 
                border: none; 
                border-radius: 3px; 
                padding: 10px; 
            }}
            QPushButton#SidebarButton1:hover, QPushButton#SidebarButton2:hover, QPushButton#SidebarButton3:hover {{ opacity: 0.9; }}

            QLabel#TotalLabel {{ 
                font-size: 14px; 
                font-weight: bold;
                color: {self.colors['total_label']}; 
            }}
            QLabel#TotalValue {{ 
                font-size: 36px; 
                font-weight: bold; 
                color: {self.colors['total_valor']}; 
                qproperty-alignment: 'AlignRight'; 
            }}
            QWidget#TrocoWidget {{ 
                background-color: {self.colors['troco_bg']}; 
                border-radius: 5px; 
            }}
            QLabel#TrocoLabel {{ 
                font-size: 18px; 
                font-weight: bold; 
                color: {self.colors['troco_fg']}; 
                background-color: transparent;
                qproperty-alignment: 'AlignCenter';
                padding: 12px;
            }}
            QPushButton#FinalizarButton {{ 
                background-color: {self.colors['finalizar_bg']}; 
                color: {self.colors['finalizar_fg']}; 
                font-size: 16px; 
                font-weight: bold; 
                padding: 15px; 
                border: none; 
                border-radius: 3px;
            }}
            QPushButton#FinalizarButton:hover {{ background-color: #2BBBAD; }}
            
            QPushButton#QuantityMinusButton {{ 
                background-color: {self.colors['button_minus']}; 
                color: white; 
                font-weight: bold; 
                border: none; 
                border-radius: 3px; 
                font-size: 14px;
            }}
            QPushButton#QuantityPlusButton {{ 
                background-color: {self.colors['button_plus']}; 
                color: white; 
                font-weight: bold; 
                border: none; 
                border-radius: 3px; 
                font-size: 14px;
            }}
            QLabel#QuantityLabel {{ 
                background-color: white; 
                font-size: 14px; 
                font-weight: bold;
            }}
        """

    def verificar_caixa_ao_iniciar(self):
        """Verifica se existe caixa aberto ao iniciar o PDV"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            caixa_aberto = self.verificar_caixa_aberto()
            
            if not caixa_aberto:
                resposta = QMessageBox.question(
                    self,
                    "Caixa Fechado",
                    "Não há caixa aberto no sistema. Deseja abrir um caixa agora?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes  # Opção padrão é Sim
                )
                
                if resposta == QMessageBox.Yes:
                    # Aqui poderia chamar a função para abrir caixa
                    # Como isso requer mais implementação, apenas mostraremos uma mensagem
                    QMessageBox.information(
                        self,
                        "Informação",
                        "Por favor, use o sistema de controle de caixa para abrir um novo caixa."
                    )
                    # Fechar o PDV, pois não há caixa aberto
                    self.close()
                else:
                    # Usuário optou por não abrir caixa, fechar o PDV
                    self.close()
            else:
                # Caixa está aberto, exibir informação
                QMessageBox.information(
                    self,
                    "Caixa Aberto",
                    f"Caixa #{caixa_aberto['codigo']} está aberto.\n"
                    f"Aberto em: {caixa_aberto['data_abertura']} às {caixa_aberto['hora_abertura']}\n"
                    f"Estação: {caixa_aberto['estacao']}"
                )
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            print(f"Erro ao verificar caixa inicial: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao verificar caixa inicial: {str(e)}")

    def criar_cabecalho_superior(self):
        header_widget = QWidget()
        header_widget.setObjectName("Header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(10)

        self.clock_label = QLabel("00:00:00")
        self.clock_label.setObjectName("ClockLabel")
        header_layout.addWidget(self.clock_label)

        # Botão Lista de Vendas com ícone
        btn_vendas = QPushButton("  Lista de Vendas")
        btn_vendas.setObjectName("HeaderButton")
        btn_vendas.setObjectName("VendasButton")
        btn_vendas.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["history"], "#FFFFFF")))
        btn_vendas.clicked.connect(self.abrir_historico_vendas)
        header_layout.addWidget(btn_vendas)

        header_layout.addStretch(1)

        # Botão Fechar Caixa com nova função
        btn_acoes = QPushButton("Fechar Caixa")
        btn_acoes.setObjectName("HeaderButton")
        btn_acoes.setObjectName("AcoesButton")
        btn_acoes.clicked.connect(self.confirmar_fechar_caixa)  # Nova função
        header_layout.addWidget(btn_acoes)

        header_layout.addStretch(1)  # Espaço antes dos botões de controle

        # Botões maiores para minimizar e sair
        btn_minimizar = QPushButton("_")
        btn_minimizar.setObjectName("MinimizeButton")
        btn_minimizar.setFixedSize(40, 30)  # Aumentado
        btn_minimizar.clicked.connect(self.showMinimized)
        header_layout.addWidget(btn_minimizar)

        btn_sair = QPushButton("X")
        btn_sair.setObjectName("ExitButton")
        btn_sair.setFixedSize(40, 30)  # Aumentado
        btn_sair.clicked.connect(self.close)
        header_layout.addWidget(btn_sair)

        return header_widget

    def verificar_caixa_aberto(self):
        """Verifica se existe um caixa aberto no sistema"""
        try:
            import os
            import sys
            from datetime import datetime
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            # Importar função do banco de dados
            from base.banco import execute_query
            
            # Buscar caixas abertos (sem data de fechamento)
            query = """
            SELECT ID, CODIGO, DATA_ABERTURA, HORA_ABERTURA, ESTACAO
            FROM CAIXA_CONTROLE
            WHERE DATA_FECHAMENTO IS NULL
            ORDER BY DATA_ABERTURA DESC, HORA_ABERTURA DESC
            """
            
            result = execute_query(query)
            
            if result and len(result) > 0:
                # Encontrou caixa aberto
                caixa = {
                    'id': result[0][0],
                    'codigo': result[0][1],
                    'data_abertura': result[0][2],
                    'hora_abertura': result[0][3],
                    'estacao': result[0][4]
                }
                return caixa
            else:
                # Nenhum caixa aberto
                return None
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            print(f"Erro ao verificar caixa aberto: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao verificar caixa aberto: {str(e)}")
            return None

    def confirmar_fechar_caixa(self):
        """Mostra diálogo para confirmar fechamento do caixa"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            # Verificar se existe caixa aberto
            caixa_aberto = self.verificar_caixa_aberto()
            
            if not caixa_aberto:
                QMessageBox.warning(self, "Aviso", "Não há caixa aberto para fechar.")
                return
            
            # Formatar mensagem com informações do caixa
            mensagem = (
                f"Deseja fechar o caixa #{caixa_aberto['codigo']}?\n\n"
                f"Aberto em: {caixa_aberto['data_abertura']} às {caixa_aberto['hora_abertura']}\n"
                f"Estação: {caixa_aberto['estacao']}"
            )
            
            # Exibir diálogo de confirmação
            resposta = QMessageBox.question(
                self,
                "Confirmação",
                mensagem,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Opção padrão é Não
            )
            
            if resposta == QMessageBox.Yes:
                # Fechar o caixa
                self.fechar_caixa_atual(caixa_aberto['id'])
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            print(f"Erro ao confirmar fechamento de caixa: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao confirmar fechamento de caixa: {str(e)}")

    def fechar_caixa_atual(self, id_caixa):
        """Fecha o caixa atual no banco de dados"""
        try:
            import os
            import sys
            from datetime import datetime
            from PyQt5.QtWidgets import QMessageBox
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            # Importar função do banco de dados
            from base.banco import execute_query
            
            # Obter data e hora atual
            agora = datetime.now()
            data_fechamento = agora.strftime("%d/%m/%Y")
            hora_fechamento = agora.strftime("%H:%M:%S")
            
            # Buscar valor de abertura para usar como fechamento (simplesmente como exemplo)
            query_valor = """
            SELECT VALOR_ABERTURA FROM CAIXA_CONTROLE WHERE ID = ?
            """
            result_valor = execute_query(query_valor, (id_caixa,))
            valor_fechamento = result_valor[0][0] if result_valor and len(result_valor) > 0 else 0.0
            
            # Atualizar registro para fechar o caixa
            query_update = """
            UPDATE CAIXA_CONTROLE
            SET DATA_FECHAMENTO = ?,
                HORA_FECHAMENTO = ?,
                VALOR_FECHAMENTO = ?
            WHERE ID = ?
            """
            
            execute_query(query_update, (data_fechamento, hora_fechamento, valor_fechamento, id_caixa))
            
            # Mostrar mensagem de sucesso
            QMessageBox.information(
                self,
                "Sucesso",
                f"Caixa fechado com sucesso!\n\nData: {data_fechamento}\nHora: {hora_fechamento}"
            )
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            print(f"Erro ao fechar caixa: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao fechar caixa: {str(e)}")

    def abrir_historico_vendas(self):
        """Abre a janela de histórico de vendas dos últimos 30 dias"""
        try:
            # Primeiro vamos verificar se o módulo Lista_vendas está acessível
            try:
                # Tentar importação com diferentes estratégias
                try:
                    import Lista_vendas
                    Lista_vendas.abrir_janela_vendas(self)
                    return
                except ImportError:
                    print("Não foi possível importar Lista_vendas diretamente, tentando caminhos alternativos...")
                    
                # Tentar com caminho absoluto
                import sys
                import os
                
                # Adicionar o diretório atual ao path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                sys.path.append(current_dir)
                
                # Tentar importar novamente
                try:
                    import Lista_vendas
                    Lista_vendas.abrir_janela_vendas(self)
                    return
                except ImportError:
                    print("Ainda não foi possível importar Lista_vendas pelo caminho absoluto...")
                
                # Se ainda não conseguiu, mostrar mensagem e usar implementação alternativa
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", 
                                "Não foi possível encontrar o módulo Lista_vendas.py.\n"
                                "Verifique se o arquivo está no diretório correto.")
                
                # Implementação alternativa simples
                self.mostrar_dialogo_vendas_alternativo()
                
            except Exception as inner_e:
                print(f"Erro ao tentar importar Lista_vendas: {inner_e}")
                raise
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", 
                                f"Erro ao abrir o histórico de vendas: {str(e)}\n\n"
                                f"Certifique-se de que o arquivo Lista_vendas.py está no diretório correto.")
    
    def mostrar_dialogo_vendas_alternativo(self):
        """Alternativa simples quando Lista_vendas não está disponível"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem
        from PyQt5.QtCore import Qt, QDate
        
        # Criar uma janela básica
        dialog = QDialog(self)
        dialog.setWindowTitle("Histórico de Vendas (Modo Alternativo)")
        dialog.setMinimumSize(800, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Mensagem informativa
        lbl_info = QLabel("Exibindo histórico simplificado de vendas (módulo Lista_vendas.py não disponível)")
        lbl_info.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(lbl_info)
        
        # Tabela básica
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "DATA", "VALOR", "FORMA PGTO", "STATUS"])
        layout.addWidget(table)
        
        # Tentar buscar algumas vendas recentes
        try:
            from base.banco import execute_query
            from datetime import datetime, timedelta
            
            # Data de 30 dias atrás
            data_limite = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Consulta básica
            query = """
            SELECT ID_VENDA, DATA_VENDA, VALOR_FINAL, FORMA_PAGAMENTO, STATUS
            FROM VENDAS
            WHERE DATA_VENDA >= ?
            ORDER BY DATA_VENDA DESC, HORA_VENDA DESC
            LIMIT 100
            """
            
            vendas = execute_query(query, (data_limite,))
            
            # Preencher a tabela
            for row, venda in enumerate(vendas):
                table.insertRow(row)
                
                # ID
                table.setItem(row, 0, QTableWidgetItem(str(venda[0])))
                
                # DATA
                data_str = venda[1]
                if hasattr(data_str, 'strftime'):
                    data_str = data_str.strftime("%d/%m/%Y")
                elif isinstance(data_str, str) and len(data_str) == 10:
                    data_str = f"{data_str[8:10]}/{data_str[5:7]}/{data_str[0:4]}"
                
                table.setItem(row, 1, QTableWidgetItem(data_str))
                
                # VALOR
                valor = float(venda[2])
                valor_formatado = f"R$ {valor:.2f}".replace('.', ',')
                table.setItem(row, 2, QTableWidgetItem(valor_formatado))
                
                # FORMA PAGAMENTO
                table.setItem(row, 3, QTableWidgetItem(str(venda[3])))
                
                # STATUS
                table.setItem(row, 4, QTableWidgetItem(str(venda[4])))
        
        except Exception as e:
            lbl_erro = QLabel(f"Erro ao buscar vendas: {str(e)}")
            lbl_erro.setStyleSheet("color: red;")
            layout.addWidget(lbl_erro)
        
        # Botão para fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(dialog.close)
        layout.addWidget(btn_fechar)
        
        dialog.exec_()

    def criar_area_esquerda(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # --- Frame Superior Esquerdo (Código de Barras e Pesquisa) ---
        top_left_frame = QFrame()
        top_left_layout = QGridLayout(top_left_frame)
        top_left_layout.setContentsMargins(0, 0, 0, 10)
        top_left_layout.setSpacing(10)

        # Ícone do olho + texto para código de barras
        barcode_layout = QHBoxLayout()
        lbl_eye_icon = QLabel()
        eye_renderer = QSvgRenderer(bytearray(SVG_ICONS["eye"], encoding='utf-8'))
        eye_pixmap = QPixmap(24, 24)
        eye_pixmap.fill(Qt.transparent)
        eye_painter = QPainter(eye_pixmap)
        eye_renderer.render(eye_painter)
        eye_painter.end()
        lbl_eye_icon.setPixmap(eye_pixmap)
        
        lbl_leitor = QLabel("UTILIZE O LEITOR PARA LER O CÓDIGO DE BARRAS")
        lbl_leitor.setStyleSheet("font-weight: bold;")
        barcode_layout.addWidget(lbl_eye_icon)
        barcode_layout.addWidget(lbl_leitor)
        barcode_layout.addStretch()
        top_left_layout.addLayout(barcode_layout, 0, 0, 1, 2)

        # Campo de código de barras com ícone - MODIFICADO PARA SER MAIOR
        barcode_input_layout = QHBoxLayout()
        barcode_icon = QLabel()
        barcode_renderer = QSvgRenderer(bytearray(SVG_ICONS["barcode"], encoding='utf-8'))
        barcode_pixmap = QPixmap(24, 24)
        barcode_pixmap.fill(Qt.transparent)
        barcode_painter = QPainter(barcode_pixmap)
        barcode_renderer.render(barcode_painter)
        barcode_painter.end()
        barcode_icon.setPixmap(barcode_pixmap)
        
        self.entry_cod_barras = QLineEdit()
        self.entry_cod_barras.setPlaceholderText("Código de Barras")
        # Aumentar tamanho do campo de código de barras
        self.entry_cod_barras.setMinimumWidth(250)  # Definir largura mínima maior
        self.entry_cod_barras.setFixedHeight(35)    # Definir altura maior
        self.entry_cod_barras.setFont(QFont("Segoe UI", 12))  # Fonte maior para melhor visibilidade
        
        barcode_input_layout.addWidget(barcode_icon)
        barcode_input_layout.addWidget(self.entry_cod_barras)
        top_left_layout.addLayout(barcode_input_layout, 1, 0)

        # Layout de pesquisa melhorado
        search_layout = QHBoxLayout()
        
        # Ícone de pesquisa + combobox
        search_combo_layout = QHBoxLayout()
        search_icon = QLabel()
        search_renderer = QSvgRenderer(bytearray(SVG_ICONS["search"], encoding='utf-8'))
        search_pixmap = QPixmap(20, 20)
        search_pixmap.fill(Qt.transparent)
        search_painter = QPainter(search_pixmap)
        search_renderer.render(search_painter)
        search_painter.end()
        search_icon.setPixmap(search_pixmap)
        
        self.combo_pesquisa = QComboBox()
        self.combo_pesquisa.addItem("Pesquisar por produtos")
        self.combo_pesquisa.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_combo_layout.addWidget(search_icon)
        search_combo_layout.addWidget(self.combo_pesquisa)
        search_layout.addLayout(search_combo_layout, 1)  # Proporção maior

        # Campo de preço
        self.entry_preco_unit = QLineEdit("0,00")
        self.entry_preco_unit.setAlignment(Qt.AlignRight)
        self.entry_preco_unit.setFixedWidth(80)
        search_layout.addWidget(self.entry_preco_unit)

        # Campo de quantidade
        self.entry_qtd_pesquisa = QLineEdit("1")
        self.entry_qtd_pesquisa.setAlignment(Qt.AlignCenter)
        self.entry_qtd_pesquisa.setFixedWidth(50)
        search_layout.addWidget(self.entry_qtd_pesquisa)
        
        top_left_layout.addLayout(search_layout, 1, 1)
        top_left_layout.setColumnStretch(1, 1)  # Coluna da pesquisa expande

        left_layout.addWidget(top_left_frame)

        # --- Tabela de Itens (sem exemplos) ---
        self.table_itens = QTableWidget()
        self.table_itens.setColumnCount(5)
        self.table_itens.setHorizontalHeaderLabels(["ITEM", "ID", "PRODUTO", "QTD", "VALOR"])
        self.table_itens.verticalHeader().setVisible(False)
        self.table_itens.setAlternatingRowColors(True)
        self.table_itens.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_itens.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_itens.setStyleSheet("QTableWidget { border: 1px solid #EEEEEE; }")
        self.table_itens.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: #F5F5F5; padding: 6px; }"
        )

        # Ajustar colunas
        header = self.table_itens.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ITEM
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # PRODUTO
        header.setSectionResizeMode(3, QHeaderView.Fixed)             # QTD
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # VALOR
        
        # Definir larguras fixas
        self.table_itens.setColumnWidth(3, 58)  # Largura fixa da coluna QTD
        self.table_itens.setColumnWidth(4, 100)

        left_layout.addWidget(self.table_itens, 1)

        # --- Rodapé Esquerdo (REESCRITO COMPLETAMENTE) ---
        bottom_left_frame = QFrame()
        bottom_left_layout = QHBoxLayout(bottom_left_frame)
        bottom_left_layout.setContentsMargins(5, 5, 5, 5)

        # Desconto com botão de edição
        desconto_layout = QHBoxLayout()
        self.lbl_desconto = QLabel("Desconto: R$ 0,00")
        desconto_layout.addWidget(self.lbl_desconto)
        
        btn_editar_desconto = QPushButton()
        btn_editar_desconto.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["edit"])))
        btn_editar_desconto.setIconSize(QSize(16, 16))
        btn_editar_desconto.setFixedSize(24, 24)
        btn_editar_desconto.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 12px;
            }
        """)
        btn_editar_desconto.setCursor(QCursor(Qt.PointingHandCursor))
        btn_editar_desconto.setToolTip("Editar desconto")
        btn_editar_desconto.clicked.connect(self.editar_desconto)
        desconto_layout.addWidget(btn_editar_desconto)
        bottom_left_layout.addLayout(desconto_layout)
        
        # Acréscimo com botão de edição
        acrescimo_layout = QHBoxLayout()
        self.lbl_acrescimo = QLabel("Acréscimo: R$ 0,00")
        acrescimo_layout.addWidget(self.lbl_acrescimo)
        
        btn_editar_acrescimo = QPushButton()
        btn_editar_acrescimo.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["edit"])))
        btn_editar_acrescimo.setIconSize(QSize(16, 16))
        btn_editar_acrescimo.setFixedSize(24, 24)
        btn_editar_acrescimo.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 12px;
            }
        """)
        btn_editar_acrescimo.setCursor(QCursor(Qt.PointingHandCursor))
        btn_editar_acrescimo.setToolTip("Editar acréscimo")
        btn_editar_acrescimo.clicked.connect(self.editar_acrescimo)
        acrescimo_layout.addWidget(btn_editar_acrescimo)
        bottom_left_layout.addLayout(acrescimo_layout)
        
        # Adicionar espaço expansível - remove a "Lista de Preços"
        bottom_left_layout.addStretch(1)
        
        # A "Lista de Preços" foi removida completamente
        
        left_layout.addWidget(bottom_left_frame)

        return left_widget

    def editar_desconto(self):
        """Abre um diálogo para editar o valor do desconto"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        # Obter o total atual da venda
        total_text = self.lbl_total_valor.text().replace('.', '').replace(',', '.')
        total_venda = float(total_text) if total_text else 0.0
        
        if total_venda <= 0:
            QMessageBox.warning(self, "Aviso", "Não é possível aplicar desconto. Não há itens no carrinho.")
            return
        
        # Valor inicial (o atual desconto ou 0)
        valor_atual = self.valor_desconto
        
        # Obter novo valor do usuário
        desconto, ok = QInputDialog.getDouble(
            self,
            "Desconto",
            "Digite o valor do desconto (R$):",
            valor_atual,
            0.0,  # Mínimo
            total_venda,  # Máximo - não pode descontar mais que o total
            2  # Precisão decimal
        )
        
        if ok:
            # Atualizar valor do desconto
            self.valor_desconto = desconto
            # Atualizar label
            desconto_formatado = f"{desconto:.2f}".replace('.', ',')
            self.lbl_desconto.setText(f"Desconto: R$ {desconto_formatado}")
            # Recalcular o total
            self.atualizar_total()

    def editar_acrescimo(self):
        """Abre um diálogo para editar o valor do acréscimo"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        # Obter o total atual da venda
        total_text = self.lbl_total_valor.text().replace('.', '').replace(',', '.')
        total_venda = float(total_text) if total_text else 0.0
        
        if total_venda <= 0:
            QMessageBox.warning(self, "Aviso", "Não é possível aplicar acréscimo. Não há itens no carrinho.")
            return
        
        # Valor inicial (o atual acréscimo ou 0)
        valor_atual = self.valor_acrescimo
        
        # Obter novo valor do usuário
        acrescimo, ok = QInputDialog.getDouble(
            self,
            "Acréscimo",
            "Digite o valor do acréscimo (R$):",
            valor_atual,
            0.0,  # Mínimo
            1000000.0,  # Máximo arbitrário
            2  # Precisão decimal
        )
        
        if ok:
            # Atualizar valor do acréscimo
            self.valor_acrescimo = acrescimo
            # Atualizar label
            acrescimo_formatado = f"{acrescimo:.2f}".replace('.', ',')
            self.lbl_acrescimo.setText(f"Acréscimo: R$ {acrescimo_formatado}")
            # Recalcular o total
            self.atualizar_total()

    def processar_codigo_barras(self):
        """Processa o código de barras quando Enter é pressionado"""
        codigo = self.entry_cod_barras.text().strip()
        if codigo:
            self.buscar_produto_por_codigo_barras(codigo)
    
    def buscar_produto_por_codigo_barras(self, codigo_barras):
        """Busca um produto pelo código de barras no banco de dados"""
        try:
            # Primeiro, vamos normalizar o código de barras (remover espaços e qualquer caractere não numérico)
            codigo_limpo = ''.join(c for c in codigo_barras if c.isdigit())
            
            # Imprimir para debug
            print(f"Buscando produto com código: {codigo_barras}, código limpo: {codigo_limpo}")
            
            # Importar funções do banco apenas quando necessário para evitar erros de importação circular
            try:
                from base.banco import buscar_produto_por_barras, buscar_produto_por_codigo
            except ImportError as e:
                print(f"Erro ao importar funções do banco: {e}")
                # Se não conseguir importar do caminho base.banco, tenta importar direto
                try:
                    import sys
                    import os
                    # Adicionar o diretório pai ao path para buscar os módulos
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from base.banco import buscar_produto_por_barras, buscar_produto_por_codigo
                except ImportError as e2:
                    print(f"Erro ao importar módulos alternativos: {e2}")
                    # Define funções vazias para evitar erros
                    def buscar_produto_por_barras(codigo): 
                        print(f"Função vazia chamada com: {codigo}")
                        return None
                    def buscar_produto_por_codigo(codigo): 
                        print(f"Função vazia chamada com: {codigo}")
                        return None
            
            # Tentar buscar pelo código de barras limpo
            produto = buscar_produto_por_barras(codigo_limpo)
            print(f"Resultado busca por código de barras: {produto}")
            
            # Se não encontrou, tentar buscar pelo código do produto
            if not produto:
                result = buscar_produto_por_codigo(codigo_limpo)
                print(f"Resultado busca por código: {result}")
                
                # Se ainda não encontrou, tente com o código original
                if not result and codigo_limpo != codigo_barras:
                    result = buscar_produto_por_codigo(codigo_barras)
                    print(f"Resultado busca por código original: {result}")
                
                if result:
                    produto = {
                        "id": result[0],
                        "codigo": result[1],
                        "nome": result[2],
                        "barras": result[3],
                        "marca": result[4],
                        "grupo": result[5],
                        "preco_compra": result[6],
                        "preco_venda": result[7],
                        "estoque": result[8]
                    }
            
            # Se encontrou o produto, atualizar a UI
            if produto:
                # Atualizar UI com os dados do produto
                self.adicionar_produto_ao_carrinho(produto)
                # Limpar o campo de código de barras
                self.entry_cod_barras.clear()
                # Focar novamente no campo para a próxima leitura
                self.entry_cod_barras.setFocus()
                return True
            else:
                # Produto não encontrado - mostrar mensagem mais detalhada
                from PyQt5.QtWidgets import QMessageBox
                
                # Criar mensagem amigável
                msg = QMessageBox()
                msg.setWindowTitle("Produto não encontrado")
                msg.setText(f"O produto com código {codigo_barras} não foi encontrado no cadastro.")
                msg.setIcon(QMessageBox.Warning)
                
                # Adicionar botão para cadastrar produto
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Yes)
                msg.setButtonText(QMessageBox.Yes, "Cadastrar Produto")
                
                # Executar a caixa de diálogo
                resposta = msg.exec_()
                
                # Verificar se o usuário deseja cadastrar o produto
                if resposta == QMessageBox.Yes:
                    self.abrir_cadastro_produto(codigo_barras)
                
                # Limpar o campo e focar para nova leitura
                self.entry_cod_barras.clear()
                self.entry_cod_barras.setFocus()
                return False
                    
        except Exception as e:
            print(f"Erro ao buscar produto: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao buscar produto: {str(e)}")
            return False

    def abrir_cadastro_produto(self, codigo_barras=None):
        """Abre a tela de cadastro de produto, opcionalmente preenchendo o código de barras"""
        try:
            # Aqui você pode chamar a tela de cadastro de produtos
            # Se você tiver um módulo para isso, pode importá-lo aqui
            
            try:
                # Tentar importar a tela de cadastro
                import cadastro_produtos
                cadastro_produtos.abrir_tela_cadastro(codigo_barras, self)
            except ImportError:
                # Se não conseguir importar, pelo menos mostrar uma mensagem
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Cadastro de Produto", 
                                    f"O produto com código {codigo_barras} precisa ser cadastrado.\n"
                                    f"Por favor, use a tela de cadastro de produtos.")
        except Exception as e:
            print(f"Erro ao abrir cadastro de produto: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir cadastro de produto: {str(e)}")

    def adicionar_produto_ao_carrinho(self, produto):
        """Adiciona o produto encontrado à tabela de itens"""
        # Obter o próximo número de item
        proximo_item = self.table_itens.rowCount() + 1
        
        # Obter informações do produto
        id_produto = produto.get("codigo", "")
        nome = produto.get("nome", "")
        preco = float(produto.get("preco_venda", 0))
        
        # Formatar nome do produto (código + nome)
        nome_formatado = f"{id_produto} - {nome}"
        
        # Adicionar à tabela
        self.add_item_tabela(proximo_item, id_produto, nome_formatado, 1, preco)
        
        # Atualizar o total
        self.atualizar_total()
        
        # Focar novamente no campo de código de barras para o próximo produto
        self.entry_cod_barras.setFocus()

    def add_item_tabela(self, item, id_prod, produto, qtd, valor):
        row_position = self.table_itens.rowCount()
        self.table_itens.insertRow(row_position)

        # Item
        item_widget = QTableWidgetItem(str(item))
        item_widget.setTextAlignment(Qt.AlignCenter)
        self.table_itens.setItem(row_position, 0, item_widget)
        
        # ID
        id_widget = QTableWidgetItem(str(id_prod))
        id_widget.setTextAlignment(Qt.AlignCenter)
        self.table_itens.setItem(row_position, 1, id_widget)
        
        # Produto
        self.table_itens.setItem(row_position, 2, QTableWidgetItem(produto))
        
        # Quantidade (widget ultra-compacto)
        quantity_layout = QHBoxLayout()
        quantity_layout.setContentsMargins(0, 0, 0, 0)
        quantity_layout.setSpacing(0)  # Sem espaçamento
        
        quantity_widget = QWidget()
        quantity_widget.setMaximumWidth(60)  # Limitar largura máxima
        quantity_widget.setLayout(quantity_layout)
        
        # Botão "-" super compacto
        btn_minus = QPushButton("-")
        btn_minus.setFixedSize(16, 16)  # Reduzido para 16x16
        btn_minus.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 1px;
                font-size: 9px;
                padding: 0px;
                margin: 0px;
            }
        """)
        btn_minus.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Label de valor ainda mais compacto
        lbl_value = QLabel(str(qtd))
        lbl_value.setFixedWidth(16)  # Reduzido para 16
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet("""
            QLabel {
                background-color: white;
                font-size: 10px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Botão "+" super compacto
        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(16, 16)  # Reduzido para 16x16
        btn_plus.setStyleSheet("""
            QPushButton {
                background-color: #00BCD4;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 1px;
                font-size: 9px;
                padding: 0px;
                margin: 0px;
            }
        """)
        btn_plus.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Adicionar ao layout
        quantity_layout.addWidget(btn_minus)
        quantity_layout.addWidget(lbl_value)
        quantity_layout.addWidget(btn_plus)
        
        # Armazenar o valor atual
        quantity_widget.value = qtd
        
        # Funções para manipular o valor
        def increase_value():
            quantity_widget.value += 1
            lbl_value.setText(str(quantity_widget.value))
            self.atualizar_total()
        
        def decrease_value():
            if quantity_widget.value == 1:
                # Confirmar remoção
                from PyQt5.QtWidgets import QMessageBox
                resposta = QMessageBox.question(
                    self, 
                    "Remover Produto",
                    "Deseja remover esse produto?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if resposta == QMessageBox.Yes:
                    # Remover a linha
                    self.table_itens.removeRow(row_position)
                    self.atualizar_total()
            else:
                # Diminuir o valor
                quantity_widget.value -= 1
                lbl_value.setText(str(quantity_widget.value))
                self.atualizar_total()
        
        # Conectar sinais
        btn_plus.clicked.connect(increase_value)
        btn_minus.clicked.connect(decrease_value)
        
        # Função para obter o valor
        def get_value():
            return quantity_widget.value
        
        # Adicionar método para acessar o valor
        quantity_widget.get_value = get_value
        
        # Adicionar à tabela
        self.table_itens.setCellWidget(row_position, 3, quantity_widget)
        
        # Valor
        valor_str = f"R$ {valor:.2f}".replace('.', ',')
        valor_item = QTableWidgetItem(valor_str)
        valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_itens.setItem(row_position, 4, valor_item)

    def criar_area_direita(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        # --- Botões Superiores Direita com SVG ---
        top_right_layout = QHBoxLayout()
        
        # Botão 1: Listar Clientes
        btn_clientes = QPushButton()
        btn_clientes.setObjectName("SidebarButton1")
        btn_clientes.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["user"], "#FFFFFF")))
        btn_clientes.setIconSize(QSize(24, 24))
        btn_clientes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_clientes.setCursor(QCursor(Qt.PointingHandCursor))
        btn_clientes.setToolTip("Listar Clientes")
        btn_clientes.clicked.connect(self.listar_clientes)
        top_right_layout.addWidget(btn_clientes)
        
        # Botão 2: Listar Produtos
        btn_produtos = QPushButton()
        btn_produtos.setObjectName("SidebarButton2")
        btn_produtos.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["list"], "#FFFFFF")))
        btn_produtos.setIconSize(QSize(24, 24))
        btn_produtos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_produtos.setCursor(QCursor(Qt.PointingHandCursor))
        btn_produtos.setToolTip("Listar Produtos")
        btn_produtos.clicked.connect(self.listar_produtos)
        top_right_layout.addWidget(btn_produtos)
        
        # O terceiro botão foi removido
        
        right_layout.addLayout(top_right_layout)

        right_layout.addStretch(1)  # Empurra o resto para baixo

        # --- Total ---
        lbl_total_texto = QLabel("TOTAL R$:")
        lbl_total_texto.setObjectName("TotalLabel")
        right_layout.addWidget(lbl_total_texto)

        self.lbl_total_valor = QLabel("0,00")
        self.lbl_total_valor.setObjectName("TotalValue")
        right_layout.addWidget(self.lbl_total_valor)

        # --- Forma de Pagamento com todas as opções da imagem ---
        lbl_forma_pagamento = QLabel("Forma de Pagamento")
        lbl_forma_pagamento.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(lbl_forma_pagamento)
        
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItem("Selecione o Tipo de pagamento")
        self.combo_pagamento.addItem("01 - Dinheiro")
        self.combo_pagamento.addItem("02 - Cheque")
        self.combo_pagamento.addItem("03 - Cartão de Crédito")
        self.combo_pagamento.addItem("04 - Cartão de Débito")
        self.combo_pagamento.addItem("05 - Crédito Loja")
        self.combo_pagamento.addItem("06 - Crediário")
        self.combo_pagamento.addItem("10 - Vale Alimentação")
        self.combo_pagamento.addItem("11 - Vale Refeição")
        self.combo_pagamento.addItem("12 - Vale Presente")
        self.combo_pagamento.addItem("13 - Vale Combustível")
        self.combo_pagamento.addItem("14 - Duplicata Mercantil")
        self.combo_pagamento.addItem("15 - Boleto Bancário")
        self.combo_pagamento.addItem("16 - Depósito Bancário")
        self.combo_pagamento.addItem("17 - Pagamento Instantâneo (PIX)")
        self.combo_pagamento.addItem("90 - Sem pagamento")
        self.combo_pagamento.addItem("99 - Outros")
        
        self.combo_pagamento.setCurrentIndex(0)  # Iniciar com "Selecione o Tipo de pagamento"
        self.combo_pagamento.currentIndexChanged.connect(self.atualizar_layout_pagamento)
        
        right_layout.addWidget(self.combo_pagamento)

        # --- Valor Recebido ---
        self.lbl_valor_recebido = QLabel("Valor Recebido")
        self.lbl_valor_recebido.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(self.lbl_valor_recebido)
        
        self.entry_valor_recebido = QLineEdit()
        self.entry_valor_recebido.setPlaceholderText("R$ 0,00")
        self.entry_valor_recebido.setAlignment(Qt.AlignRight)
        self.entry_valor_recebido.textChanged.connect(self.calcular_troco)
        right_layout.addWidget(self.entry_valor_recebido)

        # --- Troco ---
        self.troco_widget = QWidget()
        self.troco_widget.setObjectName("TrocoWidget")
        troco_layout = QVBoxLayout(self.troco_widget)
        troco_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_troco = QLabel("Troco R$ 0,00")
        self.lbl_troco.setObjectName("TrocoLabel")
        troco_layout.addWidget(self.lbl_troco)
        
        right_layout.addWidget(self.troco_widget)
        
        # Inicialmente oculta o widget de troco (até que a forma de pagamento adequada seja selecionada)
        self.troco_widget.setVisible(False)
        self.lbl_valor_recebido.setVisible(False)
        self.entry_valor_recebido.setVisible(False)

        # --- Botão Finalizar com ícone SVG ---
        self.btn_finalizar = QPushButton("Finalizar R$ 0,00")
        self.btn_finalizar.setObjectName("FinalizarButton")
        check_icon = self.create_svg_icon(SVG_ICONS["check"], "#FFFFFF")
        self.btn_finalizar.setIcon(QIcon(check_icon))
        self.btn_finalizar.setIconSize(QSize(24, 24))
        self.btn_finalizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_finalizar.clicked.connect(self.finalizar_venda_com_cupom)
        right_layout.addWidget(self.btn_finalizar)

        return right_widget


    # 2. Adicionar o método para atualizar o layout conforme a forma de pagamento escolhida

    def atualizar_layout_pagamento(self, index):
        """Atualiza o layout baseado na forma de pagamento selecionada"""
        if index <= 0:
            # Nenhuma forma de pagamento selecionada ou "Selecione o Tipo de pagamento"
            self.lbl_valor_recebido.setVisible(False)
            self.entry_valor_recebido.setVisible(False)
            self.troco_widget.setVisible(False)
            return
        
        forma_pagamento = self.combo_pagamento.currentText()
        
        # Formas de pagamento onde o valor recebido é relevante (e pode haver troco)
        formas_com_valor_recebido = ["01 - Dinheiro"]
        
        # Formas de pagamento onde o valor recebido é relevante mas sem troco
        formas_sem_troco = ["02 - Cheque", "17 - Pagamento Instantâneo (PIX)"]
        
        # Mostrar/ocultar elementos com base na forma de pagamento
        if forma_pagamento in formas_com_valor_recebido:
            self.lbl_valor_recebido.setVisible(True)
            self.entry_valor_recebido.setVisible(True)
            self.troco_widget.setVisible(True)
            self.calcular_troco()  # Atualizar troco
        elif forma_pagamento in formas_sem_troco:
            self.lbl_valor_recebido.setVisible(True)
            self.entry_valor_recebido.setVisible(True)
            self.troco_widget.setVisible(False)
            self.entry_valor_recebido.clear()  # Limpar valor recebido
        else:
            # Outras formas de pagamento não precisam de valor recebido nem troco
            self.lbl_valor_recebido.setVisible(False)
            self.entry_valor_recebido.setVisible(False)
            self.troco_widget.setVisible(False)
            self.entry_valor_recebido.clear()  # Limpar valor recebido


    # 3. Melhorar o método calcular_troco para ser mais robusto

    def calcular_troco(self):
        """Calcula o troco com base no valor recebido e total da venda"""
        try:
            # Verificar se a forma de pagamento é dinheiro
            forma_pagamento = self.combo_pagamento.currentText()
            if forma_pagamento != "01 - Dinheiro":
                self.troco_widget.setVisible(False)
                return
            
            # Obter o total da venda
            total_text = self.lbl_total_valor.text().replace('.', '').replace(',', '.')
            total = float(total_text) if total_text else 0.0
            
            # Verificar se há itens na venda
            if total <= 0:
                self.troco_widget.setVisible(False)
                return
            
            # Obter o valor recebido
            valor_recebido_text = self.entry_valor_recebido.text().replace('R$', '').replace('.', '').replace(',', '.')
            
            # Se valor recebido estiver vazio, não mostrar troco
            if not valor_recebido_text.strip():
                self.troco_widget.setVisible(False)
                return
                
            valor_recebido = float(valor_recebido_text) if valor_recebido_text else 0.0
            
            # Calcular o troco
            troco = valor_recebido - total
            
            # Atualizar o widget de troco
            self.troco_widget.setVisible(True)
            
            # Formatar e exibir o troco
            troco_formatado = f"{troco:.2f}".replace('.', ',')
            
            # Se o troco for negativo, significa que falta dinheiro
            if troco < 0:
                valor_faltante = abs(troco)
                valor_faltante_formatado = f"{valor_faltante:.2f}".replace('.', ',')
                self.lbl_troco.setText(f"Faltam R$ {valor_faltante_formatado}")
                self.lbl_troco.setStyleSheet("color: #FF5252; font-size: 18px; font-weight: bold; background-color: transparent; qproperty-alignment: 'AlignCenter'; padding: 12px;")
            else:
                self.lbl_troco.setText(f"Troco R$ {troco_formatado}")
                self.lbl_troco.setStyleSheet("color: #673AB7; font-size: 18px; font-weight: bold; background-color: transparent; qproperty-alignment: 'AlignCenter'; padding: 12px;")
            
            # Atualizar o texto do botão finalizar
            total_formatado = f"{total:.2f}".replace('.', ',')
            self.btn_finalizar.setText(f"Finalizar R$ {total_formatado}")
            
        except (ValueError, TypeError) as e:
            # Em caso de erro de conversão, ocultar o troco
            self.troco_widget.setVisible(False)
        except Exception as e:
            print(f"Erro ao calcular troco: {e}")
            self.troco_widget.setVisible(False)

    def finalizar_venda_com_cupom(self):
        """
        Método focado em abrir a janela de seleção de cupom e depois finalizar a venda.
        """
        try:
            # Obter o total da venda
            total_text = self.lbl_total_valor.text().replace('.', '').replace(',', '.')
            total = float(total_text) if total_text else 0.0
            
            if total <= 0:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "Não há itens para finalizar a venda.")
                return
            
            # Obter a forma de pagamento
            indice_pagamento = self.combo_pagamento.currentIndex()
            if indice_pagamento <= 0:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "Selecione uma forma de pagamento.")
                return
                    
            forma_pagamento = self.combo_pagamento.currentText()
            
            # Validar pagamentos em dinheiro
            if forma_pagamento == "01 - Dinheiro":
                valor_recebido_text = self.entry_valor_recebido.text().replace('R$', '').replace('.', '').replace(',', '.')
                
                if not valor_recebido_text.strip():
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Aviso", "Digite o valor recebido em dinheiro.")
                    return
                    
                valor_recebido = float(valor_recebido_text) if valor_recebido_text else 0.0
                
                if valor_recebido < total:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Aviso", "O valor recebido é menor que o total da venda.")
                    return
            
            # Formas que exigem valor recebido
            formas_com_valor = ["01 - Dinheiro", "02 - Cheque", "17 - Pagamento Instantâneo (PIX)"]
            
            if forma_pagamento in formas_com_valor and not self.entry_valor_recebido.text().strip():
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", f"Digite o valor recebido para pagamento com {forma_pagamento}.")
                return
            
            # Obter itens da venda
            itens = []
            for row in range(self.table_itens.rowCount()):
                item = {
                    'id_produto': self.table_itens.item(row, 1).text(),
                    'produto': self.table_itens.item(row, 2).text(),
                    'quantidade': self.table_itens.cellWidget(row, 3).get_value(),
                    'valor_unitario': self.table_itens.item(row, 4).text().replace('R$ ', '').replace(',', '.')
                }
                itens.append(item)
            
            # ETAPA CRUCIAL: Abrir o diálogo de cupom fiscal
            # Usando importação explícita para depuração
            print("\n==== ABRINDO DIÁLOGO DE SELEÇÃO DE CUPOM ====")
            
            # Importação feita dentro da função
            try:
                import os
                import sys
                
                # Adicionar o diretório atual ao path do Python
                # Isso garante que o arquivo cupom_fiscal.py será encontrado
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                    print(f"Adicionado diretório ao path: {current_dir}")
                    
                # Importar o módulo (será procurado no diretório atual)
                import cupom_fiscal
                print("✅ Módulo cupom_fiscal importado com sucesso!")
                
                # Chamar a função para exibir o diálogo
                print(f"Chamando cupom_fiscal.solicitar_tipo_cupom com total={total}")
                tipo_cupom, cpf = cupom_fiscal.solicitar_tipo_cupom(total, self)
                
                print(f"Resultado: tipo_cupom={tipo_cupom}, cpf={cpf}")
                
                # Se o usuário cancelou, interromper o processo
                if tipo_cupom is None:
                    print("Operação cancelada pelo usuário.")
                    return
                
                # Se chegou aqui, temos um cupom selecionado!
                # Agora finalizar a venda no banco de dados
                print(f"Registrando venda com cupom: {tipo_cupom}, CPF: {cpf}")
                id_venda = self.registrar_venda_no_banco(total, forma_pagamento, itens, tipo_cupom, cpf)
                
                # Opcional: imprimir o cupom
                if hasattr(self, 'imprimir_cupom'):
                    self.imprimir_cupom(id_venda, tipo_cupom, cpf)
                
                # Limpar a venda
                self.limpar_venda()
                
                # Mostrar mensagem de sucesso
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Sucesso", f"Venda #{id_venda} finalizada com sucesso!")
                
            except ImportError as e:
                from PyQt5.QtWidgets import QMessageBox
                print(f"ERRO DE IMPORTAÇÃO: {e}")
                QMessageBox.critical(self, "Erro", f"Não foi possível importar o módulo cupom_fiscal. Erro: {str(e)}\n\nVerifique se o arquivo cupom_fiscal.py está no mesmo diretório que este programa.")
                return
                
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                print(f"ERRO GERAL: {e}")
                import traceback
                traceback.print_exc()
                
                # Perguntar se deseja continuar sem o cupom
                resposta = QMessageBox.question(
                    self,
                    "Erro na Seleção de Cupom",
                    f"Ocorreu um erro ao selecionar o tipo de cupom: {str(e)}\n\nDeseja continuar sem a seleção de cupom?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if resposta == QMessageBox.Yes:
                    # Continuar com valores padrão
                    id_venda = self.registrar_venda_no_banco(total, forma_pagamento, itens, "NAO_FISCAL", "")
                    self.limpar_venda()
                    QMessageBox.information(self, "Sucesso", f"Venda #{id_venda} finalizada com sucesso (sem cupom)!")
                else:
                    return
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            print(f"ERRO NA FINALIZAÇÃO: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda: {str(e)}")

    def imprimir_cupom(self, id_venda, tipo_cupom, cpf):
        """Imprime o cupom fiscal ou não fiscal e gera um PDF"""
        try:
            print(f"\n===== IMPRIMINDO CUPOM =====")
            print(f"ID da Venda: {id_venda}")
            print(f"Tipo de Cupom: {tipo_cupom}")
            print(f"CPF: {cpf if cpf else 'Não informado'}")
            
            # Importar o gerador de cupom (tentar importação local primeiro)
            try:
                import os
                import sys
                import datetime
                
                # Adicionar diretório atual ao path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                
                # Importar o gerador de cupom
                try:
                    from gerador_cupom import gerar_cupom_pdf
                    print("✅ Módulo gerador_cupom importado com sucesso!")
                except ImportError:
                    # Definir função inline caso o arquivo não exista
                    print("⚠️ Módulo gerador_cupom não encontrado. Usando função inline.")
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.units import mm
                    import datetime
                    import os
                    import random
                    
                    def gerar_cupom_pdf(id_venda, tipo_cupom, cpf, data_venda, itens, total, forma_pagamento, 
                                dir_saida="cupons", nome_empresa="MB SISTEMA", 
                                cnpj="36.920.085/0001-73"):
                        """Versão simplificada da função de geração de cupom"""
                        # Criar diretório de saída
                        if not os.path.exists(dir_saida):
                            os.makedirs(dir_saida)
                        
                        # Nome do arquivo
                        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        nome_arquivo = f"cupom_{tipo_cupom}_{id_venda}_{timestamp}.pdf"
                        caminho_arquivo = os.path.join(dir_saida, nome_arquivo)
                        
                        # Tamanho do papel
                        largura = 80 * mm
                        altura = 180 * mm
                        
                        # Criar PDF
                        c = canvas.Canvas(caminho_arquivo, pagesize=(largura, altura))
                        
                        # Conteúdo básico
                        c.setFont("Helvetica-Bold", 12)
                        c.drawCentredString(largura/2, altura - 15*mm, nome_empresa)
                        
                        c.setFont("Helvetica", 8)
                        c.drawCentredString(largura/2, altura - 25*mm, f"CNPJ: {cnpj}")
                        
                        c.setFont("Helvetica-Bold", 10)
                        if tipo_cupom == "NAO_FISCAL":
                            c.drawCentredString(largura/2, altura - 35*mm, "SEM VALOR FISCAL")
                            c.setFont("Helvetica", 8)
                            c.drawCentredString(largura/2, altura - 40*mm, "Documento emitido em ambiente de homologação")
                        elif tipo_cupom == "FISCAL":
                            c.drawCentredString(largura/2, altura - 35*mm, "CUPOM FISCAL")
                        else:
                            c.drawCentredString(largura/2, altura - 35*mm, "COMPROVANTE DE CRÉDITO")
                        
                        c.setFont("Helvetica", 8)
                        c.drawString(10*mm, altura - 55*mm, f"Venda #{id_venda}")
                        c.drawString(10*mm, altura - 60*mm, f"Data: {data_venda.strftime('%d/%m/%Y %H:%M:%S')}")
                        
                        if cpf:
                            c.drawString(10*mm, altura - 65*mm, f"CPF: {cpf}")
                        else:
                            c.drawString(10*mm, altura - 65*mm, "CONSUMIDOR NÃO IDENTIFICADO")
                        
                        c.drawString(10*mm, altura - 75*mm, f"Total: R$ {total:.2f}".replace('.', ','))
                        c.drawString(10*mm, altura - 80*mm, f"Pagamento: {forma_pagamento}")
                        
                        c.save()
                        return caminho_arquivo
                
                # Obter os itens da venda
                itens = []
                total = 0.0
                
                for row in range(self.table_itens.rowCount()):
                    valor_texto = self.table_itens.item(row, 4).text().replace("R$ ", "").replace(".", "").replace(",", ".")
                    valor_unitario = float(valor_texto)
                    quantidade = self.table_itens.cellWidget(row, 3).get_value()
                    
                    item = {
                        'produto': self.table_itens.item(row, 2).text(),
                        'quantidade': quantidade,
                        'valor_unitario': valor_unitario
                    }
                    itens.append(item)
                    total += valor_unitario * quantidade
                
                # Forma de pagamento
                forma_pagamento = self.combo_pagamento.currentText()
                
                # Data atual
                data_venda = datetime.datetime.now()
                
                # Gerar o PDF
                caminho_pdf = gerar_cupom_pdf(
                    id_venda=id_venda,
                    tipo_cupom=tipo_cupom,
                    cpf=cpf,
                    data_venda=data_venda,
                    itens=itens,
                    total=total,
                    forma_pagamento=forma_pagamento,
                    nome_empresa="MB SISTEMA"
                )
                
                # Exibir mensagem de sucesso
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, 
                    "Cupom Gerado",
                    f"Cupom {'Fiscal' if tipo_cupom == 'FISCAL' else 'Não Fiscal' if tipo_cupom == 'NAO_FISCAL' else 'de Crédito'} gerado com sucesso!\n\n"
                    f"Arquivo salvo em: {caminho_pdf}\n\n"
                    f"Venda #{id_venda}"
                )
                
                # Tentar abrir o PDF automaticamente
                try:
                    import subprocess
                    import platform
                    
                    sistema = platform.system()
                    if sistema == "Windows":
                        os.startfile(caminho_pdf)
                    elif sistema == "Darwin":  # macOS
                        subprocess.call(["open", caminho_pdf])
                    else:  # Linux ou outros
                        subprocess.call(["xdg-open", caminho_pdf])
                        
                    print(f"PDF aberto automaticamente: {caminho_pdf}")
                except Exception as e:
                    print(f"Não foi possível abrir o PDF automaticamente: {e}")
                    print(f"O PDF foi salvo em: {caminho_pdf}")
                
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                print(f"Erro ao gerar PDF: {e}")
                import traceback
                traceback.print_exc()
                
                QMessageBox.warning(
                    self,
                    "Erro ao Gerar PDF",
                    f"Não foi possível gerar o PDF do cupom: {str(e)}\n\n"
                    f"Verifique se as bibliotecas necessárias estão instaladas:\n"
                    f"pip install reportlab"
                )
            
        except Exception as e:
            print(f"Erro ao imprimir cupom: {e}")
            import traceback
            traceback.print_exc()

    def limpar_venda(self):
        """Limpa a venda atual, resetando campos e tabela"""
        # Limpar a tabela
        self.table_itens.setRowCount(0)
        
        # Resetar valores
        self.lbl_total_valor.setText("0,00")
        self.entry_valor_recebido.clear()
        self.lbl_troco.setText("Troco R$ 0,00")
        self.lbl_troco.setStyleSheet("color: #673AB7; font-size: 18px; font-weight: bold; background-color: transparent; qproperty-alignment: 'AlignCenter'; padding: 12px;")
        self.btn_finalizar.setText("Finalizar R$ 0,00")
        
        # Resetar forma de pagamento
        self.combo_pagamento.setCurrentIndex(0)
        
        # Resetar desconto e acréscimo
        self.valor_desconto = 0.0
        self.valor_acrescimo = 0.0
        self.lbl_desconto.setText("Desconto: R$ 0,00")
        self.lbl_acrescimo.setText("Acréscimo: R$ 0,00")
        
        # Ocultar elementos de pagamento
        self.troco_widget.setVisible(False)
        self.lbl_valor_recebido.setVisible(False)
        self.entry_valor_recebido.setVisible(False)
        
        # Focar no campo de código de barras
        self.entry_cod_barras.setFocus()

    def listar_clientes(self):
        """Abre uma janela para listar os clientes cadastrados"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
            from PyQt5.QtWidgets import QHeaderView, QLineEdit, QLabel, QMessageBox
            
            # Criar uma janela de diálogo para listar clientes
            dialog = QDialog(self)
            dialog.setWindowTitle("Lista de Clientes")
            dialog.setMinimumSize(800, 500)
            
            # Layout principal
            layout = QVBoxLayout(dialog)
            
            # Área de pesquisa
            search_layout = QHBoxLayout()
            search_label = QLabel("Pesquisar:")
            self.search_cliente = QLineEdit()
            self.search_cliente.setPlaceholderText("Digite o nome do cliente para pesquisar")
            search_button = QPushButton("Buscar")
            search_button.clicked.connect(lambda: self.buscar_clientes(table))
            
            search_layout.addWidget(search_label)
            search_layout.addWidget(self.search_cliente, 1)
            search_layout.addWidget(search_button)
            
            layout.addLayout(search_layout)
            
            # Tabela de clientes
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["ID", "Nome", "Tipo", "Documento", "Telefone"])
            
            # Ajustar colunas
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            
            layout.addWidget(table)
            
            # Botões de ação
            button_layout = QHBoxLayout()
            
            selecionar_btn = QPushButton("Selecionar")
            selecionar_btn.clicked.connect(lambda: self.selecionar_cliente(table, dialog))
            
            novo_btn = QPushButton("Novo Cliente")
            novo_btn.clicked.connect(self.novo_cliente)
            
            fechar_btn = QPushButton("Fechar")
            fechar_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(novo_btn)
            button_layout.addStretch(1)
            button_layout.addWidget(selecionar_btn)
            button_layout.addWidget(fechar_btn)
            
            layout.addLayout(button_layout)
            
            # Carregar dados
            self.carregar_clientes(table)
            
            # Conectar o evento de duplo clique para selecionar cliente
            table.doubleClicked.connect(lambda: self.selecionar_cliente(table, dialog))
            
            # Mostrar diálogo
            dialog.exec_()
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao listar clientes: {str(e)}")
            print(f"Erro ao listar clientes: {e}")
            import traceback
            traceback.print_exc()

    def carregar_clientes(self, table):
        """Carrega os clientes do banco de dados na tabela"""
        try:
            # Limpar tabela
            table.setRowCount(0)
            
            # Importar função do banco de dados
            import os
            import sys
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            from base.banco import execute_query
            
            # Consulta para obter os clientes
            query = """
            SELECT ID, NOME, TIPO_PESSOA, DOCUMENTO, TELEFONE
            FROM PESSOAS
            WHERE (TIPO_PESSOA = 'Física' OR TIPO_PESSOA = 'Jurídica')
            ORDER BY NOME
            """
            
            result = execute_query(query)
            
            # Preencher a tabela
            for row, cliente in enumerate(result):
                table.insertRow(row)
                
                # ID
                table.setItem(row, 0, QTableWidgetItem(str(cliente[0])))
                
                # Nome
                table.setItem(row, 1, QTableWidgetItem(cliente[1] if cliente[1] else ""))
                
                # Tipo
                table.setItem(row, 2, QTableWidgetItem(cliente[2] if cliente[2] else ""))
                
                # Documento
                table.setItem(row, 3, QTableWidgetItem(cliente[3] if cliente[3] else ""))
                
                # Telefone
                table.setItem(row, 4, QTableWidgetItem(cliente[4] if cliente[4] else ""))
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao carregar clientes: {str(e)}")
            print(f"Erro ao carregar clientes: {e}")

    def buscar_clientes(self, table):
        """Busca clientes pelo termo digitado"""
        try:
            termo = self.search_cliente.text().strip()
            
            if not termo:
                # Se não houver termo, mostrar todos os clientes
                self.carregar_clientes(table)
                return
            
            # Limpar tabela
            table.setRowCount(0)
            
            # Importar função do banco de dados
            import os
            import sys
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            from base.banco import execute_query
            
            # Consulta para buscar os clientes
            query = """
            SELECT ID, NOME, TIPO_PESSOA, DOCUMENTO, TELEFONE
            FROM PESSOAS
            WHERE (TIPO_PESSOA = 'Física' OR TIPO_PESSOA = 'Jurídica')
            AND (NOME LIKE ? OR DOCUMENTO LIKE ?)
            ORDER BY NOME
            """
            
            # Parâmetros para busca (usando % como curinga)
            params = (f"%{termo}%", f"%{termo}%")
            
            result = execute_query(query, params)
            
            # Preencher a tabela
            for row, cliente in enumerate(result):
                table.insertRow(row)
                
                # ID
                table.setItem(row, 0, QTableWidgetItem(str(cliente[0])))
                
                # Nome
                table.setItem(row, 1, QTableWidgetItem(cliente[1] if cliente[1] else ""))
                
                # Tipo
                table.setItem(row, 2, QTableWidgetItem(cliente[2] if cliente[2] else ""))
                
                # Documento
                table.setItem(row, 3, QTableWidgetItem(cliente[3] if cliente[3] else ""))
                
                # Telefone
                table.setItem(row, 4, QTableWidgetItem(cliente[4] if cliente[4] else ""))
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao buscar clientes: {str(e)}")
            print(f"Erro ao buscar clientes: {e}")

    def selecionar_cliente(self, table, dialog):
        """Seleciona o cliente e fecha o diálogo"""
        try:
            # Obter a linha selecionada
            selected_rows = table.selectionModel().selectedRows()
            
            if not selected_rows:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "Selecione um cliente.")
                return
            
            # Obter o ID e nome do cliente
            row = selected_rows[0].row()
            id_cliente = table.item(row, 0).text()
            nome_cliente = table.item(row, 1).text()
            
            # Aqui você pode definir o cliente selecionado para a venda
            # Por exemplo, adicionando um atributo na classe:
            self.cliente_atual = {
                'id': id_cliente,
                'nome': nome_cliente
            }
            
            # Opcional: você pode exibir o cliente selecionado em algum label na interface
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Cliente Selecionado", f"Cliente: {nome_cliente} (ID: {id_cliente})")
            
            # Fechar o diálogo
            dialog.accept()
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao selecionar cliente: {str(e)}")
            print(f"Erro ao selecionar cliente: {e}")

    def novo_cliente(self):
        """Abre a tela de cadastro de cliente"""
        try:
            # Aqui você pode chamar a tela de cadastro de clientes
            # Se você tiver um módulo para isso, pode importá-lo aqui
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Novo Cliente", 
                                "Esta função abrirá a tela de cadastro de clientes.\n"
                                "Por favor, implemente a chamada para o módulo de cadastro de clientes.")
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir cadastro de cliente: {str(e)}")
            print(f"Erro ao abrir cadastro de cliente: {e}")


    # 3. Agora vamos adicionar a função para listar produtos:

    def listar_produtos(self):
        """Abre uma janela para listar os produtos cadastrados"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
            from PyQt5.QtWidgets import QHeaderView, QLineEdit, QLabel, QMessageBox
            
            # Criar uma janela de diálogo para listar produtos
            dialog = QDialog(self)
            dialog.setWindowTitle("Lista de Produtos")
            dialog.setMinimumSize(800, 500)
            
            # Layout principal
            layout = QVBoxLayout(dialog)
            
            # Área de pesquisa
            search_layout = QHBoxLayout()
            search_label = QLabel("Pesquisar:")
            self.search_produto = QLineEdit()
            self.search_produto.setPlaceholderText("Digite o nome ou código do produto para pesquisar")
            search_button = QPushButton("Buscar")
            search_button.clicked.connect(lambda: self.buscar_produtos(table))
            
            search_layout.addWidget(search_label)
            search_layout.addWidget(self.search_produto, 1)
            search_layout.addWidget(search_button)
            
            layout.addLayout(search_layout)
            
            # Tabela de produtos
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Código", "Nome", "Marca", "Preço Venda", "Estoque", "Grupo"])
            
            # Ajustar colunas
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
            
            layout.addWidget(table)
            
            # Botões de ação
            button_layout = QHBoxLayout()
            
            adicionar_btn = QPushButton("Adicionar ao Carrinho")
            adicionar_btn.clicked.connect(lambda: self.adicionar_produto_da_lista(table, dialog))
            
            novo_btn = QPushButton("Novo Produto")
            novo_btn.clicked.connect(self.novo_produto)
            
            fechar_btn = QPushButton("Fechar")
            fechar_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(novo_btn)
            button_layout.addStretch(1)
            button_layout.addWidget(adicionar_btn)
            button_layout.addWidget(fechar_btn)
            
            layout.addLayout(button_layout)
            
            # Carregar dados
            self.carregar_produtos(table)
            
            # Conectar o evento de duplo clique para adicionar produto
            table.doubleClicked.connect(lambda: self.adicionar_produto_da_lista(table, dialog))
            
            # Mostrar diálogo
            dialog.exec_()
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao listar produtos: {str(e)}")
            print(f"Erro ao listar produtos: {e}")
            import traceback
            traceback.print_exc()

    def carregar_produtos(self, table):
        """Carrega os produtos do banco de dados na tabela"""
        try:
            # Limpar tabela
            table.setRowCount(0)
            
            # Importar função do banco de dados
            import os
            import sys
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            from base.banco import execute_query
            
            # Primeiro, vamos verificar as colunas existentes na tabela PRODUTOS
            structure_query = """
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'PRODUTOS'
            ORDER BY RDB$FIELD_POSITION
            """
            
            try:
                # Tentar obter a estrutura da tabela
                columns = execute_query(structure_query)
                print("Colunas encontradas na tabela PRODUTOS:")
                
                # Lista para armazenar os nomes das colunas
                column_names = []
                
                for col in columns:
                    # Firebird retorna nomes de coluna com espaços, então vamos remover esses espaços
                    col_name = col[0].strip() if col[0] else ""
                    column_names.append(col_name)
                    print(f"  - {col_name}")
                
                print(f"Total de colunas: {len(column_names)}")
                
                # Verificar se as colunas essenciais existem
                # Vamos mapear os nomes que queremos com possíveis alternativas
                column_mapping = {
                    "CODIGO": ["CODIGO", "ID", "ID_PRODUTO", "PRODUTO_ID", "COD"],
                    "NOME": ["NOME", "DESCRICAO", "PRODUTO", "DESCR"],
                    "MARCA": ["MARCA", "FABRICANTE", "FORNECEDOR"],
                    "PRECO_VENDA": ["PRECO_VENDA", "VALOR_VENDA", "PRECO", "VALOR", "PRECO_VAREJO"],
                    "ESTOQUE": ["ESTOQUE", "ESTOQUE_ATUAL", "QTD", "QUANTIDADE"],
                    "GRUPO": ["GRUPO", "CATEGORIA", "DEPARTAMENTO", "TIPO"]
                }
                
                # Função para encontrar a coluna correspondente
                def find_column(desired, alternatives):
                    for alt in alternatives:
                        if alt in column_names:
                            return alt
                    return None
                
                # Construir a consulta dinâmica com as colunas existentes
                selected_columns = []
                column_aliases = []
                
                for desired, alternatives in column_mapping.items():
                    found = find_column(desired, alternatives)
                    if found:
                        selected_columns.append(found)
                        if found != desired:
                            column_aliases.append(f"{found} as {desired}")
                        else:
                            column_aliases.append(found)
                    else:
                        # Se não encontrar, use um valor padrão
                        selected_columns.append("'N/A' as " + desired)
                        column_aliases.append("'N/A' as " + desired)
                
                # Construir a consulta final
                query = f"""
                SELECT {', '.join(column_aliases)}
                FROM PRODUTOS
                """
                
                # Adicionar ordenação se a coluna NOME existir
                if "NOME" in column_names:
                    query += " ORDER BY NOME"
                elif "DESCRICAO" in column_names:
                    query += " ORDER BY DESCRICAO"
                
                print(f"Consulta construída: {query}")
                
            except Exception as structure_error:
                # Se houver erro ao obter a estrutura, usar uma consulta simplificada
                print(f"Erro ao obter estrutura da tabela: {structure_error}")
                print("Usando consulta simplificada...")
                
                # Consulta simplificada usando * para obter todas as colunas
                query = "SELECT * FROM PRODUTOS"
                
            # Executar a consulta final
            print(f"Executando consulta: {query}")
            result = execute_query(query)
            
            # Verificar a quantidade de colunas e ajustar os cabeçalhos da tabela
            if result and len(result) > 0:
                num_columns = len(result[0])
                if num_columns < 6:  # Se tiver menos de 6 colunas
                    # Ajustar os cabeçalhos da tabela para o número correto de colunas
                    headers = ["Código", "Nome", "Marca", "Preço", "Estoque", "Grupo"][:num_columns]
                    table.setColumnCount(num_columns)
                    table.setHorizontalHeaderLabels(headers)
                    
                    # Ajustar o redimensionamento de colunas
                    header = table.horizontalHeader()
                    if num_columns == 1:
                        header.setSectionResizeMode(0, QHeaderView.Stretch)
                    else:
                        for i in range(num_columns):
                            if i == 1:  # Nome do produto (ou equivalente)
                                header.setSectionResizeMode(i, QHeaderView.Stretch)
                            else:
                                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            
            # Preencher a tabela
            for row, produto in enumerate(result):
                table.insertRow(row)
                
                # Preencher cada coluna disponível
                for col, valor in enumerate(produto):
                    if col >= table.columnCount():
                        break
                        
                    # Verificar se é coluna de preço (geralmente a 3ª coluna, índice 2)
                    if col == 2 and isinstance(valor, (int, float)):
                        # Formatar como moeda
                        valor_formatado = f"R$ {float(valor):.2f}".replace('.', ',')
                        item = QTableWidgetItem(valor_formatado)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        table.setItem(row, col, item)
                    # Verificar se é coluna de estoque (geralmente a 4ª coluna, índice 3)    
                    elif col == 3 and isinstance(valor, (int, float)):
                        # Formatar como número inteiro
                        item = QTableWidgetItem(str(int(valor)))
                        item.setTextAlignment(Qt.AlignCenter)
                        table.setItem(row, col, item)
                    else:
                        # Qualquer outro tipo de dado
                        table.setItem(row, col, QTableWidgetItem(str(valor) if valor is not None else ""))
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos: {str(e)}")
            print(f"Erro ao carregar produtos: {e}")
            import traceback
            traceback.print_exc()


    # Também precisamos atualizar o método buscar_produtos para usar a mesma lógica:

    def buscar_produtos(self, table):
        """Busca produtos pelo termo digitado"""
        try:
            termo = self.search_produto.text().strip()
            
            if not termo:
                # Se não houver termo, mostrar todos os produtos
                self.carregar_produtos(table)
                return
            
            # Limpar tabela
            table.setRowCount(0)
            
            # Importar função do banco de dados
            import os
            import sys
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            from base.banco import execute_query
            
            # Vamos obter as colunas disponíveis para construir a consulta
            structure_query = """
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'PRODUTOS'
            ORDER BY RDB$FIELD_POSITION
            """
            
            try:
                # Tentar obter a estrutura
                columns = execute_query(structure_query)
                column_names = [col[0].strip() if col[0] else "" for col in columns]
                
                # Verificar se as colunas para pesquisa existem
                search_columns = []
                
                # Possíveis colunas de pesquisa com alternativas
                possible_columns = {
                    "NOME": ["NOME", "DESCRICAO", "PRODUTO", "DESCR"],
                    "CODIGO": ["CODIGO", "ID", "ID_PRODUTO", "PRODUTO_ID", "COD"],
                    "BARRAS": ["BARRAS", "CODIGO_BARRAS", "EAN", "GTIN", "COD_BARRAS"]
                }
                
                # Função para encontrar a coluna correspondente
                def find_column(alternatives):
                    for alt in alternatives:
                        if alt in column_names:
                            return alt
                    return None
                
                # Construir a lista de colunas para pesquisa
                for key, alternatives in possible_columns.items():
                    column = find_column(alternatives)
                    if column:
                        search_columns.append(column)
                
                # Se não encontrou nenhuma coluna para pesquisa, usar todas as colunas de texto
                if not search_columns:
                    print("Não foi possível identificar colunas específicas para pesquisa.")
                    query = """
                    SELECT *
                    FROM PRODUTOS
                    """
                    result = execute_query(query)
                else:
                    # Construir a cláusula WHERE
                    where_clause = " OR ".join([f"{col} LIKE ?" for col in search_columns])
                    
                    # Construir a consulta completa
                    query = f"""
                    SELECT *
                    FROM PRODUTOS
                    WHERE {where_clause}
                    """
                    
                    # Preparar os parâmetros
                    params = tuple([f"%{termo}%" for _ in search_columns])
                    
                    print(f"Consulta de busca: {query}")
                    print(f"Parâmetros: {params}")
                    
                    # Executar a consulta
                    result = execute_query(query, params)
            
            except Exception as structure_error:
                # Se houver erro, usar uma consulta simplificada
                print(f"Erro ao obter estrutura para pesquisa: {structure_error}")
                print("Usando consulta de pesquisa simplificada...")
                
                # Consulta simplificada
                query = """
                SELECT *
                FROM PRODUTOS
                """
                
                # Executar sem filtro (retorna todos)
                result = execute_query(query)
            
            # Preencher a tabela
            num_columns = table.columnCount()
            
            for row, produto in enumerate(result):
                table.insertRow(row)
                
                # Preencher cada coluna disponível
                for col, valor in enumerate(produto):
                    if col >= num_columns:
                        break
                        
                    # Verificar se é coluna de preço (geralmente a 3ª coluna, índice 2)
                    if col == 2 and isinstance(valor, (int, float)):
                        # Formatar como moeda
                        valor_formatado = f"R$ {float(valor):.2f}".replace('.', ',')
                        item = QTableWidgetItem(valor_formatado)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        table.setItem(row, col, item)
                    # Verificar se é coluna de estoque (geralmente a 4ª coluna, índice 3)    
                    elif col == 3 and isinstance(valor, (int, float)):
                        # Formatar como número inteiro
                        item = QTableWidgetItem(str(int(valor)))
                        item.setTextAlignment(Qt.AlignCenter)
                        table.setItem(row, col, item)
                    else:
                        # Qualquer outro tipo de dado
                        table.setItem(row, col, QTableWidgetItem(str(valor) if valor is not None else ""))
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao buscar produtos: {str(e)}")
            print(f"Erro ao buscar produtos: {e}")
            import traceback
            traceback.print_exc()


    # Correção 1: Melhorar o método adicionar_produto_da_lista para extrair o preço corretamente

    def adicionar_produto_da_lista(self, table, dialog):
        """Adiciona o produto selecionado ao carrinho"""
        try:
            # Obter a linha selecionada
            selected_rows = table.selectionModel().selectedRows()
            
            if not selected_rows:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "Selecione um produto.")
                return
            
            # Obter dados do produto
            row = selected_rows[0].row()
            
            # Verificar o número de colunas disponíveis
            num_cols = table.columnCount()
            
            # Obter o código do produto (coluna 0)
            codigo = table.item(row, 0).text() if table.item(row, 0) else ""
            
            # Obter o nome do produto (coluna 1)
            nome = table.item(row, 1).text() if num_cols > 1 and table.item(row, 1) else ""
            
            # Obter o preço - melhorado para procurar em qualquer coluna que pareça conter um preço
            preco = 0.0
            
            # Primeiro, tentar encontrar na coluna 3 (índice 2) que geralmente contém o preço
            if num_cols > 2 and table.item(row, 2) and table.item(row, 2).text():
                preco_str = table.item(row, 2).text()
                try:
                    # Se contém R$, remover e converter
                    if "R$" in preco_str:
                        preco = float(preco_str.replace("R$", "").replace(".", "").replace(",", ".").strip())
                    # Se não, tentar converter direto (pode ser apenas um número)
                    else:
                        preco = float(preco_str.replace(",", ".").strip())
                except ValueError:
                    print(f"Não foi possível converter o valor '{preco_str}' na coluna 2")
            
            # Se ainda não tiver preço, procurar em todas as colunas
            if preco <= 0:
                for col_idx in range(num_cols):
                    if table.item(row, col_idx) and table.item(row, col_idx).text():
                        valor_text = table.item(row, col_idx).text()
                        
                        # Verificar se parece ser um valor monetário (contém R$ ou é um número)
                        if "R$" in valor_text:
                            try:
                                # Limpar e converter
                                valor_limpo = valor_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                                preco = float(valor_limpo)
                                print(f"Encontrou preço na coluna {col_idx}: {preco}")
                                break
                            except ValueError:
                                continue
            
            # Se ainda não tiver preço e houver apenas números na coluna 2, usar isso
            if preco <= 0 and num_cols > 2 and table.item(row, 2):
                try:
                    valor_text = table.item(row, 2).text().strip()
                    if valor_text and all(c.isdigit() or c in ",.+-" for c in valor_text):
                        preco = float(valor_text.replace(",", "."))
                        print(f"Usando valor numérico da coluna 2: {preco}")
                except ValueError:
                    pass
            
            # Fallback: se ainda não tiver preço, solicitar ao usuário
            if preco <= 0:
                from PyQt5.QtWidgets import QInputDialog, QMessageBox
                
                preco, ok = QInputDialog.getDouble(
                    self,
                    "Preço do Produto",
                    f"Digite o preço para '{nome}':",
                    0.0,
                    0.0,
                    10000.0,
                    2
                )
                
                if not ok:
                    QMessageBox.warning(self, "Aviso", "Operação cancelada pelo usuário.")
                    return
            
            # Debbugging - mostrar o preço encontrado
            print(f"Código: {codigo}, Nome: {nome}, Preço: {preco}")
            
            # Criar um objeto produto
            produto = {
                "codigo": codigo,
                "nome": nome,
                "preco_venda": preco
            }
            
            # Adicionar ao carrinho
            self.adicionar_produto_ao_carrinho(produto)
            
            # Confirmar adição
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Produto Adicionado", 
                                f"Produto '{nome}' adicionado ao carrinho com preço R$ {preco:.2f}".replace('.', ','))
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar produto: {str(e)}")
            print(f"Erro ao adicionar produto: {e}")
            import traceback
            traceback.print_exc()

    # Correção 2: Garantir que os produtos são adicionados com valor correto

    def adicionar_produto_ao_carrinho(self, produto):
        """Adiciona o produto encontrado à tabela de itens"""
        # Obter o próximo número de item
        proximo_item = self.table_itens.rowCount() + 1
        
        # Obter informações do produto
        id_produto = produto.get("codigo", "")
        nome = produto.get("nome", "")
        preco = float(produto.get("preco_venda", 0))
        
        # Verificação para garantir que o preço não seja zero
        if preco <= 0:
            from PyQt5.QtWidgets import QInputDialog, QMessageBox
            
            # Solicitar o preço ao usuário se for zero
            preco, ok = QInputDialog.getDouble(
                self,
                "Preço do Produto",
                f"Digite o preço para '{nome}':",
                0.0,
                0.0,
                10000.0,
                2
            )
            
            if not ok:
                QMessageBox.warning(self, "Aviso", "Produto não adicionado: preço não informado.")
                return
        
        # Formatar nome do produto (código + nome)
        nome_formatado = f"{id_produto} - {nome}"
        
        # Adicionar à tabela
        self.add_item_tabela(proximo_item, id_produto, nome_formatado, 1, preco)
        
        # Atualizar o total
        self.atualizar_total()
        
        # Focar novamente no campo de código de barras para o próximo produto
        self.entry_cod_barras.setFocus()

    def novo_produto(self):
        """Abre a tela de cadastro de produto"""
        try:
            # Aqui você pode chamar a tela de cadastro de produtos
            # Se você tiver um módulo para isso, pode importá-lo aqui
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Novo Produto", 
                                "Esta função abrirá a tela de cadastro de produtos.\n"
                                "Por favor, implemente a chamada para o módulo de cadastro de produtos.")
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir cadastro de produto: {str(e)}")
            print(f"Erro ao abrir cadastro de produto: {e}")

    def finalizar_venda(self):
        """Finaliza a venda atual e registra no banco de dados"""
        try:
            # Obter o total da venda
            total_text = self.lbl_total_valor.text().replace('.', '').replace(',', '.')
            total = float(total_text) if total_text else 0.0
            
            if total <= 0:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "Não há itens para finalizar a venda.")
                return
            
            # Obter a forma de pagamento
            forma_pagamento = self.combo_pagamento.currentText()
            
            # Obter os itens da venda
            itens = []
            for row in range(self.table_itens.rowCount()):
                item = {
                    'id_produto': self.table_itens.item(row, 1).text(),
                    'produto': self.table_itens.item(row, 2).text(),
                    'quantidade': self.table_itens.cellWidget(row, 3).get_value(),
                    'valor_unitario': self.table_itens.item(row, 4).text().replace('R$ ', '').replace(',', '.')
                }
                itens.append(item)
            
            # Registrar a venda no banco de dados
            id_venda = self.registrar_venda_no_banco(total, forma_pagamento, itens)
            
            # Limpar a tabela e resetar os campos
            self.limpar_venda()
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Sucesso", f"Venda #{id_venda} finalizada com sucesso!")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda: {str(e)}")

    def registrar_venda_no_banco(self, total, forma_pagamento, itens, tipo_cupom="NAO_FISCAL", cpf=""):
        """Registra a venda na tabela VENDAS do banco de dados"""
        try:
            from base.banco import execute_query
            from datetime import datetime
            
            # Imprimir informações para debug
            print("\n===== INICIANDO REGISTRO DE VENDA NO BANCO =====")
            print(f"Total: {total}, Forma de pagamento: {forma_pagamento}")
            print(f"Desconto: {self.valor_desconto}, Acréscimo: {self.valor_acrescimo}")
            print(f"Tipo de Cupom: {tipo_cupom}, CPF: {cpf}")
            print(f"Itens: {itens}")
            
            # Obter a data e hora atual
            now = datetime.now()
            data_venda = now.strftime("%Y-%m-%d")  # Formato para o banco: YYYY-MM-DD
            hora_venda = now.strftime("%H:%M:%S")  # Formato para o banco: HH:MM:SS
            
            print("\n----- ANALISANDO ESTRUTURA DAS TABELAS -----")
            
            # Verificar a estrutura real da tabela VENDAS
            structure_query_vendas = """
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'VENDAS'
            ORDER BY RDB$FIELD_POSITION
            """
            
            try:
                vendas_fields = execute_query(structure_query_vendas)
                print("\nColunas da tabela VENDAS:")
                
                # Lista para armazenar nomes das colunas (sem espaços)
                campos_vendas = []
                
                for field in vendas_fields:
                    # Remover espaços em branco do nome do campo (Firebird adiciona espaços)
                    field_name = field[0].strip() if field[0] else ""
                    campos_vendas.append(field_name)
                    print(f"  - {field_name}")
                print(f"Total de colunas em VENDAS: {len(vendas_fields)}")
                
                # Verificar se existem campos para tipo de cupom e CPF
                tem_tipo_cupom = any(campo for campo in campos_vendas if "TIPO_CUPOM" in campo.upper() or "CUPOM_TIPO" in campo.upper())
                tem_cpf = any(campo for campo in campos_vendas if "CPF" in campo.upper() or "DOCUMENTO" in campo.upper())
                
                print(f"Tem campo para tipo de cupom: {tem_tipo_cupom}")
                print(f"Tem campo para CPF: {tem_cpf}")
                
            except Exception as e:
                print(f"Erro ao obter estrutura da tabela VENDAS: {e}")
                # Continuar mesmo com o erro
                tem_tipo_cupom = False
                tem_cpf = False
            
            # Verificar a estrutura real da tabela VENDAS_ITENS
            structure_query_itens = """
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'VENDAS_ITENS'
            ORDER BY RDB$FIELD_POSITION
            """
            
            try:
                vendas_itens_fields = execute_query(structure_query_itens)
                print("\nColunas da tabela VENDAS_ITENS:")
                item_id_field = None  # Vamos descobrir qual campo usar para o ID do produto
                
                for field in vendas_itens_fields:
                    # Remover espaços em branco do nome do campo
                    field_name = field[0].strip() if field[0] else ""
                    print(f"  - {field_name}")
                    
                    # Detectar automaticamente o campo de ID do produto
                    if field_name.upper() in ['ID_PRODUTO', 'CODIGO', 'PRODUTO_ID', 'ID_PROD', 'PRODUTO']:
                        item_id_field = field_name
                        print(f"  >>> Possível campo para ID do produto: {field_name}")
                
                if not item_id_field:
                    # Se não encontrou nenhum campo óbvio, procurar por qualquer campo que contenha "PROD"
                    for field in vendas_itens_fields:
                        field_name = field[0].strip() if field[0] else ""
                        if "PROD" in field_name.upper():
                            item_id_field = field_name
                            print(f"  >>> Campo alternativo para ID do produto: {field_name}")
                            break
                
                if not item_id_field:
                    # Se ainda não encontrou, tentar qualquer campo com "ID"
                    for field in vendas_itens_fields:
                        field_name = field[0].strip() if field[0] else ""
                        if "ID" in field_name.upper() and field_name.upper() != 'ID_VENDA':
                            item_id_field = field_name
                            print(f"  >>> Campo alternativo para ID do produto: {field_name}")
                            break
                
                print(f"Total de colunas em VENDAS_ITENS: {len(vendas_itens_fields)}")
                
                if not item_id_field:
                    raise Exception("Não foi possível identificar o campo para o ID do produto na tabela VENDAS_ITENS")
                
            except Exception as e:
                print(f"Erro ao obter estrutura da tabela VENDAS_ITENS: {e}")
                # Se der erro aqui, vamos tentar com um nome padrão
                item_id_field = "ID_PRODUTO"
            
            print("\n----- REGISTRANDO A VENDA PRINCIPAL -----")
            
            # Registrar a venda principal - construindo a query com base nos campos disponíveis
            fields = ["DATA_VENDA", "HORA_VENDA", "ID_CLIENTE", "ID_VENDEDOR", 
                    "VALOR_TOTAL", "DESCONTO", "VALOR_FINAL", "FORMA_PAGAMENTO", "STATUS"]
            values = ["?"] * 9  # 9 placeholders para os campos padrão
            
            # Adicionar campos para tipo de cupom e CPF se existirem
            params = [data_venda, hora_venda, 0, 0, 
                    total + self.valor_desconto - self.valor_acrescimo, 
                    self.valor_desconto, total, forma_pagamento, "Finalizada"]
            
            if tem_tipo_cupom:
                # Encontrar o nome real do campo
                tipo_cupom_field = next(campo for campo in campos_vendas 
                                    if "TIPO_CUPOM" in campo.upper() or "CUPOM_TIPO" in campo.upper())
                fields.append(tipo_cupom_field)
                values.append("?")
                params.append(tipo_cupom)
            
            if tem_cpf:
                # Encontrar o nome real do campo
                cpf_field = next(campo for campo in campos_vendas 
                            if "CPF" in campo.upper() or "DOCUMENTO" in campo.upper())
                fields.append(cpf_field)
                values.append("?")
                params.append(cpf)
            
            # Construir a query final
            query_venda = f"""
            INSERT INTO VENDAS (
                {', '.join(fields)}
            ) VALUES ({', '.join(values)})
            """
            
            print(f"Executando query de inserção de venda: {query_venda}")
            print(f"Parâmetros: {params}")
            
            # Executar a inserção da venda
            execute_query(query_venda, params)
            
            # Obter o ID da venda inserida
            query_id = "SELECT MAX(ID_VENDA) FROM VENDAS"
            result = execute_query(query_id)
            id_venda = result[0][0] if result and result[0][0] else 0
            print(f"ID da venda registrada: {id_venda}")
            
            print("\n----- REGISTRANDO OS ITENS DA VENDA -----")
            
            # Construir a query de inserção de itens dinamicamente com base no campo descoberto
            query_item = f"""
            INSERT INTO VENDAS_ITENS (
                ID_VENDA, {item_id_field}, QUANTIDADE, VALOR_UNITARIO, VALOR_TOTAL
            ) VALUES (?, ?, ?, ?, ?)
            """
            
            print(f"Query para itens: {query_item}")
            
            # Registrar os itens da venda
            for item in itens:
                # Calcular o valor total do item
                valor_unitario = float(item['valor_unitario'])
                quantidade = int(item['quantidade'])
                valor_total = valor_unitario * quantidade
                
                # Obter o código do produto
                codigo_produto = item['id_produto']
                
                print(f"Inserindo item: ID_VENDA={id_venda}, {item_id_field}={codigo_produto}, QTD={quantidade}, VALOR_UNIT={valor_unitario}, TOTAL={valor_total}")
                
                # Executar a inserção do item
                execute_query(query_item, (
                    id_venda, codigo_produto, quantidade, valor_unitario, valor_total
                ))
                
                print(f"Item inserido com sucesso: {codigo_produto}")
            
            print("\n===== VENDA FINALIZADA COM SUCESSO =====")
            return id_venda
                
        except Exception as e:
            print(f"\n***** ERRO AO REGISTRAR VENDA *****")
            print(f"Erro detalhado: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Erro ao registrar venda: {str(e)}")
        
    def limpar_venda(self):
        """Limpa a venda atual, resetando campos e tabela"""
        # Limpar a tabela
        self.table_itens.setRowCount(0)
        
        # Resetar valores
        self.lbl_total_valor.setText("0,00")
        self.entry_valor_recebido.clear()
        self.lbl_troco.setText("Troco R$ 0,00")
        self.btn_finalizar.setText("Finalizar R$ 0,00")
        
        # Resetar desconto e acréscimo
        self.valor_desconto = 0.0
        self.valor_acrescimo = 0.0
        self.lbl_desconto.setText("Desconto: R$ 0,00")
        self.lbl_acrescimo.setText("Acréscimo: R$ 0,00")
        
        # Focar no campo de código de barras
        self.entry_cod_barras.setFocus()

    def calcular_troco(self):
        """Calcula o troco com base no valor recebido e total da venda"""
        try:
            # Obter o total da venda
            total_text = self.lbl_total_valor.text().replace('.', '').replace(',', '.')
            total = float(total_text) if total_text else 0.0
            
            # Obter o valor recebido
            valor_recebido_text = self.entry_valor_recebido.text().replace('R$', '').replace('.', '').replace(',', '.')
            valor_recebido = float(valor_recebido_text) if valor_recebido_text else 0.0
            
            # Calcular o troco
            troco = valor_recebido - total
            
            # Atualizar a exibição
            troco_formatado = f"{troco:.2f}".replace('.', ',')
            self.lbl_troco.setText(f"Troco R$ {troco_formatado}")
            
            # Atualizar o texto do botão finalizar
            total_formatado = f"{total:.2f}".replace('.', ',')
            self.btn_finalizar.setText(f"Finalizar R$ {total_formatado}")
            
        except (ValueError, TypeError) as e:
            # Em caso de erro de conversão, manter os valores padrão
            self.lbl_troco.setText("Troco R$ 0,00")
        except Exception as e:
            print(f"Erro ao calcular troco: {e}")

    def atualizar_total(self):
        """Atualiza o valor total da compra"""
        # Calcular o subtotal (soma dos itens)
        subtotal = 0.0
        for row in range(self.table_itens.rowCount()):
            # Obter o valor do item na coluna de valor
            valor_texto = self.table_itens.item(row, 4).text()
            
            # Obter a quantidade na coluna de quantidade
            quantidade_widget = self.table_itens.cellWidget(row, 3)
            quantidade = quantidade_widget.get_value() if quantidade_widget else 1
            
            # Converter o valor de texto para float
            try:
                # Remover "R$ " e substituir vírgula por ponto
                valor_limpo = valor_texto.replace("R$ ", "").replace(".", "").replace(",", ".")
                valor = float(valor_limpo)
                # Adicionar ao subtotal (valor * quantidade)
                subtotal += valor * quantidade
            except (ValueError, AttributeError):
                continue
        
        # Aplicar desconto e acréscimo
        total_com_ajustes = subtotal - self.valor_desconto + self.valor_acrescimo
        
        # Garantir que o total não seja negativo
        if total_com_ajustes < 0:
            total_com_ajustes = 0
        
        # Atualizar o label com o total formatado
        total_formatado = f"{total_com_ajustes:.2f}".replace(".", ",")
        self.lbl_total_valor.setText(total_formatado)
        
        # Atualizar o botão finalizar
        self.btn_finalizar.setText(f"Finalizar R$ {total_formatado}")
        
        # Recalcular o troco se houver valor recebido
        if self.entry_valor_recebido.text():
            self.calcular_troco()


    def create_svg_icon(self, svg_content, color="#000000"):
        """Função auxiliar para criar pixmap a partir de SVG com cor personalizada"""
        svg = svg_content.replace('fill="currentColor"', f'fill="{color}"')
        renderer = QSvgRenderer(bytearray(svg, encoding='utf-8'))
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def iniciar_relogio(self):
        timer = QTimer(self)
        timer.timeout.connect(self.atualizar_relogio)
        timer.start(1000)  # Atualiza a cada segundo
        self.atualizar_relogio()  # Chama imediatamente

    def atualizar_relogio(self):
        current_time = QDateTime.currentDateTime()
        time_str = current_time.toString('hh:mm:ss')
        self.clock_label.setText(time_str)

    def keyPressEvent(self, event):
        """Captura eventos de teclado globalmente"""
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Quando pressionar Enter, verificar se temos um código de barras
            if self.entry_cod_barras.text():
                self.buscar_produto_por_codigo_barras(self.entry_cod_barras.text())
        else:
            # Qualquer outra tecla que não seja de controle é adicionada ao campo de código de barras
            # A maioria dos leitores termina com um Enter automaticamente
            if (not event.modifiers() and event.text().isalnum() or 
                event.key() in [Qt.Key_Backspace, Qt.Key_Delete]):
                
                # Focar no campo de código de barras se não estiver focado
                if not self.entry_cod_barras.hasFocus():
                    self.entry_cod_barras.setFocus()
                    # Limpar o campo se já tinha algo e se não for uma tecla de edição
                    if event.key() not in [Qt.Key_Backspace, Qt.Key_Delete]:
                        self.entry_cod_barras.clear()
                
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Definir fonte padrão
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = PDVWindow()
    sys.exit(app.exec_())