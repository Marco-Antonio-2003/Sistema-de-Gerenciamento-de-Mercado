import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFrame)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt

class ManutencaoNotasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manutenção de Notas Fiscais")
        self.setGeometry(300, 200, 600, 400)
        self.setStyleSheet("background-color: #272525;")
        self.initUI()
        
    def initUI(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título da janela
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #005079; border-radius: 5px;")
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("Manutenção de Notas Fiscais")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        main_layout.addWidget(title_frame)
        
        # Texto de instruções
        instruction_label = QLabel("Selecione o tipo de nota fiscal:")
        instruction_label.setFont(QFont("Arial", 14))
        instruction_label.setStyleSheet("color: white; margin-top: 20px;")
        instruction_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(instruction_label)
        
        # Botões para os tipos de notas fiscais - estilo atualizado
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Função para criar botões com estilo consistente
        def create_note_button(text, func):
            button = QPushButton(text)
            button.setFixedSize(300, 60)
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.setFont(QFont("Arial", 14, QFont.Bold))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #005079; 
                    color: white; 
                    border: none; 
                    border-radius: 5px;
                    padding: 10px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #003d5c;
                }
                QPushButton:pressed {
                    background-color: #00283d;
                }
            """)
            button.clicked.connect(func)
            return button
        
        # Botão NFC-e
        btn_nfce = create_note_button("NFC-e", lambda: self.open_nota_fiscal("NFC-e"))
        
        # Botão CF-e SAT
        btn_sat = create_note_button("CF-e SAT", lambda: self.open_nota_fiscal("CF-e SAT"))
        
        # Botão NFE
        btn_nfe = create_note_button("NFE", lambda: self.open_nota_fiscal("NFE"))
        
        # Adicionar botões ao layout
        buttons_layout.addWidget(btn_nfce)
        buttons_layout.addWidget(btn_sat)
        buttons_layout.addWidget(btn_nfe)
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
    
    def open_nota_fiscal(self, tipo_nota):
        """
        Abre a tela específica para o tipo de nota fiscal selecionado.
        """
        print(f"Selecionado: {tipo_nota}")
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Mapear o tipo de nota para o arquivo Python correspondente
            nota_files = {
                "NFC-e": os.path.join(script_dir, "nfce.py"),
                "CF-e SAT": os.path.join(script_dir, "sat.py"),
                "NFE": os.path.join(script_dir, "nfe.py")
            }
            
            # Verificar se o arquivo existe e executá-lo
            if tipo_nota in nota_files:
                file_path = nota_files[tipo_nota]
                
                # Verificar se o arquivo existe
                if os.path.exists(file_path):
                    subprocess.Popen([sys.executable, file_path])
                else:
                    # Se o arquivo não existe, criar uma cópia do nfe.py com o nome apropriado
                    source_file = os.path.join(script_dir, "nfe.py")
                    if os.path.exists(source_file):
                        with open(source_file, 'r', encoding='utf-8') as src:
                            content = src.read()
                        
                        # Substituir o nome da classe
                        if tipo_nota == "NFC-e":
                            content = content.replace("NFEWindow", "NFCEWindow")
                        elif tipo_nota == "CF-e SAT":
                            content = content.replace("NFEWindow", "SATWindow")
                        
                        # Escrever o novo arquivo
                        with open(file_path, 'w', encoding='utf-8') as dst:
                            dst.write(content)
                        
                        # Executar o arquivo recém-criado
                        subprocess.Popen([sys.executable, file_path])
                    else:
                        print(f"Arquivo fonte não encontrado: {source_file}")
        except Exception as e:
            print(f"Erro ao abrir tela de {tipo_nota}: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManutencaoNotasWindow()
    window.show()
    sys.exit(app.exec_())