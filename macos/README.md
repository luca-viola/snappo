# Snappo for macOS

A menu bar app for grabbing the screen into the clipboard, with barcode and OCR
recognition. It is written in Python with
[rumps](https://github.com/jaredks/rumps) and packaged with
[py2app](https://py2app.readthedocs.io/).

## Requirements

The Makefile expects Python 3.11 from Homebrew at `/opt/homebrew/bin/python3.11`.

```sh
brew install python@3.11 tesseract zbar
/opt/homebrew/bin/python3.11 -m pip install -r requirements.txt py2app
```

`imgtocb.py` runs with whichever `python3` comes first on your `PATH`, and that
Python needs PyObjC, which rumps installs.

## Build

```sh
make        # creates dist/snappo.app
make clean  # removes build and dist
```

The Makefile builds with py2app's `-A` flag. That makes an alias bundle, which
runs from this folder and can't be copied to another Mac.

## Run without building

```sh
/opt/homebrew/bin/python3.11 snappo.py
```

Run it from this folder, because the icons and images are loaded by relative
path.
