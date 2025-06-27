"""
Script para compilar o MB Sistema em um executável (VERSÃO MELHORADA)
Salve este arquivo na pasta raiz do projeto e execute-o com:
python build_exe.py
"""

import os
import shutil
import subprocess
import sys

def main():
    print("Preparando para compilar MB Sistema para executável...")
    
    # --- Verificação de Módulos (sem alterações) ---
    # (Toda a sua parte de verificação de módulos permanece aqui)

    # --- Limpeza de Builds Anteriores (Recomendado) ---
    print("Limpando builds anteriores...")
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('MBSistema.spec'):
        os.remove('MBSistema.spec')

    # --- Comando PyInstaller Mais Robusto ---
    print("Executando PyInstaller...")

    # Parâmetros para o PyInstaller
    pyinstaller_params = [
        sys.executable, "-m", "PyInstaller",
        "login.py",
        "--name", "MBSistema",
        "--onefile",
        "--windowed",
        # <<< MELHORIA >>> Adiciona o diretório raiz aos caminhos de busca de módulos
        # Isso ajuda o PyInstaller a encontrar pacotes como 'ecommerce', 'base', etc.
        "--paths", ".",
    ]

    # Adicionar ícone se existir
    if os.path.exists("ico-img/icone.ico"):
        pyinstaller_params.extend(["--icon", "ico-img/icone.ico"])

    # <<< MELHORIA >>> Adicionar dados de forma explícita
    # O formato é 'origem:destino_dentro_do_exe'
    data_to_add = [
        "ico-img", "base", "PDV", "geral", "vendas", "produtos_e_servicos",
        "compras", "financeiro", "relatorios", "notas_fiscais", "ferramentas",
        "ecommerce" # Adiciona a pasta de ecommerce explicitamente
    ]
    for data in data_to_add:
        if os.path.exists(data):
            pyinstaller_params.extend(["--add-data", f"{data}{os.pathsep}{data}"])
        else:
            print(f"AVISO: Diretório de dados '{data}' não encontrado!")

    # Adicionar syncthing.exe se existir
    if os.path.exists("syncthing.exe"):
        pyinstaller_params.extend(["--add-data", f"syncthing.exe{os.pathsep}."])

    # <<< MELHORIA >>> Adicionar importações ocultas de forma explícita
    hidden_imports = [
        'requests', 'urllib3', 'idna', 'chardet', 'certifi', 
        'PyQt5.QtSvg', 'reportlab.pdfgen.canvas', 'reportlab.lib.pagesizes', 
        'reportlab.platypus', 'escpos.printer', 'win32api', 'win32print',
        'dotenv', 'webbrowser',
        # <<< ADICIONADO >>> Força a inclusão dos módulos do seu novo pacote
        'ecommerce.mercado_livre',
        'ecommerce.mercado_livre_backend',
        'ecommerce.configuracoes'
    ]
    for hi in hidden_imports:
        pyinstaller_params.extend(["--hidden-import", hi])

    # Executar o comando completo
    print(f"Comando PyInstaller: {' '.join(pyinstaller_params)}")
    subprocess.run(pyinstaller_params)
    
    # --- Verificação Final ---
    exe_path = os.path.join("dist", "MBSistema.exe")
    if os.path.exists(exe_path):
        print("\nCompilação concluída com sucesso!")
        print(f"O executável está disponível em: {exe_path}")
    else:
        print("\nAVISO: A compilação pode não ter sido concluída corretamente.")
        print("Verifique as mensagens de erro acima.")

if __name__ == "__main__":
    main()