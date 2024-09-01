# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MorseCodeX.py'],
    pathex=[],
    binaries=[],
    datas=[('morse_table.json', './conf'), ('MASTER.SCP', './conf'), ('MASUSVE.SCP', './conf'), ('NAQPCW.txt', './conf'), ('ca_counties.txt', './conf'), ('MASTERDX.SCP', './conf'), ('states_provinces.txt', './conf'), ('letters.txt', './conf'), ('numbers.txt', './conf'), ('qrn.wav', './conf'), ('CWOPS_3600-DDD.txt', './conf'), ('MorseCodeX.ico', './')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MorseCodeX',
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
    icon=['MorseCodeX.ico'],
    version='version.txt',
)
