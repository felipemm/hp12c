# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data'), ('hp12c/resources', 'hp12c/resources')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'PIL', 'PIL.Image', 'PIL.ImageTk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5.QtBluetooth', 'PyQt5.Qt3DCore', 'PyQt5.Qt3DRender', 'PyQt5.Qt3DQuick', 'PyQt5.Qt3DInput', 'PyQt5.Qt3DLogic', 'PyQt5.Qt3DAnimation', 'PyQt5.Qt3DExtras', 'PyQt5.QtQuick', 'PyQt5.QtQuick3D', 'PyQt5.QtQuickWidgets', 'PyQt5.QtQml', 'PyQt5.QtWebEngine', 'PyQt5.QtWebEngineCore', 'PyQt5.QtPdf', 'PyQt5.QtBodymovin', 'PyQt5.QtGamepad'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='hp12c',
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
    icon=['hp12c/resources/skins/argentum/icon.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hp12c',
)
app = BUNDLE(
    coll,
    name='hp12c.app',
    icon='hp12c/resources/skins/argentum/icon.png',
    bundle_identifier='com.hp12c.emulator',
)
