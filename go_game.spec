# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get the absolute path to the game directory
game_path = os.path.abspath(os.path.join(SPECPATH, 'game'))
images_path = os.path.join(game_path, 'images')

a = Analysis(
    ['match.py'],
    pathex=[],
    binaries=[],
    datas=[(images_path, 'game/images')],  # Include the entire images directory
    hiddenimports=[],
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
    name='Go Game',
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
)
