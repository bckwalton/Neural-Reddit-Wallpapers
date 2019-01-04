# Neural-Reddit-Wallpapers
Wallpapers from Reddit, with your own personal Neural Network curator. Powered by a tensorflow CNN (Keras).

Simple Start (.exe start):
In order to get started, the best way (if you just want to run it in its default mode) is to head into 'dist/latest' and download the whole folder. Unzip that folder (if needed) and then unzip the WallpaperHour.zip (make sure to make sure the z0 files are next to the .zip so the file extracts properly. Then run WallpaperHour.exe, It will run in the background if you just run the WallpaperHour.exe directly; or if you want to see what its up to and do some minor debugging open command prompt from that folder and run ./WallpaperHour.exe.

Coders Start:
Alright, in order to run it with the tray icon attached run tray-test.py (better name pending), Or run WallpaperHour if you don't want any frills. The ML model lives in WallReadML (The model is mainly based on the test CNN from Keras documentation with a few more layers and tweaks I'll modify it more to be more tailored for the task at hand). tray-test.py (better name is seriously coming) acts as the main app and tray launcher. redditbackground.py is the main function base for getting and setting wallpapers.

Training:
Once you launch the app in one of the ways above (whichever one, doesn't matter) there will be a new folder thats created in the folder where the application was run named 'wallHour'. The root of that directory will have all unclassified backgrounds. To train the model make sure you have at least 2 examples in 'wallHour/Dislike' and 'wallHour/Like'. The best way to do that is to wait for app to run enough times (if your running with the tray icon you can also just select 'change wallpaper' enough times). You can also just fill the folders with wallpapers you like from other sources. Whichever way you choose to meet the quota once you've met it the next time it tries to get a new wallpaper it will generate 2 .wal files. Those are the saved weights for the model, this is done so that the model doesn't have to be retrained every run, it will only be retrained if more files are added to Like or Dislike.

Profit
