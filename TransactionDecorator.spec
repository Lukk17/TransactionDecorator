# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\gui.py'],
    pathex=['.'], # Assuming the .spec file is in the project root
    binaries=[],
    datas=[
        ('src/config/*', 'config/'),
        ('src/gui_elements/*', 'gui_elements/'),
        ('src/processor/*', 'processor/'),
        ('src/utils/*', 'utils/')
    ],
    hiddenimports=[
        'chardet',
        'json',
        'pandas',
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'PySide6.QtCore',
        'numpy'
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TransactionDecorator',
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
    icon=['./icons/logo.ico'],
    one_file=True,
)
