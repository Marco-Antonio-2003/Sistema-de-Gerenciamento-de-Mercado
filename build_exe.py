"""
Script para compilar o MB Sistema em um único executável (Modo --onefile)
"""

import os
import shutil
import subprocess
import sys

def main():
    print("Preparando para compilar MB Sistema em um único executável...")
    
    # --- Limpeza ---
    print("Limpando builds anteriores...")
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('MBSistema.spec'):
        os.remove('MBSistema.spec')

    # --- Comando PyInstaller com --onefile ---
    print("Executando PyInstaller...")

    pyinstaller_params = [
        sys.executable, "-m", "PyInstaller",
        "login.py",
        "--name", "MBSistema",
        "--onefile",  # <<< AQUI ESTÁ A CHAVE: Voltamos para o modo de arquivo único
        "--windowed",
        "--paths", ".",
    ]

    # Adicionar ícone
    if os.path.exists("ico-img/icone.ico"):
        pyinstaller_params.extend(["--icon", "ico-img/icone.ico"])

    # Adicionar dados e binários que precisam ser extraídos em tempo de execução
    data_to_add = [
        "ico-img", "base", "PDV", "geral", "vendas", "produtos_e_servicos",
        "compras", "financeiro", "relatorios", "notas_fiscais", "ferramentas",
        "mercado_livre", "cupons"
    ]
    for folder_name in data_to_add:
        if os.path.exists(folder_name):
            pyinstaller_params.extend(["--add-data", f"{folder_name};{folder_name}"])

    files_to_add = ["syncthing.exe", "assistente_historico.json"]
    for file_name in files_to_add:
        if os.path.exists(file_name):
            pyinstaller_params.extend(["--add-data", f"{file_name};."])

    # Adicionar importações ocultas
    hidden_imports = [
        'requests', 'urllib3', 'idna', 'chardet', 'certifi', 'ctypes',
        'PyQt5.QtSvg', 'reportlab.pdfgen.canvas', 'reportlab.lib.pagesizes', 
        'reportlab.platypus', 'escpos.printer', 'win32api', 'win32print',
        'dotenv', 'webbrowser', 'mercado_livre.main_final', 'mercado_livre.gerar_tokens',
    ]
    for hi in hidden_imports:
        pyinstaller_params.extend(["--hidden-import", hi])

    # Executar o comando
    print(f"\nComando PyInstaller: {' '.join(pyinstaller_params)}\n")
    try:
        subprocess.run(pyinstaller_params, check=True)
    except subprocess.CalledProcessError:
        print("\nERRO: O PyInstaller falhou.")
        return

    # --- Verificação Final ---
    exe_path = os.path.join("dist", "MBSistema.exe")
    if os.path.exists(exe_path):
        print("\nCompilação concluída com sucesso!")
        print(f"O executável único está disponível em: dist\\MBSistema.exe")
    else:
        print("\nAVISO: A compilação pode não ter sido concluída corretamente.")

if __name__ == "__main__":
    main()