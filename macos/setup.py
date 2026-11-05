from setuptools import setup

APP = ['snappo.py']
DATA_FILES = ['VERSION', 'ui_abstract.py', 'ui_macos.py', 'permissions.py', 'imgtocb.py', 'snappo.sh', 'images']
OPTIONS = {
    'iconfile':'snappo.icns',    
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
        # macOS tracks permissions by this ID. Notifications also need it.
        'CFBundleIdentifier': 'io.github.luca-viola.snappo',
    },
    'packages': ['rumps', 'objc', 'os', 'subprocess', 'ctypes', 'Cocoa', 'AppKit', 'Foundation'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
