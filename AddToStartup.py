import os, sys
import winshell

def create_startup():
    startup = winshell.startup() # use common=1 for all users
    print(startup)
    winshell.CreateShortcut(
    Path=os.path.join (os.getcwd(), "WallpaperHour.exe"),
    Target=sys.executable,
    Icon=(sys.executable, 0),
    Description="Wallpaper Hour"
    )

    winshell.CreateShortcut(
    Path=os.path.join (winshell.startup(), "WallpaperHour.lnk"),
    Target=sys.executable,
    Icon=(sys.executable, 0),
    Description="Wallpaper Hour"
    )
if __name__ == "__main__":
    create_startup()