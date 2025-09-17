# utils/paths.py
import os
import sys

def get_app_base_path():
    """
    Retorna o caminho base da aplicação, lidando com PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Estamos executando como um executável empacotado (PyInstaller)
        # O caminho base é o diretório do executável
        return os.path.dirname(sys.executable)
    else:
        # Estamos executando como um script Python normal
        # O caminho base é o diretório do script principal
        # (Isso assume que o script principal está no mesmo nível de "base" e "financeiro")
        # Se __file__ estiver em um subdiretório (ex: main_app/main.py),
        # você pode precisar de mais os.path.dirname()
        return os.path.dirname(os.path.abspath(sys.argv[0])) # Usa sys.argv[0] para o script principal