# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from pathlib import Path
import os

DEMO_BUILD = os.environ.get('DARMANSOFT_DEMO_BUILD') == '1'
LAUNCHER = '../desktop_launcher_demo.py' if DEMO_BUILD else '../desktop_launcher.py'
PRODUCT_EXE = 'DarmanSoftDemo' if DEMO_BUILD else 'Clinita'

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('django')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('core')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('patients')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('appointments')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('billing')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('definitions')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('reception')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('records')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('accounts')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('accounting')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('aesthetics')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('dentistry')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('licensing')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Django templates are runtime files and must be copied explicitly into the
# Windows bundle.  This also keeps newly added panels available after install.
for app_name in ('core', 'patients', 'appointments', 'billing', 'definitions', 'reception', 'records', 'accounts', 'accounting', 'aesthetics', 'dentistry', 'licensing'):
    template_dir = Path('..') / app_name / 'templates'
    if template_dir.exists():
        datas.append((str(template_dir), f'{app_name}/templates'))

hiddenimports += [
    'aesthetics.apps', 'aesthetics.models', 'aesthetics.forms', 'aesthetics.urls', 'aesthetics.views',
    'dentistry.apps', 'dentistry.models', 'dentistry.forms', 'dentistry.urls', 'dentistry.views',
    'licensing.apps', 'licensing.middleware', 'licensing.service', 'licensing.urls', 'licensing.views',
]


a = Analysis(
    [LAUNCHER],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name=PRODUCT_EXE,
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=PRODUCT_EXE,
)
