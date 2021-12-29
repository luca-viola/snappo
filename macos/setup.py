from setuptools import setup

APP = ['snappo.py']
#DATA_FILES = ['imgtocb.py','snappo.sh','./images/noimg_red.png','./images/clear.png','./images/lens.png','./images/copy.png']
DATA_FILES = ['imgtocb.py','snappo.sh','images']
OPTIONS = {
    'iconfile':'snappo.icns',    
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps','objc','os','subprocess','Cocoa','AppKit','Foundation'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
