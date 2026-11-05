# Snappo

**SN**apshot **APP**licati**O**n, a screenshot tool with barcode and OCR
capabilities, as a GNOME Shell extension.

Grab the desktop, a monitor, a window or an area into the clipboard. Then, with
one click, replace it with the text or barcode found in the image, ready to
paste.

This is a rewrite of the Python [Snappo](https://github.com/luca-viola/snappo).
It runs inside GNOME Shell, so it works on Wayland without `gnome-screenshot`,
`xclip`, `xdotool` or `xrandr`.

## Requirements

- GNOME Shell 51
- For OCR only: `tesseract` for text and `zbarimg` for barcodes

Snappo works without the OCR tools. If one is missing when you click **OCR**,
the notification names it and offers a **Copy command** button with the install
command for your distro. Snappo never installs anything itself.

| Distro | Command |
| --- | --- |
| Fedora, RHEL | `sudo dnf install tesseract zbar` |
| Debian, Ubuntu | `sudo apt install tesseract-ocr zbar-tools` |
| Arch | `sudo pacman -S tesseract tesseract-data-eng zbar` |
| openSUSE | `sudo zypper install tesseract-ocr zbar` |

## Installation

```sh
make install
```

Log out and back in so GNOME Shell finds the extension, then:

```sh
gnome-extensions enable snappo@lviola
```

`make uninstall` removes it. `make pack` builds a zip in `dist/`.

## Usage

Click the camera in the top bar.

| Menu item | What it does |
| --- | --- |
| **Grab Desktop..** | Captures all monitors. Parts of the image no monitor covers are transparent. |
| **1, 2, ...** | Captures one monitor, `*` marks the primary. Shown with two or more monitors. |
| **Grab Window..** | Hover to highlight a window, click to capture it. Escape cancels. |
| **Grab Area..** | Drag a rectangle. Escape cancels. |
| **Set Delay..** | Seconds to wait, 0 to 100. The top bar shows the countdown. |
| **Clipboard..** | Opens the snapshot in your image viewer. |
| **Copy..** | Puts the snapshot back in the clipboard. |
| **Save as..** | Saves the snapshot as a PNG file. |
| **Clear..** | Empties the clipboard and deletes the snapshot. |
| **OCR** | Looks for a barcode, then for text, and puts the result in the clipboard. |
| **About..** | Shows credits and license. |

With a delay set, you choose the window or area first and the capture happens
after the countdown, so you can open a menu or a tooltip in the meantime. A
window is captured even if something covers it by then. Starting another grab
replaces one that is counting down.

## Privacy

The snapshot is stored in `$XDG_RUNTIME_DIR/snappo/`, readable only by you and
deleted at logout. It stays there when the screen locks, but a countdown is
cancelled so nothing captures the lock screen.

## License

GPL-3.0-or-later, see [LICENSE](LICENSE).
