# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for LabQC standalone Windows executable.

Build command:
    pip install pyinstaller
    pyinstaller labqc.spec

Output:
    dist/LabQC.exe  -- double-click to run
"""

import os
import sys
from pathlib import Path

# Paths relative to this spec file
ROOT = Path(SPECPATH).resolve()
FRONTEND_DIST = ROOT / "frontend" / "dist"
ENTRY_SCRIPT = ROOT / "run_labqc.py"

# Collect frontend dist as data files
frontend_data = []
if FRONTEND_DIST.exists():
    for root, dirs, files in os.walk(FRONTEND_DIST):
        for f in files:
            src = Path(root) / f
            rel = src.relative_to(FRONTEND_DIST)
            dest_dir = f"frontend_dist/{rel.parent}"
            frontend_data.append((str(src), dest_dir))

a = Analysis(
    [str(ENTRY_SCRIPT)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=frontend_data,
    hiddenimports=[
        "backend",
        "backend.main",
        "backend.db",
        "backend.db.database",
        "backend.auth",
        "backend.routers",
        "backend.routers.auth",
        "backend.routers.qc",
        "backend.routers.sigma",
        "backend.routers.validation",
        "backend.routers.audit",
        "backend.routers.lots",
        "backend.routers.rag",
        "backend.routers.eqa",
        "backend.routers.lis",
        "backend.routers.settings",
        "backend.models",
        "backend.models.qc_models",
        "backend.models.sigma_models",
        "backend.models.validation_models",
        "backend.models.audit_models",
        "backend.models.lot_models",
        "backend.models.eqa_models",
        "backend.models.settings_models",
        "backend.services",
        "backend.services.lis_parser",
        "sqlalchemy.sql.default_comparator",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "PIL",
        "cv2",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LabQC",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,       # Show console window (useful for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "frontend" / "dist" / "favicon.svg") if (ROOT / "frontend" / "dist" / "favicon.svg").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LabQC",
)
