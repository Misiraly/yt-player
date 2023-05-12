import msvcrt
import time
from multiprocessing import Process, Value

import lib_sorter as ls
from modules import formatter

# from random import randint


music_lib = r"C:\Users\mihaly.kotiers\Desktop\trhow\yt-player\music_lib.txt"
#!
EXIT_CHARS = {"q", "exit"}

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
        time.sleep(0.125)
        if v.value != "b":
            i -= 0.125
    key = "q"
    v.value = key


def ask(v: Value):
    key = v.value
    while key != "q":
        # if we don't check for this below, then the Process actually DOESN'T
        # STOP or FUCKS UP or smth even after TERMINATING IT. Cuh
        if msvcrt.kbhit():
            key = msvcrt.getch().decode("ASCII").lower()
            v.value = key
        time.sleep(0.05)


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
        if key in STATUS_CHAR and key not in {"n", "np"}:
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
        print(line.center(info_length))
    print()
    print()
    print(left_marge + "[||] - p  [►] - l  [■] - q   Replay - r")
    print()


def player_loop(media, v_duration, v: Value):
    start_time = time.time()
    key = v.value
    Bar = ProgressBar(v_duration, start_time)
    while key != "q":
        if key == "p":
            Bar.pause_time = time.time()
            Bar.down_time = time.time() - Bar.pause_time
            media.pause()
            Bar.pause()
            v.value = "b"
        elif key == "s":
            media.stop()
            Bar.down = True
            Bar.c_time = 0
            Bar.start_time = time.time()
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


def cli_gui(v_title, v_duration, media):
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
    player_loop(media, v_duration, v)
    p_count.terminate()
    p_ask.terminate()
    p_count.join()
    p_ask.join()
    media.stop()
    print()


class BaseInterface:
    page = dict()
    page["header"] = ["\n"] + formatter.abc_rower("  PYTHON MUSIC") + ["\n"]
    page["body"] = list()
    page["prompt"] = ["[>] URL or song Number [>]: "]
    page["closer"] = [
        "\n***     ..bideo.. emth!!!~` щ(`Д´щ;)    ***",
        "\n" + "-" * 80 + "\n",
    ]
    page_width = 80
    song = {
        "title": "dummy",
        "url": "https://www.youtube.com/watch?v=fWh6J5Tg274",
    }
    ydl_opts = {"format": "bestaudio"}
    song_info = None
    tab_array = list()
    wspace = " "
    ell = "..."
    nell = "   "
    media = None

    def __init__(self):
        self.table = ls.pull_csv_as_df()

    def print_closer(self):
        for entry in self.page["closer"]:
            print(entry)

    def double_table(self):
        half = len(self.table.index) // 2 + len(self.table.index) % 2
        part_line = self.page_width // 2
        title_l = part_line - len(self.wspace) - len(self.ell)
        tst = ["" for i in range(half)]  # two-side-table :3
        titles = self.table["title"].values.tolist()
        for i, song in enumerate(titles):
            title = song.ljust(title_l)
            if len(title) > title_l:
                title = title[: title_l - 3] + self.ell
            tst[i % half] = (
                tst[i % half]
                + str(i).ljust(2)
                + self.wspace
                + title
                + self.wspace * (1 - (i // half))
            )
        self.page["body"] = tst

    def show_article(self):
        self.table = ls.pull_csv_as_df()
        self.double_table()
        article = (
            self.page["header"] + self.page["body"]
        )  # + _page["prompt"] + _page["closer"]
        for line in article:
            print(line)
