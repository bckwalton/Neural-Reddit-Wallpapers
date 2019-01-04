import time
from timeit import default_timer as timer
import redditbackground
import click

def oneRun():

    redditbackground.setBackgroundFromSubreddit('wallpapers',sort='hot',timePeriod='day',requested=True)

def main():
    while True:
        print("Getting Wallpaper...")
        start = timer()
        topImage, decision = redditbackground.setBackgroundFromSubreddit('wallpapers',sort='hot',timePeriod='day')
        end = timer()
        print("Set!")
        print("It took about:", int(end - start),
              "seconds to get and set the wallpaper.")
        print("Waiting 1 hour.")
        if decision is 'Like':
            time.sleep((60) * 60)

# from tendo import singleton
# me = singleton.SingleInstance()
def main_loop():
    while True:
        try:
            main()
        except Exception:
            time.sleep(30)
            main()
    # print("Title: " + image["title"])

if __name__ == "__main__":
    main_loop()

