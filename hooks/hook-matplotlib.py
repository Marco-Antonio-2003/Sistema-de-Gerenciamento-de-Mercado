
# hook-matplotlib.py
from PyInstaller.utils.hooks import collect_all

# Coletar todos os pacotes, dados e binários relacionados ao matplotlib
datas, binaries, hiddenimports = collect_all('matplotlib')
