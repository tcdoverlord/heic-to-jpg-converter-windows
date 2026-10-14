# Build this specification on Windows. PyInstaller does not cross-compile.
from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
)

hidden_imports = collect_submodules("pillow_heif")
binaries = collect_dynamic_libs("pillow_heif")
data_files = collect_data_files("pillow_heif")

analysis = Analysis(
    ["main.py"],
    pathex=["src"],
    binaries=binaries,
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="HEIC_to_JPG_Converter_TCDOVERLORD",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
