# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# ------------------------------------------------------------
# Platform‑specific icon selection
# ------------------------------------------------------------
if sys.platform == "darwin":
    icon_file = "assets/FreshNamerIcon.icns"
elif sys.platform == "win32":
    icon_file = "assets/FreshNamerIcon.ico"
else:
    icon_file = "assets/FreshNamerIcon.png"

# ------------------------------------------------------------
# Icons file paths
# ------------------------------------------------------------
datas = [
    ("assets/FreshNamerIcon.png", "assets"),
    ("assets/FreshNamerIcon.ico", "assets"),
    ("assets/FreshNamerIcon.icns", "assets"),
]

# ------------------------------------------------------------
# Main analysis step
# ------------------------------------------------------------
a = Analysis(
    ['GUI.py'],                 # your entry point
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# ------------------------------------------------------------
# Python bytecode archive
# ------------------------------------------------------------
pyz = PYZ(a.pure)

# ------------------------------------------------------------
# Executable configuration
# ------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FreshNamer',
    icon=icon_file,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,              # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,       # macOS only; safe to leave off
    target_arch=None,
    codesign_identity=None,     # macOS signing handled separately
    entitlements_file=None,
)

# ------------------------------------------------------------
# Final bundled output
# ------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FreshNamer',
)
