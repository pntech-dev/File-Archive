# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

cryptography_datas, cryptography_binaries, cryptography_hiddenimports = collect_all('cryptography')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=cryptography_binaries,
    datas=[
        ('password.key', '.'),
        ('keyfile.key', '.'),
        ('config.yaml', '.'),
        ('version 4.0.0.txt', '.'),
        ('updater.exe', '.')
    ] + cryptography_datas,
    hiddenimports=['PyYaml'] + cryptography_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'email',
        'http',
        'xmlrpc',
        'pydoc',
        'doctest',
        'PyQt5.QtSql',
        'PyQt5.QtTest',
        'PyQt5.QtNetwork',
        'PyQt5.QtXml',
        'PyQt5.QtWebEngine',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtNfc',
        'PyQt5.QtSensors',
        'PyQt5.QtSerialPort',
        'PyQt5.QtPositioning'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='File Archive',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='File Archive',
)