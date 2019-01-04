import ctypes
import json
import os
import string
import time
import urllib.request
from WallReadML import predict_LD
from random import randint
import subprocess
import imghdr
import scipy
import tensorflow
import keras
# from scipy.interpolate.interpnd import array

try:
    from PIL import Image
except ImportError:
    print("DEV: Don't mind me I'm just getting PIL (Pillow) for you.")
    time.sleep(3)
    os.system('python -m pip install Pillow')
    print('DEV:','Enjoy your pillow!')
    from PIL import Image

try:
    from win10toast import ToastNotifier
except ImportError:
    print("DEV: Don't mind me I'm just getting win10toast (Toast Notification system) for you.")
    time.sleep(3)
    os.system('python -m pip install pypiwin32')
    os.system('python -m pip install setuptools')
    os.system('python -m pip install win10toast')
    print('DEV:','Enjoy your win10toast!')
    from win10toast import ToastNotifier


toaster = ToastNotifier()

resolution = None
working_dir = 'wallHour/'
def res(filename):
    global resolution
    im = Image.open(filename)
    resolution = im.size
    # print('Resolution: [%d x %d]' % im.size)  # returns (width, height) tuple
    return(im.size)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def setBackgroundFromSubreddit(subredditName, sort="top",timePeriod="week",requested=False):
    global resolution
    patience = 0
    if requested:
        toaster.show_toast("Changing Wallpaper","Requesting New Wallpaper please wait...", icon_path=resource_path("icon.ico"), duration=6)
    while patience < 3:
        topImagePost = getTopImageFromSubreddit(subredditName,sort,timePeriod)
        imageFilename, imageFilepath = storeImageInStoredBackgroundsFolder(topImagePost)
        if os.path.isfile(imageFilepath):
            resolution = res(imageFilepath)
            print('Resolution: [%d x %d]' % resolution)
            path = working_dir + imageFilename
            path = imageFilepath
            result = predict_LD(path,working_dir=working_dir)
            if result is not 'Like':
                while result[0] is not 'Like':
                    print(str(imageFilename),':',result[0], ' Certainty:', result[1])
                    topImagePost = getTopImageFromSubreddit(subredditName,sort,timePeriod)
                    imageFilename, imageFilepath = storeImageInStoredBackgroundsFolder(topImagePost)
                    resolution = res(imageFilepath)
                    print('Resolution: [%d x %d]' % resolution)
                    path = imageFilepath
                    result = predict_LD(path, working_dir=working_dir)
                    print(str(imageFilename),':',result[0], ' Certainty:', result[1])
            try:
                toaster.show_toast("New Wallpaper! By: "+str(topImagePost["author"]),"Title: "+str(topImagePost["title"])+"\nResolution: "+str(resolution)+"\nScore:"+str(topImagePost['score']), icon_path=resource_path("icon.ico"), duration=5)
            except Exception:
                print("Failed to show toast, that would've been cool... ")
            setImageAsBackground(imageFilename, imageFilepath=imageFilepath)
            print("Title: " + topImagePost["title"])
            return topImagePost, result[0]


def getTopImageFromSubreddit(subredditName,sort,timePeriod):
    topImagePosts = getTopImagePostsFromSubreddit(subredditName,sort,timePeriod)
    val = randint(0, 9)
    print('Random value: ', val)
    while True:
        try:
            topPost = topImagePosts[int(val)]["data"]
            break
        except Exception:
            time.sleep(10)
    return topPost


def getTopImagePostsFromSubreddit(subredditName,sort,timePeriod=None):
    if timePeriod:
        subredditPostsUrl = "https://www.reddit.com/r/" + subredditName + \
            "/search.json?q=url:.jpg+OR+url:.png&sort="+str(sort)+"&restrict_sr=1&t=week"
    else:
        subredditPostsUrl = "https://www.reddit.com/r/" + subredditName + \
            "/search.json?q=url:.jpg+OR+url:.png&sort="+str(sort)+"&restrict_sr=1"
    while True:
        try:
            postsAsJsonRawText = urllib.request.urlopen(
                subredditPostsUrl).read()
            break
        except urllib.error.HTTPError as err:
            time.sleep(5)
    decodedJson = json.loads(postsAsJsonRawText.decode('utf-8'))
    posts = decodedJson["data"]["children"]
    return posts

def files(root):  
    for path, subdirs, files in os.walk(root):
        for name in files:
            yield os.path.join(path, name)

def files_name(root):  
    for path, subdirs, files in os.walk(root):
        for name in files:
            yield name

def find_files_path(root, filename):
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name == filename:
                path = os.path.dirname(os.path.realpath( (path + "//" + name) )) + "\\" + filename
                return path
def storeImageInStoredBackgroundsFolder(image):
    createStoredBackgroundsFolderIfNotExists()
    imageTitle = str(image['title'].translate(string.punctuation).strip().replace(" ", "_")).replace(".",'-')
    imageFilename = "bg_" + str(imageTitle) + ".png"
    if not imageFilename in files_name(working_dir):
        open(working_dir + imageFilename, "wb").write(urllib.request.urlopen(image["url"]).read())
        print('Files True Type:', imghdr.what(working_dir + imageFilename))
    imageFilepath = find_files_path(working_dir, imageFilename)
    print("Name:",imageFilename,"Path:",imageFilepath)
    return imageFilename, imageFilepath


def createStoredBackgroundsFolderIfNotExists():
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)


def setImageAsBackground(imageFilename,imageFilepath):
    try:
        try:
            print("Name:",imageFilename)
            print("Path:",imageFilepath,"EOP")
            # print(getFullPathOfImage(imageFilename),' VS ',imageFilepath)

            ctypes.windll.user32.SystemParametersInfoW(
                20, 0, imageFilepath, 0)
        except Exception:
            script_tail = '''gsettings set org.gnome.desktop.background picture-uri file:///'''
            script_tail = "file:///"+imageFilepath
            subprocess.check_output(['gsettings','set','org.gnome.desktop.background','picture-uri',script_tail])
    except Exception:
        print('DEV: Hmm... I was unable to set the wallpaper! This is a Windows or Gnome based linux system right? Odd.')
        time.sleep(10)
        print('DEV: I think...')
        time.sleep(3)
        print("DEV: I think I should kill myself... I'm a process though so this shouldn't hurt much.")
        time.sleep(2)
        print('DEV: Probably...')
        time.sleep(2)
        print("DEV: OK. ok. I'm going to do it. Tell my DEV to fix this crap! :'( ")
        time.sleep(3)
        exit()



def getFullPathOfImage(imageFilename):
    global resolution
    path = os.path.dirname(
        os.path.realpath(
            working_dir + imageFilename)) + "\\" + imageFilename
    print(path)
    resolution = res(path)
    return os.path.dirname(
        os.path.realpath(
            working_dir + imageFilename)) + "\\" + imageFilename
