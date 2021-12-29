#!/usr/bin/env python3
import os
import subprocess
import threading
import time

import rumps
import Cocoa

import objc
from AppKit import *
from Foundation import *
from ui_abstract import *


class ImageResolver(ImageResolverAbstract):
    path="macos/images"
    STOCK_MISSING_IMAGE = "noimg_red.png"
    STOCK_PRINT_PREVIEW = "lens.png"
    STOCK_COPY = "copy.png"
    STOCK_CLEAR = "clear.png"

    def __init__(self):
        pass

    def resolve(self,image):
        path = self.path+"/"+image
        return path

    def get_noimg_icon(self):
        return self.resolve(self.STOCK_MISSING_IMAGE)

    def get_lens_icon(self):
        return self.resolve(self.STOCK_PRINT_PREVIEW)

    def get_copy_icon(self):
        return self.resolve(self.STOCK_COPY)

    def get_clear_icon(self):
        return self.resolve(self.STOCK_CLEAR)


class Notification(NotificationAbstract):
    def __init__(self):
        super().__init__()

    def new(self, summary='', body=''):
        self.summary = summary
        self.body = body
        return self

    def show(self):
        rumps.notification(self.app, self.summary, self.body, data=None, sound=True)


class Alert(object):
    def __init__(self, message="Default Message", info_text="", buttons=["OK"]):
        super(Alert, self).__init__()
        self.messageText = message
        self.informativeText = info_text
        self.buttons = buttons
        self.buttonPressed = None

    def show(self):
        alert = NSAlert.alloc().init()
        rect = NSMakeRect(0, 0, 400, 0)
        nsview = NSView.alloc().initWithFrame_(rect)
        alert.setAccessoryView_(nsview)
        alert.setMessageText_(self.messageText)
        alert.setInformativeText_(self.informativeText)
        alert.setAlertStyle_(NSInformationalAlertStyle)
        for button in self.buttons:
            alert.addButtonWithTitle_(button)
        self.buttonPressed = alert.runModal()
        return self.buttonPressed


class Snappo(SnappoAbstract):
    def __init__(self, screen_grabber, clipboard_manager, notification_manager, image_resolver, image_changing_notifier):
        self.BASH_FILE = "macos/snappo.sh"
        super().__init__(screen_grabber, clipboard_manager, notification_manager, image_resolver, image_changing_notifier)

        self.delay = 0
        self.items=[]

        abspath = os.path.abspath(__file__)
        self.dirname = os.path.dirname(abspath)

        self.app = rumps.App(self.APP_INDICATOR)
        self.app.title = "📷"
        self._build_menu()

    def _add_menu_item(self, label, callback):
        return self._add_menu_item_with_icon(label, None, callback)

    def _add_direct_menu_item(self, menu_item):
        self.items.append(menu_item)
        return menu_item

    def _add_menu_item_with_icon(self, label, icon_id, callback):
        menu_item = rumps.MenuItem(title=label, callback=callback, icon=icon_id)
        self.items.append(menu_item)
        return menu_item

    def _build_menu(self):
        self.grab_desktop_menuitem = self._add_menu_item(label="Grab Desktop..", callback=self._grab_desktop)
        self.monitors = self.get_monitors()
        _entries = []
        if(len(self.monitors))>1:
          for i in range(0, len(self.monitors)):
              self._add_menu_item(label="  "+str(i+1)+"  "+self.monitors[i], callback=self._grab_desktop)
        self.grab_window_menu_item = self._add_menu_item(label="Grab Window..", callback=self._grab_window)
        self.grab_area_menu_item = self._add_menu_item(label="Grab Area..", callback=self._grab_area)
        self._add_direct_menu_item(rumps.separator)
        self.delay_label_menu_item = self._add_menu_item(label="Set Delay..", callback=self.show_delay_dialog)
        self.delay_menu_item = self._add_direct_menu_item(rumps.SliderMenuItem(value=0, dimensions=(180,25), callback=self._set_delay))
        self._add_direct_menu_item(rumps.separator)
        self.clipboard_menu_item = self._add_menu_item_with_icon(label="Clibpoard..", callback=self.show_thumb, icon_id=ImageResolver().get_noimg_icon())
        self.image_changing_notifier.set_image_changing_notifier(self.clipboard_menu_item)
        self.copy_menu_item = self._add_menu_item_with_icon(label="Copy..", callback=self.clipboard_manager.copy, icon_id=ImageResolver().get_copy_icon())
        self.clear_menu_item = self._add_menu_item_with_icon(label="Clear..", callback=self.clipboard_manager.clear, icon_id=ImageResolver().get_clear_icon())
        self._add_direct_menu_item(rumps.separator)
        self.ocr_menu_item = self._add_menu_item(label="OCR", callback=self.screen_grabber.ocr)
        self._add_direct_menu_item(rumps.separator)
        self.about_menu_item = self._add_menu_item(label="About..", callback=self.show_about_dialog)
        self.app.menu = self.items

    def _set_delay(self, widget):
        self.delay = int(widget.value)

        label = "Set Delay.."
        if self.delay>0:
            label = label+"("+str(self.delay)+"s)"
        self.delay_label_menu_item.title = label

    def quit(self, widget):
        pass

    def _update_clipboard_icon(self, delay):
        time.sleep(delay)
        self.clipboard_menu_item.set_icon(ImageResolver().get_lens_icon())

    def _grab(self, what, delay=0, which_desktop=""):
        self.screen_grabber.grab(what, delay, which_desktop)
        x = threading.Thread(target=self._update_clipboard_icon, args=(delay,))
        x.start()

    def _grab_desktop(self, sender):
        which_desktop=sender.title.strip().split()[0]
        if which_desktop != 'Grab' or len(self.monitors) ==1 :
            self._grab("desktop", self.delay, "1" if which_desktop == 'Grab' else which_desktop)
        else:
          Cocoa.NSBeep()

    def _grab_window(self, sender):
        self._grab("window", self.delay)

    def _grab_area(self, sender):
        self._grab("area", self.delay)

    def show_thumb(self, sender):
        self.screen_grabber.display()

    def show_about_dialog(self, widget):
        press = Alert("Snappo", "A Screenshot tool with Barcode/OCR capabilites\n\n© 2021 by Luca Viola\n\nSnappo on github: https://github.com/luca-viola/snappo\nLicense: GPL V3 - http://www.gnu.org/licenses/").show()

    def show_delay_dialog(self, widget):
        Cocoa.NSBeep()

    def get_monitors(self):
        result = subprocess.run(['system_profiler SPDisplaysDataType | grep -i resolution | awk \'{print $2 "x" $4}\''],
                                shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip().split('\n')
        return result

    def run(self):
        self.app.run()
