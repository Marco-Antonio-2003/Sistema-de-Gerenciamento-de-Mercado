import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QTextEdit, QDateEdit, QMessageBox, QSizePolicy,
                           QComboBox, QCalendarWidget)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QDate


class LancamentoFinanceiro(QWidget):
    def __init__(self, janela_parent=None):
        super().__init__()
        self.janela_parent = janela_parent
        self.initUI()
        
    def create_palette(self):
        """Cria uma paleta com cor de fundo azul escuro"""
        from PyQt5.QtGui import QPalette, QColor
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
        titulo = QLabel("Gerar lançamento Financeiro")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo, 1)  # 1 para expandir
        
        # Espaço para alinhar com o botão voltar
        spacer = QWidget()
        spacer.setFixedWidth(btn_voltar.sizeHint().width())
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
        num_parcelas_layout.addWidget(self.num_parcelas_input)
        
        linha2_layout.addLayout(num_parcelas_layout)
        
        # Valor
        valor_layout = QHBoxLayout()
        valor_label = QLabel("Valor:")
        valor_label.setStyleSheet("color: white; font-size: 16px;")
        valor_layout.addWidget(valor_label)
        
        self.valor_input = QLineEdit()
        self.valor_input.setStyleSheet(lineedit_style)
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
        
        # Terceira linha: Cliente
        linha3_layout = QHBoxLayout()
        
        # Cliente
        cliente_label = QLabel("Cliente:")
        cliente_label.setStyleSheet("color: white; font-size: 16px;")
        linha3_layout.addWidget(cliente_label)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setStyleSheet(lineedit_style)
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
        self.como_pago_input.setStyleSheet("""
            QComboBox {
                background-color: #fffff0;
                border: 1px solid #cccccc;
                padding: 6px;
                font-size: 13px;
                min-height: 20px;
                max-height: 30px;
                border-radius: 4px;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #cccccc;
                border-left-style: solid;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #0078d7;
                selection-color: white;
            }
        """)
        linha4_layout.addWidget(self.como_pago_input, 1)  # 1 para expandir
        
        main_layout.addLayout(linha4_layout)
        
        # Área de observações (campo grande)
        self.observacoes_input = QTextEdit()
        self.observacoes_input.setStyleSheet(textedit_style)
        self.observacoes_input.setMinimumHeight(150)
        main_layout.addWidget(self.observacoes_input)
        
        # Botões na parte inferior
        botoes_layout = QHBoxLayout()
        
        # Botão montar parcela
        btn_montar_parcela = QPushButton("montar parcela")
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
            num_parcelas = int(self.num_parcelas_input.text())
            valor_total = float(self.valor_input.text().replace(".", "").replace(",", "."))
            
            valor_parcela = valor_total / num_parcelas
            
            # Montar texto com as parcelas
            texto_parcelas = "Parcelas geradas:\n\n"
            data_vencimento = self.primeiro_vencimento_input.date()
            
            for i in range(1, num_parcelas + 1):
                texto_parcelas += f"Parcela {i}: R$ {valor_parcela:.2f} - Vencimento: {data_vencimento.toString('dd/MM/yyyy')}\n"
                data_vencimento = data_vencimento.addMonths(1)  # Próximo mês
            
            # Mostrar no campo de observações
            self.observacoes_input.setText(texto_parcelas)
            
            self.mostrar_mensagem("Sucesso", f"Foram geradas {num_parcelas} parcelas de R$ {valor_parcela:.2f}")
            
        except ValueError:
            self.mostrar_mensagem("Erro", "Por favor, informe valores numéricos válidos!")
    
    def incluir(self):
        """Ação do botão incluir"""
        # Verificar se todos os campos obrigatórios foram preenchidos
        if not self.cliente_input.text():
            self.mostrar_mensagem("Atenção", "Por favor, informe o cliente!")
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
        
        if self.observacoes_input.toPlainText() == "":
            self.mostrar_mensagem("Atenção", "Por favor, monte as parcelas antes de incluir!")
            return
        
        # Se todos os campos foram preenchidos
        data_emissao = self.data_emissao_input.date().toString("dd/MM/yyyy")
        primeiro_vencimento = self.primeiro_vencimento_input.date().toString("dd/MM/yyyy")
        num_parcelas = self.num_parcelas_input.text()
        valor = self.valor_input.text()
        seu_codigo = self.seu_codigo_input.text()
        cliente = self.cliente_input.text()
        como_pago = self.como_pago_input.currentText()
        observacoes = self.observacoes_input.toPlainText()
        
        print(f"Lançamento financeiro incluído:")
        print(f"Data Emissão: {data_emissao}")
        print(f"1º Vencimento: {primeiro_vencimento}")
        print(f"Num. Parcelas: {num_parcelas}")
        print(f"Valor: {valor}")
        print(f"Seu Código: {seu_codigo}")
        print(f"Cliente: {cliente}")
        print(f"Como vai ser pago: {como_pago}")
        print(f"Observações: {observacoes}")
        
        # Limpar os campos após salvar
        self.num_parcelas_input.clear()
        self.valor_input.clear()
        self.seu_codigo_input.clear()
        self.cliente_input.clear()
        self.como_pago_input.setCurrentIndex(0)
        self.observacoes_input.clear()
        
        # Mostrar mensagem de sucesso
        self.mostrar_mensagem("Sucesso", "Lançamento financeiro incluído com sucesso!")
    
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
    
    lancamento_widget = LancamentoFinanceiro(window)  # Passa a janela como parent
    window.setCentralWidget(lancamento_widget)
    
    window.show()
    sys.exit(app.exec_())