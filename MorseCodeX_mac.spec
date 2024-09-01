# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MorseCodeX.py'],
    pathex=[],
    binaries=[('_sounddevice_data/portaudio-binaries/libportaudio.dylib', './_sounddevice_data/portaudio-binaries')],
    datas=[('morse_table.json', './conf'), ('MASTER.SCP', './conf'), ('MASUSVE.SCP', './conf'), ('NAQPCW.txt', './conf'), ('ca_counties.txt', './conf'), ('MASTERDX.SCP', './conf'), ('states_provinces.txt', './conf'), ('letters.txt', './conf'), ('numbers.txt', './conf'), ('qrn.wav', './conf'), ('CWOPS_3600-DDD.txt', './conf')],
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
	'CFBundleShortVersionString': '1.0 RC3'
    }
	
)
