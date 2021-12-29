from abc import ABCMeta, abstractmethod
import os

APP_INDICATOR = "Snappo"


class ImageResolverAbstract(metaclass=ABCMeta):
    @abstractmethod
    def get_noimg_icon(self):
        pass

    @abstractmethod
    def get_lens_icon(self):
        pass

    @abstractmethod
    def get_clear_icon(self):
        pass


class NotificationAbstract(metaclass=ABCMeta):
    summary = None
    body = None

    def __init__(self):
        self.app=APP_INDICATOR

    @abstractmethod
    def new(self, summary='', body=''):
        pass

    @abstractmethod
    def show(self):
        pass


class SnappoAbstract(metaclass=ABCMeta):
    BASH_FILE = "snappo.sh"

    delay = 0
    menu = None
    clipboard_manager = None
    screen_grabber = None

    def __init__(self, screen_grabber, clipboard_manager, notification_manager, image_resolver, image_changing_notifier):
        self.APP_INDICATOR = APP_INDICATOR
        self.clipboard_manager = clipboard_manager
        self.screen_grabber = screen_grabber
        self.notification_manager = notification_manager
        self.image_resolver = image_resolver
        self.image_changing_notifier = image_changing_notifier
        self.BASH_PATH = os.path.dirname(os.path.abspath(__file__)) + "/" + self.BASH_FILE

    @abstractmethod
    def _add_menu_item(self, label, callback):
        pass

    @abstractmethod
    def _add_menu_item_with_icon(self, label, icon_id, callback):
        pass

    @abstractmethod
    def _build_menu(self):
        pass

    @abstractmethod
    def show_thumb(self, widget):
        pass

    @abstractmethod
    def _set_delay(self, widget):
        pass

    @abstractmethod
    def show_about_dialog(self, widget):
        pass

    @abstractmethod
    def show_delay_dialog(self, widget):
        pass

    @abstractmethod
    def _grab_desktop(self, widget):
        pass

    @abstractmethod
    def _grab_window(self, widget):
        pass

    @abstractmethod
    def _grab_area(self, widget):
        pass

    @abstractmethod
    def quit(self, widget):
        pass
