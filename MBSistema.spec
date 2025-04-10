# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['login.py'],
    pathex=[],
    binaries=[],
    datas=[('geral', 'geral'), ('vendas', 'vendas'), ('produtos_e_servicos', 'produtos_e_servicos'), ('compras', 'compras'), ('financeiro', 'financeiro'), ('relatorios', 'relatorios'), ('notas_fiscais', 'notas_fiscais'), ('ferramentas', 'ferramentas'), ('ico-img', 'ico-img'), ],
    hiddenimports=['requests', 'urllib3', 'idna', 'chardet', 'certifi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
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
