# Snappo.spec
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['snappo.py'],               # Entry point
    pathex=['.'],                # Base path of the project
    binaries=[],                 # Add binaries here if needed
    datas=[
        ('macos', 'Frameworks/macos'),     # Include macos directory
        ('VERSION', 'Frameworks'),        # Include VERSION file
        ('camera.svg', '.'),     # Include specific SVG file
        ('hour_glass.svg', '.'), # Include specific SVG file
    ],
    hiddenimports=collect_submodules('utils'),  # Automatically includes utils/ folder
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
    name='Snappo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='macos/snappo.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Snappo'
)

