# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Assets (иконки и ресурсы) — опциональны
import os
SPEC_DIR = os.path.dirname(os.path.abspath(SPECPATH))
ROOT_DIR = os.path.abspath(os.path.join(SPEC_DIR, '..'))
assets_dir = os.path.join(ROOT_DIR, 'assets')
datas = [
    ('../config.json', '.'),
    ('../core', 'core'),
    ('../modules', 'modules'),
    ('../voice', 'voice'),
    ('../ui', 'ui'),
    ('../automation', 'automation'),
    ('../ai', 'ai'),
    ('../smart_home', 'smart_home'),
    ('../mobile', 'mobile'),
]
if os.path.isdir(assets_dir):
    datas.append(('../assets', 'assets'))

# Иконка — только если файл существует
icon_path = os.path.join(assets_dir, 'jarvis.ico') if os.path.isdir(assets_dir) else None
if icon_path and not os.path.isfile(icon_path):
    icon_path = None

a = Analysis(
    ['../main.py'],
    pathex=[ROOT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pyttsx3',
        'speech_recognition',
        'psutil',
        'win32gui',
        'win32con',
        'pycaw',
        'comtypes',
        'pystray',
        'PIL',
        'openai',
        'sklearn',
        'aiohttp',
        'websockets',
        'dotenv',
        'qrcode',
        'numpy',
        'scipy',
        'joblib',
        'cv2',
        'pytesseract',
        'sounddevice',
        'pygame',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
    ],
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
    name='JARVIS',
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
    icon=icon_path,
    version='version_info.txt',
)
