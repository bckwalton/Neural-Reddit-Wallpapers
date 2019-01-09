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
import ssl
import random
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

def like():
    fil = open(str(working_dir + 'record.txt'),'r')
    name = None
    path = None
    lines = fil.readlines()
    for line in lines:
        if 'Name: ' in line:
            name = line.split('Name: ')[1]
            print('Liked:',name)
        elif 'Path: ':
            path = line.split('Path: ')[1]
    fil.close()
    if '\Like\\' in path:
        toaster.show_toast("You already liked this","I guess you reeaallyy like it", icon_path=resource_path("icon.ico"), duration=5)
    else:
        os.rename(path,str('./' + working_dir + 'Like/'+(name[0:len(name)-1])))
        like_dis_store(name[0:len(name)-1])
        toaster.show_toast("Liked!","Awesome! I'll show you more pictures like this then :) ", icon_path=resource_path("icon.ico"), duration=5)

def dislike():
    fil = open(str(working_dir + 'record.txt'),'r')
    name = None
    path = None
    lines = fil.readlines()
    for line in lines:
        if 'Name: ' in line:
            name = line.split('Name: ')[1]
            print('Disliked:',name)
        elif 'Path: ':
            path = line.split('Path: ')[1]
    fil.close()
    if '\Dislike\\' in path:
        toaster.show_toast("You already disliked this","I'll get you something else...", icon_path=resource_path("icon.ico"), duration=2)
    else:
        os.rename(path,str('./' + working_dir + 'Dislike/'+(name[0:len(name)-1])))
        like_dis_store(name[0:len(name)-1])
        toaster.show_toast("Disliked","I'll get you something else, and not show you photos like this going foward", icon_path=resource_path("icon.ico"), duration=2)

def like_dis_store(name):
    path = find_files_path(working_dir,name)
    fil = open(str(working_dir + 'record.txt'),'w')
    print('Updating file')
    line = 'Name: ' + name
    line2 = 'Path: ' + path
    fil.write(line)
    fil.write('\n')
    fil.write(line2)
    fil.close()
    print('Successful update')

def setBackgroundFromSubreddit(subredditName, sort="top",timePeriod="week",requested=False):
    global resolution
    patience = 0
    if requested:
        toaster.show_toast("Changing Wallpaper","Requesting New Wallpaper please wait...", icon_path=resource_path("icon.ico"), duration=6)
    past_numbers = []
    while patience < 3:
        topImagePost, picked_number = getTopImageFromSubreddit(subredditName,sort,timePeriod,blocked_numbers=past_numbers)
        past_numbers.append(picked_number)
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
                    topImagePost, picked_number = getTopImageFromSubreddit(subredditName,sort,timePeriod,blocked_numbers=past_numbers)
                    past_numbers.append(picked_number)
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
            try:
                like_dis_store(imageFilename)
            except Exception:
                print('Failed to store record of current wallpaper')
            # like_dis()
            print("Title: " + topImagePost["title"])
            return topImagePost, result[0]

            


def getTopImageFromSubreddit(subredditName,sort,timePeriod,blocked_numbers=[]):
    topImagePosts = getTopImagePostsFromSubreddit(subredditName,sort,timePeriod)
    choices = list(set(list(range(len(topImagePosts)))) - set(blocked_numbers))
    print("Total available choices:",len(choices))
    val = random.choice(choices)
    print('Random choice: ', val)
    while True:
        try:
            topPost = topImagePosts[int(val)]["data"]
            break
        except Exception as e:
            print(e)
            time.sleep(10)
    return topPost, val


def getTopImagePostsFromSubreddit(subredditName,sort,timePeriod='week'):
    ban_sleep = 1
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    while True:
        val = randint(0,1) #Yeah it seems that Reddit throttles hitting the main page of a subreddit but not search... odd.
        # val = 1
        print('Front page coin flip:',val)
        if val == 1:
            if timePeriod:
                subredditPostsUrl = "https://www.reddit.com/r/" + subredditName + "/search.json?q=url:.jpg+OR+url:.png&sort="+str(sort)+"&restrict_sr=1&t="+str(timePeriod).lower()
            else:
                subredditPostsUrl = "https://www.reddit.com/r/" + subredditName + \
                    "/search.json?q=url:.jpg+OR+url:.png&sort="+str(sort)+"&restrict_sr=1"
        else:
            print('Front it is')
            if timePeriod:
                subredditPostsUrl = "https://www.reddit.com/r/" + subredditName + ".json?sort="+str(sort)+"&restrict_sr=1&t="+str(timePeriod).lower()
            else:
                subredditPostsUrl = "https://www.reddit.com/r/" + subredditName + ".json?sort="+str(sort)+"&restrict_sr=1"
        try:
            request = urllib.request.Request(subredditPostsUrl, headers={'User-Agent': user_agent})
            postsAsJsonRawText = urllib.request.urlopen(request).read()
            decodedJson = json.loads(postsAsJsonRawText.decode('utf-8'))
            break
        except (urllib.error.HTTPError, urllib.error.URLError, ssl.SSLEOFError, json.decoder.JSONDecodeError) as err:
            if '429' in str(err):
                ban_sleep += ban_sleep
                print('We have been politely asked to stop DDOSing. Complying.', str( ban_sleep/60 ) ,'minute wait enacted (',err,')')
                time.sleep(ban_sleep)
            else:
                print('Network issue detected, or invalid response. Sleeping 15 (',err,')')
                time.sleep(15)
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
