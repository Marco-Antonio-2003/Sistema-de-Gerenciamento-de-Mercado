"""
Script para compilar o MB Sistema em um executável
Salve este arquivo na pasta raiz do projeto e execute-o com:
python build_exe.py
"""

import os
import shutil
import subprocess
import sys

def main():
    print("Preparando para compilar MB Sistema para executável...")
    
    # Verificar se o PyInstaller está instalado
    try:
        import PyInstaller
        print("PyInstaller encontrado!")
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Verificar e instalar requests se necessário
    try:
        import requests
        print("Módulo requests encontrado!")
    except ImportError:
        print("Módulo requests não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
    
    # Garantir que formulario_empresa.py existe em geral/
    geral_dir = os.path.join("geral")
    if not os.path.exists(geral_dir):
        os.makedirs(geral_dir)
    
    formulario_path = os.path.join(geral_dir, "formulario_empresa.py")
    if not os.path.exists(formulario_path):
        print(f"Criando arquivo {formulario_path}")
        # Aqui você pode copiar seu formulario_empresa.py original ou criar um básico
        # Este é apenas um placeholder
        with open(formulario_path, 'w', encoding='utf-8') as f:
            f.write("""from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox, QTableWidgetItem)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FormularioEmpresa(QWidget):
    def __init__(self, parent_window, form_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.form_window = form_window
        self.initUI()
        
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("Cadastro de Empresa")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Estilo comum para QLineEdit
        lineedit_style = '''
            QLineEdit {
                background-color: #fffff0;
                padding: 8px;
                font-size: 12px;
                min-height: 35px;
            }
        '''
        
        # Campo Nome
        self.nome_label = QLabel("Nome:")
        self.nome_label.setFont(QFont("Arial", 12))
        self.nome_label.setStyleSheet("color: white;")
        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet(lineedit_style)
        form_layout.addRow(self.nome_label, self.nome_input)
        
        # Campo CNPJ
        self.cnpj_label = QLabel("CNPJ:")
        self.cnpj_label.setFont(QFont("Arial", 12))
        self.cnpj_label.setStyleSheet("color: white;")
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setStyleSheet(lineedit_style)
        form_layout.addRow(self.cnpj_label, self.cnpj_input)
        
        # Botão Salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet('''
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 10px 20px;
                border: 1px solid #cccccc;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        ''')
        self.btn_salvar.clicked.connect(self.salvar_empresa)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(self.btn_salvar, 0, Qt.AlignCenter)
        
        # Estilo de fundo
        self.setStyleSheet("background-color: #043b57;")
        
    def salvar_empresa(self):
        nome = self.nome_input.text()
        cnpj = self.cnpj_input.text()
        
        # Validação básica
        if not nome or not cnpj:
            QMessageBox.warning(self, "Campos obrigatórios", "Por favor, preencha todos os campos.")
            return
        
        # Obter o próximo código disponível (exemplo simplificado)
        ultimo_codigo = 0
        for row in range(self.parent_window.table.rowCount()):
            codigo = int(self.parent_window.table.item(row, 0).text())
            if codigo > ultimo_codigo:
                ultimo_codigo = codigo
        
        novo_codigo = ultimo_codigo + 1
        
        # Adicionar à tabela
        row = self.parent_window.table.rowCount()
        self.parent_window.table.insertRow(row)
        self.parent_window.table.setItem(row, 0, QTableWidgetItem(str(novo_codigo)))
        self.parent_window.table.setItem(row, 1, QTableWidgetItem(nome))
        self.parent_window.table.setItem(row, 2, QTableWidgetItem(cnpj))
        
        # Mostrar mensagem de sucesso
        QMessageBox.information(self, "Sucesso", "Empresa cadastrada com sucesso!")
        
        # Limpar campos
        self.nome_input.clear()
        self.cnpj_input.clear()
        
        # Fechar o formulário, se necessário
        if self.form_window:
            self.form_window.close()
""")
    
    # Verificar e criar pasta para ícones específicos na pasta de destino
    print("Verificando ícones específicos...")
    ico_img_dir = "ico-img"
    if os.path.exists(ico_img_dir):
        # Verificar se os ícones específicos existem
        calendar_icon = os.path.join(ico_img_dir, "calendar-outline.svg")
        down_arrow_icon = os.path.join(ico_img_dir, "down-arrow.png")
        
        if os.path.exists(calendar_icon):
            print(f"Ícone de calendário encontrado: {calendar_icon}")
        else:
            print(f"AVISO: Ícone de calendário não encontrado em {calendar_icon}")
            
        if os.path.exists(down_arrow_icon):
            print(f"Ícone de seta para baixo encontrado: {down_arrow_icon}")
        else:
            print(f"AVISO: Ícone de seta para baixo não encontrado em {down_arrow_icon}")
    else:
        print(f"AVISO: Diretório de ícones {ico_img_dir} não encontrado!")
    
    # Criar arquivo spec personalizado
    print("Criando arquivo spec personalizado...")
    subprocess.run([
        "pyi-makespec",
        "--onefile",
        "--windowed",
        "--name", "MBSistema",
        "--icon=ico-img/icone.ico" if os.path.exists("ico-img/icone.ico") else "",
        # Adicionar módulos que precisam ser incluídos explicitamente
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=idna",
        "--hidden-import=chardet",
        "--hidden-import=certifi",
        "login.py"
    ])
    
    # Modificar o arquivo spec para incluir todos os recursos necessários
    print("Modificando arquivo spec...")
    with open("MBSistema.spec", "r", encoding="utf-8") as f:
        spec_content = f.read()
    
    # Modificar para incluir todos os diretórios e arquivos específicos
    if "datas=[]" in spec_content:
        # Incluir diretórios completos
        data_dirs = [
            "geral", "vendas", "produtos_e_servicos", "compras", 
            "financeiro", "relatorios", "notas_fiscais", "ferramentas"
        ]
        
        # Adicionar diretório de ícones e arquivos específicos
        data_str = "datas=["
        
        # Adicionar diretórios completos
        for d in data_dirs:
            if os.path.exists(d):
                data_str += f"('{d}', '{d}'), "
        
        # Adicionar diretório de ícones com tratamento especial
        if os.path.exists(ico_img_dir):
            data_str += f"('{ico_img_dir}', '{ico_img_dir}'), "
            
            # Adicionar arquivos específicos de ícones individualmente para garantir
            calendar_icon = os.path.join(ico_img_dir, "calendar-outline.svg")
            down_arrow_icon = os.path.join(ico_img_dir, "down-arrow.png")
            
            if os.path.exists(calendar_icon):
                data_str += f"('{calendar_icon}', '{ico_img_dir}'), "
            
            if os.path.exists(down_arrow_icon):
                data_str += f"('{down_arrow_icon}', '{ico_img_dir}'), "
        
        data_str += "]"
        
        spec_content = spec_content.replace("datas=[]", data_str)
    
    # Garantir que os hiddenimports incluam requests e suas dependências
    if "hiddenimports=[]" in spec_content:
        spec_content = spec_content.replace(
            "hiddenimports=[]",
            "hiddenimports=['requests', 'urllib3', 'idna', 'chardet', 'certifi']"
        )
    
    with open("MBSistema.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    # Compilar o executável
    print("Compilando o executável...")
    subprocess.run(["pyinstaller", "MBSistema.spec"])
    
    # Verificar se a compilação foi bem-sucedida
    exe_path = os.path.join("dist", "MBSistema.exe")
    if os.path.exists(exe_path):
        print("\nCompilação concluída com sucesso!")
        print(f"O executável está disponível em: {exe_path}")
        
        # Verificar se a pasta ico-img foi incluída no executável
        dist_ico_img = os.path.join("dist", "ico-img")
        if not os.path.exists(dist_ico_img):
            print("\nAVISO: A pasta ico-img não foi encontrada no diretório dist.")
            print("Copiando manualmente a pasta ico-img para o diretório dist...")
            
            # Copiar manualmente a pasta ico-img para o diretório dist
            if os.path.exists(ico_img_dir):
                shutil.copytree(ico_img_dir, dist_ico_img)
                print("Pasta ico-img copiada com sucesso para o diretório dist.")
    else:
        print("\nAVISO: A compilação pode não ter sido concluída corretamente.")
        print("Verifique as mensagens de erro acima.")

if __name__ == "__main__":
    main()
