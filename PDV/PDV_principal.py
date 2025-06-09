import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSpacerItem, QSizePolicy, QGridLayout, QToolButton,
    QMessageBox, QDialog, QListWidget, QListWidgetItem, QScrollArea
)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QCursor, QPainter
from PyQt5.QtCore import Qt, QDateTime, QTimer, QSize
from PyQt5.QtSvg import QSvgRenderer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gerador_cupom import gerar_e_imprimir_cupom
try:
    pass  # Add the code to be executed here
except Exception as e:
    print(f"An error occurred: {e}")
    # Importar os módulos do sistema
    from base.banco import buscar_produto_por_barras, buscar_produto_por_codigo
    # Importar a classe/função para listar vendas
    import Lista_vendas
except ImportError as e:
    print(f"AVISO: Erro de importação: {e}")
    # Funções vazias para evitar erros
    def buscar_produto_por_barras(codigo): return None
    def buscar_produto_por_codigo(codigo): return None


class BarcodeSuggestionWidget(QWidget):
    """Widget corrigido para seleção de produtos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_pdv = parent
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Lista de sugestões
        self.lista_sugestoes = QListWidget()
        self.lista_sugestoes.setStyleSheet("""
            QListWidget {
                border: 2px solid #2196F3;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
                max-height: 200px;
                min-width: 400px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
                background-color: white;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #E3F2FD;
            }
        """)
        
        self.lista_sugestoes.setMaximumHeight(200)
        self.lista_sugestoes.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.lista_sugestoes.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout.addWidget(self.lista_sugestoes)
        
        # Conectar eventos
        self.lista_sugestoes.itemClicked.connect(self.item_selecionado)
        self.lista_sugestoes.itemDoubleClicked.connect(self.item_selecionado)
        self.lista_sugestoes.itemActivated.connect(self.item_selecionado)
        
        # Dados dos produtos e quantidade
        self.produtos_data = []
        self.quantidade_selecionada = 1
    
    def mostrar_sugestoes(self, codigo_parcial, produtos):
        """Mostra as sugestões com informação de quantidade"""
        print(f"\n🎨 === MOSTRANDO SUGESTÕES ===")
        print(f"Código parcial: {codigo_parcial}")
        print(f"Produtos recebidos: {len(produtos)}")
        print(f"Quantidade detectada: {self.quantidade_selecionada}")
        
        self.lista_sugestoes.clear()
        self.produtos_data = []
        
        if not produtos or len(produtos) == 0:
            print("❌ Nenhum produto para mostrar")
            self.hide()
            return
        
        # Informação sobre quantidade
        quantidade_info = f" (Qtd: {self.quantidade_selecionada})" if self.quantidade_selecionada > 1 else ""
        
        # Adicionar produtos à lista
        for i, produto in enumerate(produtos):
            try:
                print(f"📦 Processando produto {i+1}: {produto}")
                
                # Extrair informações do produto
                codigo_barras = str(produto[0]) if len(produto) > 0 and produto[0] else ""
                codigo_produto = str(produto[1]) if len(produto) > 1 and produto[1] else ""
                nome_produto = str(produto[2]) if len(produto) > 2 and produto[2] else "Produto sem nome"
                
                # Obter preço
                preco = 0.0
                if len(produto) > 3 and produto[3] is not None:
                    try:
                        preco = float(produto[3])
                    except (ValueError, TypeError):
                        preco = 0.0
                
                # Formatar preço
                preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
                
                # Criar texto do item com quantidade destacada
                if codigo_barras and codigo_barras != "None" and codigo_barras != "":
                    texto_item = f"🔗 {codigo_barras} | {codigo_produto} - {nome_produto[:35]} | {preco_formatado}{quantidade_info}"
                else:
                    texto_item = f"📦 {codigo_produto} - {nome_produto[:40]} | {preco_formatado}{quantidade_info}"
                
                # Adicionar item à lista
                item = QListWidgetItem(texto_item)
                
                # Tooltip informativo
                tooltip_text = f"Código: {codigo_produto}\nNome: {nome_produto}\nPreço: {preco_formatado}"
                if self.quantidade_selecionada > 1:
                    total_item = preco * self.quantidade_selecionada
                    tooltip_text += f"\nQuantidade a adicionar: {self.quantidade_selecionada}"
                    tooltip_text += f"\nTotal do item: R$ {total_item:.2f}"
                
                item.setToolTip(tooltip_text)
                self.lista_sugestoes.addItem(item)
                
                # Armazenar dados do produto
                self.produtos_data.append({
                    'codigo_barras': codigo_barras,
                    'codigo': codigo_produto,
                    'nome': nome_produto,
                    'preco_venda': preco
                })
                
                print(f"  📝 Produto armazenado: {self.produtos_data[-1]}")
                
            except Exception as e:
                print(f"❌ Erro ao processar produto {i+1}: {e}")
                continue
        
        # Mostrar o widget se houver itens
        if self.lista_sugestoes.count() > 0:
            print(f"✅ Exibindo widget com {self.lista_sugestoes.count()} itens")
            self.posicionar_widget()
            self.show()
            self.lista_sugestoes.setCurrentRow(0)  # Selecionar primeiro item
            self.lista_sugestoes.setFocus()  # Dar foco à lista
            print("✅ Widget exibido e focado!")
        else:
            print("❌ Nenhum item para exibir")
            self.hide()
    
    def item_selecionado(self, item):
        """Chamado quando um item é selecionado - SEM CONFIRMAÇÃO DUPLA"""
        print("🖱️ === ITEM SELECIONADO ===")
        try:
            # Obter o índice do item selecionado
            row = self.lista_sugestoes.currentRow()
            print(f"🎯 Linha selecionada: {row}")
            print(f"🎯 Total de produtos: {len(self.produtos_data)}")
            print(f"🔢 Quantidade para adicionar: {self.quantidade_selecionada}")
            
            if 0 <= row < len(self.produtos_data):
                produto = self.produtos_data[row]
                print(f"📦 Produto selecionado: {produto}")
                
                # Verificar se tem PDV principal
                if not self.parent_pdv:
                    print("❌ Referência ao PDV principal não encontrada")
                    return
                
                # REMOVER CONFIRMAÇÃO PARA QUANTIDADE > 1
                # A confirmação já foi feita na busca inicial, não precisamos confirmar novamente
                
                # Verificar se produto já existe na tabela
                produto_existe = False
                codigo_produto = produto.get('codigo', '')
                
                for row_tabela in range(self.parent_pdv.table_itens.rowCount()):
                    id_produto_tabela = self.parent_pdv.table_itens.item(row_tabela, 1).text()
                    
                    if id_produto_tabela == codigo_produto:
                        # Produto já existe, aumentar a quantidade
                        produto_existe = True
                        print(f"🔄 Produto já existe na tabela, atualizando quantidade...")
                        
                        quantity_widget = self.parent_pdv.table_itens.cellWidget(row_tabela, 3)
                        if quantity_widget and hasattr(quantity_widget, 'value'):
                            # Aumentar a quantidade
                            nova_quantidade = quantity_widget.value + self.quantidade_selecionada
                            quantity_widget.value = nova_quantidade
                            
                            # Atualizar o label da quantidade
                            for child in quantity_widget.children():
                                if hasattr(child, 'setText'):
                                    child.setText(str(nova_quantidade))
                                    break
                            
                            # Recalcular o total da linha
                            try:
                                valor_unitario = float(produto.get('preco_venda', 0))
                                novo_total = valor_unitario * nova_quantidade
                                novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                                valor_total_item = QTableWidgetItem(novo_total_str)
                                valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                self.parent_pdv.table_itens.setItem(row_tabela, 5, valor_total_item)
                                print(f"✅ Quantidade atualizada para {nova_quantidade} na linha existente")
                            except Exception as e:
                                print(f"❌ Erro ao recalcular total: {e}")
                        break
                
                # Se o produto não existe, adicionar nova linha
                if not produto_existe:
                    print(f"➕ Adicionando novo produto com quantidade {self.quantidade_selecionada}")
                    if self.quantidade_selecionada == 1:
                        # Usar método normal para quantidade 1
                        self.parent_pdv.adicionar_produto_ao_carrinho(produto)
                    else:
                        # Usar método específico para quantidade maior que 1
                        self.parent_pdv.adicionar_produto_com_quantidade_especifica(produto, self.quantidade_selecionada)
                
                # Atualizar o total geral
                self.parent_pdv.atualizar_total()
                
                # MOSTRAR MENSAGEM SIMPLES DE SUCESSO (sem confirmação extra)
                print(f"✅ {self.quantidade_selecionada} unidades adicionadas com sucesso!")
                
                # Limpar e focar no campo
                self.parent_pdv.entry_cod_barras.clear()
                self.parent_pdv.entry_cod_barras.setFocus()
                
                # Esconder widget
                self.hide()
                
                print("✅ Produto adicionado com sucesso!")
                
            else:
                print(f"❌ Linha inválida: {row}")
                
        except Exception as e:
            print(f"❌ Erro ao selecionar produto: {e}")
            import traceback
            traceback.print_exc()
    
    def keyPressEvent(self, event):
        """Trata eventos de teclado no widget de sugestões"""
        print(f"⌨️ Tecla pressionada no widget: {event.key()}")
        
        if event.key() == Qt.Key_Escape:
            print("⌨️ ESC - escondendo sugestões")
            self.hide()
            if self.parent_pdv:
                self.parent_pdv.entry_cod_barras.setFocus()
                
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            print("⌨️ ENTER - selecionando produto")
            # Simular clique no item atual
            current_item = self.lista_sugestoes.currentItem()
            if current_item:
                self.item_selecionado(current_item)
            
        elif event.key() == Qt.Key_Up:
            current = self.lista_sugestoes.currentRow()
            if current > 0:
                self.lista_sugestoes.setCurrentRow(current - 1)
                print(f"⌨️ UP - linha {current - 1}")
                
        elif event.key() == Qt.Key_Down:
            current = self.lista_sugestoes.currentRow()
            if current < self.lista_sugestoes.count() - 1:
                self.lista_sugestoes.setCurrentRow(current + 1)
                print(f"⌨️ DOWN - linha {current + 1}")
        else:
            # Reenviar tecla para o campo de código de barras
            if self.parent_pdv and hasattr(self.parent_pdv, 'entry_cod_barras'):
                self.parent_pdv.entry_cod_barras.keyPressEvent(event)
    
    def posicionar_widget(self):
        """Posiciona o widget abaixo do campo de código de barras"""
        try:
            if self.parent_pdv and hasattr(self.parent_pdv, 'entry_cod_barras'):
                campo_barras = self.parent_pdv.entry_cod_barras
                
                # Obter posição global do campo
                pos_global = campo_barras.mapToGlobal(campo_barras.rect().bottomLeft())
                
                # Posicionar abaixo do campo
                self.move(pos_global.x(), pos_global.y() + 2)
                
                # Ajustar largura para coincidir com o campo (ou um pouco maior)
                largura_minima = max(campo_barras.width(), 400)
                self.setFixedWidth(largura_minima)
                
                print(f"📍 Widget posicionado em ({pos_global.x()}, {pos_global.y() + 2}) com largura {largura_minima}")
        except Exception as e:
            print(f"❌ Erro ao posicionar widget: {e}")
    
    def item_duplo_clique(self, item):
        """Chamado quando um item recebe duplo clique"""
        print("🖱️ Item selecionado via duplo clique")
        self.selecionar_produto_atual()
    
    def selecionar_produto_atual(self):
        """Seleciona o produto atual da lista"""
        try:
            row = self.lista_sugestoes.currentRow()
            print(f"🎯 Selecionando produto da linha {row}")
            
            if 0 <= row < len(self.produtos_data):
                produto = self.produtos_data[row]
                print(f"📦 Produto selecionado: {produto}")
                
                # ===== NOVA FUNCIONALIDADE: Verificar quantidade selecionada =====
                quantidade_para_adicionar = getattr(self, 'quantidade_selecionada', 1)
                
                if quantidade_para_adicionar > 1:
                    print(f"🔢 Adicionando {quantidade_para_adicionar} unidades do produto")
                    
                    # Confirmar quantidade alta
                    from PyQt5.QtWidgets import QMessageBox
                    nome_produto = produto.get('nome', 'Produto')
                    resposta = QMessageBox.question(
                        self.parent_pdv,
                        "Confirmar Quantidade",
                        f"Adicionar {quantidade_para_adicionar} unidades de:\n{nome_produto}?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if resposta == QMessageBox.No:
                        print("❌ Usuário cancelou a adição com quantidade")
                        self.hide()
                        if self.parent_pdv:
                            self.parent_pdv.entry_cod_barras.clear()
                            self.parent_pdv.entry_cod_barras.setFocus()
                        return
                    
                    # ===== CORRIGIDO: Verificar se o produto já existe na tabela =====
                    produto_existe = False
                    codigo_produto = produto.get('codigo', '')
                    
                    # Procurar se o produto já está na tabela
                    for row_tabela in range(self.parent_pdv.table_itens.rowCount()):
                        id_produto_tabela = self.parent_pdv.table_itens.item(row_tabela, 1).text()
                        
                        if id_produto_tabela == codigo_produto:
                            # Produto já existe, aumentar a quantidade
                            produto_existe = True
                            
                            # Obter o widget de quantidade desta linha
                            quantity_widget = self.parent_pdv.table_itens.cellWidget(row_tabela, 3)
                            if quantity_widget and hasattr(quantity_widget, 'get_value'):
                                # Aumentar a quantidade
                                nova_quantidade = quantity_widget.value + quantidade_para_adicionar
                                quantity_widget.value = nova_quantidade
                                
                                # Atualizar o label da quantidade
                                # Encontrar o label dentro do widget
                                for child in quantity_widget.children():
                                    if hasattr(child, 'setText'):
                                        child.setText(str(nova_quantidade))
                                        break
                                
                                # Recalcular o total da linha
                                try:
                                    valor_unitario = float(produto.get('preco_venda', 0))
                                    novo_total = valor_unitario * nova_quantidade
                                    novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                                    valor_total_item = QTableWidgetItem(novo_total_str)
                                    valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                    self.parent_pdv.table_itens.setItem(row_tabela, 5, valor_total_item)
                                except Exception as e:
                                    print(f"Erro ao recalcular total: {e}")
                                
                                print(f"✅ Quantidade atualizada para {nova_quantidade} na linha existente")
                            break
                    
                    # Se o produto não existe, adicionar nova linha com a quantidade especificada
                    if not produto_existe:
                        if self.parent_pdv:
                            # Adicionar como uma única linha com a quantidade especificada
                            self.parent_pdv.adicionar_produto_ao_carrinho_com_quantidade(produto, quantidade_para_adicionar)
                            print(f"✅ Nova linha criada com {quantidade_para_adicionar} unidades!")
                    
                    # Atualizar o total geral
                    if self.parent_pdv:
                        self.parent_pdv.atualizar_total()
                    
                    # Mostrar mensagem de sucesso
                    QMessageBox.information(
                        self.parent_pdv,
                        "Produto Adicionado", 
                        f"✅ {quantidade_para_adicionar} unidades adicionadas com sucesso!"
                    )
                    
                else:
                    # Quantidade normal (1 unidade)
                    if self.parent_pdv:
                        self.parent_pdv.adicionar_produto_ao_carrinho(produto)
                        print("✅ 1 unidade adicionada ao carrinho!")
                
                # Limpar e focar no campo
                if self.parent_pdv:
                    self.parent_pdv.entry_cod_barras.clear()
                    self.parent_pdv.entry_cod_barras.setFocus()
                
                # Esconder widget
                self.hide()
            else:
                print(f"❌ Linha inválida: {row}")
        except Exception as e:
            print(f"❌ Erro ao selecionar produto: {e}")
            import traceback
            traceback.print_exc()

    def adicionar_produto_com_quantidade_da_sugestao(self, produto, quantidade):
        """Adiciona produto vindo da lista de sugestões - SEM CONFIRMAÇÃO DUPLA"""
        try:
            print(f"🎯 Adicionando: {produto} com quantidade {quantidade}")
            
            # REMOVER TODAS AS CONFIRMAÇÕES - apenas adicionar diretamente
            
            # Verificar se produto já existe
            codigo = str(produto.get('codigo', ''))
            for row in range(self.table_itens.rowCount()):
                if self.table_itens.item(row, 1).text() == codigo:
                    # Produto existe - somar quantidade
                    widget = self.table_itens.cellWidget(row, 3)
                    if widget and hasattr(widget, 'value'):
                        nova_qtd = widget.value + quantidade
                        widget.value = nova_qtd
                        # Atualizar display
                        for child in widget.children():
                            if hasattr(child, 'setText'):
                                child.setText(str(nova_qtd))
                                break
                        # Recalcular total
                        preco = float(produto.get('preco_venda', 0))
                        novo_total = preco * nova_qtd
                        total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                        item = QTableWidgetItem(total_str)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.table_itens.setItem(row, 5, item)
                    self.atualizar_total()
                    return True
            
            # Produto não existe - criar nova linha
            if quantidade == 1:
                self.adicionar_produto_ao_carrinho(produto)
            else:
                self.adicionar_produto_com_quantidade_especifica(produto, quantidade)
            
            self.atualizar_total()
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def conectar_eventos_codigo_barras(self):
        """Conecta os eventos relacionados ao código de barras - VERSÃO CORRIGIDA"""
        try:
            if not hasattr(self, 'entry_cod_barras'):
                print("❌ Widget entry_cod_barras não encontrado!")
                return
            
            # Conectar evento de mudança de texto
            self.entry_cod_barras.textChanged.connect(self.buscar_sugestoes_codigo_barras)
            print("✅ Evento textChanged conectado")
            
            # Conectar evento de Enter
            self.entry_cod_barras.returnPressed.connect(self.processar_codigo_barras)
            print("✅ Evento returnPressed conectado")
            
            # ===== CRUCIAL: Verificar se o widget de sugestões tem referência ao PDV =====
            if hasattr(self, 'widget_sugestoes'):
                self.widget_sugestoes.parent_pdv = self
                print("✅ Referência do widget de sugestões configurada")
            
            print("✅ Todos os eventos conectados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao conectar eventos: {e}")
            import traceback
            traceback.print_exc()

    # ===== NOVA FUNÇÃO: Adicionar produto com quantidade específica =====
    def adicionar_produto_ao_carrinho_com_quantidade(self, produto, quantidade):
        """Adiciona o produto encontrado à tabela de itens com quantidade específica"""
        # Obter o próximo número de item
        proximo_item = self.table_itens.rowCount() + 1
        
        # Obter informações do produto
        id_produto = produto.get("codigo", "")
        nome = produto.get("nome", "")
        preco = float(produto.get("preco_venda", 0))
        
        # Formatar nome do produto (código + nome)
        nome_formatado = f"{id_produto} - {nome}"
        
        # Adicionar à tabela com a quantidade especificada
        self.add_item_tabela(proximo_item, id_produto, nome_formatado, quantidade, preco)
        
        # Atualizar o total
        self.atualizar_total()
        
        # Focar novamente no campo de código de barras para o próximo produto
        self.entry_cod_barras.setFocus()
    
    def keyPressEvent(self, event):
        """Trata eventos de teclado no widget de sugestões"""
        if event.key() == Qt.Key_Escape:
            print("⌨️ ESC pressionado - escondendo sugestões")
            self.hide()
            if self.parent_pdv:
                self.parent_pdv.entry_cod_barras.setFocus()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            print("⌨️ ENTER pressionado - selecionando produto")
            self.selecionar_produto_atual()
        elif event.key() == Qt.Key_Up:
            current = self.lista_sugestoes.currentRow()
            if current > 0:
                self.lista_sugestoes.setCurrentRow(current - 1)
                print(f"⌨️ UP - linha {current - 1}")
        elif event.key() == Qt.Key_Down:
            current = self.lista_sugestoes.currentRow()
            if current < self.lista_sugestoes.count() - 1:
                self.lista_sugestoes.setCurrentRow(current + 1)
                print(f"⌨️ DOWN - linha {current + 1}")
        else:
            # Reenviar tecla para o campo de código de barras
            if self.parent_pdv and hasattr(self.parent_pdv, 'entry_cod_barras'):
                self.parent_pdv.entry_cod_barras.keyPressEvent(event)


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

        # ========================================
        # NOVO: Criar componentes de sugestões ANTES dos widgets principais
        # ========================================
        
        # Criar widget de sugestões de código de barras
        self.widget_sugestoes = BarcodeSuggestionWidget(self)
        
        # Timer para evitar muitas consultas ao banco durante digitação rápida
        self.timer_busca = QTimer()
        self.timer_busca.setSingleShot(True)
        self.timer_busca.timeout.connect(self.executar_busca_sugestoes)
        self.timer_busca.setInterval(300)  # 300ms de delay

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
        
        # Configurar o combo de pesquisa
        self.configurar_combo_pesquisa()
        
        # Conectar eventos EXISTENTES
        self.entry_cod_barras.returnPressed.connect(self.processar_codigo_barras)
        self.entry_valor_recebido.textChanged.connect(self.calcular_troco)
        
        # Configurar para receber o foco e para tela cheia
        self.setFocusPolicy(Qt.StrongFocus)
        self.entry_cod_barras.setFocus()
        self.showFullScreen()
        
        # ========================================
        # NOVO: Conectar eventos de sugestões APÓS todos widgets serem criados
        # ========================================
        self.conectar_eventos_codigo_barras()

    def conectar_eventos_codigo_barras(self):
        """Conecta os eventos relacionados ao código de barras após widgets serem criados"""
        try:
            # Verificar se o widget existe
            if not hasattr(self, 'entry_cod_barras'):
                print("❌ Widget entry_cod_barras não encontrado!")
                return
                
            # Conectar evento de mudança de texto para busca em tempo real
            self.entry_cod_barras.textChanged.connect(self.buscar_sugestoes_codigo_barras)
            print("✅ Eventos de código de barras conectados com sucesso!")
            
            # Teste: simular digitação para verificar se está funcionando
            print("🧪 Testando conexão...")
            
        except Exception as e:
            print(f"❌ Erro ao conectar eventos de código de barras: {e}")
            import traceback
            traceback.print_exc()

    def buscar_sugestoes_codigo_barras(self):
        """Inicia busca de sugestões com delay para evitar muitas consultas"""
        try:
            # Parar timer anterior se estiver rodando
            self.timer_busca.stop()
            
            # Obter texto atual
            codigo_parcial = self.entry_cod_barras.text().strip()
            
            # Debug - imprimir o que está sendo digitado
            print(f"🔍 Código digitado: '{codigo_parcial}' (tamanho: {len(codigo_parcial)})")
            
            # Se texto muito curto ou vazio, esconder sugestões
            if len(codigo_parcial) < 2:
                print("❌ Texto muito curto, escondendo sugestões")
                self.widget_sugestoes.hide()
                return
            
            print("⏰ Iniciando timer para busca...")
            # Iniciar timer para busca com delay
            self.timer_busca.start()
            
        except Exception as e:
            print(f"❌ Erro em buscar_sugestoes_codigo_barras: {e}")
            import traceback
            traceback.print_exc()

    def executar_busca_sugestoes(self):
        """Executa a busca de sugestões no banco de dados - VERSÃO CORRIGIDA"""
        try:
            codigo_parcial = self.entry_cod_barras.text().strip()
            
            print(f"🚀 === EXECUTANDO BUSCA DE SUGESTÕES ===")
            print(f"Código digitado: '{codigo_parcial}'")
            
            # ===== DETECÇÃO DE PADRÕES DE QUANTIDADE - MELHORADA =====
            codigo_para_buscar = codigo_parcial
            quantidade_detectada = 1  # Quantidade padrão
            
            # Padrões suportados:
            # 1. *10 78 (asterisco + quantidade + espaço + código)
            # 2. 10*78 (quantidade + asterisco + código)
            # 3. 10* 78 (quantidade + asterisco + espaço + código)
            
            if "*" in codigo_parcial:
                try:
                    print(f"🔍 Detectado asterisco no código, analisando padrão...")
                    
                    # Padrão 1: *quantidade código (ex: *10 78)
                    if codigo_parcial.startswith("*"):
                        partes = codigo_parcial.split(" ", 1)
                        if len(partes) == 2:
                            quantidade_str = partes[0][1:]  # Remove o *
                            codigo_para_buscar = partes[1].strip()
                            if quantidade_str.isdigit():
                                quantidade_detectada = int(quantidade_str)
                                print(f"🔢 Padrão *quantidade código detectado: Qtd={quantidade_detectada}, Código='{codigo_para_buscar}'")
                            else:
                                print(f"⚠️ Quantidade inválida após asterisco: '{quantidade_str}'")
                                self.widget_sugestoes.hide()
                                return
                    
                    # Padrões 2 e 3: quantidade*código ou quantidade* código (ex: 10*78 ou 10* 78)
                    else:
                        # Dividir pelo asterisco
                        partes_asterisco = codigo_parcial.split("*", 1)
                        if len(partes_asterisco) == 2:
                            quantidade_str = partes_asterisco[0].strip()
                            codigo_parte = partes_asterisco[1].strip()
                            
                            print(f"🔍 Analisando partes: quantidade='{quantidade_str}', código='{codigo_parte}'")
                            
                            # Validar e converter quantidade
                            if quantidade_str.isdigit():
                                quantidade_detectada = int(quantidade_str)
                                codigo_para_buscar = codigo_parte
                                print(f"🔢 Padrão quantidade*código detectado: Qtd={quantidade_detectada}, Código='{codigo_para_buscar}'")
                            else:
                                print(f"⚠️ Quantidade inválida antes do asterisco: '{quantidade_str}'")
                                codigo_para_buscar = codigo_parcial
                                quantidade_detectada = 1
                    
                    # Validações de quantidade
                    if quantidade_detectada <= 0:
                        print(f"⚠️ Quantidade deve ser maior que zero: {quantidade_detectada}")
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "Quantidade Inválida", 
                                        f"A quantidade deve ser maior que zero. Você digitou: {quantidade_detectada}")
                        self.widget_sugestoes.hide()
                        return
                        
                    if quantidade_detectada > 9999:
                        print(f"⚠️ Quantidade muito alta: {quantidade_detectada}")
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "Quantidade Muito Alta", 
                                        f"A quantidade máxima é 9999. Você digitou: {quantidade_detectada}")
                        self.widget_sugestoes.hide()
                        return
                            
                except ValueError as ve:
                    print(f"⚠️ Erro ao processar quantidade: {ve}")
                    codigo_para_buscar = codigo_parcial
                    quantidade_detectada = 1
                except Exception as e:
                    print(f"❌ Erro inesperado ao processar quantidade: {e}")
                    codigo_para_buscar = codigo_parcial
                    quantidade_detectada = 1
            
            # Verificar se ainda há código suficiente para buscar
            if len(codigo_para_buscar) < 1:
                print("❌ Código muito curto para buscar sugestões")
                self.widget_sugestoes.hide()
                return
            
            print(f"📋 Resultado da análise:")
            print(f"  Código original: '{codigo_parcial}'")
            print(f"  Código para buscar: '{codigo_para_buscar}'")
            print(f"  Quantidade detectada: {quantidade_detectada}")
            
            # ===== CONFIGURAR A QUANTIDADE NO WIDGET DE SUGESTÕES =====
            print(f"🔧 Configurando quantidade {quantidade_detectada} no widget de sugestões...")
            self.widget_sugestoes.quantidade_selecionada = quantidade_detectada
            
            # ===== BUSCA NO BANCO DE DADOS =====
            # Importar função do banco de dados
            import os
            import sys
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            print(f"📁 Diretórios no path: {current_dir}, {parent_dir}")
            
            # Tentar importar execute_query
            try:
                from base.banco import execute_query
                print("✅ execute_query importado com sucesso!")
            except ImportError as import_error:
                print(f"❌ Erro ao importar execute_query: {import_error}")
                self.widget_sugestoes.hide()
                return
            
            # DESCOBRIR a estrutura real da tabela
            print(f"\n🔍 === DESCOBRINDO ESTRUTURA DA TABELA PRODUTOS ===")
            
            try:
                # Query para descobrir os campos da tabela PRODUTOS
                structure_query = """
                SELECT RDB$FIELD_NAME, RDB$FIELD_POSITION
                FROM RDB$RELATION_FIELDS
                WHERE RDB$RELATION_NAME = 'PRODUTOS'
                ORDER BY RDB$FIELD_POSITION
                """
                
                campos_result = execute_query(structure_query)
                print(f"✅ Estrutura obtida! Encontrados {len(campos_result)} campos:")
                
                # Extrair nomes dos campos
                nomes_campos = []
                for campo in campos_result:
                    nome_campo = campo[0].strip() if campo[0] else ""
                    nomes_campos.append(nome_campo)
                    print(f"  📋 {campo[1]}: {nome_campo}")
                
                # MAPEAR campos para busca
                campos_mapeados = {
                    'codigo_barras': None,
                    'codigo_produto': None,
                    'nome_produto': None,
                    'preco_venda': None
                }
                
                # Possíveis nomes para cada tipo de campo
                mapeamento = {
                    'codigo_barras': ['BARRAS', 'CODIGO_BARRAS', 'EAN', 'GTIN', 'COD_BARRAS', 'EAN13'],
                    'codigo_produto': ['CODIGO', 'ID', 'ID_PRODUTO', 'PRODUTO_ID', 'COD', 'COD_PRODUTO'],
                    'nome_produto': ['NOME', 'DESCRICAO', 'PRODUTO', 'DESCR', 'DESCRITIVO', 'NOME_PRODUTO'],
                    'preco_venda': ['PRECO_VENDA', 'VALOR_VENDA', 'PRECO', 'VALOR', 'PRECO_VAREJO', 'VALOR_UNITARIO']
                }
                
                # Encontrar os campos reais
                for tipo, possiveis_nomes in mapeamento.items():
                    for nome in possiveis_nomes:
                        if nome in nomes_campos:
                            campos_mapeados[tipo] = nome
                            print(f"✅ {tipo} -> {nome}")
                            break
                    
                    if not campos_mapeados[tipo]:
                        print(f"⚠️ Campo {tipo} não encontrado!")
                
                # CONSTRUIR queries baseadas nos campos encontrados
                produtos_encontrados = []
                
                # Query 1: Buscar por código de barras
                if campos_mapeados['codigo_barras']:
                    print(f"\n🔍 Buscando por código de barras ({campos_mapeados['codigo_barras']})...")
                    
                    query_barras = f"""
                    SELECT {campos_mapeados['codigo_barras']}, {campos_mapeados['codigo_produto'] or 'NULL'}, 
                        {campos_mapeados['nome_produto'] or 'NULL'}, {campos_mapeados['preco_venda'] or 'NULL'}
                    FROM PRODUTOS
                    WHERE {campos_mapeados['codigo_barras']} LIKE ?
                    ORDER BY {campos_mapeados['codigo_barras']}
                    FETCH FIRST 10 ROWS ONLY
                    """
                    
                    try:
                        param_busca = f"{codigo_para_buscar}%"
                        print(f"🔍 Executando: {query_barras}")
                        print(f"🔍 Parâmetro: {param_busca}")
                        
                        result_barras = execute_query(query_barras, (param_busca,))
                        print(f"✅ Encontrados {len(result_barras)} produtos por código de barras")
                        
                        for produto in result_barras:
                            if produto not in produtos_encontrados:
                                produtos_encontrados.append(produto)
                        
                    except Exception as e:
                        print(f"❌ Erro na busca por código de barras: {e}")
                
                # Query 2: Buscar por código do produto
                if campos_mapeados['codigo_produto'] and len(produtos_encontrados) < 10:
                    print(f"\n🔍 Buscando por código do produto ({campos_mapeados['codigo_produto']})...")
                    
                    query_codigo = f"""
                    SELECT {campos_mapeados['codigo_barras'] or 'NULL'}, {campos_mapeados['codigo_produto']}, 
                        {campos_mapeados['nome_produto'] or 'NULL'}, {campos_mapeados['preco_venda'] or 'NULL'}
                    FROM PRODUTOS
                    WHERE CAST({campos_mapeados['codigo_produto']} AS VARCHAR(50)) LIKE ?
                    ORDER BY {campos_mapeados['codigo_produto']}
                    FETCH FIRST 10 ROWS ONLY
                    """
                    
                    try:
                        param_busca = f"{codigo_para_buscar}%"
                        print(f"🔍 Executando: {query_codigo}")
                        print(f"🔍 Parâmetro: {param_busca}")
                        
                        result_codigo = execute_query(query_codigo, (param_busca,))
                        print(f"✅ Encontrados {len(result_codigo)} produtos por código")
                        
                        for produto in result_codigo:
                            # Evitar duplicatas
                            codigo_produto = str(produto[1]) if len(produto) > 1 else ""
                            if not any(str(p[1]) == codigo_produto for p in produtos_encontrados):
                                produtos_encontrados.append(produto)
                        
                    except Exception as e:
                        print(f"❌ Erro na busca por código: {e}")
            
            except Exception as structure_error:
                print(f"❌ Erro ao obter estrutura da tabela: {structure_error}")
                # Fallback com consulta simples
                try:
                    fallback_query = "SELECT * FROM PRODUTOS WHERE CODIGO LIKE ? LIMIT 10"
                    produtos_encontrados = execute_query(fallback_query, (f"{codigo_para_buscar}%",))
                except:
                    produtos_encontrados = []
            
            # MOSTRAR RESULTADOS
            print(f"\n📊 === RESULTADOS DA BUSCA ===")
            print(f"Total de produtos encontrados: {len(produtos_encontrados)}")
            print(f"Quantidade configurada no widget: {self.widget_sugestoes.quantidade_selecionada}")
            
            if len(produtos_encontrados) > 0:
                print("🎯 Produtos encontrados:")
                for i, produto in enumerate(produtos_encontrados[:5]):
                    print(f"  {i+1}: {produto}")
                
                # Verificar se a quantidade foi configurada corretamente
                if self.widget_sugestoes.quantidade_selecionada != quantidade_detectada:
                    print(f"⚠️ AVISO: Quantidade não foi configurada corretamente!")
                    print(f"  Esperado: {quantidade_detectada}")
                    print(f"  Atual: {self.widget_sugestoes.quantidade_selecionada}")
                    # Forçar a configuração
                    self.widget_sugestoes.quantidade_selecionada = quantidade_detectada
                    print(f"🔧 Quantidade forçada para: {quantidade_detectada}")
                
                # Mostrar as sugestões
                print(f"🎨 Chamando mostrar_sugestoes com {len(produtos_encontrados)} produtos...")
                self.widget_sugestoes.mostrar_sugestoes(codigo_para_buscar, produtos_encontrados)
                print("✅ Widget de sugestões exibido!")
            else:
                print("❌ Nenhum produto encontrado")
                self.widget_sugestoes.hide()
                
        except Exception as e:
            print(f"❌ ERRO GERAL em executar_busca_sugestoes: {e}")
            import traceback
            traceback.print_exc()
            self.widget_sugestoes.hide()

    def esconder_sugestoes_codigo_barras(self):
        """Esconde o widget de sugestões"""
        if hasattr(self, 'widget_sugestoes'):
            self.widget_sugestoes.hide()

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

        # Botão Lista de Vendas com ícone - ADICIONADO F3
        btn_vendas = QPushButton("  Lista de Vendas (F3)")
        btn_vendas.setObjectName("HeaderButton")
        btn_vendas.setObjectName("VendasButton")
        btn_vendas.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["history"], "#FFFFFF")))
        btn_vendas.clicked.connect(self.abrir_historico_vendas)
        header_layout.addWidget(btn_vendas)

        header_layout.addStretch(1)

        # Botão Fechar Caixa com nova função - ADICIONADO F7
        btn_acoes = QPushButton("Fechar Caixa (F7)")
        btn_acoes.setObjectName("HeaderButton")
        btn_acoes.setObjectName("AcoesButton")
        btn_acoes.clicked.connect(self.confirmar_fechar_caixa)
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

    def configurar_combo_pesquisa(self):
        """Configura o combo de pesquisa para buscar produtos diretamente"""
        # Desconectar sinais existentes para evitar chamadas duplicadas
        try:
            self.combo_pesquisa.currentIndexChanged.disconnect()
        except:
            pass  # Ignora se não houver conexões
        
        # Limpar o combo
        self.combo_pesquisa.clear()
        
        # Adicionar item padrão
        self.combo_pesquisa.addItem("Pesquisar produtos (F2)")
        
        # Tornar o combo editável para permitir digitação
        self.combo_pesquisa.setEditable(True)
        
        # Configurar para mostrar um menu suspenso com os resultados
        self.combo_pesquisa.setInsertPolicy(QComboBox.NoInsert)
        
        # Conectar sinais
        self.combo_pesquisa.lineEdit().returnPressed.connect(self.pesquisar_produto_combo)
    
    def pesquisar_produto_combo(self):
        """Pesquisa um produto a partir do texto digitado no combo"""
        texto_pesquisa = self.combo_pesquisa.currentText().strip()
        
        if not texto_pesquisa or texto_pesquisa == "Pesquisar produtos (F2)":
            return
        
        try:
            # Importar função do banco de dados
            import os
            import sys
            
            # Adicionar diretório pai ao path para acessar a pasta base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            from base.banco import execute_query
            
            # Determinar as colunas para pesquisa
            # Primeiro, obter a estrutura da tabela
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
                
                # Possíveis colunas de pesquisa com alternativas
                possible_columns = {
                    "NOME": ["NOME", "DESCRICAO", "PRODUTO", "DESCR"],
                    "CODIGO": ["CODIGO", "ID", "ID_PRODUTO", "PRODUTO_ID", "COD"],
                    "BARRAS": ["BARRAS", "CODIGO_BARRAS", "EAN", "GTIN", "COD_BARRAS"]
                }
                
                # Construir a lista de colunas para pesquisa
                search_columns = []
                for key, alternatives in possible_columns.items():
                    for alt in alternatives:
                        if alt in column_names:
                            search_columns.append(alt)
                            break
                
                # Se não encontrou nenhuma coluna para pesquisa, usar consulta genérica
                if not search_columns:
                    query = "SELECT * FROM PRODUTOS"
                    params = ()
                else:
                    # Construir a cláusula WHERE para pesquisa por texto
                    where_clause = " OR ".join([f"{col} LIKE ?" for col in search_columns])
                    params = tuple([f"%{texto_pesquisa}%" for _ in search_columns])
                    
                    query = f"""
                    SELECT * FROM PRODUTOS
                    WHERE {where_clause}
                    ORDER BY NOME
                    LIMIT 20
                    """
            
            except Exception as structure_error:
                # Consulta simplificada em caso de erro
                print(f"Erro ao obter estrutura: {structure_error}")
                query = "SELECT * FROM PRODUTOS LIMIT 20"
                params = ()
            
            # Executar a consulta para buscar produtos
            result = execute_query(query, params)
            
            # Se não encontrou resultados
            if not result or len(result) == 0:
                self.combo_pesquisa.showPopup()  # Fecha o popup se estiver aberto
                QMessageBox.information(self, "Pesquisa", f"Nenhum produto encontrado com '{texto_pesquisa}'")
                return
            
            # Se encontrou apenas um resultado, adicionar diretamente
            if len(result) == 1:
                produto_encontrado = result[0]
                
                # Criar dicionário com os dados do produto
                try:
                    produto = {
                        "id": produto_encontrado[0],
                        "codigo": produto_encontrado[1] if len(produto_encontrado) > 1 else produto_encontrado[0],
                        "nome": produto_encontrado[2] if len(produto_encontrado) > 2 else "Produto",
                        "preco_venda": float(produto_encontrado[3]) if len(produto_encontrado) > 3 and produto_encontrado[3] is not None else 0
                    }
                    
                    # Adicionar ao carrinho diretamente
                    self.adicionar_produto_ao_carrinho(produto)
                    
                    # Limpar e resetar o combo
                    self.combo_pesquisa.lineEdit().clear()
                    self.combo_pesquisa.setCurrentIndex(0)
                    return
                    
                except Exception as e:
                    print(f"Erro ao processar produto único: {e}")
            
            # Se encontrou múltiplos resultados, mostrar diálogo de seleção
            self.mostrar_selecao_produtos(result)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar produto: {str(e)}")
            print(f"Erro na pesquisa: {e}")

    def keyPressEvent(self, event):
        """Captura eventos de teclado globalmente"""
        # Se o widget de sugestões estiver visível e ativo
        if hasattr(self, 'widget_sugestoes') and self.widget_sugestoes.isVisible():
            if event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape]:
                # Reenviar evento para o widget de sugestões
                self.widget_sugestoes.keyPressEvent(event)
                return
        
        if event.key() == Qt.Key_Escape:
            # Esconder sugestões primeiro, depois tratar escape normal
            if hasattr(self, 'widget_sugestoes') and self.widget_sugestoes.isVisible():
                self.widget_sugestoes.hide()
                return
            
            if self.isFullScreen():
                self.showNormal()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Quando pressionar Enter, verificar se temos um código de barras
            if self.entry_cod_barras.text():
                self.buscar_produto_por_codigo_barras(self.entry_cod_barras.text())
        # Adicionar captura das teclas de função
        elif event.key() == Qt.Key_F1:
            # F1 - Listar Clientes
            self.listar_clientes()
        elif event.key() == Qt.Key_F2:
            # F2 - Listar Produtos
            self.listar_produtos()
        elif event.key() == Qt.Key_F3:
            # F3 - Lista de Vendas
            self.abrir_historico_vendas()
        elif event.key() == Qt.Key_F4:
            # F4 - Finalizar Venda (SEM CUPOM)
            self.finalizar_venda_simples()
        elif event.key() == Qt.Key_F5:
            # F5 - Editar Desconto
            self.editar_desconto()
        elif event.key() == Qt.Key_F6:
            # F6 - Editar Acréscimo
            self.editar_acrescimo()
        elif event.key() == Qt.Key_F7:
            # F7 - Fechar Caixa
            self.confirmar_fechar_caixa()
        elif event.key() == Qt.Key_F8:
            # F8 - Limpar Venda
            self.limpar_venda()
        elif event.key() == Qt.Key_F9:
            # F9 - Selecionar Forma de Pagamento
            self.selecionar_forma_pagamento()
        elif event.key() == Qt.Key_F11:
            # F11 - Debug da estrutura das tabelas (hidden feature)
            self.debug_estrutura_tabelas()
        elif event.key() == Qt.Key_F12:
            # F12 - Testar conexão com banco (hidden feature)
            self.testar_conexao_banco()
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


    def mostrar_selecao_produtos(self, produtos):
        """Mostra um diálogo para selecionar entre vários produtos encontrados"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Produto")
        dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout(dialog)
        
        # Label informativo
        lbl_info = QLabel("Selecione um produto para adicionar ao carrinho:")
        layout.addWidget(lbl_info)
        
        # Tabela de produtos
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Código", "Nome", "Preço", "Estoque"])
        
        # Ajustar comportamento da tabela
        table.setSelectionBehavior(QTableWidget.SelectRows)  # Selecionar linha inteira
        table.setSelectionMode(QTableWidget.SingleSelection)  # Permitir apenas uma seleção
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Não permitir edição
        
        # Ajustar cabeçalhos
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Preencher a tabela com os produtos
        for row, produto in enumerate(produtos):
            table.insertRow(row)
            
            # Código (assumindo que está na primeira posição)
            codigo = str(produto[0]) if produto[0] is not None else ""
            table.setItem(row, 0, QTableWidgetItem(codigo))
            
            # Nome (assumindo que está na segunda posição, se existir)
            nome = str(produto[1]) if len(produto) > 1 and produto[1] is not None else ""
            table.setItem(row, 1, QTableWidgetItem(nome))
            
            # Preço (assumindo que está na terceira posição, se existir)
            if len(produto) > 2 and produto[2] is not None and isinstance(produto[2], (int, float)):
                preco = float(produto[2])
                preco_str = f"R$ {preco:.2f}".replace('.', ',')
                item_preco = QTableWidgetItem(preco_str)
                item_preco.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                table.setItem(row, 2, item_preco)
            else:
                table.setItem(row, 2, QTableWidgetItem(""))
            
            # Estoque (assumindo que está na quarta posição, se existir)
            if len(produto) > 3 and produto[3] is not None and isinstance(produto[3], (int, float)):
                estoque = int(produto[3])
                table.setItem(row, 3, QTableWidgetItem(str(estoque)))
            else:
                table.setItem(row, 3, QTableWidgetItem(""))
        
        layout.addWidget(table)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(dialog.reject)
        
        btn_selecionar = QPushButton("Adicionar ao Carrinho (Enter)")
        btn_selecionar.setDefault(True)  # Tornar este o botão padrão para Enter
        
        def selecionar_e_fechar():
            rows = table.selectionModel().selectedRows()
            if rows:
                row = rows[0].row()
                # Obter dados do produto selecionado
                codigo = table.item(row, 0).text()
                nome = table.item(row, 1).text()
                preco_str = table.item(row, 2).text().replace("R$ ", "").replace(".", "").replace(",", ".")
                preco = float(preco_str) if preco_str else 0.0
                
                # Criar dicionário com os dados do produto
                produto = {
                    "codigo": codigo,
                    "nome": nome,
                    "preco_venda": preco
                }
                
                # Adicionar ao carrinho
                self.adicionar_produto_ao_carrinho(produto)
                
                # Limpar e resetar o combo
                self.combo_pesquisa.lineEdit().clear()
                self.combo_pesquisa.setCurrentIndex(0)
                
                dialog.accept()
        
        btn_selecionar.clicked.connect(selecionar_e_fechar)
        
        # Conectar duplo clique na tabela para selecionar
        table.doubleClicked.connect(selecionar_e_fechar)
        
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_selecionar)
        
        layout.addLayout(btn_layout)
        
        # Modificar o keyPressEvent do diálogo para capturar Enter
        original_key_press = dialog.keyPressEvent
        
        def new_key_press(event):
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                selecionar_e_fechar()
            else:
                original_key_press(event)
        
        dialog.keyPressEvent = new_key_press
        
        # Selecionar a primeira linha automaticamente
        if table.rowCount() > 0:
            table.selectRow(0)
        
        # Mostrar o diálogo
        dialog.exec_()

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
        self.table_itens.setColumnCount(6)
        self.table_itens.setHorizontalHeaderLabels(["ITEM", "ID", "PRODUTO", "QTD", "VALOR", "TOTAL"])
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
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # TOTAL
        
        # Definir larguras fixas
        self.table_itens.setColumnWidth(3, 58)  # Largura fixa da coluna QTD
        self.table_itens.setColumnWidth(4, 100)

        left_layout.addWidget(self.table_itens, 1)

        # --- Rodapé Esquerdo (Desconto e Acréscimo) ---
        bottom_left_frame = QFrame()
        bottom_left_layout = QHBoxLayout(bottom_left_frame)
        bottom_left_layout.setContentsMargins(5, 5, 5, 5)

        # Desconto com botão de edição - ADICIONADO F5
        desconto_layout = QHBoxLayout()
        self.lbl_desconto = QLabel("Desconto: R$ 0,00 (F5)")
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
        btn_editar_desconto.setToolTip("Editar desconto (F5)")
        btn_editar_desconto.clicked.connect(self.editar_desconto)
        desconto_layout.addWidget(btn_editar_desconto)
        bottom_left_layout.addLayout(desconto_layout)
        
        # Acréscimo com botão de edição - ADICIONADO F6
        acrescimo_layout = QHBoxLayout()
        self.lbl_acrescimo = QLabel("Acréscimo: R$ 0,00 (F6)")
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
        btn_editar_acrescimo.setToolTip("Editar acréscimo (F6)")
        btn_editar_acrescimo.clicked.connect(self.editar_acrescimo)
        acrescimo_layout.addWidget(btn_editar_acrescimo)
        bottom_left_layout.addLayout(acrescimo_layout)
        
        # Adicionar espaço expansível
        bottom_left_layout.addStretch(1)
        
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
        # Esconder widget de sugestões
        self.widget_sugestoes.hide()
        
        codigo = self.entry_cod_barras.text().strip()
        if codigo:
            self.buscar_produto_por_codigo_barras(codigo)

    def buscar_produto_por_codigo_barras(self, codigo_barras):
        """Busca um produto pelo código de barras no banco de dados - SEM CONFIRMAÇÃO DUPLA"""
        try:
            # ===== FUNCIONALIDADE MELHORADA: Detectar quantidade =====
            quantidade_personalizada = 1  # Quantidade padrão
            codigo_original = codigo_barras.strip()
            
            print(f"🔍 Processando código original: '{codigo_original}'")
            
            # Suporte para múltiplos formatos:
            # 1. *10 78 (asterisco + quantidade + espaço + código)
            # 2. 10*78 (quantidade + asterisco + código) 
            # 3. 10* 78 (quantidade + asterisco + espaço + código)
            
            if "*" in codigo_original:
                try:
                    # Padrão 1: *quantidade código
                    if codigo_original.startswith("*"):
                        partes = codigo_original.split(" ", 1)
                        if len(partes) == 2:
                            quantidade_str = partes[0][1:]  # Remove o *
                            codigo_barras = partes[1].strip()
                            quantidade_personalizada = int(quantidade_str)
                            print(f"🔢 Formato *quantidade código: {quantidade_personalizada} x {codigo_barras}")
                    
                    # Padrão 2 e 3: quantidade*código
                    else:
                        partes_asterisco = codigo_original.split("*", 1)
                        if len(partes_asterisco) == 2:
                            quantidade_str = partes_asterisco[0].strip()
                            codigo_barras = partes_asterisco[1].strip()
                            
                            if quantidade_str.isdigit():
                                quantidade_personalizada = int(quantidade_str)
                                print(f"🔢 Formato quantidade*código: {quantidade_personalizada} x {codigo_barras}")
                            else:
                                raise ValueError("Quantidade inválida")
                    
                    # Validações
                    if quantidade_personalizada <= 0:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "Quantidade Inválida", 
                                        f"A quantidade deve ser maior que zero. Você digitou: {quantidade_personalizada}")
                        self.entry_cod_barras.clear()
                        self.entry_cod_barras.setFocus()
                        return False
                    
                    if quantidade_personalizada > 9999:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "Quantidade Muito Alta", 
                                        f"A quantidade máxima é 9999. Você digitou: {quantidade_personalizada}")
                        self.entry_cod_barras.clear()
                        self.entry_cod_barras.setFocus()
                        return False
                            
                except ValueError:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Formato Inválido", 
                                    "Formatos válidos:\n• 10*78 (quantidade*código)\n• *10 78 (*quantidade código)")
                    self.entry_cod_barras.clear()
                    self.entry_cod_barras.setFocus()
                    return False
            
            # ===== BUSCA DO PRODUTO (código existente) =====
            codigo_limpo = ''.join(c for c in codigo_barras if c.isdigit())
            print(f"Buscando produto com código: {codigo_barras}, código limpo: {codigo_limpo}")
            
            try:
                from base.banco import buscar_produto_por_barras, buscar_produto_por_codigo
            except ImportError as e:
                print(f"Erro ao importar funções do banco: {e}")
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from base.banco import buscar_produto_por_barras, buscar_produto_por_codigo
                except ImportError as e2:
                    print(f"Erro ao importar módulos alternativos: {e2}")
                    def buscar_produto_por_barras(codigo): return None
                    def buscar_produto_por_codigo(codigo): return None
            
            # Buscar produto
            produto = buscar_produto_por_barras(codigo_limpo)
            print(f"Resultado busca por código de barras: {produto}")
            
            if not produto:
                result = buscar_produto_por_codigo(codigo_limpo)
                print(f"Resultado busca por código: {result}")
                
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
            
            # ===== ADICIONAR PRODUTO COM QUANTIDADE - SEM CONFIRMAÇÃO DUPLA =====
            if produto:
                # REMOVER A CONFIRMAÇÃO AQUI - apenas adicionar diretamente
                print(f"✅ Produto encontrado, adicionando {quantidade_personalizada} unidades...")
                
                # Verificar se produto já existe na tabela
                produto_existe = False
                codigo_produto = produto.get("codigo", "")
                
                for row_tabela in range(self.table_itens.rowCount()):
                    id_produto_tabela = self.table_itens.item(row_tabela, 1).text()
                    
                    if id_produto_tabela == codigo_produto:
                        # Produto já existe, aumentar a quantidade
                        produto_existe = True
                        
                        quantity_widget = self.table_itens.cellWidget(row_tabela, 3)
                        if quantity_widget and hasattr(quantity_widget, 'value'):
                            # Aumentar a quantidade
                            nova_quantidade = quantity_widget.value + quantidade_personalizada
                            quantity_widget.value = nova_quantidade
                            
                            # Atualizar o label da quantidade
                            for child in quantity_widget.children():
                                if hasattr(child, 'setText'):
                                    child.setText(str(nova_quantidade))
                                    break
                            
                            # Recalcular o total da linha
                            try:
                                valor_unitario = float(produto.get('preco_venda', 0))
                                novo_total = valor_unitario * nova_quantidade
                                novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                                valor_total_item = QTableWidgetItem(novo_total_str)
                                valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                self.table_itens.setItem(row_tabela, 5, valor_total_item)
                            except Exception as e:
                                print(f"Erro ao recalcular total: {e}")
                            
                            print(f"✅ Quantidade atualizada para {nova_quantidade} na linha existente")
                        break
                
                # Se o produto não existe, adicionar como nova linha
                if not produto_existe:
                    # Adicionar múltiplas vezes ou criar linha com quantidade
                    if quantidade_personalizada == 1:
                        self.adicionar_produto_ao_carrinho(produto)
                    else:
                        # Criar uma linha com a quantidade especificada
                        self.adicionar_produto_com_quantidade_especifica(produto, quantidade_personalizada)
                
                # Atualizar total geral
                self.atualizar_total()
                
                # MOSTRAR MENSAGEM SIMPLES (sem confirmação extra)
                if quantidade_personalizada > 1:
                    print(f"✅ {quantidade_personalizada} unidades adicionadas!")
                
                # Limpar e focar
                self.entry_cod_barras.clear()
                self.entry_cod_barras.setFocus()
                return True
            else:
                # Produto não encontrado
                from PyQt5.QtWidgets import QMessageBox
                msg = QMessageBox()
                msg.setWindowTitle("Produto não encontrado")
                msg.setText(f"O produto com código {codigo_barras} não foi encontrado no cadastro.")
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Yes)
                msg.setButtonText(QMessageBox.Yes, "Cadastrar Produto")
                
                resposta = msg.exec_()
                if resposta == QMessageBox.Yes:
                    self.abrir_cadastro_produto(codigo_barras)
                
                self.entry_cod_barras.clear()
                self.entry_cod_barras.setFocus()
                return False
                    
        except Exception as e:
            print(f"Erro ao buscar produto: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao buscar produto: {str(e)}")
            return False
    
    
    def adicionar_produto_com_quantidade_especifica(self, produto, quantidade):
        """Adiciona um produto com quantidade específica - SEM CONFIRMAÇÃO"""
        try:
            print(f"➕ === ADICIONANDO PRODUTO COM QUANTIDADE ESPECÍFICA ===")
            print(f"Produto: {produto}")
            print(f"Quantidade: {quantidade}")
            
            # Obter o próximo número de item
            proximo_item = self.table_itens.rowCount() + 1
            
            # Obter informações do produto
            id_produto = produto.get("codigo", "")
            nome = produto.get("nome", "")
            preco = float(produto.get("preco_venda", 0))
            
            # Formatar nome do produto (código + nome)
            nome_formatado = f"{id_produto} - {nome}"
            
            print(f"📝 Dados formatados:")
            print(f"  Item: {proximo_item}")
            print(f"  ID: {id_produto}")
            print(f"  Nome: {nome_formatado}")
            print(f"  Quantidade: {quantidade}")
            print(f"  Preço: {preco}")
            
            # Adicionar à tabela com a quantidade especificada (SEM CONFIRMAÇÃO)
            self.add_item_tabela_com_quantidade(proximo_item, id_produto, nome_formatado, quantidade, preco)
            
            print(f"✅ Produto adicionado com {quantidade} unidades: {nome_formatado}")
            
        except Exception as e:
            print(f"❌ Erro ao adicionar produto com quantidade específica: {e}")
            import traceback
            traceback.print_exc()

    def add_item_tabela_com_quantidade(self, item, id_prod, produto, qtd, valor):
        """Adiciona item na tabela com quantidade inicial específica - VERSÃO FINAL"""
        print(f"📊 === ADICIONANDO ITEM NA TABELA ===")
        print(f"Item: {item}, ID: {id_prod}, Produto: {produto}, Qtd: {qtd}, Valor: {valor}")
        
        row_position = self.table_itens.rowCount()
        self.table_itens.insertRow(row_position)

        # ITEM
        item_widget = QTableWidgetItem(str(item))
        item_widget.setTextAlignment(Qt.AlignCenter)
        self.table_itens.setItem(row_position, 0, item_widget)
        
        # ID
        id_widget = QTableWidgetItem(str(id_prod))
        id_widget.setTextAlignment(Qt.AlignCenter)
        self.table_itens.setItem(row_position, 1, id_widget)
        
        # PRODUTO
        self.table_itens.setItem(row_position, 2, QTableWidgetItem(produto))
        
        # ===== QTD (WIDGET COM QUANTIDADE INICIAL CORRETA) =====
        quantity_layout = QHBoxLayout()
        quantity_layout.setContentsMargins(0, 0, 0, 0)
        quantity_layout.setSpacing(0)
        
        quantity_widget = QWidget()
        quantity_widget.setMaximumWidth(60)
        quantity_widget.setLayout(quantity_layout)
        
        # Botão -
        btn_minus = QPushButton("-")
        btn_minus.setFixedSize(16, 16)
        btn_minus.setStyleSheet("""
            QPushButton {
                background-color: #F44336; color: white; font-weight: bold;
                border: none; border-radius: 1px; font-size: 9px;
            }
        """)
        
        # Label com quantidade inicial - USAR QUANTIDADE DO PARÂMETRO!
        lbl_value = QLabel(str(qtd))
        lbl_value.setFixedWidth(16)
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet("""
            QLabel {
                background-color: white; font-size: 10px; font-weight: bold;
            }
        """)
        
        # Botão +
        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(16, 16)
        btn_plus.setStyleSheet("""
            QPushButton {
                background-color: #00BCD4; color: white; font-weight: bold;
                border: none; border-radius: 1px; font-size: 9px;
            }
        """)
        
        quantity_layout.addWidget(btn_minus)
        quantity_layout.addWidget(lbl_value)
        quantity_layout.addWidget(btn_plus)
        
        # CRUCIAL: Definir o valor inicial correto!
        quantity_widget.value = qtd  # ← USAR A QUANTIDADE PASSADA!
        
        print(f"🔢 Valor inicial do widget: {quantity_widget.value}")
        
        # Funções de incremento/decremento SEM CONFIRMAÇÃO EXTRA
        def increase_value():
            quantity_widget.value += 1
            lbl_value.setText(str(quantity_widget.value))
            # Recalcular total
            novo_total = valor * quantity_widget.value
            novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
            valor_total_item = QTableWidgetItem(novo_total_str)
            valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_itens.setItem(row_position, 5, valor_total_item)
            self.atualizar_total()

        def decrease_value():
            if quantity_widget.value == 1:
                # Apenas uma confirmação simples para remoção
                from PyQt5.QtWidgets import QMessageBox
                if QMessageBox.question(self, "Remover Produto", "Deseja remover esse produto?") == QMessageBox.Yes:
                    self.table_itens.removeRow(row_position)
                    self.atualizar_total()
            else:
                quantity_widget.value -= 1
                lbl_value.setText(str(quantity_widget.value))
                # Recalcular total
                novo_total = valor * quantity_widget.value
                novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                valor_total_item = QTableWidgetItem(novo_total_str)
                valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_itens.setItem(row_position, 5, valor_total_item)
                self.atualizar_total()

        btn_plus.clicked.connect(increase_value)
        btn_minus.clicked.connect(decrease_value)
        quantity_widget.get_value = lambda: quantity_widget.value
        
        self.table_itens.setCellWidget(row_position, 3, quantity_widget)
        
        # VALOR UNITÁRIO
        valor_str = f"R$ {valor:.2f}".replace('.', ',')
        valor_item = QTableWidgetItem(valor_str)
        valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_itens.setItem(row_position, 4, valor_item)

        # TOTAL - USAR QUANTIDADE INICIAL CORRETA!
        valor_total = valor * qtd  # ← QUANTIDADE DO PARÂMETRO!
        valor_total_str = f"R$ {valor_total:.2f}".replace('.', ',')
        valor_total_item = QTableWidgetItem(valor_total_str)
        valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_itens.setItem(row_position, 5, valor_total_item)
        
        print(f"💰 Valor total: {valor} × {qtd} = {valor_total}")
        print(f"✅ Item adicionado na linha {row_position} com {qtd} unidades")

    # MÉTODO ADICIONAL: Para adicionar aos métodos da classe PDVWindow
    def adicionar_produto_ao_carrinho_com_quantidade(self, produto, quantidade):
        """Adiciona o produto encontrado à tabela de itens com quantidade específica"""
        # Obter o próximo número de item
        proximo_item = self.table_itens.rowCount() + 1
        
        # Obter informações do produto
        id_produto = produto.get("codigo", "")
        nome = produto.get("nome", "")
        preco = float(produto.get("preco_venda", 0))
        
        # Formatar nome do produto (código + nome)
        nome_formatado = f"{id_produto} - {nome}"
        
        # Adicionar à tabela com a quantidade especificada
        self.add_item_tabela_com_quantidade(proximo_item, id_produto, nome_formatado, quantidade, preco)
        
        # Atualizar o total
        self.atualizar_total()
        
        # Focar novamente no campo de código de barras para o próximo produto
        self.entry_cod_barras.setFocus()

    def mostrar_sugestoes_melhorado(self, codigo_parcial, produtos):
        """Versão melhorada do mostrar_sugestoes que exibe a quantidade"""
        print(f"\n🎨 === MOSTRANDO SUGESTÕES MELHORADAS ===")
        print(f"Código parcial: {codigo_parcial}")
        print(f"Produtos recebidos: {len(produtos)}")
        
        self.lista_sugestoes.clear()
        self.produtos_data = []
        
        if not produtos or len(produtos) == 0:
            print("❌ Nenhum produto para mostrar")
            self.hide()
            return
        
        # ===== OBTER QUANTIDADE SELECIONADA =====
        quantidade_info = ""
        quantidade = getattr(self, 'quantidade_selecionada', 1)
        
        if quantidade > 1:
            quantidade_info = f" (Qtd: {quantidade})"
            print(f"🔢 Mostrando sugestões com quantidade: {quantidade}")
        
        # Adicionar produtos à lista
        for i, produto in enumerate(produtos):
            try:
                print(f"📦 Processando produto {i+1}: {produto}")
                
                # Extrair informações do produto
                codigo_barras = str(produto[0]) if len(produto) > 0 and produto[0] else ""
                codigo_produto = str(produto[1]) if len(produto) > 1 and produto[1] else ""
                nome_produto = str(produto[2]) if len(produto) > 2 and produto[2] else "Produto sem nome"
                
                # Obter preço
                preco = 0.0
                if len(produto) > 3 and produto[3] is not None:
                    try:
                        preco = float(produto[3])
                    except (ValueError, TypeError):
                        preco = 0.0
                
                print(f"  ✅ Código Barras: {codigo_barras}")
                print(f"  ✅ Código Produto: {codigo_produto}")
                print(f"  ✅ Nome: {nome_produto[:30]}...")
                print(f"  ✅ Preço: {preco}")
                
                # Formatar preço
                preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
                
                # ===== CRIAR TEXTO COM QUANTIDADE DESTACADA =====
                if codigo_barras and codigo_barras != "None" and codigo_barras != "":
                    texto_item = f"🔗 {codigo_barras} | {codigo_produto} - {nome_produto[:35]} | {preco_formatado}{quantidade_info}"
                else:
                    texto_item = f"📦 {codigo_produto} - {nome_produto[:40]} | {preco_formatado}{quantidade_info}"
                
                print(f"  📝 Texto: {texto_item}")
                
                # Adicionar item à lista
                item = QListWidgetItem(texto_item)
                
                # ===== TOOLTIP COM INFORMAÇÕES DETALHADAS =====
                tooltip_text = f"Código: {codigo_produto}\nNome: {nome_produto}\nPreço: {preco_formatado}"
                if quantidade > 1:
                    tooltip_text += f"\nQuantidade a adicionar: {quantidade}"
                    total_item = preco * quantidade
                    total_formatado = f"R$ {total_item:.2f}".replace('.', ',')
                    tooltip_text += f"\nTotal do item: {total_formatado}"
                
                item.setToolTip(tooltip_text)
                self.lista_sugestoes.addItem(item)
                
                # Armazenar dados do produto
                self.produtos_data.append({
                    'codigo_barras': codigo_barras,
                    'codigo': codigo_produto,
                    'nome': nome_produto,
                    'preco_venda': preco
                })
                
            except Exception as e:
                print(f"❌ Erro ao processar produto {i+1}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Mostrar o widget se houver itens
        if self.lista_sugestoes.count() > 0:
            print(f"✅ Exibindo widget com {self.lista_sugestoes.count()} itens")
            self.posicionar_widget()
            self.show()
            self.lista_sugestoes.setCurrentRow(0)
            print("✅ Widget exibido!")
        else:
            print("❌ Nenhum item para exibir")
            self.hide()


    def selecionar_produto_melhorado(self):
        """Versão melhorada da seleção que suporta quantidade"""
        try:
            row = self.lista_sugestoes.currentRow()
            print(f"🎯 Selecionando produto da linha {row}")
            
            if 0 <= row < len(self.produtos_data):
                produto = self.produtos_data[row]
                print(f"📦 Produto selecionado: {produto}")
                
                # ===== OBTER QUANTIDADE SELECIONADA =====
                quantidade_para_adicionar = getattr(self, 'quantidade_selecionada', 1)
                
                if quantidade_para_adicionar > 1:
                    print(f"🔢 Adicionando {quantidade_para_adicionar} unidades do produto")
                    
                    # Confirmar quantidade alta
                    from PyQt5.QtWidgets import QMessageBox
                    nome_produto = produto.get('nome', 'Produto')
                    preco = produto.get('preco_venda', 0)
                    total_item = preco * quantidade_para_adicionar
                    
                    resposta = QMessageBox.question(
                        self.parent_pdv,
                        "Confirmar Quantidade",
                        f"Adicionar {quantidade_para_adicionar} unidades de:\n{nome_produto}\n\n"
                        f"Preço unitário: R$ {preco:.2f}\n"
                        f"Total do item: R$ {total_item:.2f}",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if resposta == QMessageBox.No:
                        print("❌ Usuário cancelou a adição com quantidade")
                        self.hide()
                        if self.parent_pdv:
                            self.parent_pdv.entry_cod_barras.clear()
                            self.parent_pdv.entry_cod_barras.setFocus()
                        return
                    
                    # ===== VERIFICAR SE PRODUTO JÁ EXISTE =====
                    produto_existe = False
                    codigo_produto = produto.get('codigo', '')
                    
                    for row_tabela in range(self.parent_pdv.table_itens.rowCount()):
                        id_produto_tabela = self.parent_pdv.table_itens.item(row_tabela, 1).text()
                        
                        if id_produto_tabela == codigo_produto:
                            # Produto já existe, aumentar a quantidade
                            produto_existe = True
                            
                            quantity_widget = self.parent_pdv.table_itens.cellWidget(row_tabela, 3)
                            if quantity_widget and hasattr(quantity_widget, 'value'):
                                nova_quantidade = quantity_widget.value + quantidade_para_adicionar
                                quantity_widget.value = nova_quantidade
                                
                                # Atualizar o label da quantidade
                                for child in quantity_widget.children():
                                    if hasattr(child, 'setText'):
                                        child.setText(str(nova_quantidade))
                                        break
                                
                                # Recalcular o total da linha
                                try:
                                    valor_unitario = float(produto.get('preco_venda', 0))
                                    novo_total = valor_unitario * nova_quantidade
                                    novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                                    valor_total_item = QTableWidgetItem(novo_total_str)
                                    valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                    self.parent_pdv.table_itens.setItem(row_tabela, 5, valor_total_item)
                                except Exception as e:
                                    print(f"Erro ao recalcular total: {e}")
                                
                                print(f"✅ Quantidade atualizada para {nova_quantidade} na linha existente")
                            break
                    
                    # Se o produto não existe, adicionar nova linha
                    if not produto_existe:
                        if self.parent_pdv:
                            self.parent_pdv.adicionar_produto_com_quantidade_especifica(produto, quantidade_para_adicionar)
                            print(f"✅ Nova linha criada com {quantidade_para_adicionar} unidades!")
                    
                    # Atualizar o total geral
                    if self.parent_pdv:
                        self.parent_pdv.atualizar_total()
                    
                    # Mostrar mensagem de sucesso
                    QMessageBox.information(
                        self.parent_pdv,
                        "Produto Adicionado", 
                        f"✅ {quantidade_para_adicionar} unidades adicionadas com sucesso!\n"
                        f"Total do item: R$ {total_item:.2f}"
                    )
                    
                else:
                    # Quantidade normal (1 unidade)
                    if self.parent_pdv:
                        self.parent_pdv.adicionar_produto_ao_carrinho(produto)
                        print("✅ 1 unidade adicionada ao carrinho!")
                
                # Limpar e focar no campo
                if self.parent_pdv:
                    self.parent_pdv.entry_cod_barras.clear()
                    self.parent_pdv.entry_cod_barras.setFocus()
                
                # Esconder widget
                self.hide()
            else:
                print(f"❌ Linha inválida: {row}")
        except Exception as e:
            print(f"❌ Erro ao selecionar produto: {e}")
            import traceback
            traceback.print_exc()

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
            
            # NOVO: Recalcular o total da linha
            try:
                novo_total = valor * quantity_widget.value
                novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                valor_total_item = QTableWidgetItem(novo_total_str)
                valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_itens.setItem(row_position, 5, valor_total_item)
            except Exception as e:
                print(f"Erro ao recalcular total: {e}")
            
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
                
                # NOVO: Recalcular o total da linha
                try:
                    novo_total = valor * quantity_widget.value
                    novo_total_str = f"R$ {novo_total:.2f}".replace('.', ',')
                    valor_total_item = QTableWidgetItem(novo_total_str)
                    valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table_itens.setItem(row_position, 5, valor_total_item)
                except Exception as e:
                    print(f"Erro ao recalcular total: {e}")
                
                self.atualizar_total()

        # Conectar sinais (MANTENHA essas linhas)
        btn_plus.clicked.connect(increase_value)
        btn_minus.clicked.connect(decrease_value)
        
        # Função para obter o valor
        def get_value():
            return quantity_widget.value
        
        # Adicionar método para acessar o valor
        quantity_widget.get_value = get_value
        
        # Adicionar à tabela
        self.table_itens.setCellWidget(row_position, 3, quantity_widget)
        
        # Valor unitário
        valor_str = f"R$ {valor:.2f}".replace('.', ',')
        valor_item = QTableWidgetItem(valor_str)
        valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_itens.setItem(row_position, 4, valor_item)

        # TOTAL (valor unitário × quantidade) - TOTAL
        valor_total = valor * qtd
        valor_total_str = f"R$ {valor_total:.2f}".replace('.', ',')
        valor_total_item = QTableWidgetItem(valor_total_str)
        valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_itens.setItem(row_position, 5, valor_total_item)

    def criar_area_direita(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)    
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        # --- Botões Superiores Direita com SVG ---
        top_right_layout = QHBoxLayout()
        
        # Botão 1: Listar Clientes - ADICIONADO F1
        btn_clientes = QPushButton("Clientes (F1)")
        btn_clientes.setObjectName("SidebarButton1")
        btn_clientes.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["user"], "#FFFFFF")))
        btn_clientes.setIconSize(QSize(24, 24))
        btn_clientes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_clientes.setCursor(QCursor(Qt.PointingHandCursor))
        btn_clientes.setToolTip("Listar Clientes (F1)")
        btn_clientes.clicked.connect(self.listar_clientes)
        top_right_layout.addWidget(btn_clientes)
        
        # Botão 2: Listar Produtos - ADICIONADO F2
        btn_produtos = QPushButton("Produtos (F2)")
        btn_produtos.setObjectName("SidebarButton2")
        btn_produtos.setIcon(QIcon(self.create_svg_icon(SVG_ICONS["list"], "#FFFFFF")))
        btn_produtos.setIconSize(QSize(24, 24))
        btn_produtos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_produtos.setCursor(QCursor(Qt.PointingHandCursor))
        btn_produtos.setToolTip("Listar Produtos (F2)")
        btn_produtos.clicked.connect(self.listar_produtos)
        top_right_layout.addWidget(btn_produtos)
        
        right_layout.addLayout(top_right_layout)

        right_layout.addStretch(1)  # Empurra o resto para baixo

        # --- Total ---
        lbl_total_texto = QLabel("TOTAL R$:")
        lbl_total_texto.setObjectName("TotalLabel")
        right_layout.addWidget(lbl_total_texto)

        self.lbl_total_valor = QLabel("0,00")
        self.lbl_total_valor.setObjectName("TotalValue")
        right_layout.addWidget(self.lbl_total_valor)

        # --- Forma de Pagamento ---
        lbl_forma_pagamento = QLabel("Forma de Pagamento (F9)")  # MODIFICADO - adicionado (F9)
        lbl_forma_pagamento.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(lbl_forma_pagamento)
        
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItem("Selecione o Tipo de pagamento (F9)")  # MODIFICADO - adicionado (F9)
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
        
        self.combo_pagamento.setCurrentIndex(0)
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
        
        # Inicialmente oculta o widget de troco
        self.troco_widget.setVisible(False)
        self.lbl_valor_recebido.setVisible(False)
        self.entry_valor_recebido.setVisible(False)

        # --- Botão Finalizar SIMPLES (SEM CUPOM) ---
        self.btn_finalizar = QPushButton("Finalizar R$ 0,00 (F4)")
        self.btn_finalizar.setObjectName("FinalizarButton")
        check_icon = self.create_svg_icon(SVG_ICONS["check"], "#FFFFFF")
        self.btn_finalizar.setIcon(QIcon(check_icon))
        self.btn_finalizar.setIconSize(QSize(24, 24))
        self.btn_finalizar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_finalizar.clicked.connect(self.finalizar_venda_simples)  # MUDOU AQUI
        right_layout.addWidget(self.btn_finalizar)

        # --- Botão adicional para Limpar Venda (F8) ---
        self.btn_limpar_venda = QPushButton("Limpar Venda (F8)")
        self.btn_limpar_venda.setObjectName("ClearButton")
        self.btn_limpar_venda.setStyleSheet("""
            QPushButton#ClearButton { 
                background-color: #f44336; 
                color: white; 
                font-size: 14px; 
                font-weight: bold; 
                padding: 10px; 
                border: none; 
                border-radius: 3px; 
                margin-top: 10px;
            }
            QPushButton#ClearButton:hover { 
                background-color: #e53935; 
            }
        """)
        self.btn_limpar_venda.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_limpar_venda.clicked.connect(self.limpar_venda)
        right_layout.addWidget(self.btn_limpar_venda)

        return right_widget
    
    def selecionar_forma_pagamento(self):
        """Abre um diálogo para seleção rápida da forma de pagamento"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout
            from PyQt5.QtWidgets import QLabel, QMessageBox
            from PyQt5.QtCore import Qt
            
            # Criar diálogo
            dialog = QDialog(self)
            dialog.setWindowTitle("Selecionar Forma de Pagamento (F9)")
            dialog.setMinimumSize(400, 500)
            dialog.setMaximumSize(450, 600)
            
            # Layout principal
            layout = QVBoxLayout(dialog)
            
            # Título
            titulo = QLabel("Selecione a forma de pagamento:")
            titulo.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
            layout.addWidget(titulo)
            
            # Lista de formas de pagamento
            lista = QListWidget()
            lista.setStyleSheet("""
                QListWidget {
                    font-size: 12px;
                    padding: 5px;
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #EEEEEE;
                }
                QListWidget::item:selected {
                    background-color: #2196F3;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #E3F2FD;
                }
            """)
            
            # Adicionar itens da lista (exceto o primeiro que é o placeholder)
            formas_pagamento = [
                "01 - Dinheiro",
                "02 - Cheque", 
                "03 - Cartão de Crédito",
                "04 - Cartão de Débito",
                "05 - Crédito Loja",
                "06 - Crediário",
                "10 - Vale Alimentação",
                "11 - Vale Refeição",
                "12 - Vale Presente",
                "13 - Vale Combustível",
                "14 - Duplicata Mercantil",
                "15 - Boleto Bancário",
                "16 - Depósito Bancário",
                "17 - Pagamento Instantâneo (PIX)",
                "90 - Sem pagamento",
                "99 - Outros"
            ]
            
            for forma in formas_pagamento:
                item = QListWidgetItem(forma)
                lista.addItem(item)
            
            # Selecionar o item atual se houver algum selecionado
            indice_atual = self.combo_pagamento.currentIndex()
            if indice_atual > 0:  # Se não for o placeholder
                lista.setCurrentRow(indice_atual - 1)  # -1 porque a lista não tem o placeholder
            else:
                lista.setCurrentRow(0)  # Selecionar o primeiro por padrão
            
            layout.addWidget(lista)
            
            # Instruções
            instrucoes = QLabel("Use as setas ↑↓ para navegar e Enter para confirmar, ou Esc para cancelar")
            instrucoes.setStyleSheet("color: #666666; font-size: 10px; padding: 5px;")
            instrucoes.setAlignment(Qt.AlignCenter)
            layout.addWidget(instrucoes)
            
            # Botões
            button_layout = QHBoxLayout()
            
            btn_cancelar = QPushButton("Cancelar (Esc)")
            btn_cancelar.clicked.connect(dialog.reject)
            
            btn_confirmar = QPushButton("Confirmar (Enter)")
            btn_confirmar.setDefault(True)
            btn_confirmar.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            
            def confirmar_selecao():
                row = lista.currentRow()
                if row >= 0:
                    # Atualizar o combo principal (+1 porque o combo tem o placeholder no índice 0)
                    self.combo_pagamento.setCurrentIndex(row + 1)
                    # Atualizar layout de pagamento
                    self.atualizar_layout_pagamento(row + 1)
                    dialog.accept()
            
            btn_confirmar.clicked.connect(confirmar_selecao)
            
            button_layout.addWidget(btn_cancelar)
            button_layout.addStretch()
            button_layout.addWidget(btn_confirmar)
            
            layout.addLayout(button_layout)
            
            # Eventos de teclado
            def handle_key_press(event):
                if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                    confirmar_selecao()
                elif event.key() == Qt.Key_Escape:
                    dialog.reject()
                elif event.key() == Qt.Key_Up:
                    current = lista.currentRow()
                    if current > 0:
                        lista.setCurrentRow(current - 1)
                elif event.key() == Qt.Key_Down:
                    current = lista.currentRow()
                    if current < lista.count() - 1:
                        lista.setCurrentRow(current + 1)
                else:
                    # Para teclas numéricas 0-9, selecionar a forma correspondente
                    if event.text().isdigit():
                        digit = int(event.text())
                        # Mapear dígitos para índices das formas de pagamento mais comuns
                        digit_map = {
                            1: 0,   # 01 - Dinheiro
                            2: 1,   # 02 - Cheque
                            3: 2,   # 03 - Cartão de Crédito
                            4: 3,   # 04 - Cartão de Débito
                            5: 4,   # 05 - Crédito Loja
                            6: 5,   # 06 - Crediário
                            0: 13,  # PIX (17 - Pagamento Instantâneo)
                        }
                        
                        if digit in digit_map and digit_map[digit] < lista.count():
                            lista.setCurrentRow(digit_map[digit])
                            confirmar_selecao()  # Confirmar automaticamente
            
            # Conectar evento de duplo clique
            lista.itemDoubleClicked.connect(confirmar_selecao)
            
            # Aplicar evento de teclado ao diálogo
            dialog.keyPressEvent = handle_key_press
            
            # Focar na lista
            lista.setFocus()
            
            # Mostrar diálogo
            dialog.exec_()
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir seleção de pagamento: {str(e)}")
            print(f"Erro ao abrir seleção de pagamento: {e}")

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

    def atualizar_botao_finalizar(self, valor_total=None):
        """Atualiza o texto do botão finalizar garantindo que o indicador (F4) esteja sempre presente"""
        if valor_total is None:
            valor_total = self.lbl_total_valor.text()
            
        self.btn_finalizar.setText(f"Finalizar R$ {valor_total} (F4)")

    def atualizar_total(self):
        """Atualiza o valor total da compra"""
        # Calcular o subtotal (soma dos itens)
        subtotal = 0.0
        for row in range(self.table_itens.rowCount()):
            # Obter o valor total da linha na coluna TOTAL (índice 5)
            total_texto = self.table_itens.item(row, 5).text()
            
            # Converter o valor de texto para float
            try:
                # Remover "R$ " e substituir vírgula por ponto
                total_limpo = total_texto.replace("R$ ", "").replace(".", "").replace(",", ".")
                total = float(total_limpo)
                # Adicionar ao subtotal
                subtotal += total
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
        
        # Atualizar o botão finalizar com o novo método dedicado
        self.atualizar_botao_finalizar(total_formatado)
        
        # Recalcular o troco se houver valor recebido
        if self.entry_valor_recebido.text():
            self.calcular_troco()

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
            
            # Obter o valor recebido - CORRIGIDO: apenas um replace para 'R$ '
            valor_recebido_text = self.entry_valor_recebido.text().replace('R$ ', '').replace('.', '').replace(',', '.')
            
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
            
            # Atualizar o texto do botão finalizar - ADICIONADO (F4)
            total_formatado = f"{total:.2f}".replace('.', ',')
            self.btn_finalizar.setText(f"Finalizar R$ {total_formatado} (F4)")
            
        except (ValueError, TypeError) as e:
            # Em caso de erro de conversão, ocultar o troco
            self.troco_widget.setVisible(False)
        except Exception as e:
            print(f"Erro ao calcular troco: {e}")
            self.troco_widget.setVisible(False)

    def testar_conexao_banco(self):
        """Testa a conexão com o banco e a estrutura das tabelas necessárias"""
        try:
            from base.banco import execute_query
            
            print("\n🔍 === TESTANDO CONEXÃO E ESTRUTURA DO BANCO ===")
            
            # Teste 1: Conexão básica
            try:
                result = execute_query("SELECT 1 FROM RDB$DATABASE")
                print("✅ Conexão com banco estabelecida")
            except Exception as e:
                print(f"❌ Erro de conexão: {e}")
                return False
            
            # Teste 2: Existência das tabelas
            tabelas_necessarias = ['VENDAS', 'VENDAS_ITENS', 'PRODUTOS']
            
            for tabela in tabelas_necessarias:
                try:
                    query = f"""
                    SELECT COUNT(*) FROM RDB$RELATIONS 
                    WHERE RDB$RELATION_NAME = '{tabela}' 
                    AND RDB$RELATION_TYPE = 0
                    """
                    result = execute_query(query)
                    
                    if result and result[0][0] > 0:
                        print(f"✅ Tabela {tabela} existe")
                    else:
                        print(f"❌ Tabela {tabela} não encontrada")
                        return False
                        
                except Exception as e:
                    print(f"❌ Erro ao verificar tabela {tabela}: {e}")
                    return False
            
            print("✅ Todas as verificações passaram")
            return True
            
        except Exception as e:
            print(f"❌ Erro geral no teste de conexão: {e}")
            return False

    def debug_estrutura_tabelas(self):
        """Função para debugar a estrutura das tabelas VENDAS e VENDAS_ITENS"""
        try:
            from base.banco import execute_query
            
            print("\n" + "="*60)
            print("🔍 DEBUG: ESTRUTURA DAS TABELAS")
            print("="*60)
            
            # Verificar tabela VENDAS
            print("\n📋 TABELA VENDAS:")
            try:
                query_vendas = """
                SELECT RDB$FIELD_NAME, RDB$FIELD_POSITION
                FROM RDB$RELATION_FIELDS
                WHERE RDB$RELATION_NAME = 'VENDAS'
                ORDER BY RDB$FIELD_POSITION
                """
                
                result_vendas = execute_query(query_vendas)
                for pos, (field_name, position) in enumerate(result_vendas):
                    print(f"  {position}: {field_name.strip()}")
                    
            except Exception as e:
                print(f"❌ Erro ao obter estrutura da tabela VENDAS: {e}")
            
            # Verificar tabela VENDAS_ITENS
            print("\n📋 TABELA VENDAS_ITENS:")
            try:
                query_itens = """
                SELECT RDB$FIELD_NAME, RDB$FIELD_POSITION
                FROM RDB$RELATION_FIELDS
                WHERE RDB$RELATION_NAME = 'VENDAS_ITENS'
                ORDER BY RDB$FIELD_POSITION
                """
                
                result_itens = execute_query(query_itens)
                for pos, (field_name, position) in enumerate(result_itens):
                    print(f"  {position}: {field_name.strip()}")
                    
            except Exception as e:
                print(f"❌ Erro ao obter estrutura da tabela VENDAS_ITENS: {e}")
            
            # Verificar tabela PRODUTOS (para referência)
            print("\n📋 TABELA PRODUTOS:")
            try:
                query_produtos = """
                SELECT RDB$FIELD_NAME, RDB$FIELD_POSITION
                FROM RDB$RELATION_FIELDS
                WHERE RDB$RELATION_NAME = 'PRODUTOS'
                ORDER BY RDB$FIELD_POSITION
                """
                
                result_produtos = execute_query(query_produtos)
                for pos, (field_name, position) in enumerate(result_produtos):
                    print(f"  {position}: {field_name.strip()}")
                    
            except Exception as e:
                print(f"❌ Erro ao obter estrutura da tabela PRODUTOS: {e}")
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"❌ Erro geral no debug de estrutura: {e}")

    def finalizar_venda_simples(self):
        """
        Finaliza a venda: registra no banco, pergunta sobre CPF na nota e imprime o cupom fiscal.
        AGORA COM SUPORTE A TROCO!
        """
        try:
            # 1️⃣ Testa conexão com o banco
            print("🔍 Testando conexão com banco...")
            if not self.testar_conexao_banco():
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Erro",
                    "Erro na conexão com o banco de dados ou estrutura das tabelas."
                    "\nVerifique o console para mais detalhes.")
                return

            # 2️⃣ Obter e validar total da venda
            total_text = self.lbl_total_valor.text().replace('.', '').replace(',', '.')
            total = float(total_text) if total_text else 0.0
            if total <= 0:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "Não há itens para finalizar a venda.")
                return

            # 3️⃣ Obter forma de pagamento
            indice_pagamento = self.combo_pagamento.currentIndex()
            if indice_pagamento <= 0:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "Selecione uma forma de pagamento.")
                return
            forma_pagamento = self.combo_pagamento.currentText()

            # 4️⃣ NOVO: Calcular valor recebido e troco
            valor_recebido = None
            troco = None
            
            # Se a forma de pagamento for dinheiro, obter o valor recebido e calcular troco
            if forma_pagamento == "01 - Dinheiro":
                valor_recebido_text = self.entry_valor_recebido.text().replace('R$ ', '').replace('.', '').replace(',', '.')
                if not valor_recebido_text.strip():
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Aviso", "Digite o valor recebido em dinheiro.")
                    return
                
                valor_recebido = float(valor_recebido_text)
                if valor_recebido < total:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Aviso", "O valor recebido é menor que o total da venda.")
                    return
                
                # Calcular troco
                troco = valor_recebido - total
                print(f"💰 Valores calculados: Total={total:.2f}, Valor Recebido={valor_recebido:.2f}, Troco={troco:.2f}")
            
            # Para outras formas de pagamento com valor obrigatório
            formas_com_valor = ["02 - Cheque", "17 - Pagamento Instantâneo (PIX)"]
            if forma_pagamento in formas_com_valor:
                valor_recebido_text = self.entry_valor_recebido.text().replace('R$ ', '').replace('.', '').replace(',', '.')
                if not valor_recebido_text.strip():
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Aviso", f"Digite o valor recebido para pagamento com {forma_pagamento}.")
                    return
                
                valor_recebido = float(valor_recebido_text)
                troco = 0.0  # Não há troco para essas formas de pagamento
                print(f"💰 Pagamento sem troco: Total={total:.2f}, Valor Recebido={valor_recebido:.2f}")

            # 5️⃣ Verificar estoque (código existente mantido)
            try:
                from base.banco import execute_query
                structure_query = """
                    SELECT RDB$FIELD_NAME
                    FROM RDB$RELATION_FIELDS
                    WHERE RDB$RELATION_NAME = 'PRODUTOS'
                    ORDER BY RDB$FIELD_POSITION
                """
                produtos_fields = execute_query(structure_query)
                alternativas = ["ESTOQUE","QUANTIDADE_ESTOQUE","ESTOQUE_ATUAL","QTD","QUANTIDADE","SALDO","SALDO_ESTOQUE"]
                estoque_field = next((f[0].strip() for f in produtos_fields if f[0] and f[0].strip().upper() in alternativas), None)
                if estoque_field:
                    sem_estoque = []
                    for row in range(self.table_itens.rowCount()):
                        id_prod = self.table_itens.item(row,1).text()
                        qtd = self.table_itens.cellWidget(row,3).get_value()
                        nome = self.table_itens.item(row,2).text()
                        q = execute_query(f"SELECT {estoque_field} FROM PRODUTOS WHERE CODIGO = ?", (id_prod,))
                        if q and q[0][0] is not None and float(q[0][0]) < qtd:
                            sem_estoque.append((nome, float(q[0][0]), qtd))
                    if sem_estoque:
                        from PyQt5.QtWidgets import QMessageBox
                        msg = "Estoque insuficiente:\n" + '\n'.join(f"{n}: disp {e}, ped {p}" for n,e,p in sem_estoque)
                        escolha = QMessageBox.question(self, "Estoque Insuficiente", msg, QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
                        if escolha == QMessageBox.No:
                            return
            except Exception as e:
                print(f"Erro ao verificar estoque: {e}")

            # 6️⃣ Montar lista de itens
            itens = []
            for row in range(self.table_itens.rowCount()):
                itens.append({
                    'id_produto': self.table_itens.item(row,1).text(),
                    'produto': self.table_itens.item(row,2).text(),
                    'quantidade': self.table_itens.cellWidget(row,3).get_value(),
                    'valor_unitario': self.table_itens.item(row,4).text().replace('R$ ','').replace(',', '.')
                })

            # 7️⃣ Perguntar CPF na nota e registrar + imprimir cupom
            from cpf_nota import solicitar_tipo_cupom
            tipo, cpf = solicitar_tipo_cupom(total, self)
            if not tipo:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Cancelado", "Finalização de venda cancelada.")
                return

            # Registrar venda no banco e obter ID
            id_venda = self.registrar_venda_no_banco(
                total,                       # total primeiro, como o método espera
                forma_pagamento,             # forma de pagamento segundo
                itens,                       # lista de itens terceiro
                cpf if tipo=='COM_CPF' else None
            )

            # 8️⃣ MODIFICADO: Gerar e imprimir cupom fiscal COM TROCO
            from gerador_cupom import gerar_e_imprimir_cupom
            from datetime import datetime
            
            # Log dos valores que serão passados para impressão
            if valor_recebido is not None:
                print(f"💰 Enviando para impressão: Valor Recebido=R${valor_recebido:.2f}")
            if troco is not None:
                print(f"💰 Enviando para impressão: Troco=R${troco:.2f}")
            
            resultado = gerar_e_imprimir_cupom(
                id_venda=id_venda,
                tipo_cupom='FISCAL' if tipo=='COM_CPF' else 'NAO_FISCAL',
                cpf=cpf,
                data_venda=datetime.now(),
                itens=itens,
                total=total,
                forma_pagamento=forma_pagamento,
                imprimir_automaticamente=True,
                valor_recebido=valor_recebido,  # 🆕 NOVO PARÂMETRO!
                troco=troco                     # 🆕 NOVO PARÂMETRO!
            )
            
            if not resultado['sucesso']:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Impressão", f"Falha ao imprimir cupom:\n{resultado['mensagem']}")

            # 9️⃣ Confirmação e limpeza
            from PyQt5.QtWidgets import QMessageBox
            
            # Mensagem de confirmação mais informativa
            mensagem_sucesso = "Venda finalizada com sucesso!"
            if troco is not None and troco > 0:
                mensagem_sucesso += f"\n\n💰 Troco a devolver: R$ {troco:.2f}"
            elif valor_recebido is not None and valor_recebido == total:
                mensagem_sucesso += f"\n\n✅ Pagamento exato (sem troco)"
            
            QMessageBox.information(self, "Venda Finalizada", mensagem_sucesso)
            self.limpar_venda()
            return

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            print(f"ERRO NA FINALIZAÇÃO: {e}")
            import traceback; traceback.print_exc()
            self.debug_estrutura_tabelas()
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda:\n{e}\nVeja console para debug.")


    def registrar_venda_no_banco(self, total, forma_pagamento, itens, tipo_cupom="SEM_CUPOM", cpf=""):
        """Registra a venda na tabela VENDAS do banco de dados - SEM CUPOM"""
        try:
            from base.banco import execute_query
            from datetime import datetime
            
            # Imprimir informações para debug
            print("\n===== INICIANDO REGISTRO DE VENDA NO BANCO (SEM CUPOM) =====")
            print(f"Total: {total}, Forma de pagamento: {forma_pagamento}")
            print(f"Desconto: {self.valor_desconto}, Acréscimo: {self.valor_acrescimo}")
            print(f"Tipo: {tipo_cupom} (SEM CUPOM FISCAL)")
            print(f"Itens: {itens}")
            
            # Obter a data e hora atual
            now = datetime.now()
            data_venda = now.strftime("%Y-%m-%d")  # Formato para o banco: YYYY-MM-DD
            hora_venda = now.strftime("%H:%M:%S")  # Formato para o banco: HH:MM:SS
            
            print("\n----- REGISTRANDO A VENDA PRINCIPAL -----")
            
            # Primeiro, descobrir a estrutura da tabela VENDAS
            structure_query_vendas = """
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'VENDAS'
            ORDER BY RDB$FIELD_POSITION
            """
            
            try:
                vendas_fields = execute_query(structure_query_vendas)
                print(f"✅ Colunas encontradas na tabela VENDAS:")
                
                # Listar todas as colunas disponíveis
                available_vendas_columns = []
                for field in vendas_fields:
                    field_name = field[0].strip() if field[0] else ""
                    available_vendas_columns.append(field_name)
                    print(f"  - {field_name}")
                
                # Mapear possíveis nomes para cada coluna da tabela VENDAS
                vendas_column_mapping = {
                    'data_venda': ['DATA_VENDA', 'DATA', 'DT_VENDA'],
                    'hora_venda': ['HORA_VENDA', 'HORA', 'HR_VENDA'],
                    'id_cliente': ['ID_CLIENTE', 'CLIENTE_ID', 'CLIENTE'],
                    'id_vendedor': ['ID_VENDEDOR', 'VENDEDOR_ID', 'VENDEDOR'],
                    'valor_total': ['VALOR_TOTAL', 'TOTAL', 'VL_TOTAL'],
                    'desconto': ['DESCONTO', 'VL_DESCONTO', 'VALOR_DESCONTO'],
                    'valor_final': ['VALOR_FINAL', 'VL_FINAL', 'TOTAL_FINAL'],
                    'forma_pagamento': ['FORMA_PAGAMENTO', 'FORMA_PGTO', 'PAGAMENTO'],
                    'status': ['STATUS', 'SITUACAO', 'ST_VENDA']
                }
                
                # Encontrar os nomes reais das colunas para VENDAS
                real_vendas_columns = {}
                vendas_values = []
                vendas_placeholders = []
                
                for logical_name, alternatives in vendas_column_mapping.items():
                    found = False
                    for alt in alternatives:
                        if alt in available_vendas_columns:
                            real_vendas_columns[logical_name] = alt
                            print(f"✅ {logical_name} -> {alt}")
                            found = True
                            break
                    
                    if not found:
                        print(f"⚠️ Coluna não encontrada para {logical_name}, pulando...")
                        continue
                    
                    # Adicionar valor correspondente
                    if logical_name == 'data_venda':
                        vendas_values.append(data_venda)
                    elif logical_name == 'hora_venda':
                        vendas_values.append(hora_venda)
                    elif logical_name == 'id_cliente':
                        vendas_values.append(0)
                    elif logical_name == 'id_vendedor':
                        vendas_values.append(0)
                    elif logical_name == 'valor_total':
                        vendas_values.append(total + self.valor_desconto - self.valor_acrescimo)
                    elif logical_name == 'desconto':
                        vendas_values.append(self.valor_desconto)
                    elif logical_name == 'valor_final':
                        vendas_values.append(total)
                    elif logical_name == 'forma_pagamento':
                        vendas_values.append(forma_pagamento)
                    elif logical_name == 'status':
                        vendas_values.append("Finalizada")
                    
                    vendas_placeholders.append("?")
                
                # Construir a query de inserção dinamicamente
                column_names = ", ".join(real_vendas_columns.values())
                placeholders = ", ".join(vendas_placeholders)
                
                query_venda = f"""
                INSERT INTO VENDAS ({column_names}) VALUES ({placeholders})
                """
                
                print(f"📝 Query de venda construída: {query_venda}")
                print(f"📝 Valores: {vendas_values}")
                
                # Executar a inserção da venda
                execute_query(query_venda, vendas_values)
                
            except Exception as vendas_error:
                print(f"❌ Erro ao inserir venda com estrutura dinâmica: {vendas_error}")
                print("🔄 Tentando com estrutura padrão...")
                
                # FALLBACK: usar estrutura padrão
                query_venda = """
                INSERT INTO VENDAS (
                    DATA_VENDA, HORA_VENDA, ID_CLIENTE, ID_VENDEDOR, 
                    VALOR_TOTAL, DESCONTO, VALOR_FINAL, FORMA_PAGAMENTO, STATUS
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = [data_venda, hora_venda, 0, 0, 
                        total + self.valor_desconto - self.valor_acrescimo, 
                        self.valor_desconto, total, forma_pagamento, "Finalizada"]
                
                print(f"Executando query de inserção de venda (fallback): {query_venda}")
                print(f"Parâmetros: {params}")
                
                # Executar a inserção da venda
                execute_query(query_venda, params)
            
            # Obter o ID da venda inserida - melhorado
            try:
                # Primeiro tentar descobrir o nome da coluna ID
                id_column_query = """
                SELECT RDB$FIELD_NAME
                FROM RDB$RELATION_FIELDS
                WHERE RDB$RELATION_NAME = 'VENDAS'
                AND (RDB$FIELD_NAME LIKE '%ID%' OR RDB$FIELD_NAME LIKE '%VENDA%')
                ORDER BY RDB$FIELD_POSITION
                """
                
                id_columns = execute_query(id_column_query)
                id_field_name = None
                
                for col in id_columns:
                    field_name = col[0].strip()
                    if any(keyword in field_name.upper() for keyword in ['ID_VENDA', 'IDVENDA', 'ID']):
                        id_field_name = field_name
                        break
                
                if not id_field_name:
                    id_field_name = "ID_VENDA"  # fallback
                
                query_id = f"SELECT MAX({id_field_name}) FROM VENDAS"
                print(f"🔍 Buscando ID da venda com query: {query_id}")
                
                result = execute_query(query_id)
                id_venda = result[0][0] if result and result[0][0] else 0
                print(f"✅ ID da venda registrada: {id_venda}")
                
            except Exception as id_error:
                print(f"❌ Erro ao obter ID da venda: {id_error}")
                # Tentar fallback
                try:
                    query_id = "SELECT MAX(ID_VENDA) FROM VENDAS"
                    result = execute_query(query_id)
                    id_venda = result[0][0] if result and result[0][0] else 0
                    print(f"✅ ID da venda (fallback): {id_venda}")
                except:
                    print("❌ Não foi possível obter ID da venda")
                    id_venda = 1  # ID genérico para continuar
            
            print("\n----- REGISTRANDO OS ITENS DA VENDA -----")
            
            # Descobrir a estrutura real da tabela VENDAS_ITENS
            structure_query_itens = """
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'VENDAS_ITENS'
            ORDER BY RDB$FIELD_POSITION
            """
            
            try:
                vendas_itens_fields = execute_query(structure_query_itens)
                print(f"✅ Colunas encontradas na tabela VENDAS_ITENS:")
                
                # Listar todas as colunas disponíveis
                available_columns = []
                for field in vendas_itens_fields:
                    field_name = field[0].strip() if field[0] else ""
                    available_columns.append(field_name)
                    print(f"  - {field_name}")
                
                # Mapear possíveis nomes para cada tipo de coluna necessária
                column_mapping = {
                    'id_venda': ['ID_VENDA', 'VENDA_ID', 'IDVENDA'],
                    'id_produto': ['ID_PRODUTO', 'CODIGO', 'PRODUTO_ID', 'ID_PROD', 'PRODUTO', 'CODIGO_PRODUTO', 'COD_PRODUTO'],
                    'quantidade': ['QUANTIDADE', 'QTD', 'QTDE', 'QTD_VENDIDA'],
                    'valor_unitario': ['VALOR_UNITARIO', 'PRECO_UNITARIO', 'VALOR_UNIT', 'PRECO_UNIT', 'VALOR'],
                    'valor_total': ['VALOR_TOTAL', 'TOTAL', 'VALOR_ITEM', 'SUBTOTAL']
                }
                
                # Encontrar os nomes reais das colunas
                real_columns = {}
                for logical_name, alternatives in column_mapping.items():
                    found = False
                    for alt in alternatives:
                        if alt in available_columns:
                            real_columns[logical_name] = alt
                            print(f"✅ {logical_name} -> {alt}")
                            found = True
                            break
                    
                    if not found:
                        print(f"❌ Não foi possível encontrar coluna para {logical_name}")
                        # Para colunas críticas, usar o primeiro nome da lista como fallback
                        real_columns[logical_name] = alternatives[0]
                        print(f"⚠️ Usando fallback: {logical_name} -> {alternatives[0]}")
                
                # Construir a query de inserção dinamicamente
                query_item = f"""
                INSERT INTO VENDAS_ITENS (
                    {real_columns['id_venda']}, 
                    {real_columns['id_produto']}, 
                    {real_columns['quantidade']}, 
                    {real_columns['valor_unitario']}, 
                    {real_columns['valor_total']}
                ) VALUES (?, ?, ?, ?, ?)
                """
                
                print(f"📝 Query construída: {query_item}")
                
                # Registrar os itens da venda
                for item in itens:
                    try:
                        # Calcular o valor total do item
                        valor_unitario = float(item['valor_unitario'])
                        quantidade = int(item['quantidade'])
                        valor_total = valor_unitario * quantidade
                        
                        # Obter o código do produto
                        codigo_produto = item['id_produto']
                        
                        print(f"📦 Inserindo item: ID_VENDA={id_venda}, {real_columns['id_produto']}={codigo_produto}, QTD={quantidade}, VALOR_UNIT={valor_unitario}, TOTAL={valor_total}")
                        
                        # Executar a inserção do item
                        execute_query(query_item, (
                            id_venda, codigo_produto, quantidade, valor_unitario, valor_total
                        ))
                        
                        print(f"✅ Item inserido com sucesso: {codigo_produto}")
                        
                    except Exception as item_error:
                        print(f"❌ Erro ao inserir item {codigo_produto}: {item_error}")
                        # Continuar com os próximos itens mesmo se um falhar
                        continue
                        
            except Exception as structure_error:
                print(f"❌ Erro ao obter estrutura de VENDAS_ITENS: {structure_error}")
                
                # FALLBACK: Tentar com nomes mais comuns
                print("🔄 Tentando fallback com nomes comuns...")
                
                # Tentar diferentes combinações de nomes de colunas
                fallback_combinations = [
                    # Combinação 1: Nomes mais comuns
                    {
                        'query': """
                        INSERT INTO VENDAS_ITENS (ID_VENDA, CODIGO, QUANTIDADE, VALOR_UNITARIO, VALOR_TOTAL) 
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        'description': 'ID_VENDA, CODIGO, QUANTIDADE, VALOR_UNITARIO, VALOR_TOTAL'
                    },
                    # Combinação 2: Variação com PRODUTO_ID
                    {
                        'query': """
                        INSERT INTO VENDAS_ITENS (ID_VENDA, PRODUTO_ID, QUANTIDADE, VALOR_UNITARIO, VALOR_TOTAL) 
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        'description': 'ID_VENDA, PRODUTO_ID, QUANTIDADE, VALOR_UNITARIO, VALOR_TOTAL'
                    },
                    # Combinação 3: Variação com QTD
                    {
                        'query': """
                        INSERT INTO VENDAS_ITENS (ID_VENDA, CODIGO, QTD, VALOR_UNITARIO, VALOR_TOTAL) 
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        'description': 'ID_VENDA, CODIGO, QTD, VALOR_UNITARIO, VALOR_TOTAL'
                    }
                ]
                
                # Tentar cada combinação até uma funcionar
                for i, combination in enumerate(fallback_combinations):
                    try:
                        print(f"🧪 Testando combinação {i+1}: {combination['description']}")
                        
                        # Testar com o primeiro item
                        if itens:
                            test_item = itens[0]
                            valor_unitario = float(test_item['valor_unitario'])
                            quantidade = int(test_item['quantidade'])
                            valor_total = valor_unitario * quantidade
                            codigo_produto = test_item['id_produto']
                            
                            execute_query(combination['query'], (
                                id_venda, codigo_produto, quantidade, valor_unitario, valor_total
                            ))
                            
                            print(f"✅ Combinação {i+1} funcionou! Inserindo todos os itens...")
                            
                            # Se funcionou, inserir todos os itens restantes
                            for item in itens[1:]:  # Pular o primeiro que já foi inserido
                                valor_unitario = float(item['valor_unitario'])
                                quantidade = int(item['quantidade'])
                                valor_total = valor_unitario * quantidade
                                codigo_produto = item['id_produto']
                                
                                execute_query(combination['query'], (
                                    id_venda, codigo_produto, quantidade, valor_unitario, valor_total
                                ))
                                
                                print(f"✅ Item inserido: {codigo_produto}")
                            
                            break  # Sair do loop se deu certo
                            
                    except Exception as combination_error:
                        print(f"❌ Combinação {i+1} falhou: {combination_error}")
                        continue
                else:
                    # Se nenhuma combinação funcionou
                    raise Exception("Não foi possível inserir itens na tabela VENDAS_ITENS. Verifique a estrutura da tabela.")
            
            print("\n----- ATUALIZANDO ESTOQUE DOS PRODUTOS -----")

            # Verificar a estrutura da tabela PRODUTOS para encontrar o campo de estoque
            structure_query_produtos = """
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'PRODUTOS'
            ORDER BY RDB$FIELD_POSITION
            """

            try:
                produtos_fields = execute_query(structure_query_produtos)
                
                # Possíveis nomes para o campo de estoque
                estoque_alternatives = ["ESTOQUE", "QUANTIDADE_ESTOQUE", "ESTOQUE_ATUAL", "QTD", "QUANTIDADE", "SALDO", "SALDO_ESTOQUE"]
                
                # Encontrar o nome real da coluna de estoque
                estoque_field = None
                for field in produtos_fields:
                    field_name = field[0].strip() if field[0] else ""
                    
                    # Verificar se este campo corresponde a alguma alternativa para estoque
                    if field_name.upper() in [alt.upper() for alt in estoque_alternatives]:
                        estoque_field = field_name
                        print(f"  >>> Campo de estoque encontrado: {estoque_field}")
                        break
                
                if not estoque_field:
                    raise Exception("Não foi possível identificar o campo de estoque na tabela PRODUTOS")
                
                # Agora vamos atualizar o estoque para cada item vendido
                for item in itens:
                    codigo_produto = item['id_produto']
                    quantidade = int(item['quantidade'])
                    
                    # Query para atualizar o estoque
                    query_update_estoque = f"""
                    UPDATE PRODUTOS
                    SET {estoque_field} = {estoque_field} - ?
                    WHERE CODIGO = ?
                    """
                    
                    print(f"Atualizando estoque do produto {codigo_produto}: reduzindo em {quantidade} unidades")
                    print(f"Query: {query_update_estoque}")
                    
                    # Executar a atualização
                    execute_query(query_update_estoque, (quantidade, codigo_produto))
                    print(f"Estoque atualizado com sucesso para o produto {codigo_produto}")
                    
                print("\n===== ESTOQUE ATUALIZADO COM SUCESSO =====")
                
            except Exception as e:
                print(f"\n***** ERRO AO ATUALIZAR ESTOQUE *****")
                print(f"Erro detalhado: {e}")
                import traceback
                traceback.print_exc()

            print("\n===== VENDA FINALIZADA COM SUCESSO (SEM CUPOM) =====")
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
        self.btn_finalizar.setText("Finalizar R$ 0,00 (F4)")  # ADICIONADO (F4)
        
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
        self.esconder_sugestoes_codigo_barras()

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
            
            # Configurar comportamento de seleção
            table.setSelectionBehavior(QTableWidget.SelectRows)  # Selecionar linha inteira
            table.setSelectionMode(QTableWidget.SingleSelection)  # Permitir apenas uma seleção
            
            layout.addWidget(table)
            
            # Botões de ação
            button_layout = QHBoxLayout()
            
            adicionar_btn = QPushButton("Adicionar ao Carrinho (F6)")
            adicionar_btn.clicked.connect(lambda: self.adicionar_produto_da_lista(table, dialog))
            
            fechar_btn = QPushButton("Fechar (ESC)")
            fechar_btn.clicked.connect(dialog.close)
            
            button_layout.addStretch(1)
            button_layout.addWidget(adicionar_btn)
            button_layout.addWidget(fechar_btn)
            
            layout.addLayout(button_layout)
            
            # Carregar dados
            self.carregar_produtos(table)
            
            # Conectar o evento de duplo clique para adicionar produto
            table.doubleClicked.connect(lambda: self.adicionar_produto_da_lista(table, dialog))
            
            # Adicionar captura de teclas para o diálogo
            original_key_press = dialog.keyPressEvent
            
            def new_key_press(event):
                if event.key() == Qt.Key_F6:
                    self.adicionar_produto_da_lista(table, dialog)
                elif event.key() == Qt.Key_Escape:
                    dialog.close()
                elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                    self.adicionar_produto_da_lista(table, dialog)
                else:
                    original_key_press(event)
            
            dialog.keyPressEvent = new_key_press
            
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
            
            # Consulta direta para obter CODIGO, NOME, MARCA, PRECO_VENDA, ESTOQUE, GRUPO
            simple_query = """
            SELECT CODIGO, NOME, MARCA, PRECO_VENDA, ESTOQUE, GRUPO 
            FROM PRODUTOS 
            ORDER BY NOME
            """
            
            try:
                # Tentar primeiro uma consulta simples e direta
                result = execute_query(simple_query)
                print("Consulta simples de produtos executada com sucesso")
                
            except Exception as simple_query_error:
                print(f"Erro na consulta simples: {simple_query_error}")
                
                # Se a consulta simples falhar, tentar a abordagem dinâmica
                structure_query = """
                SELECT RDB$FIELD_NAME
                FROM RDB$RELATION_FIELDS
                WHERE RDB$RELATION_NAME = 'PRODUTOS'
                ORDER BY RDB$FIELD_POSITION
                """
                
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
                
                # Mapeamento de colunas com possíveis nomes
                column_mapping = {
                    "CODIGO": ["CODIGO", "ID", "ID_PRODUTO", "PRODUTO_ID", "COD"],
                    "NOME": ["NOME", "DESCRICAO", "PRODUTO", "DESCR", "DESCRITIVO"],
                    "MARCA": ["MARCA", "FABRICANTE", "FORNECEDOR", "MARCA_PRODUTO"],
                    "PRECO_VENDA": ["PRECO_VENDA", "VALOR_VENDA", "PRECO", "VALOR", "PRECO_VAREJO", "VALOR_UNITARIO"],
                    "ESTOQUE": ["QUANTIDADE_ESTOQUE", "ESTOQUE", "ESTOQUE_ATUAL", "QTD", "QUANTIDADE", "SALDO", "SALDO_ESTOQUE"],
                    "GRUPO": ["GRUPO", "CATEGORIA", "DEPARTAMENTO", "TIPO", "CATEGORIA_PRODUTO"]
                }
                
                # Tentar encontrar os nomes de colunas reais no banco
                def find_real_column(alternatives):
                    for alt in alternatives:
                        if alt in column_names:
                            return alt
                    return None
                
                # Construir a consulta dinâmica
                selected_columns = []
                for field, alternatives in column_mapping.items():
                    real_column = find_real_column(alternatives)
                    if real_column:
                        selected_columns.append(f"{real_column} AS {field}")
                    else:
                        selected_columns.append(f"NULL AS {field}")
                
                dynamic_query = f"""
                SELECT {', '.join(selected_columns)}
                FROM PRODUTOS
                ORDER BY {find_real_column(column_mapping['NOME']) or 'CODIGO'}
                """
                
                print(f"Consulta dinâmica: {dynamic_query}")
                result = execute_query(dynamic_query)
            
            # Preencher a tabela com os resultados
            for row, produto in enumerate(result):
                table.insertRow(row)
                
                # Para cada coluna disponível
                for col_idx, valor in enumerate(produto):
                    if col_idx >= table.columnCount():
                        continue
                    
                    # Se não tiver valor, mostrar '-' em vez de 'N/A'
                    if valor is None:
                        table.setItem(row, col_idx, QTableWidgetItem("-"))
                        continue
                    
                    # Formatação específica para cada tipo de coluna
                    if col_idx == 3:  # Preço (índice 3)
                        # Formatar como moeda
                        try:
                            preco = float(valor)
                            preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
                            item = QTableWidgetItem(preco_formatado)
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                            table.setItem(row, col_idx, item)
                        except (ValueError, TypeError):
                            table.setItem(row, col_idx, QTableWidgetItem("-"))
                            
                    elif col_idx == 4:  # Estoque (índice 4)
                        # Formatar como número inteiro
                        try:
                            estoque = int(float(valor))
                            item = QTableWidgetItem(str(estoque))
                            item.setTextAlignment(Qt.AlignCenter)
                            table.setItem(row, col_idx, item)
                        except (ValueError, TypeError):
                            table.setItem(row, col_idx, QTableWidgetItem("-"))
                            
                    else:
                        # Outros campos como texto
                        table.setItem(row, col_idx, QTableWidgetItem(str(valor)))
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos: {str(e)}")
            print(f"Erro ao carregar produtos: {e}")
            import traceback
            traceback.print_exc()

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
            
            # Consulta simples primeiro
            try:
                simple_query = """
                SELECT CODIGO, NOME, MARCA, PRECO_VENDA, ESTOQUE, GRUPO
                FROM PRODUTOS
                WHERE (CODIGO LIKE ?) OR (NOME LIKE ?) OR (MARCA LIKE ?)
                ORDER BY NOME
                """
                
                params = (f"%{termo}%", f"%{termo}%", f"%{termo}%")
                result = execute_query(simple_query, params)
                
            except Exception as simple_query_error:
                print(f"Erro na busca simples: {simple_query_error}")
                
                # Se falhar, usar consulta dinâmica
                structure_query = """
                SELECT RDB$FIELD_NAME
                FROM RDB$RELATION_FIELDS
                WHERE RDB$RELATION_NAME = 'PRODUTOS'
                ORDER BY RDB$FIELD_POSITION
                """
                
                columns = execute_query(structure_query)
                column_names = [col[0].strip() if col[0] else "" for col in columns]
                
                # Possíveis colunas de pesquisa com alternativas
                search_mapping = {
                    "CODIGO": ["CODIGO", "ID", "ID_PRODUTO", "PRODUTO_ID", "COD"],
                    "NOME": ["NOME", "DESCRICAO", "PRODUTO", "DESCR", "DESCRITIVO"],
                    "MARCA": ["MARCA", "FABRICANTE", "FORNECEDOR", "MARCA_PRODUTO"],
                    "BARRAS": ["BARRAS", "CODIGO_BARRAS", "EAN", "GTIN", "COD_BARRAS"]
                }
                
                # Tentar encontrar as colunas reais
                def find_real_column(alternatives):
                    for alt in alternatives:
                        if alt in column_names:
                            return alt
                    return None
                
                # Construir a cláusula WHERE
                search_columns = []
                for field, alternatives in search_mapping.items():
                    real_column = find_real_column(alternatives)
                    if real_column:
                        search_columns.append(real_column)
                
                # Se não encontrou nenhuma coluna para pesquisa, usar todas as de texto
                if not search_columns:
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
            
            # Preencher a tabela com os resultados
            for row, produto in enumerate(result):
                table.insertRow(row)
                
                # Para cada coluna disponível
                for col_idx, valor in enumerate(produto):
                    if col_idx >= table.columnCount():
                        continue
                    
                    # Se não tiver valor, mostrar '-' em vez de 'N/A'
                    if valor is None:
                        table.setItem(row, col_idx, QTableWidgetItem("-"))
                        continue
                    
                    # Formatação específica para cada tipo de coluna
                    if col_idx == 3:  # Preço (índice 3)
                        # Formatar como moeda
                        try:
                            preco = float(valor)
                            preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
                            item = QTableWidgetItem(preco_formatado)
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                            table.setItem(row, col_idx, item)
                        except (ValueError, TypeError):
                            table.setItem(row, col_idx, QTableWidgetItem("-"))
                            
                    elif col_idx == 4:  # Estoque (índice 4)
                        # Formatar como número inteiro
                        try:
                            estoque = int(float(valor))
                            item = QTableWidgetItem(str(estoque))
                            item.setTextAlignment(Qt.AlignCenter)
                            table.setItem(row, col_idx, item)
                        except (ValueError, TypeError):
                            table.setItem(row, col_idx, QTableWidgetItem("-"))
                            
                    else:
                        # Outros campos como texto
                        table.setItem(row, col_idx, QTableWidgetItem(str(valor)))
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao buscar produtos: {str(e)}")
            print(f"Erro ao buscar produtos: {e}")
            import traceback
            traceback.print_exc()

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
            
            # Obter o preço
            preco = 0.0
            
            # Tentar obter o preço da coluna 3 (índice 2)
            if num_cols > 2 and table.item(row, 2) and table.item(row, 2).text():
                preco_str = table.item(row, 2).text()
                try:
                    # Se contém R$, remover e converter
                    if "R$" in preco_str:
                        preco = float(preco_str.replace("R$", "").replace(".", "").replace(",", ".").strip())
                    # Se não, tentar converter direto
                    else:
                        preco = float(preco_str.replace(",", ".").strip())
                except ValueError:
                    preco = 0.0
            
            # Se não conseguir obter o preço, buscar o produto no banco de dados
            if preco <= 0:
                try:
                    from base.banco import buscar_produto_por_codigo
                    produto_db = buscar_produto_por_codigo(codigo)
                    
                    if produto_db and len(produto_db) > 7:
                        preco = float(produto_db[7])  # Posição onde normalmente está o preço_venda
                    
                except Exception as db_error:
                    print(f"Erro ao buscar preço no banco: {db_error}")
                    # Continuar com o preço 0
            
            # Criar um objeto produto (usando sempre o preço do banco)
            produto = {
                "codigo": codigo,
                "nome": nome,
                "preco_venda": preco
            }
            
            # Adicionar ao carrinho
            self.adicionar_produto_ao_carrinho(produto)
            
            # Fechar o diálogo
            dialog.accept()
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar produto: {str(e)}")
            print(f"Erro ao adicionar produto: {e}")
            import traceback
            traceback.print_exc()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Definir fonte padrão
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = PDVWindow()
    sys.exit(app.exec_())