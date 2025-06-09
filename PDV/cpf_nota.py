import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class CpfNotaDialog(QDialog):
    """Diálogo para entrada de CPF e Nome do cliente"""
    cpf_dados_inseridos = pyqtSignal(str, str)  # CPF, Nome
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CPF NA NOTAS")
        self.setFixedSize(450, 200)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("CPF NA NOTAS")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Campo CPF
        cpf_layout = QHBoxLayout()
        lbl_cpf = QLabel("CPF")
        lbl_cpf.setFixedWidth(80)
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("000.000.000-00")
        self.cpf_input.setMaxLength(14)  # Máximo com formatação
        self.cpf_input.textChanged.connect(self.formatar_cpf)
        cpf_layout.addWidget(lbl_cpf)
        cpf_layout.addWidget(self.cpf_input)
        layout.addLayout(cpf_layout)
        
        # Campo Nome do cliente
        nome_layout = QHBoxLayout()
        lbl_nome = QLabel("Nome do cliente\n(Opcional)")
        lbl_nome.setFixedWidth(80)
        lbl_nome.setAlignment(Qt.AlignTop)
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome do cliente (opcional)")
        nome_layout.addWidget(lbl_nome)
        nome_layout.addWidget(self.nome_input)
        layout.addLayout(nome_layout)
        
        # Botão Emitir
        btn_emitir = QPushButton("EMITIR")
        btn_emitir.setStyleSheet("""
            QPushButton {
                background-color: #00FF7F;
                color: black;
                font-weight: bold;
                font-size: 12px;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00E68C;
            }
        """)
        btn_emitir.clicked.connect(self.emitir_cupom)
        layout.addWidget(btn_emitir)
    
    def formatar_cpf(self, texto):
        """Formata o CPF automaticamente enquanto o usuário digita"""
        # Remove tudo que não é número
        numeros = ''.join(filter(str.isdigit, texto))
        
        # Limita a 11 dígitos
        numeros = numeros[:11]
        
        # Aplica a formatação
        if len(numeros) <= 3:
            formatado = numeros
        elif len(numeros) <= 6:
            formatado = f"{numeros[:3]}.{numeros[3:]}"
        elif len(numeros) <= 9:
            formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
        else:
            formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        
        # Evita loop infinito ao atualizar o texto
        if formatado != texto:
            posicao_cursor = self.cpf_input.cursorPosition()
            self.cpf_input.setText(formatado)
            
            # Ajusta a posição do cursor
            nova_posicao = posicao_cursor
            if len(formatado) > len(texto):
                nova_posicao += 1
            elif len(formatado) < len(texto):
                nova_posicao -= 1
            
            nova_posicao = max(0, min(nova_posicao, len(formatado)))
            self.cpf_input.setCursorPosition(nova_posicao)
    
    def emitir_cupom(self):
        cpf_formatado = self.cpf_input.text().strip()
        nome = self.nome_input.text().strip()
        
        if not cpf_formatado:
            QMessageBox.warning(self, "Campo obrigatório", "Por favor, digite o CPF.")
            return
        
        # Remove a formatação para validar
        cpf_limpo = ''.join(filter(str.isdigit, cpf_formatado))
        
        if len(cpf_limpo) != 11:
            QMessageBox.warning(
                self, "CPF inválido", "O CPF deve conter 11 dígitos numéricos."
            )
            return
        
        self.cpf_dados_inseridos.emit(cpf_limpo, nome)
        self.accept()

class CupomDialogSimples(QDialog):
    # sinal: tipo_cupom ('COM_CPF' ou 'SEM_CPF'), cpf opcional
    cupom_selecionado = pyqtSignal(str, str)

    def __init__(self, total_venda=0.0, parent=None):
        super().__init__(parent)
        self.total_venda = total_venda
        self.setWindowTitle("Finalizar Venda")
        self.setFixedSize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        
        # Exibir valor total
        if self.total_venda > 0:
            lbl_total = QLabel(f"Total: R$ {self.total_venda:.2f}".replace('.', ','))
            lbl_total.setAlignment(Qt.AlignCenter)
            lbl_total.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(lbl_total)

        # Botões principais
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(20)
        
        # Botão CPF na nota (verde)
        btn_com = QPushButton("CPF NA NOTA")
        btn_com.setStyleSheet("""
            QPushButton {
                background-color: #00FF7F;
                color: black;
                font-weight: bold;
                font-size: 12px;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00E68C;
            }
        """)
        btn_com.clicked.connect(self.opcao_com)
        
        # Botão Sem CPF na nota (laranja)
        btn_sem = QPushButton("SEM CPF NA NOTA")
        btn_sem.setStyleSheet("""
            QPushButton {
                background-color: #FF8C42;
                color: black;
                font-weight: bold;
                font-size: 12px;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #FF7A28;
            }
        """)
        btn_sem.clicked.connect(self.opcao_sem)
        
        btns_layout.addWidget(btn_com)
        btns_layout.addWidget(btn_sem)
        layout.addLayout(btns_layout)

    def opcao_com(self):
        """Abre o diálogo de CPF na nota"""
        dialog_cpf = CpfNotaDialog(self)
        
        def handle_cpf_dados(cpf, nome):
            # Mantém compatibilidade: emite apenas tipo e CPF
            self.cupom_selecionado.emit('COM_CPF', cpf)
        
        dialog_cpf.cpf_dados_inseridos.connect(handle_cpf_dados)
        
        if dialog_cpf.exec_() == QDialog.Accepted:
            self.accept()

    def opcao_sem(self):
        """Vai direto para a próxima página sem CPF"""
        self.cupom_selecionado.emit('SEM_CPF', '')
        self.accept()


def solicitar_tipo_cupom(total_venda=0.0, parent=None):
    dialog = CupomDialogSimples(total_venda, parent)
    resultado = [None, None]
    
    def handler(tipo, cpf):
        resultado[0], resultado[1] = tipo, cpf
    
    dialog.cupom_selecionado.connect(handler)
    
    if dialog.exec_() == QDialog.Accepted:
        return tuple(resultado)
    return None, None

# Exemplo de uso
if __name__ == '__main__':
    app = QApplication(sys.argv)
    tipo, cpf = solicitar_tipo_cupom(123.45)
    if tipo:
        print('Tipo:', tipo)
        print('CPF:', cpf or 'Não informado')
    else:
        print('Cancelado')
    sys.exit(0)