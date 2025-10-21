# build_exe.py - VERSÃO ATUALIZADA - MODO --onefile COM BANCO EXTERNO, CONFIG.INI E FAVORITES.JSON

import os
import shutil
import subprocess
import sys
import json

def main():
    NOME_DO_PROGRAMA = "MBSistema"
    PONTO_DE_ENTRADA = "login.py"

    print(f"Preparando para compilar '{NOME_DO_PROGRAMA}' em um único executável...")
    
    # --- Limpeza ---
    print("Limpando builds e distribuições anteriores...")
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists(f'{NOME_DO_PROGRAMA}.spec'):
        os.remove(f'{NOME_DO_PROGRAMA}.spec')

    # --- Comando PyInstaller com --onefile ---
    pyinstaller_params = [
        sys.executable, "-m", "PyInstaller",
        PONTO_DE_ENTRADA,
        "--name", NOME_DO_PROGRAMA,
        "--onefile",
        #"--windowed",
        "--noconfirm",  # Evita perguntas durante a compilação
    ]

    # Adicionar ícone
    if os.path.exists("ico-img/icone.ico"):
        pyinstaller_params.extend(["--icon", "ico-img/icone.ico"])

    # --- INCLUSÃO DE DADOS DENTRO DO .EXE ---
    # Lista de pastas que serão empacotadas DENTRO do .exe.
    pastas_de_dados_internas = [
        "ico-img", "PDV", "geral", "vendas", "produtos_e_servicos",
        "compras", "financeiro", "relatorios", "notas_fiscais", "ferramentas",
        "mercado_livre", "cupons"
    ]
    
    print("\nAdicionando pastas de dados ao executável:")
    for pasta in pastas_de_dados_internas:
        if os.path.exists(pasta):
            pyinstaller_params.extend(["--add-data", f"{pasta}{os.pathsep}{pasta}"])
            print(f"- {pasta}")

    # Adicionar arquivos avulsos DENTRO do .exe, incluindo config.json (se existir para dev) e favorites.json
    arquivos_de_dados_internos = ["syncthing.exe", "assistente_historico.json"]
    if os.path.exists("config.json"):  # Só adiciona se existir (para testes dev)
        arquivos_de_dados_internos.append("config.json")
        print("- config.json (para fallback dev)")
    
    # Adição do novo arquivo favorites.json
    caminho_favorites = "config/favorites.json"
    if os.path.exists(caminho_favorites):
        arquivos_de_dados_internos.append(caminho_favorites)
        print("- config/favorites.json (novo arquivo de favoritos)")

    # Remova "base/config.ini" se não usar mais; ou mude para "base/config.json" se quiser lá
    for arquivo in arquivos_de_dados_internos:
        if os.path.exists(arquivo):
            destino = os.path.dirname(arquivo) if os.path.dirname(arquivo) else "."
            pyinstaller_params.extend(["--add-data", f"{arquivo}{os.pathsep}{destino}"])
            print(f"- {arquivo}")

    # --- Adicionar importações ocultas ---
    hidden_imports = [
        'requests', 'urllib3', 'idna', 'chardet', 'certifi', 'ctypes',
        'PyQt5.QtSvg', 'PyQt5.QtPrintSupport',
        'reportlab.pdfgen.canvas', 'reportlab.lib.pagesizes', 
        'reportlab.platypus', 'escpos.printer', 'win32api', 'win32print',
        'dotenv', 'webbrowser', 'fdb', 'matplotlib.backends.backend_qtagg',
        'pytz', 'configparser'  # Adicionado para garantir que configparser seja incluído
    ]
    hidden_imports.extend(['mercado_livre.main_final'])

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
    print("\nLembre-se: Para distribuir, você precisa do MBSistema.exe e da pasta 'base' ao seu lado, caso o banco de dados externo seja necessário.")
    print("------------------------------------------------------")

if __name__ == "__main__":
    main()