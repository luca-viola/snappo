#!/usr/bin/env python3
import signal
import platform

import rumps

from ui_abstract import *

whatos = platform.system()
if whatos == 'Darwin':
    from ui_macos import Snappo, ImageResolver, Notification
    #rumps.debug_mode(True)
    BASH_FILE="macos/snappo.sh"
else:
    from ui_gnome import Snappo, ImageResolver, Notification
    BASH_FILE="linux/snappo.sh"

BASH_PATH = os.path.dirname(os.path.abspath(__file__)) + "/" + BASH_FILE


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
    def __init__(self, notification_manager, image_resolver, image_changing_notifier):
        self.notification_manager = notification_manager
        self.image_resolver = image_resolver
        self.image_changing_notifier = image_changing_notifier
        self.BASH_PATH = BASH_PATH

    def grab(self, what, delay=0, which_desktop=""):
        if what in ['area', 'desktop', 'window']:
            os.system(self.BASH_PATH + " " + what + " " + str(delay) + " " + which_desktop)
            thumb = self.image_resolver.get_lens_icon()
            self.image_changing_notifier.set_icon(thumb)

    def ocr(self, widget):
        ret = os.system(self.BASH_PATH + " ocr")
        if ret == 0:
            self.notification_manager.new("OCR Completed.", "You can now press CTRL+V to paste text.").show()
        else:
            self.notification_manager.new("OCR Error.", "The clipboard seems empty, grab an image first.").show()

    def display(self):
        ret = os.system(self.BASH_PATH + " display")
        if ret != 0:
            self.notification_manager.new("Clipboard Error.", "The clipboard seems empty, grab an image first.").show()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    notification_manager = Notification()
    image_resolver = ImageResolver()
    image_changing_notifier = ImageChangingNotifier()

    clipboard_manager = ClipBoardManager(notification_manager, image_resolver, image_changing_notifier)
    screen_grabber = ScreenGrabber(notification_manager, image_resolver, image_changing_notifier)
    app = Snappo(screen_grabber, clipboard_manager, notification_manager, image_resolver, image_changing_notifier)
    app.run()


if __name__ == '__main__':
    main()
