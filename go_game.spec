# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get absolute paths
base_path = SPECPATH
game_path = os.path.join(base_path, 'game')
images_path = os.path.join(game_path, 'images')
audio_path = os.path.join(game_path, 'audio')
img_path = os.path.join(base_path, 'img')

# Ensure the rules file exists
rules_file = os.path.join(img_path, 'Rules of Go Game.txt')
if not os.path.exists(rules_file):
    raise FileNotFoundError(f"Rules file not found at: {rules_file}")

a = Analysis(
    ['main.py'],
    pathex=[base_path],  # Add base path to Python path
    binaries=[],
    datas=[
        (images_path, 'game/images'),
        (audio_path, 'game/audio'),
        (rules_file, os.path.join('img')),  # Include just the rules file
    ],
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
    console=True,  # Temporarily set to True to see any errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
