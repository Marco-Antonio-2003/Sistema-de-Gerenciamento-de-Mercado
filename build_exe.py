# build_exe.py - VERSÃO FINAL CORRIGIDA

import os
import shutil
import subprocess
import sys

def main():
    NOME_DO_PROGRAMA = "MBSistema"
    PONTO_DE_ENTRADA = "login.py"

    print(f"Preparando para compilar '{NOME_DO_PROGRAMA}' em um único executável...")
    
    # Limpeza
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    if os.path.exists(f'{NOME_DO_PROGRAMA}.spec'):
        os.remove(f'{NOME_DO_PROGRAMA}.spec')

    # Comando PyInstaller
    pyinstaller_params = [
        sys.executable, "-m", "PyInstaller",
        PONTO_DE_ENTRADA,
        "--name", NOME_DO_PROGRAMA,
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
    ]

    # Ícone
    if os.path.exists("ico-img/icone.ico"):
        pyinstaller_params.extend(["--icon", "ico-img/icone.ico"])

    # --- INCLUSÃO DE DADOS DENTRO DO .EXE ---
    # **CORREÇÃO 1:** REMOVIDA A PASTA 'base' DESTA LISTA.
    # Agora, o banco de dados NÃO será empacotado dentro do .exe.
    pastas_de_dados_internas = [
        "PDV", "geral", "vendas", "produtos_e_servicos",
        "compras", "financeiro", "relatorios", "notas_fiscais", 
        "ferramentas", "mercado_livre", "cupons", "ico-img"
    ]
    
    print("\nAdicionando pastas de dados ao executável:")
    for pasta in pastas_de_dados_internas:
        if os.path.exists(pasta):
            pyinstaller_params.extend(["--add-data", f"{pasta}{os.pathsep}{pasta}"])
            print(f"- {pasta}")

    # Adicionar arquivos avulsos DENTRO do .exe
    arquivos_de_dados_internos = ["syncthing.exe", "assistente_historico.json"]
    for arquivo in arquivos_de_dados_internos:
         if os.path.exists(arquivo):
            pyinstaller_params.extend(["--add-data", f"{arquivo}{os.pathsep}."])
            print(f"- {arquivo}")


    # --- Adicionar importações ocultas ---
    # **CORREÇÃO 2:** ADICIONADO 'PyQt5.QtPrintSupport'.
    hidden_imports = [
        'requests', 'urllib3', 'idna', 'chardet', 'certifi', 'ctypes',
        'PyQt5.QtSvg', 'PyQt5.QtPrintSupport',  # <<< MÓDULO ADICIONADO AQUI
        'reportlab.pdfgen.canvas', 'reportlab.lib.pagesizes', 
        'reportlab.platypus', 'escpos.printer', 'win32api', 'win32print',
        'dotenv', 'webbrowser', 'fdb'
    ]
    for hi in hidden_imports:
        pyinstaller_params.extend(["--hidden-import", hi])

    # Executar o comando de compilação
    print(f"\nComando PyInstaller final:\n{' '.join(pyinstaller_params)}\n")
    try:
        subprocess.run(pyinstaller_params, check=True, text=True, capture_output=False)
    except subprocess.CalledProcessError as e:
        print("\nERRO: O PyInstaller falhou.")
        if e.stderr: print(f"Saída do erro:\n{e.stderr}")
        return

    print("\n------------------------------------------------------")
    print("✅ Compilação concluída com sucesso!")
    print(f"O executável está pronto em: .\\dist\\{NOME_DO_PROGRAMA}.exe")
    print("\nLembre-se: Para o programa funcionar, ele precisa da pasta 'base' ao seu lado.")
    print("------------------------------------------------------")

if __name__ == "__main__":
    main()