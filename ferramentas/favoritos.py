import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QGraphicsDropShadowEffect, QScrollArea, 
    QCheckBox, QListWidget, QPushButton,QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtCore import Qt

class SeletorModulosEstilizado(QDialog):
    """
    Uma janela de diálogo com estilo para selecionar módulos favoritos.
    Esta classe agora herda de QDialog para se integrar com a janela principal.
    """
    def __init__(self, modulos_disponiveis, favoritos_atuais, parent=None):
        super().__init__(parent)
        
        # Recebe os módulos e favoritos da tela principal
        self.modulos_disponiveis = sorted(list(modulos_disponiveis))
        self.favoritos_atuais = favoritos_atuais
        
        self.initUI()
        self.setWindowTitle("Gerenciar Módulos Favoritos")
        
        # Preenche a lista da direita com os favoritos que já estavam selecionados
        self.atualizar_tela_principal()

    def initUI(self):
        """
        Inicializa a interface do usuário com o estilo profissional.
        """
        self.setMinimumSize(900, 700)
        self.setModal(True) # Torna a janela modal, bloqueando a principal
        
        self.setStyleSheet("background-color: #0a3b59;")

        central_widget = QWidget(self) # O widget central agora é filho direto do QDialog
        main_layout = QVBoxLayout(self) # O layout principal é aplicado diretamente ao QDialog
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        title_label = QLabel("Adicionar ou Remover Módulos Favoritos")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        content_container = QFrame()
        content_container.setStyleSheet("background-color: #0a3b59; border-radius: 10px;")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(5, 5)
        content_container.setGraphicsEffect(shadow)
        
        sections_layout = QHBoxLayout(content_container)
        sections_layout.setSpacing(20)
        sections_layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== SEÇÃO DE MÓDULOS (Esquerda) =====
        modulos_frame = QFrame()
        modulos_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        modulos_layout = QVBoxLayout(modulos_frame)
        
        modulos_label = QLabel("Módulos Disponíveis")
        modulos_label.setFont(QFont("Arial", 14, QFont.Bold))
        modulos_layout.addWidget(modulos_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white; border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)

        self.checkboxes = []
        for modulo_nome in self.modulos_disponiveis:
            checkbox = QCheckBox(modulo_nome)
            checkbox.setFont(QFont("Arial", 12))
            
            # Marca o checkbox se ele já for um favorito
            if modulo_nome in self.favoritos_atuais:
                checkbox.setChecked(True)
                
            checkbox.stateChanged.connect(self.atualizar_tela_principal)
            scroll_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
        
        scroll_area.setWidget(scroll_content)
        modulos_layout.addWidget(scroll_area)
        sections_layout.addWidget(modulos_frame, 1)
        
        # ===== SEÇÃO DA TELA PRINCIPAL (Direita) =====
        principal_frame = QFrame()
        principal_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        principal_layout = QVBoxLayout(principal_frame)
        
        principal_label = QLabel("Favoritos Selecionados")
        principal_label.setFont(QFont("Arial", 14, QFont.Bold))
        principal_layout.addWidget(principal_label)
        
        self.lista_tela_principal = QListWidget()
        self.lista_tela_principal.setStyleSheet("background-color: white; border: none; font-size: 12pt;")
        principal_layout.addWidget(principal_frame, 1)
        
        main_layout.addWidget(content_container)

        # ===== BOTÃO DE CONFIRMAÇÃO =====
        confirm_button = QPushButton("Confirmar")
        confirm_button.setFont(QFont("Arial", 12, QFont.Bold))
        confirm_button.setCursor(QCursor(Qt.PointingHandCursor))
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: white;
                border-radius: 5px;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00b248;
            }
        """)
        confirm_button.clicked.connect(self.confirmar_selecao)
        main_layout.addWidget(confirm_button)

    def atualizar_tela_principal(self):
        """
        Atualiza a lista de módulos e impõe um limite de 8 seleções.
        """
        modulos_selecionados = []
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                modulos_selecionados.append(checkbox.text())

        # --- NOVO: Lógica para limitar a seleção ---
        if len(modulos_selecionados) > 6:
            # Pega o checkbox que acabou de ser marcado
            sender = self.sender()
            if sender:
                # Bloqueia os sinais para evitar um loop infinito
                sender.blockSignals(True)
                # Desmarca o checkbox que excedeu o limite
                sender.setChecked(False)
                # Libera os sinais novamente
                sender.blockSignals(False)
            
            # Mostra um aviso para o usuário
            QMessageBox.warning(self, "Limite Atingido", "Você pode selecionar no máximo 6 módulos favoritos.")
            
            # Remove o item excedente da lista
            modulos_selecionados.pop()

        # Atualiza a lista da direita
        self.lista_tela_principal.clear()
        self.lista_tela_principal.addItems(sorted(modulos_selecionados))

    def confirmar_selecao(self):
        """
        Ação executada quando o botão Confirmar é clicado.
        Fecha a janela com o status 'Accepted'.
        """
        self.accept()

    def get_selecao_final(self):
        """
        Retorna a lista final de módulos selecionados.
        Este método será chamado pela janela principal após o fechamento.
        """
        modulos_selecionados = []
        for i in range(self.lista_tela_principal.count()):
            modulos_selecionados.append(self.lista_tela_principal.item(i).text())
        return modulos_selecionados

if __name__ == '__main__':
    # Código de exemplo para testar a janela de forma independente
    app = QApplication(sys.argv)
    
    # Simula os dados que viriam da tela principal
    modulos_teste = [
        "Cadastro de Clientes", "Produtos", "Pedido de vendas", 
        "Controle de caixa (PDV)", "Consulta CNPJ", "Fornecedores"
    ]
    favoritos_teste = ["Produtos", "Cadastro de Clientes"]
    
    janela = SeletorModulosEstilizado(modulos_disponiveis=modulos_teste, favoritos_atuais=favoritos_teste)
    
    # Em um teste, podemos verificar o resultado
    resultado = janela.exec_()
    if resultado == QDialog.Accepted:
        print("Seleção confirmada!")
        selecao = janela.get_selecao_final()
        print("Favoritos escolhidos:", selecao)
    else:
        print("Seleção cancelada.")
        
    sys.exit(0)