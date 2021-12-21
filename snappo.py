#/bin/env python3
import os
import signal

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
import warnings
#warnings.filterwarnings("default")
warnings.filterwarnings("ignore")

APPINDICATOR_ID = 'Snappo'
BASH_FILE = "snappo.sh"
BASH_PATH = os.path.abspath(BASH_FILE)

class ClipBoardManager:
    clipboard = None

    def __init__(self):
        self.image_display = None
        self.clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)

    def copy(self, widget):
        os.system(BASH_PATH+" copy")

    def clear(self, widget):
        self.clipboard.clear()
        self.clipboard.set_text("", -1)
        os.system(BASH_PATH+" clear")
        thumb = gtk.Image.new_from_icon_name(gi.repository.Gtk.STOCK_MISSING_IMAGE, gi.repository.Gtk.IconSize.DIALOG)
        self.image_display.set_image(thumb)

    def copy_image(self):
        img_data = self.clipboard.wait_for_image()
        if img_data is not None:
            thumb = gtk.Image()
            thumb.set_from_pixbuf(img_data)
            return thumb

    def set_image_display(self, clipboard_item):
        self.image_display = clipboard_item


class ScreenGrabber:
    image_display = None
    clipboard_manager = None

    def __init__(self,cliboard_manager):
        self.clipboard_manager = cliboard_manager
        notify.init(APPINDICATOR_ID)

    def grab(self, what):
        if what in ['area', 'desktop', 'window']:
            os.system(BASH_PATH + " " + what)
            thumb = clipboard_manager.copy_image()
            self.image_display.set_image(thumb)

    def ocr(self, widget):
        ret = os.system(BASH_PATH + " ocr")
        if ret == 0:
          notify.Notification.new("OCR Completed.", "You can now press CTRL+V to paste text.").show()
        else:
          notify.Notification.new("OCR Error.", "The clipboard seems empty, grab an image first.").show()

    def set_image_display(self, clipboard_item):
        self.image_display = clipboard_item


class Snappo:
    screen_grabber = None
    clipboard_manager = None
    menu = None

    def __init__(self, screen_grabber, clipboard_manager):
        self.screen_grabber = screen_grabber
        self.clipboard_manager = clipboard_manager

        indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('camera.svg'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.menu = gtk.Menu()
        indicator.set_menu(self.menu)
        notify.init(APPINDICATOR_ID)
        self._build_menu()
        self.menu.show_all()
        gtk.main()

    def _add_menu_item(self, label, callback):
        menu_item = gtk.MenuItem.new_with_label(label)
        menu_item.connect('activate', callback)
        self.menu.append(menu_item)
        return menu_item

    def _add_menu_item_with_icon(self, label, icon_id, callback):
        menu_item = gtk.ImageMenuItem()
        menu_item.set_label(label)
        thumb = gtk.Image.new_from_icon_name(icon_id, gi.repository.Gtk.IconSize.DIALOG)
        menu_item.set_always_show_image(True)
        menu_item.set_image(thumb)
        menu_item.connect('activate', callback)
        self.menu.append(menu_item)
        return menu_item

    def _build_menu(self):
        self._add_menu_item('Grab Desktop..', self._grab_desktop)
        self._add_menu_item('Grab Window..', self._grab_window)
        self._add_menu_item('Grab Area..', self._grab_area)
        self.menu.append(gtk.SeparatorMenuItem())
        clipboard_item = self._add_menu_item_with_icon('Clipboard', gi.repository.Gtk.STOCK_MISSING_IMAGE, self.show_thumb)
        self.screen_grabber.set_image_display(clipboard_item)
        self.clipboard_manager.set_image_display(clipboard_item)
        self._add_menu_item_with_icon('Copy', gi.repository.Gtk.STOCK_COPY, self.clipboard_manager.copy)
        self._add_menu_item_with_icon('Clear', gi.repository.Gtk.STOCK_CLEAR, self.clipboard_manager.clear)
        self.menu.append(gtk.SeparatorMenuItem())
        self._add_menu_item('OCR', self.screen_grabber.ocr)
        self.menu.append(gtk.SeparatorMenuItem())
        self._add_menu_item('Quit', self.quit)

    def show_thumb(self, widget):
        os.system(BASH_PATH + " display")

    def _grab_desktop(self, widget): self.screen_grabber.grab('desktop')
    def _grab_window(self, widget): self.screen_grabber.grab('window')
    def _grab_area(self, widget): self.screen_grabber.grab('area')

    def quit(self, widget):
        notify.uninit()
        gtk.main_quit()


clipboard_manager = ClipBoardManager()
screen_grabber = ScreenGrabber(clipboard_manager)
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main = Snappo(screen_grabber, clipboard_manager)
