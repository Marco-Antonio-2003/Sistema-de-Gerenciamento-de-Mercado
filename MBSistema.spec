# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['login.py'],
    pathex=[],
    binaries=[],
    datas=[('geral', 'geral'), ('vendas', 'vendas'), ('produtos_e_servicos', 'produtos_e_servicos'), ('compras', 'compras'), ('financeiro', 'financeiro'), ('relatorios', 'relatorios'), ('notas_fiscais', 'notas_fiscais'), ('ferramentas', 'ferramentas'), ('PDV', 'PDV'), ('base', 'base'), ('ico-img', 'ico-img'), ('ico-img\calendar-outline.svg', 'ico-img'), ('ico-img\down-arrow.png', 'ico-img'), ],
    hiddenimports=['requests', 'urllib3', 'idna', 'chardet', 'certifi', 'PyQt5', 'PyQt5.QtSvg', 'matplotlib', 'matplotlib.backends.backend_qt5agg', 'matplotlib.figure', 'numpy', 'datetime', 'reportlab', 'reportlab.pdfgen', 'reportlab', 'reportlab.pdfgen', 'reportlab.pdfgen.canvas', 'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.units', 'reportlab.lib.styles', 'reportlab.lib.enums', 'reportlab.lib.colors', 'reportlab.platypus', 'reportlab.lib'],
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
