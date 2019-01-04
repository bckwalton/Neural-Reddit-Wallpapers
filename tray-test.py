from infi.systray import SysTrayIcon
import WallpaperHour
from WallpaperHour import oneRun
import threading
from win10toast import ToastNotifier
import os
systray=None
t2 = None
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        import sys
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
try:
    def change(systray):
        print('Changing wallpaper on request')
        t1 = threading.Thread(target=oneRun)
        t1.start()
    def on_quit_callback(systray):
        exit()
    menu_options = (("Change Wallpaper", None, change),)
    systray = SysTrayIcon("icon.ico", "Wallpaper Hour", menu_options, on_quit=on_quit_callback)
    systray.start()
    WallpaperHour.main_loop()
except RuntimeError:
    pass



