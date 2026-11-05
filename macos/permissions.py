"""The macOS Screen Recording permission (TCC), through CoreGraphics.

Without it, screencapture doesn't report an error the app can see: it produces
an image of just the wallpaper, or none at all. So it is checked before a grab.
"""
import ctypes
import subprocess

COREGRAPHICS = "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
SETTINGS_URL = "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"


def _call(name, default):
    # The functions don't exist before macOS 10.15, which has no such permission.
    try:
        function = getattr(ctypes.CDLL(COREGRAPHICS), name)
    except (OSError, AttributeError):
        return default
    function.restype = ctypes.c_bool
    return function()


def has_screen_recording_access():
    """Doesn't prompt. Stays False after granting until the app is reopened."""
    return _call("CGPreflightScreenCaptureAccess", True)


def request_screen_recording_access():
    """Adds the app to the list in System Settings, prompting the first time."""
    return _call("CGRequestScreenCaptureAccess", True)


def open_screen_recording_settings():
    subprocess.run(["open", SETTINGS_URL])
