# helper.py - Auxilia com caminhos no executável
import os
import sys

def get_base_path():
    # Retorna o caminho base da aplicação, funcionando tanto em desenvolvimento quanto empacotado
    if getattr(sys, 'frozen', False):
        # Executando como .exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Executando em modo de desenvolvimento
        return os.path.dirname(os.path.abspath(__file__))

# Exemplo de uso:
# base_dir = get_base_path()
# db_path = os.path.join(base_dir, "base", "database.db")
