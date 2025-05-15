#lançamento financeiro
import sys
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTextEdit, QDateEdit, QMessageBox, QSizePolicy,
                           QComboBox, QCalendarWidget)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QDate

# Importar funções do banco
from base.banco import (verificar_tabela_recebimentos_clientes, criar_recebimento,
                       listar_clientes, buscar_recebimento_por_codigo, registrar_pagamento)

from base.banco import verificar_e_corrigir_tabela_recebimentos
verificar_e_corrigir_tabela_recebimentos()


class LancamentoFinanceiroWindow(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        
        # Verificar se a tabela existe
        self.verificar_tabela()
        
        # Lista para armazenar os clientes (ID, Nome)
        self.clientes = []
        
        self.initUI()
        
        # Carregar a lista de clientes
        self.carregar_clientes()
    
    def verificar_tabela(self):
        """Verifica se a tabela de recebimentos existe no banco de dados"""
        try:
            verificar_tabela_recebimentos_clientes()
        except Exception as e:
            print(f"Erro ao verificar tabela de recebimentos: {e}")
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#003b57"))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette
    
    def carregar_clientes(self):
        """Carrega a lista de clientes do banco de dados"""
        try:
            self.clientes = listar_clientes()
            
            # Limpar o ComboBox
            self.cliente_input.clear()
            
            # Adicionar item padrão
            self.cliente_input.addItem("Selecione um cliente")
            
            # Adicionar os clientes ao ComboBox
            for id_cliente, nome in self.clientes:
                self.cliente_input.addItem(nome)
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            # Adicionar alguns clientes de exemplo como fallback
            self.cliente_input.clear()
            self.cliente_input.addItem("Selecione um cliente")
            self.cliente_input.addItem("Cliente Exemplo 1")
            self.cliente_input.addItem("Cliente Exemplo 2")
            self.cliente_input.addItem("Cliente Exemplo 3")
    
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
        titulo = QLabel("Gerar lançamento Financeiro")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
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
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QCalendarWidget QToolButton {
                background-color: white;
                color: black;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f0f0f0;
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
        
        # Estilo para QTextEdit
        textedit_style = """
            QTextEdit {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                border-radius: 4px;
            }
            QTextEdit:focus {
                border: 1px solid #0078d7;
            }
        """
        
        # Primeira linha: Data da Emissão e 1º Vencimento
        linha1_layout = QHBoxLayout()
        
        # Data da Emissão
        data_emissao_layout = QHBoxLayout()
        data_emissao_label = QLabel("Data da Emissão:")
        data_emissao_label.setStyleSheet("color: white; font-size: 16px;")
        data_emissao_layout.addWidget(data_emissao_label)
        
        self.data_emissao_input = QDateEdit(QDate.currentDate())
        self.data_emissao_input.setCalendarPopup(True)
        self.data_emissao_input.setStyleSheet(dateedit_style)
        data_emissao_layout.addWidget(self.data_emissao_input)
        
        linha1_layout.addLayout(data_emissao_layout)
        
        # Espaçamento
        linha1_layout.addSpacing(30)
        
        # 1º Vencimento
        primeiro_vencimento_layout = QHBoxLayout()
        primeiro_vencimento_label = QLabel("1º Vencimento")
        primeiro_vencimento_label.setStyleSheet("color: white; font-size: 16px;")
        primeiro_vencimento_layout.addWidget(primeiro_vencimento_label)
        
        self.primeiro_vencimento_input = QDateEdit(QDate.currentDate().addDays(30))  # Padrão: 30 dias após data atual
        self.primeiro_vencimento_input.setCalendarPopup(True)
        self.primeiro_vencimento_input.setStyleSheet(dateedit_style)
        primeiro_vencimento_layout.addWidget(self.primeiro_vencimento_input)
        
        linha1_layout.addLayout(primeiro_vencimento_layout)
        
        main_layout.addLayout(linha1_layout)
        
        # Segunda linha: Num. parcelas, Valor e Seu código
        linha2_layout = QHBoxLayout()
        
        # Num. parcelas
        num_parcelas_layout = QHBoxLayout()
        num_parcelas_label = QLabel("Num. parcelas:")
        num_parcelas_label.setStyleSheet("color: white; font-size: 16px;")
        num_parcelas_layout.addWidget(num_parcelas_label)
        
        self.num_parcelas_input = QLineEdit()
        self.num_parcelas_input.setStyleSheet(lineedit_style)
        self.num_parcelas_input.setText("1")  # Valor padrão
        num_parcelas_layout.addWidget(self.num_parcelas_input)
        
        linha2_layout.addLayout(num_parcelas_layout)
        
        # Valor
        valor_layout = QHBoxLayout()
        valor_label = QLabel("Valor:")
        valor_label.setStyleSheet("color: white; font-size: 16px;")
        valor_layout.addWidget(valor_label)
        
        self.valor_input = QLineEdit()
        self.valor_input.setStyleSheet(lineedit_style)
        self.valor_input.setPlaceholderText("0,00")
        valor_layout.addWidget(self.valor_input)
        
        linha2_layout.addLayout(valor_layout)
        
        # Seu código
        seu_codigo_layout = QHBoxLayout()
        seu_codigo_label = QLabel("Seu código:")
        seu_codigo_label.setStyleSheet("color: white; font-size: 16px;")
        seu_codigo_layout.addWidget(seu_codigo_label)
        
        self.seu_codigo_input = QLineEdit()
        self.seu_codigo_input.setStyleSheet(lineedit_style)
        seu_codigo_layout.addWidget(self.seu_codigo_input)
        
        linha2_layout.addLayout(seu_codigo_layout)
        
        main_layout.addLayout(linha2_layout)
        
        # Terceira linha: Cliente (agora como ComboBox)
        linha3_layout = QHBoxLayout()
        
        # Cliente
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        linha3_layout.addWidget(cliente_label)
        
        # Alterado de QLineEdit para QComboBox
        self.cliente_input = QComboBox()
        self.cliente_input.setStyleSheet(combobox_style)
        self.cliente_input.setEditable(True)  # Permite digitação para busca rápida
        self.cliente_input.setMaxVisibleItems(10)
        linha3_layout.addWidget(self.cliente_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha3_layout)
        
        # Quarta linha: Como vai ser pago
        linha4_layout = QHBoxLayout()
        
        # Como vai ser pago
        como_pago_label = QLabel("Como vai ser pago:")
        como_pago_label.setStyleSheet("color: white; font-size: 16px;")
        linha4_layout.addWidget(como_pago_label)
        
        self.como_pago_input = QComboBox()
        self.como_pago_input.addItems(["Selecione a forma de pagamento", "Boleto", "Cartão", "Pix", "Dinheiro", "Transferência", "Cheque", "Outro"])
        self.como_pago_input.setStyleSheet(combobox_style)
        linha4_layout.addWidget(self.como_pago_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha4_layout)
        
        # Área de observações (campo grande)
        observacoes_label = QLabel("Observações / Parcelas:")
        observacoes_label.setStyleSheet("color: white; font-size: 16px;")
        main_layout.addWidget(observacoes_label)
        
        self.observacoes_input = QTextEdit()
        self.observacoes_input.setStyleSheet(textedit_style)
        self.observacoes_input.setMinimumHeight(150)
        main_layout.addWidget(self.observacoes_input)
        
        # Botões na parte inferior
        botoes_layout = QHBoxLayout()
        
        # Botão montar parcela
        btn_montar_parcela = QPushButton("Montar Parcelas")
        btn_montar_parcela.setStyleSheet("""
            QPushButton {
                background-color: #005079;
                color: white;
                border: none;
                padding: 15px 20px;
                font-size: 16px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #003d5c;
            }
        """)
        btn_montar_parcela.clicked.connect(self.montar_parcela)
        botoes_layout.addWidget(btn_montar_parcela, 0, Qt.AlignRight)
        
        # Botão Incluir
        btn_incluir = QPushButton("Incluir")
        btn_incluir.setStyleSheet("""
            QPushButton {
                background-color: #00E676;
                color: black;
                border: none;
                padding: 15px 20px;
                font-size: 16px;
                border-radius: 4px;
                text-align: center;
                min-width: 400px;
            }
            QPushButton:hover {
                background-color: #00C853;
            }
        """)
        btn_incluir.clicked.connect(self.incluir)
        botoes_layout.addWidget(btn_incluir)
        
        main_layout.addLayout(botoes_layout)
        self.cliente_input.currentIndexChanged.connect(self.preencher_codigo_cliente)
    def obter_cliente_id(self):
        """Obtém o ID do cliente selecionado"""
        cliente_index = self.cliente_input.currentIndex()
        
        # Se é o primeiro item (Selecione um cliente) ou um cliente digitado manualmente
        if cliente_index <= 0 or cliente_index > len(self.clientes):
            return None
            
        # Retorna o ID do cliente selecionado (-1 devido ao item "Selecione um cliente")
        return self.clientes[cliente_index - 1][0]
    
    def obter_cliente_nome(self):
        """Obtém o nome do cliente, seja selecionado ou digitado"""
        cliente_index = self.cliente_input.currentIndex()
        
        # Se é um cliente da lista
        if cliente_index > 0 and cliente_index <= len(self.clientes):
            return self.clientes[cliente_index - 1][1]
            
        # Se é um cliente digitado manualmente
        return self.cliente_input.currentText().strip()
    
    def voltar(self):
        """Ação do botão voltar"""
        # Se a janela foi criada a partir de outra janela (tem um parent)
        if self.janela_parent:
            # Verifica se o parent é um QMainWindow
            if isinstance(self.janela_parent, QMainWindow):
                self.janela_parent.close()
            # Se o parent for um widget dentro de uma aplicação
            else:
                from PyQt5.QtWidgets import QApplication
                # Verifica se há uma janela principal ativa
                main_window = QApplication.activeWindow()
                if main_window:
                    main_window.close()
                    
        # Se estiver sendo executado como aplicação principal (sem parent)
        else:
            # Encerra a aplicação
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().quit()
    
    def montar_parcela(self):
        """Ação do botão montar parcela"""
        # Verificar se os campos necessários estão preenchidos
        if not self.num_parcelas_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o número de parcelas!")
            return
        
        if not self.valor_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o valor!")
            return
        
        try:
            # Converter o número de parcelas para inteiro
            num_parcelas = int(self.num_parcelas_input.text())
            if num_parcelas <= 0:
                self.mostrar_mensagem("Atenção", "O número de parcelas deve ser maior que zero!")
                return
            
            # Converter o valor para float (substitui vírgula por ponto)
            valor_texto = self.valor_input.text().replace(".", "").replace(",", ".")
            valor_total = float(valor_texto)
            if valor_total <= 0:
                self.mostrar_mensagem("Atenção", "O valor deve ser maior que zero!")
                return
            
            # Calcular o valor de cada parcela
            valor_parcela = valor_total / num_parcelas
            
            # Montar texto com as parcelas
            texto_parcelas = "Parcelas geradas:\n\n"
            data_vencimento = self.primeiro_vencimento_input.date()
            
            self.parcelas = []  # Armazenar informações das parcelas
            
            # Gerar código base se não foi informado
            codigo_base = self.seu_codigo_input.text().strip()
            if not codigo_base:
                # Usar timestamp para gerar código único
                from datetime import datetime
                codigo_base = f"REC{datetime.now().strftime('%Y%m%d%H%M')}"
                self.seu_codigo_input.setText(codigo_base)
            
            for i in range(1, num_parcelas + 1):
                vencimento_str = data_vencimento.toString('dd/MM/yyyy')
                texto_parcelas += f"Parcela {i}: R$ {valor_parcela:.2f} - Vencimento: {vencimento_str}\n"
                
                # Armazenar dados da parcela com código único para cada uma
                if num_parcelas > 1:
                    codigo_parcela = f"{codigo_base}-{i}/{num_parcelas}"
                else:
                    codigo_parcela = codigo_base
                    
                self.parcelas.append({
                    'numero': i,
                    'valor': valor_parcela,
                    'vencimento': data_vencimento.toPyDate(),
                    'codigo': codigo_parcela
                })
                
                # Próximo mês para a próxima parcela
                data_vencimento = data_vencimento.addMonths(1)
            
            # Mostrar no campo de observações
            self.observacoes_input.setText(texto_parcelas)
            
            # Mostrar mensagem de sucesso
            valor_formatado = f"{valor_parcela:.2f}".replace(".", ",")
            self.mostrar_mensagem("Sucesso", f"Foram geradas {num_parcelas} parcelas de R$ {valor_formatado}")
            
        except ValueError:
            self.mostrar_mensagem("Erro", "Por favor, informe valores numéricos válidos!")

    def processar_pagamento(self):
        """Processa o pagamento da parcela selecionada"""
        # Obter o ID do recebimento selecionado na tabela
        recebimento_id = self.obter_recebimento_selecionado()
        if not recebimento_id:
            self.mostrar_mensagem("Atenção", "Por favor, selecione um recebimento!")
            return
        
        # Obter o valor que o usuário digitou
        try:
            valor_texto = self.valor_pago_input.text().replace(".", "").replace(",", ".")
            valor_pago = float(valor_texto)
            
            if valor_pago <= 0:
                self.mostrar_mensagem("Atenção", "O valor do pagamento deve ser maior que zero!")
                return
        except ValueError:
            self.mostrar_mensagem("Erro", "Por favor, informe um valor válido!")
            return
        
        # Chamar a função de confirmar pagamento
        sucesso, mensagem = registrar_pagamento(recebimento_id, valor_pago)
        
        # Mostrar mensagem ao usuário
        if sucesso:
            self.mostrar_mensagem("Sucesso", mensagem)
            # Atualizar a tabela de recebimentos para refletir o novo status
            self.carregar_recebimentos()
        else:
            self.mostrar_mensagem("Erro", mensagem)

    def preencher_codigo_cliente(self):
        """Preenche o campo de código automaticamente com o código do cliente selecionado"""
        cliente_id = self.obter_cliente_id()
        if cliente_id:
            # Pode-se usar o ID como código ou buscar um código específico
            self.seu_codigo_input.setText(str(cliente_id))
        else:
            # Se nenhum cliente for selecionado, limpa o campo
            self.seu_codigo_input.setText(f"CL-{cliente_id}")

    # Modificação no método incluir em LancamentoFinanceiroWindow em lancamento_financeiro.py:

    def incluir(self):
        """Ação do botão incluir - Salva as parcelas no banco de dados"""
        # Verificar se todos os campos obrigatórios foram preenchidos
        cliente_nome = self.obter_cliente_nome()
        if not cliente_nome:
            self.mostrar_mensagem("Atenção", "Por favor, informe ou selecione um cliente!")
            return
        
        if not self.valor_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o valor!")
            return
        
        if not self.num_parcelas_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o número de parcelas!")
            return
        
        if self.como_pago_input.currentIndex() == 0:
            self.mostrar_mensagem("Atenção", "Por favor, selecione a forma de pagamento!")
            return
        
        # Se as parcelas não foram montadas, montar automaticamente
        if not hasattr(self, 'parcelas') or not self.parcelas:
            self.montar_parcela()
        
        try:
            # Obter dados do cabeçalho
            cliente_id = self.obter_cliente_id()
            forma_pagamento = self.como_pago_input.currentText()
            observacoes = self.observacoes_input.toPlainText()
            
            # Salvar as parcelas no banco de dados
            ids_recebimentos = []
            erros = []
            
            for parcela in self.parcelas:
                try:
                    # Usar o código da parcela que já foi gerado no método montar_parcela
                    codigo_parcela = parcela['codigo']
                    
                    print(f"\nTentando criar parcela {parcela['numero']}:")
                    print(f"  Código: {codigo_parcela}")
                    print(f"  Cliente: {cliente_nome}")
                    print(f"  Cliente ID: {cliente_id}")
                    print(f"  Vencimento: {parcela['vencimento']}")
                    print(f"  Valor: {parcela['valor']}")
                    
                    # Chamar a função de criar recebimento SEM o parâmetro valor_original
                    from base.banco import criar_recebimento
                    id_recebimento = criar_recebimento(
                        codigo=codigo_parcela,
                        cliente=cliente_nome,
                        cliente_id=cliente_id,
                        vencimento=parcela['vencimento'],
                        valor=parcela['valor']
                    )
                    
                    # Se o recebimento foi criado com sucesso, atualizar o valor original
                    if id_recebimento:
                        # Importar a função de atualizar valor original
                        from base.banco import atualizar_valor_original
                        
                        # Atualizar o valor original com o valor da parcela
                        atualizar_valor_original(
                            recebimento_id=id_recebimento,
                            valor_original=parcela['valor']
                        )
                        
                        ids_recebimentos.append(id_recebimento)
                        print(f"Parcela {parcela['numero']} criada com sucesso, ID: {id_recebimento}")
                    else:
                        erros.append(f"Parcela {parcela['numero']}: ID não retornado")
                except Exception as e:
                    erro_msg = str(e)
                    print(f"Erro ao criar parcela {parcela['numero']}: {erro_msg}")
                    erros.append(f"Parcela {parcela['numero']}: {erro_msg}")
            
            # Verificar se pelo menos uma parcela foi salva
            if ids_recebimentos:
                # Limpar os campos após salvar
                self.num_parcelas_input.setText("1")
                self.valor_input.clear()
                self.seu_codigo_input.clear()
                self.cliente_input.setCurrentIndex(0)
                self.como_pago_input.setCurrentIndex(0)
                self.observacoes_input.clear()
                
                # Remover as parcelas armazenadas
                self.parcelas = []
                
                # Mostrar mensagem de sucesso
                if erros:
                    self.mostrar_mensagem("Aviso", f"Algumas parcelas foram criadas com sucesso, mas ocorreram erros: {', '.join(erros)}")
                else:
                    self.mostrar_mensagem("Sucesso", "Parcelas incluídas com sucesso!")
            else:
                # Nenhuma parcela foi salva
                self.mostrar_mensagem("Erro", f"Nenhuma parcela foi salva. Erros: {', '.join(erros)}")
            
        except Exception as e:
            # Mostrar o erro real ao usuário
            erro_msg = str(e)
            print(f"Erro ao incluir lançamento financeiro: {erro_msg}")
            self.mostrar_mensagem("Erro", f"Falha ao incluir lançamento: {erro_msg}")



    
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
    window.setWindowTitle("Sistema - Lançamento Financeiro")
    window.setGeometry(100, 100, 1000, 600)
    window.setStyleSheet("background-color: #003b57;")
    
    lancamento_widget = LancamentoFinanceiroWindow(window)  # Passa a janela como parent
    window.setCentralWidget(lancamento_widget)
    
    window.show()
    sys.exit(app.exec_())