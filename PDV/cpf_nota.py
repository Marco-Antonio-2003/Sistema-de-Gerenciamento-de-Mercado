import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

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
        # Exibir valor total
        if self.total_venda > 0:
            lbl_total = QLabel(f"Total: R$ {self.total_venda:.2f}".replace('.', ','))
            lbl_total.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_total)

        # Botões principais
        btns_layout = QHBoxLayout()
        btn_com = QPushButton("CPF na nota")
        btn_sem = QPushButton("Não CPF na nota")
        btn_com.clicked.connect(self.opcao_com)
        btn_sem.clicked.connect(self.opcao_sem)
        btns_layout.addWidget(btn_com)
        btns_layout.addWidget(btn_sem)
        layout.addLayout(btns_layout)

    def opcao_com(self):
        cpf, ok = self.entrada_cpf()
        if not ok:
            return
        self.cupom_selecionado.emit('COM_CPF', cpf)
        self.accept()

    def opcao_sem(self):
        self.cupom_selecionado.emit('SEM_CPF', '')
        self.accept()

    def entrada_cpf(self):
        cpf, ok = QLineEdit.getText(
            self, "CPF na Nota", "Digite o CPF (somente números):"
        )
        if ok:
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            if len(cpf_limpo) != 11:
                QMessageBox.warning(
                    self, "CPF inválido", "O CPF deve conter 11 dígitos numéricos."
                )
                return '', False
            return cpf_limpo, True
        return '', False


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
