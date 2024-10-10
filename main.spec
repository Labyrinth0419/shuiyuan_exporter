# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=['.'],  # 依赖于当前目录下的其他模块
    binaries=[],
    datas=[('attachments_handler.py', 'attachments_handler.py'),
            ('audio_handler.py', 'audio_handler.py'),
            ('constant.py', 'constant.py'),
            ('video_handler.py', 'video_handler.py'),
            ('utils.py', 'utils.py'),
            ('test.py', 'test.py'),
            ('image_handler.py', 'image_handler.py'),
            ('quality_list.py', 'quality_list.py'),
            ('README.md', 'README.md')], 
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)