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
path. Run this way, macOS applies permissions to your terminal app rather than
to Snappo, and messages appear as alerts instead of notifications.

## Permissions

**Screen Recording** is the only permission Snappo needs to capture the screen.
Snappo checks it before each grab. If it's missing, Snappo explains why and can
open the right page in System Settings. After you allow it, quit and reopen
Snappo, because macOS doesn't apply the change to an app that's already running.

Snappo doesn't need Accessibility or Input Monitoring. To see notifications such
as "OCR Completed", they must be allowed for Snappo under Notifications in System
Settings.

### If captures only show the wallpaper

macOS can keep a permission that no longer applies, because rebuilding changes
the app's signature. This can happen even if Snappo looks allowed in System
Settings. To reset it:

```sh
tccutil reset ScreenCapture io.github.luca-viola.snappo
```

Then open Snappo, grab again, and allow it when asked.
