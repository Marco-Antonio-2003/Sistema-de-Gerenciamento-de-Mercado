#formulario_produtos.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QDateEdit, QComboBox, QMessageBox, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate


class FormularioProdutos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.produto_original = None  # Armazenar referência ao produto original
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
        
        # Título
        titulo = QLabel("Cadastro de Produtos")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
        header_layout.addWidget(spacer)
        
        main_layout.addLayout(header_layout)
        
        # Estilo comum para QComboBox
        combobox_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #043b57;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #0078d7;
            }
            QComboBox::item:hover {
                background-color: #043b57;
                color: white;
            }
        """
        
        # Estilo comum para QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Primeira linha de campos
        linha1_layout = QHBoxLayout()
        linha1_layout.setSpacing(20)
        
        # Campo Código
        codigo_layout = QHBoxLayout()
        codigo_label = QLabel("Código:")
        codigo_label.setStyleSheet("color: white; font-size: 14px;")
        codigo_layout.addWidget(codigo_label)
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setStyleSheet(lineedit_style)
        codigo_layout.addWidget(self.codigo_input)
        linha1_layout.addLayout(codigo_layout)
        
        # Campo Nome
        nome_layout = QHBoxLayout()
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet("color: white; font-size: 14px;")
        nome_layout.addWidget(nome_label)
        
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        nome_layout.addWidget(self.nome_input)
        linha1_layout.addLayout(nome_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha de campos
        linha2_layout = QHBoxLayout()
        linha2_layout.setSpacing(20)
        
        # Campo Código de Barras
        barras_layout = QHBoxLayout()
        barras_label = QLabel("Código de Barras:")
        barras_label.setStyleSheet("color: white; font-size: 14px;")
        barras_layout.addWidget(barras_label)
        
        self.barras_input = QLineEdit()
        self.barras_input.setStyleSheet(lineedit_style)
        barras_layout.addWidget(self.barras_input)
        linha2_layout.addLayout(barras_layout, 1)  # 1 para expandir
        
        # Campo Grupo
        grupo_layout = QHBoxLayout()
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet("color: white; font-size: 14px;")
        grupo_layout.addWidget(grupo_label)
        
        self.grupo_combo = QComboBox()
        self.grupo_combo.setStyleSheet(combobox_style)
        self.grupo_combo.addItem("Selecione um grupo")
        self.grupo_combo.addItem("Alimentos")
        self.grupo_combo.addItem("Bebidas")
        self.grupo_combo.addItem("Limpeza")
        self.grupo_combo.addItem("Higiene")
        self.grupo_combo.addItem("Hortifruti")
        self.grupo_combo.addItem("Eletrônicos")
        self.grupo_combo.addItem("Vestuário")
        self.grupo_combo.addItem("Outros")
        grupo_layout.addWidget(self.grupo_combo)
        linha2_layout.addLayout(grupo_layout)
        
        main_layout.addLayout(linha2_layout)
        
        # Terceira linha de campos
        linha3_layout = QHBoxLayout()
        linha3_layout.setSpacing(20)
        
        # Campo Marca
        marca_layout = QHBoxLayout()
        marca_label = QLabel("Marca:")
        marca_label.setStyleSheet("color: white; font-size: 14px;")
        marca_layout.addWidget(marca_label)
        
        self.marca_combo = QComboBox()
        self.marca_combo.setStyleSheet(combobox_style)
        # Adicione um botão de "+" na interface do ComboBox
        self.marca_combo.addItem("Selecione uma marca")
        self.marca_combo.addItem("Nestlé")
        self.marca_combo.addItem("Unilever")
        self.marca_combo.addItem("Procter & Gamble")
        self.marca_combo.addItem("Coca-Cola")
        self.marca_combo.addItem("Camil")
        self.marca_combo.addItem("Dell")
        self.marca_combo.addItem("Samsung")
        self.marca_combo.addItem("Lacoste")
        self.marca_combo.addItem("OMO")
        marca_layout.addWidget(self.marca_combo)
        
        linha3_layout.addLayout(marca_layout, 1)  # 1 para expandir
        
        # Campo Preço de Venda
        preco_venda_layout = QHBoxLayout()
        preco_venda_label = QLabel("Preço de venda:")
        preco_venda_label.setStyleSheet("color: white; font-size: 14px;")
        preco_venda_layout.addWidget(preco_venda_label)
        
        self.preco_venda_input = QLineEdit()
        self.preco_venda_input.setStyleSheet(lineedit_style)
        preco_venda_layout.addWidget(self.preco_venda_input)
        linha3_layout.addLayout(preco_venda_layout)
        
        # Campo Preço de Compra
        preco_compra_layout = QHBoxLayout()
        preco_compra_label = QLabel("Preço de Compra:")
        preco_compra_label.setStyleSheet("color: white; font-size: 14px;")
        preco_compra_layout.addWidget(preco_compra_label)
        
        self.preco_compra_input = QLineEdit()
        self.preco_compra_input.setStyleSheet(lineedit_style)
        preco_compra_layout.addWidget(self.preco_compra_input)
        linha3_layout.addLayout(preco_compra_layout)
        
        main_layout.addLayout(linha3_layout)
        
        # Quarta linha de campos
        linha4_layout = QHBoxLayout()
        linha4_layout.setSpacing(20)
        
        # Campo Data de Cadastro com ícone de calendário
        data_layout = QHBoxLayout()
        data_label = QLabel("Data de Cadastro:")
        data_label.setStyleSheet("color: white; font-size: 14px;")
        data_layout.addWidget(data_label)
        
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        
        # Configurar ícone de calendário
        calendario_icon_path = ""
        # Verificar se o arquivo existe
        if os.path.exists("ico-img/calendar-outline.svg"):
            calendario_icon_path = "ico-img/calendar-outline.svg"
        
        self.data_input.setStyleSheet(f"""
            QDateEdit {{
                background-color: white;
                border: 1px solid #cccccc;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                color: black;
            }}
            QDateEdit::drop-down {{
                border: none;
            }}
            QDateEdit::down-arrow {{
                width: 16px;
                height: 16px;
                image: url({calendario_icon_path});
            }}
            QDateEdit:hover {{
                border: 1px solid #0078d7;
            }}
            QCalendarWidget {{
                background-color: #043b57;
            }}
            QCalendarWidget QWidget {{
                background-color: #043b57;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: #043b57;
                color: white;
                selection-background-color: #005079;
                selection-color: white;
            }}
            QCalendarWidget QToolButton {{
                background-color: #043b57;
                color: white;
            }}
            QCalendarWidget QMenu {{
                background-color: #043b57;
                color: white;
            }}
        """)
        data_layout.addWidget(self.data_input)
        linha4_layout.addLayout(data_layout)
        
        # Campo Unidade com caixa de texto mais próxima
        unidade_layout = QHBoxLayout()
        unidade_layout.setSpacing(8)  # Reduzir espaçamento entre label e combo
        
        unidade_label = QLabel("Unidade:")
        unidade_label.setStyleSheet("color: white; font-size: 14px;")
        unidade_layout.addWidget(unidade_label)
        
        self.unidade_combo = QComboBox()
        self.unidade_combo.setStyleSheet(combobox_style)
        self.unidade_combo.addItem("Selecione uma unidade")
        self.unidade_combo.addItem("Quilograma (kg)")
        self.unidade_combo.addItem("Grama (g)")
        self.unidade_combo.addItem("Litro (L)")
        self.unidade_combo.addItem("Mililitro (mL)")
        self.unidade_combo.addItem("Unidade (un)")
        self.unidade_combo.addItem("Pacote (pct)")
        self.unidade_combo.addItem("Caixa (cx)")
        self.unidade_combo.addItem("Bandeja (bdj)")
        self.unidade_combo.addItem("Dúzia (dz)")
        self.unidade_combo.addItem("Fardo (fd)")
        self.unidade_combo.addItem("Garrafa (gf)")
        unidade_layout.addWidget(self.unidade_combo)
        linha4_layout.addLayout(unidade_layout, 1)  # 1 para expandir
        
        main_layout.addLayout(linha4_layout)
        
        # Botão Incluir
        self.btn_incluir = QPushButton("Incluir")
        self.btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00ff9d;
                color: black;
                border: none;
                padding: 15px 0;
                font-size: 16px;
                border-radius: 4px;
                margin: 20px 100px 0;
            }
            QPushButton:hover {
                background-color: #00e088;
            }
        """)
        self.btn_incluir.clicked.connect(self.incluir)
        main_layout.addWidget(self.btn_incluir)
        
        # Adicionar espaço no final
        main_layout.addStretch()
    
    def voltar(self):
        """Ação do botão voltar"""
        # Fechar a janela atual
        if hasattr(self, 'parent_widget') and self.parent_widget and hasattr(self.parent_widget, 'form_window'):
            self.parent_widget.form_window.close()
        else:
            # Se não encontrar a janela pai, tenta fechar a janela atual
            parent_window = self.window()
            if parent_window and parent_window != self:
                parent_window.close()
            else:
                print("Voltar para a tela de produtos")
    
    def incluir(self):
        """Inclui um novo produto ou salva alterações"""
        # Validar campos obrigatórios
        codigo = self.codigo_input.text()
        nome = self.nome_input.text()
        grupo = self.grupo_combo.currentText() if self.grupo_combo.currentIndex() > 0 else ""
        unidade = self.unidade_combo.currentText() if self.unidade_combo.currentIndex() > 0 else ""
        preco_venda = self.preco_venda_input.text()
        barras = self.barras_input.text()
        marca = self.marca_combo.currentText() if self.marca_combo.currentIndex() > 0 else ""
        preco_compra = self.preco_compra_input.text()
        
        if not codigo or not nome:
            self.mostrar_mensagem("Atenção", "Preencha pelo menos o código e o nome do produto!")
            return
        
        # Verificar se é uma alteração (botão com texto "Atualizar")
        eh_alteracao = self.btn_incluir.text() == "Atualizar"
        
        # Preparar dados do produto
        preco_venda_float = 0.0
        try:
            preco_venda_float = float(preco_venda.replace(',', '.')) if preco_venda else 0.0
        except ValueError:
            self.mostrar_mensagem("Erro", "Formato de preço inválido. Use apenas números e vírgula.")
            return
            
        preco_compra_float = 0.0
        try:
            preco_compra_float = float(preco_compra.replace(',', '.')) if preco_compra else 0.0
        except ValueError:
            self.mostrar_mensagem("Erro", "Formato de preço inválido. Use apenas números e vírgula.")
            return
        
        if eh_alteracao:
            # Modo de alteração - atualizar produto existente
            if self.parent_widget and hasattr(self.parent_widget, 'produtos_data'):
                for i, produto in enumerate(self.parent_widget.produtos_data):
                    if produto["codigo"] == codigo:
                        # Atualizar dados
                        self.parent_widget.produtos_data[i]["nome"] = nome
                        self.parent_widget.produtos_data[i]["codigo_barras"] = barras
                        self.parent_widget.produtos_data[i]["marca"] = marca if marca else None
                        self.parent_widget.produtos_data[i]["grupo"] = grupo if grupo != "Selecione um grupo" else None
                        self.parent_widget.produtos_data[i]["preco_venda"] = preco_venda_float
                        
                        # Atualizar campos adicionais se existirem no produto original
                        if "preco_custo" in self.parent_widget.produtos_data[i]:
                            self.parent_widget.produtos_data[i]["preco_custo"] = preco_compra_float
                        if "unidade" in self.parent_widget.produtos_data[i] or unidade != "Selecione uma unidade":
                            self.parent_widget.produtos_data[i]["unidade"] = unidade if unidade != "Selecione uma unidade" else None
                        
                        # Atualizar a tabela na tela principal
                        if hasattr(self.parent_widget, 'carregar_produtos'):
                            self.parent_widget.carregar_produtos()
                        
                        self.mostrar_mensagem("Sucesso", "Produto alterado com sucesso!")
                        self.voltar()  # Voltar para a tela anterior
                        return
                
                # Se chegou aqui, o produto não foi encontrado
                self.mostrar_mensagem("Erro", "Produto não encontrado para atualização.")
                return
        else:
            # Modo de inclusão - criar novo produto
            
            # Verificar se o código já existe
            if self.parent_widget and hasattr(self.parent_widget, 'produtos_data'):
                for produto in self.parent_widget.produtos_data:
                    if produto["codigo"] == codigo:
                        self.mostrar_mensagem("Erro", "Já existe um produto com este código!")
                        return
            
            # Criar novo produto
            novo_produto = {
                "codigo": codigo,
                "nome": nome,
                "codigo_barras": barras,
                "marca": marca if marca != "Selecione uma marca" else None,
                "grupo": grupo if grupo != "Selecione um grupo" else None,
                "preco_venda": preco_venda_float,
                "preco_custo": preco_compra_float,
                "quantidade_estoque": 0,  # Valor padrão
                "unidade": unidade if unidade != "Selecione uma unidade" else None
            }
            
            # Adicionar à lista de produtos
            if self.parent_widget and hasattr(self.parent_widget, 'produtos_data'):
                self.parent_widget.produtos_data.append(novo_produto)
                
                # Atualizar a tabela na tela principal
                if hasattr(self.parent_widget, 'carregar_produtos'):
                    self.parent_widget.carregar_produtos()
                
                self.mostrar_mensagem("Sucesso", "Produto incluído com sucesso!")
                
                # Limpar os campos para novo cadastro
                self.codigo_input.clear()
                self.nome_input.clear()
                self.barras_input.clear()
                self.marca_combo.setCurrentIndex(0)
                self.preco_venda_input.clear()
                self.preco_compra_input.clear()
                self.grupo_combo.setCurrentIndex(0)
                self.unidade_combo.setCurrentIndex(0)
                
                return
        
        # Se chegou aqui e não conseguiu salvar, exibir mensagem genérica
        self.mostrar_mensagem("Erro", "Não foi possível salvar o produto. Verifique as informações.")
    
    def mostrar_mensagem(self, titulo, texto):
        """Exibe uma caixa de mensagem"""
        msg_box = QMessageBox()
        if "Atenção" in titulo:
            msg_box.setIcon(QMessageBox.Warning)
        elif "Erro" in titulo:
            msg_box.setIcon(QMessageBox.Critical)
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
                background-color: #005079;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        msg_box.exec_()


# Para testar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Cadastro de Produtos")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("background-color: #043b57;")
    
    formulario_produtos_widget = FormularioProdutos(window)
    window.setCentralWidget(formulario_produtos_widget)
    
    window.show()
    sys.exit(app.exec_())