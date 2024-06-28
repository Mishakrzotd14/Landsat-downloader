a = Analysis(
    ['main.py', 'api/landsat_api.py', 'gui/gui.py', 'gui/gui_utils.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('api', 'api'),
        ('gui', 'gui'),
        ('D:/projects/projects_2024/romankevich_landsat/venv/Lib/site-packages/customtkinter', 'customtkinter/'),
        ('D:/projects/projects_2024/romankevich_landsat/venv/Lib/site-packages/babel', 'babel/'),
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='LandsatDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['ico/satellite.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='landsat_downloader',
)
