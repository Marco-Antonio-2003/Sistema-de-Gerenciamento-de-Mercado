import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSpacerItem, QSizePolicy, QGridLayout, QToolButton
)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QCursor, QPainter
from PyQt5.QtCore import Qt, QDateTime, QTimer, QSize
from PyQt5.QtSvg import QSvgRenderer

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
    "eye": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"></path></svg>'
}

class QuantityWidget(QWidget):
    """Widget customizado para ajuste de quantidade com botões + e -"""
    def __init__(self, initial_value=1, parent=None):
        super().__init__(parent)
        self.value = initial_value
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Botão "-"
        self.btn_minus = QPushButton("-")
        self.btn_minus.setObjectName("QuantityMinusButton")
        self.btn_minus.setFixedSize(25, 25)
        self.btn_minus.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_minus.clicked.connect(self.decrease_value)
        
        # Valor
        self.lbl_value = QLabel(str(self.value))
        self.lbl_value.setObjectName("QuantityLabel")
        self.lbl_value.setAlignment(Qt.AlignCenter)
        self.lbl_value.setFixedWidth(30)
        
        # Botão "+"
        self.btn_plus = QPushButton("+")
        self.btn_plus.setObjectName("QuantityPlusButton")
        self.btn_plus.setFixedSize(25, 25)
        self.btn_plus.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_plus.clicked.connect(self.increase_value)
        
        layout.addWidget(self.btn_minus)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.btn_plus)
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        if value >= 1:
            self.value = value
            self.lbl_value.setText(str(self.value))
    
    def increase_value(self):
        self.set_value(self.value + 1)
    
    def decrease_value(self):
        self.set_value(self.value - 1)

class PDVWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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

        # Configurar para tela cheia
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
            QPushButton#PreVendaButton {{ 
                background-color: {self.colors['button_pre_venda']}; 
                padding-left: 25px;
                padding-right: 25px;
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

    def criar_cabecalho_superior(self):
        header_widget = QWidget()
        header_widget.setObjectName("Header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(10)

        self.clock_label = QLabel("00:00:00")
        self.clock_label.setObjectName("ClockLabel")
        header_layout.addWidget(self.clock_label)

        btn_vendedor = QPushButton("Informar Vendedor")
        btn_vendedor.setObjectName("HeaderButton")
        header_layout.addWidget(btn_vendedor)

        btn_prevendas = QPushButton("Lista Pré-Vendas")
        btn_prevendas.setObjectName("HeaderButton")
        btn_prevendas.setObjectName("PreVendaButton")
        header_layout.addWidget(btn_prevendas)

        btn_vendas = QPushButton("Lista de Vendas")
        btn_vendas.setObjectName("HeaderButton")
        btn_vendas.setObjectName("VendasButton")
        header_layout.addWidget(btn_vendas)

        header_layout.addStretch(1)

        btn_acoes = QPushButton("Ações ▾")
        btn_acoes.setObjectName("HeaderButton")
        btn_acoes.setObjectName("AcoesButton")
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

        # Campo de código de barras com ícone
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

        # --- Tabela de Itens ---
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
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_itens.setColumnWidth(3, 80)
        self.table_itens.setColumnWidth(4, 100)

        # Exemplo de dados
        self.add_item_tabela(1, "19680", "27371 - LAPIS RETRATIL PROVA DAGUA PRETO UNA", 1, 19.35)
        self.add_item_tabela(2, "25210", "56754 - KAIAK FEM DEO CORPORAL", 1, 6.65)
        self.add_item_tabela(3, "19473", "29306 - CREME PENTEAR TOIN OIN OIN NATURE", 1, 9.08)
        self.add_item_tabela(4, "19535", "6319 - FACES BATOM COLOR HID FPS8 VINHO 540", 1, 3.91)

        left_layout.addWidget(self.table_itens, 1)

        # --- Rodapé Esquerdo ---
        bottom_left_frame = QFrame()
        bottom_left_layout = QHBoxLayout(bottom_left_frame)
        bottom_left_layout.setContentsMargins(5, 5, 5, 5)

        # Desconto com ícone de edição
        desconto_layout = QHBoxLayout()
        lbl_desconto = QLabel("Desconto: R$ 0,00")
        desconto_layout.addWidget(lbl_desconto)
        
        edit_icon_1 = QLabel()
        edit_renderer = QSvgRenderer(bytearray(SVG_ICONS["edit"], encoding='utf-8'))
        edit_pixmap = QPixmap(16, 16)
        edit_pixmap.fill(Qt.transparent)
        edit_painter = QPainter(edit_pixmap)
        edit_renderer.render(edit_painter)
        edit_painter.end()
        edit_icon_1.setPixmap(edit_pixmap)
        desconto_layout.addWidget(edit_icon_1)
        bottom_left_layout.addLayout(desconto_layout)
        
        # Acréscimo com ícone de edição
        acrescimo_layout = QHBoxLayout()
        lbl_acrescimo = QLabel("Acréscimo: R$ 0,00")
        acrescimo_layout.addWidget(lbl_acrescimo)
        
        edit_icon_2 = QLabel()
        edit_icon_2.setPixmap(edit_pixmap)
        acrescimo_layout.addWidget(edit_icon_2)
        bottom_left_layout.addLayout(acrescimo_layout)
        
        bottom_left_layout.addStretch(1)
        
        lbl_lista_precos = QLabel("Lista de Preços:")
        bottom_left_layout.addWidget(lbl_lista_precos)
        
        lbl_padrao = QLabel("Padrão")
        lbl_padrao.setStyleSheet("font-weight: bold;")
        bottom_left_layout.addWidget(lbl_padrao)

        left_layout.addWidget(bottom_left_frame)

        return left_widget

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
        
        # Quantidade (com widget customizado de + e -)
        quantity_widget = QuantityWidget(qtd)
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
        
        # Botão Usuário
        btn_dir1 = QPushButton()
        btn_dir1.setObjectName("SidebarButton1")
        btn_dir1.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["user"], "#FFFFFF")))
        btn_dir1.setIconSize(QSize(24, 24))
        btn_dir1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_dir1.setCursor(QCursor(Qt.PointingHandCursor))
        top_right_layout.addWidget(btn_dir1)
        
        # Botão Lista
        btn_dir2 = QPushButton()
        btn_dir2.setObjectName("SidebarButton2")
        btn_dir2.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["list"], "#FFFFFF")))
        btn_dir2.setIconSize(QSize(24, 24))
        btn_dir2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_dir2.setCursor(QCursor(Qt.PointingHandCursor))
        top_right_layout.addWidget(btn_dir2)
        
        # Botão Editar
        btn_dir3 = QPushButton()
        btn_dir3.setObjectName("SidebarButton3")
        btn_dir3.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["edit"], "#FFFFFF")))
        btn_dir3.setIconSize(QSize(24, 24))
        btn_dir3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_dir3.setCursor(QCursor(Qt.PointingHandCursor))
        top_right_layout.addWidget(btn_dir3)
        
        right_layout.addLayout(top_right_layout)

        right_layout.addStretch(1)  # Empurra o resto para baixo

        # --- Total ---
        lbl_total_texto = QLabel("TOTAL R$:")
        lbl_total_texto.setObjectName("TotalLabel")
        right_layout.addWidget(lbl_total_texto)

        self.lbl_total_valor = QLabel("1.654,75")
        self.lbl_total_valor.setObjectName("TotalValue")
        right_layout.addWidget(self.lbl_total_valor)

        # --- Forma de Pagamento ---
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["01 - Dinheiro", "02 - Cartão Débito", "03 - Cartão Crédito"])
        right_layout.addWidget(self.combo_pagamento)

        # --- Valor Recebido ---
        lbl_valor_recebido = QLabel("Valor recebido")
        lbl_valor_recebido.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(lbl_valor_recebido)
        
        self.entry_valor_recebido = QLineEdit()
        self.entry_valor_recebido.setPlaceholderText("R$ 0,00")
        self.entry_valor_recebido.setAlignment(Qt.AlignRight)
        right_layout.addWidget(self.entry_valor_recebido)

        # --- Troco ---
        troco_widget = QWidget()
        troco_widget.setObjectName("TrocoWidget")
        troco_layout = QVBoxLayout(troco_widget)
        troco_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_troco = QLabel("Troco R$ 0,00")
        self.lbl_troco.setObjectName("TrocoLabel")
        troco_layout.addWidget(self.lbl_troco)
        
        right_layout.addWidget(troco_widget)

        # --- Botão Finalizar com ícone SVG ---
        btn_finalizar = QPushButton("Finalizar R$ 0,00")
        btn_finalizar.setObjectName("FinalizarButton")
        check_icon = self.create_svg_icon(SVG_ICONS["check"], "#FFFFFF")
        btn_finalizar.setIcon(QIcon(check_icon))
        btn_finalizar.setIconSize(QSize(24, 24))
        btn_finalizar.setCursor(QCursor(Qt.PointingHandCursor))
        right_layout.addWidget(btn_finalizar)

        return right_widget

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

    # Capturar tecla Esc para sair de tela cheia
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Definir fonte padrão
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = PDVWindow()
    window.show()
    sys.exit(app.exec_())