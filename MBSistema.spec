# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['login.py'],
    pathex=[],
    binaries=[],
    datas=[('ico-img', 'ico-img'), ('PDV', 'PDV'), ('geral', 'geral'), ('vendas', 'vendas'), ('produtos_e_servicos', 'produtos_e_servicos'), ('compras', 'compras'), ('financeiro', 'financeiro'), ('relatorios', 'relatorios'), ('notas_fiscais', 'notas_fiscais'), ('ferramentas', 'ferramentas'), ('mercado_livre', 'mercado_livre'), ('cupons', 'cupons'), ('syncthing.exe', '.'), ('assistente_historico.json', '.'), ('config.json', '.')],
    hiddenimports=['requests', 'urllib3', 'idna', 'chardet', 'certifi', 'ctypes', 'PyQt5.QtSvg', 'PyQt5.QtPrintSupport', 'reportlab.pdfgen.canvas', 'reportlab.lib.pagesizes', 'reportlab.platypus', 'escpos.printer', 'win32api', 'win32print', 'dotenv', 'webbrowser', 'fdb', 'matplotlib.backends.backend_qtagg', 'pytz', 'configparser', 'mercado_livre.main_final'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MBSistema',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['ico-img\\icone.ico'],
)
