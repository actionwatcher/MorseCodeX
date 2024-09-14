# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MorseCodeX.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('current_version.ver', './'), ('version_migrations.json', './'),
        ('configs/morse_table.json', './configs'), ('configs/qrn.wav', './configs'), ('configs/kbd_mapping.txt', './configs'),
        ('data_sources/MASTERSS.SCP', './data_sources'), ('data_sources/common100.txt', './data_sources'),
        ('data_sources/MASTER.SCP', './data_sources'), ('data_sources/numbers.txt', './data_sources'),
        ('data_sources/CWOPS_3600-DDD.txt', './data_sources'), ('data_sources/MASUSVE.SCP', './data_sources'),
        ('data_sources/NAQPCW.txt', './data_sources'), ('data_sources/ca_counties.txt', './data_sources'),
        ('data_sources/MASTERDX.SCP', './data_sources'), ('data_sources/states_provinces.txt', './data_sources'),
        ('data_sources/letters.txt', './data_sources'),
        ('MorseCodeX.ico', './')
        ],
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
