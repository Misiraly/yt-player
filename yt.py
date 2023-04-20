import curses

import pafy
import vlc
import time
# import threading

# from random import randint

import lib_sorter as lib
from modules import formatter

music_lib = r"C:\Users\mihaly.kotiers\Desktop\trhow\yt-player\music_lib.txt"
EXIT_CHARS = {"q", "exit"}

"""
Title: Eddy Grant - Gimme Hope Jo Anna  1988
Author: OLD TAPES
ID: R-ZplG81oZg
Duration: 00:04:13
Rating: None
Views: 9150147
Thumbnail: http://i.ytimg.com/vi/R-ZplG81oZg/default.jpg
"""


def get_seconds(formatted_input: str = 0):
    if formatted_input == 0:
        print("[INFO] This has no length.")
        return 0
    _temp = formatted_input.split(":")
    return int(_temp[0])*3600 + int(_temp[1])*60 + int(_temp[2])

    
def thread_end_video(media, seconds: int = 0):
    time.sleep(seconds)
    media.stop()
    return "q"

def player(scr):
    curses.resize_term(10, 60)
    title_list = formatter.line_breaker(str(video.title), 58)
    for i, line in enumerate(title_list):
        scr.addstr(i + 1, 1, line)
    scr.addstr(6, 15, "        " + video.duration)
    scr.addstr(7, 15, "          (►)             ")
    scr.addstr(9, 15, "[||] - p  [►] - l  [■] - q   Replay - r")
    key = ""
    seconds = get_seconds(video.duration)
    print("video in seconds: " + str(seconds))
    print("video time: " + str(video.duration))
    # x = threading.Thread(target=thread_end_video, args=(seconds,media,), daemon=True)
    # x.start()
    while key != ord("q"):
        key = scr.getch()
        print(key)
        if key == ord("p"):
            media.pause()
            scr.addstr(7, 15, "          (||)            ")
        elif key == ord("s"):
            media.stop()
            scr.addstr(7, 15, "          (■)             ")
        elif key == ord("l"):
            media.play()
            scr.addstr(7, 15, "          (►)             ")
        elif key in {ord("r"), ord("R")}:
            media.stop()
            media.play()
            scr.addstr(7, 15, "          (►)             ")
    scr.erase()
    scr.refresh()
    media.stop()


def exit_check(cmd_input):
    if cmd_input.lower() in EXIT_CHARS:
        exit()
    return cmd_input


def check_if_num(cmd_input, tab):
    cont = False
    if cmd_input.isnumeric():
        cmd_num = int(cmd_input)
        if cmd_num not in range(len(tab)):
            cont = True
            print("Try again retard, number not on list")
            return "", cont
        else:
            return tab[cmd_num][1], cont
    elif cmd_input.lower() == "random":
        print("\n[RETARD WARNING] I disabled it, retard.\n")
        return "", True
        # return tab[randint(0,len(tab))][1], cont
    elif "https" not in cmd_input:
        print("url not good, you got a free song!")
        return "https://www.youtube.com/watch?v=R-ZplG81oZg", cont
    return cmd_input, cont


def start_input():
    cont = True
    tab = lib.pull_songs()
    prompt = "[>] URL or song Number /quit - 'q'/ [>]: "
    while cont:
        cmd_input = exit_check(input(prompt))
        url, cont = check_if_num(cmd_input, tab)
    return url


if __name__ == "__main__":
    print("\n")
    formatter.abc_rower("PYTHON MUSIC")
    print("\n")
    while True:
        url = start_input()
        print("\n" + url + "\n")
        video = pafy.new(url)
        best = video.getbestaudio()
        media = vlc.MediaPlayer(best.url)
        media.play()
        curses.wrapper(player)
        lib.inwriter(video.title, url, video.duration)
        print("\n***(bideo emth...! щ(`Д´щ;) )***")
        print("-"*80+"\n")
