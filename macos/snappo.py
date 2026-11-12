#!/usr/bin/env python3
import shutil
import signal
import subprocess

from ui_abstract import *

import rumps
from AppKit import NSAlertFirstButtonReturn, NSAlertSecondButtonReturn
from ui_macos import Snappo, ImageResolver, Notification, Alert

# An app started from Finder gets a minimal PATH, without Homebrew's folders.
for _folder in ("/opt/homebrew/bin", "/usr/local/bin"):
    if _folder not in os.environ.get("PATH", "").split(":"):
        os.environ["PATH"] = os.environ.get("PATH", "") + ":" + _folder
rumps.debug_mode(True)

BASH_PATH = os.path.dirname(os.path.abspath(__file__)) + "/snappo.sh"


class ImageChangingNotifier:
    image_changing_notifier = None

    def __init__(self):
        pass

    def set_image_changing_notifier(self, image_changing_notifier):
        self.image_changing_notifier = image_changing_notifier

    def get_image_changing_notifier(self):
        return self.image_changing_notifier

    def _has_method(self, instance, method):
        method_list = dir(instance)
        if method in method_list:
            return True
        return False

    def set_icon(self, icon):
        if self.image_changing_notifier is not None:
            if self._has_method(self.image_changing_notifier, 'set_image'):
                self.image_changing_notifier.set_image(icon)
            if self._has_method(self.image_changing_notifier, 'set_icon'):
                self.image_changing_notifier.set_icon(icon)


class ClipBoardManager:

    def __init__(self, notification_manager, image_resolver, image_changing_notifier):
        self.notification_manager = notification_manager
        self.image_resolver = image_resolver
        self.image_changing_notifier = image_changing_notifier
        self.BASH_PATH = BASH_PATH

    def copy(self, widget):
        ret = os.system(self.BASH_PATH+" copy")
        if ret != 0:
            self.notification_manager.new("Clipboard Error.", "The clipboard seems empty, grab an image first.").show()

    def clear(self, sender):
        ret = os.system(self.BASH_PATH + " clear")
        self.image_changing_notifier.set_icon(self.image_resolver.get_noimg_icon())


class ScreenGrabber:
    zbar_warned = False

    def __init__(self, notification_manager, image_resolver, image_changing_notifier):
        self.notification_manager = notification_manager
        self.image_resolver = image_resolver
        self.image_changing_notifier = image_changing_notifier
        self.BASH_PATH = BASH_PATH

    def grab(self, what, delay=0, which_desktop=""):
        if what in ['area', 'desktop', 'window']:
            os.system(self.BASH_PATH + " " + what + " " + str(int(delay)) + " " + which_desktop)
            thumb = self.image_resolver.get_lens_icon()
            self.image_changing_notifier.set_icon(thumb)

    INSTALL_COMMAND = "brew install tesseract zbar"
    BREW_URL = "https://brew.sh"

    def _show_missing_tools_alert(self, missing):
        answer = Alert(
            "OCR needs " + " and ".join(missing),
            "Snappo reads text with Tesseract and barcodes with zbar. "
            "Install them with Homebrew by typing this in Terminal:\n\n"
            "    " + self.INSTALL_COMMAND + "\n\n"
            "If Terminal says \"brew: command not found\", install Homebrew "
            "first: open " + self.BREW_URL + " and paste the one-line command "
            "from its front page into Terminal. Then run the line above.\n\n"
            "Then press OCR again. No restart is needed.",
            ["Copy Install Command", "Open brew.sh", "Close"]).show()
        if answer == NSAlertFirstButtonReturn:
            subprocess.run(["pbcopy"], input=self.INSTALL_COMMAND.encode())
        elif answer == NSAlertSecondButtonReturn:
            subprocess.run(["open", self.BREW_URL])

    def ocr(self, widget):
        # Tesseract does the text. zbar is optional: without it barcodes are skipped.
        if shutil.which("tesseract") is None:
            missing = ["Tesseract"]
            if shutil.which("zbarimg") is None:
                missing.append("zbar")
            self._show_missing_tools_alert(missing)
            return
        if shutil.which("zbarimg") is None and not self.zbar_warned:
            self.zbar_warned = True
            self.notification_manager.new(
                "Barcode reading is off.",
                "zbar isn't installed. To enable it, run: brew install zbar").show()
        ret = os.system(self.BASH_PATH + " ocr")
        if ret == 0:
            self.notification_manager.new("OCR Completed.", "You can now press CTRL+V to paste text.").show()
        else:
            self.notification_manager.new("OCR Error.", "The clipboard seems empty, grab an image first.").show()

    def display(self,widget):
        ret = os.system(self.BASH_PATH + " display")
        if ret != 0:
            self.notification_manager.new("Clipboard Error.", "The clipboard seems empty, grab an image first.").show()

    def copy_to(self,filename):
        ret = os.system(self.BASH_PATH + " copyto \""+filename+"\"")
        if ret >> 8 == 2:
            self.notification_manager.new("Save Error.", "The file could not be saved, check permissions.").show()
        if ret >> 8 == 1:
            self.notification_manager.new("Clipboard Error.", "The clipboard seems empty, grab an image first.").show()

def main(version):
    #signal.signal(signal.SIGINT, signal.SIG_DFL)
    notification_manager = Notification()
    image_resolver = ImageResolver()
    image_changing_notifier = ImageChangingNotifier()

    clipboard_manager = ClipBoardManager(notification_manager, image_resolver, image_changing_notifier)
    screen_grabber = ScreenGrabber(notification_manager, image_resolver, image_changing_notifier)
    app = Snappo(version, screen_grabber, clipboard_manager, notification_manager, image_resolver, image_changing_notifier)
    app.run()


if __name__ == '__main__':
    version = ""
    with open(os.path.dirname(__file__)+'/VERSION', 'r') as f:
        version=f.read()
    f.close()
    main(version)
