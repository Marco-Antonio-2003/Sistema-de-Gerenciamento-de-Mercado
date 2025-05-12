import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QCheckBox,
    QWidget, QDesktopWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon, QPixmap


class CupomFiscalDialog(QDialog):
    """Diálogo para selecionar o tipo de cupom ao finalizar a venda"""
    
    # Sinais personalizados
    cupom_selecionado = pyqtSignal(str, str)  # tipo_cupom, cpf
    
    def __init__(self, total_venda=0.0, parent=None):
        super().__init__(parent)
        
        self.total_venda = total_venda
        self.cpf = ""
        self.tipo_cupom = ""
        
        self.setWindowTitle("FINALIZAR VENDA")
        self.setFixedSize(700, 400)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        
        # Centralizar na tela
        self.centralizar()
        
        # Configurar layout
        self.setup_ui()
    
    def centralizar(self):
        """Centraliza a janela na tela"""
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """Configura a interface do diálogo"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        titulo = QLabel("FINALIZAR VENDA")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Valor total (opcional)
        if self.total_venda > 0:
            total_layout = QHBoxLayout()
            
            total_label = QLabel("Total:")
            total_label.setFont(QFont("Arial", 14))
            
            total_valor = QLabel(f"R$ {self.total_venda:.2f}".replace('.', ','))
            total_valor.setFont(QFont("Arial", 14, QFont.Bold))
            
            total_layout.addWidget(total_label)
            total_layout.addWidget(total_valor)
            total_layout.addStretch()
            
            main_layout.addLayout(total_layout)
        
        # Botões de opções
        options_layout = QHBoxLayout()
        options_layout.setSpacing(15)
        
        # Botão Cupom Fiscal - F9
        self.btn_cupom_fiscal = QPushButton("CUPOM FISCAL (F9)")
        self.btn_cupom_fiscal.setFixedHeight(60)
        self.btn_cupom_fiscal.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_cupom_fiscal.setStyleSheet("""
            QPushButton {
                background-color: #00BFA5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
            QPushButton:pressed {
                background-color: #00796B;
            }
        """)
        self.btn_cupom_fiscal.clicked.connect(lambda: self.selecionar_cupom("FISCAL"))
        options_layout.addWidget(self.btn_cupom_fiscal)
        
        # Botão Cupom Não Fiscal - F10
        self.btn_nao_fiscal = QPushButton("CUPOM NÃO FISCAL (F10)")
        self.btn_nao_fiscal.setFixedHeight(60)
        self.btn_nao_fiscal.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_nao_fiscal.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
        """)
        self.btn_nao_fiscal.clicked.connect(lambda: self.selecionar_cupom("NAO_FISCAL"))
        options_layout.addWidget(self.btn_nao_fiscal)
        
        # Botão Conta Crédito - F11
        self.btn_conta_credito = QPushButton("CONTA CRÉDITO (F11)")
        self.btn_conta_credito.setFixedHeight(60)
        self.btn_conta_credito.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_conta_credito.setStyleSheet("""
            QPushButton {
                background-color: #FFCA28;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFB300;
            }
            QPushButton:pressed {
                background-color: #FFA000;
            }
        """)
        self.btn_conta_credito.clicked.connect(lambda: self.selecionar_cupom("CONTA_CREDITO"))
        options_layout.addWidget(self.btn_conta_credito)
        
        main_layout.addLayout(options_layout)
        
        # Frame para CPF na Nota (inicialmente oculto)
        self.cpf_frame = QWidget()
        cpf_layout = QVBoxLayout(self.cpf_frame)
        cpf_layout.setContentsMargins(0, 10, 0, 0)
        
        # Título para CPF
        cpf_titulo = QLabel("CPF na Nota")
        cpf_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        cpf_titulo.setAlignment(Qt.AlignCenter)
        cpf_layout.addWidget(cpf_titulo)
        
        # Input para CPF
        cpf_input_layout = QHBoxLayout()
        
        cpf_label = QLabel("CPF:")
        cpf_label.setFont(QFont("Arial", 12))
        
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Digite o CPF (apenas números)")
        self.cpf_input.setMaxLength(14)  # 11 dígitos + 2 pontos + 1 traço
        self.cpf_input.setFont(QFont("Arial", 12))
        self.cpf_input.textChanged.connect(self.formatar_cpf)
        
        cpf_input_layout.addWidget(cpf_label)
        cpf_input_layout.addWidget(self.cpf_input, 1)
        
        cpf_layout.addLayout(cpf_input_layout)
        
        # Checkbox para CPF na Nota
        self.chk_sem_cpf = QCheckBox("Não informar CPF (F8)")
        self.chk_sem_cpf.setFont(QFont("Arial", 12))
        self.chk_sem_cpf.toggled.connect(self.toggle_cpf_input)
        cpf_layout.addWidget(self.chk_sem_cpf)
        
        # Botões para confirmar ou voltar
        cpf_buttons_layout = QHBoxLayout()
        
        self.btn_voltar = QPushButton("Voltar (ESC)")
        self.btn_voltar.setFont(QFont("Arial", 12))
        self.btn_voltar.clicked.connect(self.voltar_selecao)
        
        self.btn_confirmar = QPushButton("Confirmar (F12)")
        self.btn_confirmar.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)
        self.btn_confirmar.clicked.connect(self.confirmar_cpf)
        
        cpf_buttons_layout.addWidget(self.btn_voltar)
        cpf_buttons_layout.addStretch()
        cpf_buttons_layout.addWidget(self.btn_confirmar)
        
        cpf_layout.addLayout(cpf_buttons_layout)
        
        main_layout.addWidget(self.cpf_frame)
        
        # Ocultar o frame de CPF inicialmente
        self.cpf_frame.setVisible(False)
        
        # Botão para fechar o diálogo (X no canto superior direito)
        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: #FF5252;
            }
        """)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)
        
        # Adicionar o botão de fechar ao layout
        main_layout.insertWidget(0, close_button, 0, Qt.AlignRight)
        
        # Stretch para empurrar tudo para cima
        main_layout.addStretch(1)
    
    def keyPressEvent(self, event):
        """Captura eventos de teclado para responder às teclas de função"""
        # Verificar se estamos na seleção de tipo de cupom ou na tela de CPF
        if not self.cpf_frame.isVisible():
            # Primeira tela - seleção de tipo de cupom
            if event.key() == Qt.Key_F9:
                self.selecionar_cupom("FISCAL")
            elif event.key() == Qt.Key_F10:
                self.selecionar_cupom("NAO_FISCAL")
            elif event.key() == Qt.Key_F11:
                self.selecionar_cupom("CONTA_CREDITO")
            elif event.key() == Qt.Key_Escape:
                self.reject()  # Fecha o diálogo
        else:
            # Segunda tela - informação de CPF
            if event.key() == Qt.Key_F8:
                # Alternar o estado do checkbox de "Não informar CPF"
                self.chk_sem_cpf.setChecked(not self.chk_sem_cpf.isChecked())
            elif event.key() == Qt.Key_F12:
                self.confirmar_cpf()
            elif event.key() == Qt.Key_Escape:
                self.voltar_selecao()
        
        # Chamar o método da classe pai para processar outros eventos de teclado
        super().keyPressEvent(event)
    
    def selecionar_cupom(self, tipo):
        """Armazena o tipo de cupom selecionado e mostra opções de CPF"""
        self.tipo_cupom = tipo
        
        # Ocultar botões de seleção
        self.btn_cupom_fiscal.setVisible(False)
        self.btn_nao_fiscal.setVisible(False)
        self.btn_conta_credito.setVisible(False)
        
        # Mostrar opções de CPF
        self.cpf_frame.setVisible(True)
        self.cpf_input.setFocus()
    
    def voltar_selecao(self):
        """Volta para a seleção do tipo de cupom"""
        # Mostrar botões de seleção
        self.btn_cupom_fiscal.setVisible(True)
        self.btn_nao_fiscal.setVisible(True)
        self.btn_conta_credito.setVisible(True)
        
        # Ocultar opções de CPF
        self.cpf_frame.setVisible(False)
        
        # Limpar campos
        self.cpf_input.clear()
        self.chk_sem_cpf.setChecked(False)
    
    def toggle_cpf_input(self, checked):
        """Habilita/desabilita o campo de CPF"""
        self.cpf_input.setEnabled(not checked)
        if checked:
            self.cpf_input.clear()
    
    def formatar_cpf(self, text):
        """Formata o CPF enquanto o usuário digita"""
        # Remover caracteres não numéricos
        texto_limpo = ''.join(filter(str.isdigit, text))
        
        # Formatar CPF (xxx.xxx.xxx-xx)
        texto_formatado = ""
        for i, char in enumerate(texto_limpo):
            if i == 3 or i == 6:
                texto_formatado += "."
            elif i == 9:
                texto_formatado += "-"
            texto_formatado += char
            
            # Limitar a 11 dígitos
            if i >= 10:
                break
        
        # Atualizar o texto sem disparar o evento textChanged novamente
        if texto_formatado != text:
            self.cpf_input.blockSignals(True)
            self.cpf_input.setText(texto_formatado)
            self.cpf_input.setCursorPosition(len(texto_formatado))
            self.cpf_input.blockSignals(False)
    
    def confirmar_cpf(self):
        """Valida o CPF e finaliza a seleção"""
        if not self.chk_sem_cpf.isChecked():
            cpf = self.cpf_input.text()
            
            # Remover formatação
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            # Validar comprimento do CPF
            if len(cpf_limpo) != 11:
                QMessageBox.warning(self, "CPF Inválido", "Digite um CPF válido com 11 dígitos ou marque a opção 'Não informar CPF'.")
                return
            
            self.cpf = cpf
        else:
            self.cpf = ""
        
        # Emitir sinal com o tipo de cupom e CPF
        self.cupom_selecionado.emit(self.tipo_cupom, self.cpf)
        
        # Fechar o diálogo
        self.accept()


def solicitar_tipo_cupom(total_venda=0.0, parent=None):
    """
    Abre o diálogo para solicitar o tipo de cupom e CPF.
    
    Args:
        total_venda: Valor total da venda para exibir no diálogo
        parent: Widget pai
        
    Returns:
        tuple: (tipo_cupom, cpf) ou (None, None) se cancelado
    """
    dialog = CupomFiscalDialog(total_venda, parent)
    
    # Variáveis para armazenar o resultado
    resultado = [None, None]
    
    # Conectar o sinal ao handler
    def handle_cupom_selecionado(tipo, cpf):
        resultado[0] = tipo
        resultado[1] = cpf
    
    dialog.cupom_selecionado.connect(handle_cupom_selecionado)
    
    # Executar o diálogo
    if dialog.exec_() == QDialog.Accepted:
        return resultado[0], resultado[1]
    else:
        return None, None


# Teste do diálogo se executado diretamente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Testar o diálogo
    tipo_cupom, cpf = solicitar_tipo_cupom(125.75)
    
    if tipo_cupom:
        print(f"Tipo de cupom: {tipo_cupom}")
        print(f"CPF: {cpf if cpf else 'Não informado'}")
    else:
        print("Operação cancelada")
    
    sys.exit(0)