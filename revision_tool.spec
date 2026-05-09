# -*- mode: python ; coding: utf-8 -*-
# Copyright (c) 2026 王刚. All rights reserved.
import sys
from pathlib import Path

block_cipher = None

PROJECT_ROOT = Path(SPECPATH)
REVISION_TOOL_DIR = str(PROJECT_ROOT / "revision_tool")

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "revision_tool",
        "revision_tool.core",
        "revision_tool.clause_parser",
        "revision_tool.tracked_changes",
        "revision_tool.doc_compare",
        "revision_tool.table_generator",
        "revision_tool.gui",
        "lxml._elementpath",
        "lxml.etree",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "pandas", "scipy", "PIL",
        "tkinter.test", "unittest", "pydoc",
    ],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="制度修订对照表生成工具",
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
    icon=str(PROJECT_ROOT / "app_icon.ico"),
    version=str(PROJECT_ROOT / "version_info.txt"),
)
