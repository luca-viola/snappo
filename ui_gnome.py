#!/bin/env python3
import os
import shutil
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
import warnings

from ui_abstract import *


class ImageResolver(ImageResolverAbstract):
    def __init__(self):
        pass

    def resolve(self,image):
        thumb = gtk.Image.new_from_icon_name(image, gi.repository.Gtk.IconSize.DIALOG)
        return thumb

    def get_noimg_icon(self):
        return self.resolve(gi.repository.Gtk.STOCK_MISSING_IMAGE)

    def get_lens_icon(self):
        return self.resolve(gi.repository.Gtk.STOCK_PRINT_PREVIEW)

    def get_clear_icon(self):
        return self.resolve(gi.repository.Gtk.STOCK_CLEAR)

    def get_convert_icon(self):
        return self.resolve(gi.repository.Gtk.STOCK_CONVERT)


class Notification(NotificationAbstract):
    def __init__(self):
        super().__init__()
        notify.init(self.app)

    def new(self, summary='', body=''):
        self.summary = summary
        self.body = body
        return self

    def show(self):
        notify.Notification.new(self.summary, self.body).show()


class Snappo(SnappoAbstract):

    def __init__(self, version, screen_grabber, clipboard_manager, notification_manager, image_resolver, image_changing_notifier):
        self.BASH_FILE = "linux/snappo.sh"
        super().__init__(version, screen_grabber, clipboard_manager, notification_manager, image_resolver, image_changing_notifier)

        self.indicator = appindicator.Indicator.new(self.APP_INDICATOR, self.script_dir+'/camera.svg',
                                               appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.menu = gtk.Menu()
        self.indicator.set_menu(self.menu)
        self._build_menu()
        self.menu.show_all()
        gtk.main()

    def run(self):
        pass

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
        self.monitors = self.get_monitors()
        _entries = []
        if(len(self.monitors))>1:
            for i in range(0, len(self.monitors)):
                self._add_menu_item(label="  "+str(i+1)+"  "+self.monitors[i], callback=self._grab_desktop)

        self._add_menu_item('Grab Window..', self._grab_window)
        self._add_menu_item('Grab Area..', self._grab_area)
        self.menu.append(gtk.SeparatorMenuItem())
        self.delay_widget=self._add_menu_item('Set delay..', self.show_delay_dialog)
        self.menu.append(gtk.SeparatorMenuItem())
        clipboard_item = self._add_menu_item_with_icon('Clipboard', gi.repository.Gtk.STOCK_MISSING_IMAGE, self.screen_grabber.display)
        self.image_changing_notifier.set_image_changing_notifier(clipboard_item)
        self._add_menu_item_with_icon('Copy', gi.repository.Gtk.STOCK_COPY, self.clipboard_manager.copy)
        self._add_menu_item_with_icon('Save as..', gi.repository.Gtk.STOCK_SAVE, self.save_as)
        self._add_menu_item_with_icon('Clear', gi.repository.Gtk.STOCK_CLEAR, self.clipboard_manager.clear)
        self.menu.append(gtk.SeparatorMenuItem())
        self._add_menu_item('OCR', self.screen_grabber.ocr)
        self.menu.append(gtk.SeparatorMenuItem())
        self._add_menu_item('About..', self.show_about_dialog)
        self._add_menu_item('Quit', self.quit)


    def _set_delay(self, widget):
        self.delay = widget.get_value()
        label="Set Delay..."
        if self.delay>0:
          label=label+" ("+str(int(self.delay))+"s)"
        self.delay_widget.set_label(label)

    def show_about_dialog(self, widget):

        about = gtk.AboutDialog()
        about.set_title("About..")
        about.set_name("SNapshot APPlicatiOn")
        about.set_program_name("Snappo")
        about.set_version("Ver: "+self.version)
        about.set_authors(["Luca Viola"])
        about.set_copyright("© 2022 by Luca Viola")
        about.set_comments("A Screen Snapshot tool with OCR\nand Barcode recognition capabilities")
        about.set_website("https://github.com/luca-viola/snappo")
        about.set_website_label("Snappo on Github")
        about.set_logo(gi.repository.GdkPixbuf.Pixbuf.new_from_file_at_size(self.script_dir+"/camera.svg", 64, 64))
        print(self.script_dir+"/camera.svg")
        about.set_license_type(gtk.License.GPL_3_0)
        about.set_wrap_license(True)
        about.set_license("""
Snappo

Copyright (C) 2022 Luca Viola

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
        """)
        about.run()
        about.destroy()

    def show_delay_dialog(self, widget):
        msg = "Set screenshot delay in seconds:"
        title = "Set Delay"
        dialog = gtk.MessageDialog( None, gtk.DialogFlags.MODAL, gtk.MessageType.QUESTION, gtk.ButtonsType.OK,  msg)
        dialog.set_title(title)
        box = dialog.get_message_area()
        scale = gtk.Scale().new(gtk.Orientation.HORIZONTAL)
        scale.set_range(0, 100)
        scale.set_digits(0)
        scale.set_value(self.delay)
        scale.connect("value-changed", self._set_delay)
        scale.set_size_request(128, 24)
        box.pack_end(scale, False, False, 0)
        box.show_all()
        dialog.show()
        dialog.run()
        dialog.destroy()

    def _grab_desktop(self, widget):
        which_desktop=widget.get_label().strip().split()[1]
        if which_desktop[0]=='*':
            which_desktop=which_desktop[1:]
        self.screen_grabber.grab("desktop", self.delay, " " if which_desktop == 'Desktop..' else which_desktop)

    def _grab_window(self, widget): self.screen_grabber.grab('window', int(self.delay))
    def _grab_area(self, widget): self.screen_grabber.grab('area', int(self.delay))

    def get_monitors(self):
        result = subprocess.run(['xrandr | grep -i " connected" | awk \'{ print $3 $4}\''],
                                shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip().split('\n')
        for i in range(len(result)):
            result[i] = result[i].replace("right", "")
            result[i] = result[i].replace("left", "")
            result[i] = result[i].replace("(normal", "")
            result[i] = result[i].replace("primary", "*")
        return result

    def save_as(self, widget):
        action=gtk.FileChooserAction.SAVE
        chooser = gtk.FileChooserDialog(title="Save Clipboard as..",
                                        action=gtk.FileChooserAction.SAVE,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.ResponseType.CANCEL,
                                                 gtk.STOCK_SAVE,
                                                 gtk.ResponseType.OK))
        chooser.set_default_response(gtk.ResponseType.OK)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        overwrite = 0
        if chooser.run() == gtk.ResponseType.OK:
            filename = chooser.get_filename()
            if os.path.exists(filename):
                md = gtk.MessageDialog(chooser,
                                       gtk.DialogFlags.DESTROY_WITH_PARENT, gtk.MessageType.QUESTION,
                                       gtk.ButtonsType.YES_NO, "This file exists. Are you sure?")
                overwrite=md.run()
                md.destroy()
                if overwrite == gtk.ResponseType.NO:
                    return
        self.save_file(filename)
        chooser.destroy()

    def save_file(self, filename):
        self.screen_grabber.copy_to(filename)
        pass

    def quit(self, widget):
            os.system(self.BASH_PATH+" clear")
            notify.uninit()
            gtk.main_quit()
