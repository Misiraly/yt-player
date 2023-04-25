import msvcrt
import time
from multiprocessing import Process, Value

import vlc
from yt_dlp import YoutubeDL

import lib_sorter as lib_s
from modules import formatter

# from random import randint


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

STATUS_ICON = {
    "p": "(||)",
    "s": "(■) ",
    "l": "(►) ",
    "r": "(►) ",
    "status_l": 4,
    "q": "(■) ",
}
STATUS_CHAR = {"p", "s", "l", "r", "q", "n"}


def count(seconds, v: Value):
    i = seconds
    while v.value != "q" and i > 0:
        time.sleep(1)
        i -= 1
    key = "q"
    v.value = key
    # print("count key: " + key)


def ask(v: Value):
    key = v.value
    while key != "q":
        # if we don't check for this, then the Process actually DOESN'T STOP or
        # FUCKS UP or smth even after TERMINATING IT. Cuh
        if msvcrt.kbhit():
            key = msvcrt.getch().decode("ASCII").lower()
            v.value = key
        time.sleep(0.05)
        # print("ask key: " + key)


class ProgressBar:
    def __init__(self, seconds, start_time):
        self.scr_l = 60
        left_side = ""
        right_side = ""
        self.seconds = seconds
        self.is_video_long = seconds > 3599
        self.time_bar = formatted_time(0)
        self.full_time = formatted_time(seconds, self.is_video_long)
        subtract = (
            len(left_side)
            + STATUS_ICON["status_l"]
            + 1
            + len(right_side)
            + len(self.time_bar)
            + len(self.full_time)
        )
        self.bar_l = self.scr_l - subtract
        self.start_time = start_time
        self.down_time = 0
        self.pause_time = 0
        self.down = False
        self.c_time = 0
        assert self.seconds > 0.99, f"Video time too short: {self.seconds}"
        self.key = "l"

    def pause(self):
        self.down = not self.down

    def print_bar(self, key):
        if not self.down:
            self.c_time = time.time() - self.start_time - self.down_time
        ratio = self.c_time / self.seconds
        if ratio > 1:
            ratio = 1
        bar = "=" * (round((self.bar_l - 1) * ratio)) + "v"
        neg_bar = "-" * (self.bar_l - len(bar))
        if key in STATUS_CHAR and key != "n":
            self.key = key
        self.time_bar = formatted_time(self.c_time)
        progress = STATUS_ICON[self.key] + " " + self.time_bar + bar + neg_bar
        progress = progress + self.full_time
        print(progress, end="\r")


def get_seconds(formatted_input: str = 0):
    if formatted_input == 0:
        print("[INFO] This has no length.")
        return 0
    _temp = formatted_input.split(":")
    return int(_temp[0]) * 3600 + int(_temp[1]) * 60 + int(_temp[2])


def formatted_time(seconds, is_long=False):
    sec = int(seconds)
    hour = str(sec // 3600)
    hour = "0" * (2 - len(hour)) + hour
    minute = str((sec % 3600) // 60)
    minute = "0" * (2 - len(minute)) + minute
    sec = str(sec % 60)
    sec = "0" * (2 - len(sec)) + sec
    if not is_long:
        return f"{minute}:{sec}"
    return f"{hour}:{minute}:{sec}"


def player_info(title, seconds, info_length=60):
    print("-" * info_length)
    title_list = formatter.line_breaker(str(title), info_length - 2)
    left_marge = " " * 15
    for line in title_list:
        print(formatter.centered(line, info_length))
    print()
    print()
    print(left_marge + "[||] - p  [►] - l  [■] - q   Replay - r")
    print()


def player_loop(v_duration, v: Value):
    start_time = time.time()
    key = v.value
    Bar = ProgressBar(v_duration, start_time)
    while key != "q":
        if key == "p":
            Bar.pause_time = time.time()
            Bar.down_time = time.time() - Bar.pause_time
            media.pause()
            Bar.pause()
            v.value = "n"
        elif key == "s":
            media.stop()
            v.value = "n"
        elif key == "l":
            if Bar.pause_time != 0:
                Bar.down_time = time.time() - Bar.pause_time
            media.play()
            Bar.pause()
            v.value = "n"
        elif key == "r":
            media.stop()
            media.play()
            Bar.start_time = time.time()
            Bar.down_time = 0
            v.value = "n"

        Bar.print_bar(key)
        key = v.value
        time.sleep(0.05)
    v.value = "q"


def cli_gui(v_title, v_duration):
    # seconds = get_seconds(v_duration)
    player_info(v_title, v_duration)
    key = "n"
    v = Value("u", key)
    p_count = Process(
        target=count,
        args=(
            v_duration,
            v,
        ),
    )
    p_ask = Process(target=ask, args=(v,))
    p_count.start()
    p_ask.start()
    player_loop(v_duration, v)
    p_count.terminate()
    p_ask.kill()
    p_count.join()
    p_ask.join()
    # print("\n@@@ count >>> : " + str(p_count.is_alive()))
    # print("\n@@@ ask >>> : " + str(p_ask.is_alive()))
    media.stop()
    print()


def exit_check(cmd_input):
    if cmd_input.lower() in EXIT_CHARS:
        print()
        exit()
    return cmd_input


def check_if_num(cmd_input, tab, prev_url):
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
    elif cmd_input.lower() == "r":
        return prev_url, cont
    elif "https" not in cmd_input:
        print("url not good, you got a free song!")
        return "https://www.youtube.com/watch?v=R-ZplG81oZg", cont
    return cmd_input, cont


def start_input(prev_url):
    cont = True
    tab = lib_s.pull_songs()
    prompt = "[>] URL or song Number /quit - 'q'/ [>]: "
    while cont:
        cmd_input = exit_check(input(prompt))
        url, cont = check_if_num(cmd_input, tab, prev_url)
    return url


if __name__ == "__main__":
    print("\n")
    formatter.abc_rower("PYTHON MUSIC")
    print("\n")
    prev_url = "segg"
    while True:
        url = start_input(prev_url)
        # print("\n" + url + "\n")
        ydl_opts = {"format": "bestaudio"}
        with YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(url, download=False)
        v_title = song_info["title"]
        v_duration = song_info["duration"]
        media = vlc.MediaPlayer(song_info["url"])
        media.play()
        cli_gui(v_title, v_duration)
        lib_s.inwriter(v_title, url, formatted_time(v_duration))
        print("\n***(bideo emth...! щ(`Д´щ;) )***")
        print("-" * 80 + "\n")
        prev_url = url
