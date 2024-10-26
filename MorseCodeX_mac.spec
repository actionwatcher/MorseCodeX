# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MorseCodeX.py'],
    pathex=[],
    binaries=[('_sounddevice_data/portaudio-binaries/libportaudio.dylib', './_sounddevice_data/portaudio-binaries')],
    datas=[
        ('current_version.ver', './'), ('version_migrations.json', './'),
        ('configs/morse_table.json', './configs'), ('configs/qrn.wav', './configs'), ('configs/kbd_mapping.txt', './configs'),
        ('data_sources/MASTERSS.SCP', './data_sources'), ('data_sources/common100.txt', './data_sources'),
        ('data_sources/MASTER.SCP', './data_sources'), ('data_sources/numbers.txt', './data_sources'),
        ('data_sources/CWOPS_3600-DDD.txt', './data_sources'), ('data_sources/MASUSVE.SCP', './data_sources'),
        ('data_sources/NAQPCW.txt', './data_sources'), ('data_sources/ca_counties.txt', './data_sources'),
        ('data_sources/MASTERDX.SCP', './data_sources'), ('data_sources/states_provinces.txt', './data_sources'),
        ('data_sources/letters.txt', './data_sources'), ('data_sources/cqp.txt', './data_sources'),
        ('data_sources/arrl_sweepstakes.txt', './data_sources'), ('configs/message_policies.json', './configs')
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
    [],
    exclude_binaries=True,
    name='MorseCodeX',
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
    version='version.txt',
    icon=['MorseCodeX.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MorseCodeX',
)
app = BUNDLE(
    coll,
    name='MorseCodeX.app',
    icon='MorseCodeX.ico',
    bundle_identifier=None,
    info_plist={
	'CFBundleShortVersionString': '1.1.0.0'
    }
	
)
