# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dancer.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config/*', 'config'),
        ('GIFs/*', 'GIFs'),
        ('music/*', 'music'),
        ('tray_icon.py', '.'),
        ('utils.py', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Dancer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='config/icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Dancer',
)