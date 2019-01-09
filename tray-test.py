# from tendo import singleton
safe = True
try:

    # me = singleton.SingleInstance()
    # safe = True
    pass
except PermissionError:
    print('WallpaperHour is already running!')
if safe:
    from infi.systray import SysTrayIcon
    import WallpaperHour
    from WallpaperHour import oneRun
    import threading
    from redditbackground import like, dislike
    from win10toast import ToastNotifier
    import AddToStartup
    import os
    import sys
    import time

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
        AddToStartup.create_startup()
    except Exception as e:
        print('Could not add to startup:', e)
    try:
        def change(systray):
            print('Changing wallpaper on request')
            t1 = threading.Thread(target=oneRun)
            t1.start()
        def on_quit_callback(systray):
            sys.exit()
        def like_it(systray):
            t4 = threading.Thread(target=like)
            t4.start()
        def dislike_it(systray):
            t5 = threading.Thread(target=dislike)
            t5.start()
            time.sleep(5)
            t6 = threading.Thread(target=oneRun)
            t6.start()
        menu_options = (("Change Wallpaper", None, change), ("Like",None,like_it), ("Dislike",None,dislike_it),)
        systray = SysTrayIcon("icon.ico", "Wallpaper Hour", menu_options, on_quit=on_quit_callback)
        systray.start()
        WallpaperHour.main_loop()
    except RuntimeError:
        pass



