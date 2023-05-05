from datetime import datetime

import pandas as pd
import regex as re

from modules import formatter

"""
Created on Thur Nov 24 15:00:41 2022

@author: MIHALY.KOTIERS
"""

"""
Title: Eddy Grant - Gimme Hope Jo Anna  1988
Author: OLD TAPES
ID: R-ZplG81oZg
Duration: 00:04:13
Rating: None
Views: 9150147
Thumbnail: http://i.ytimg.com/vi/R-ZplG81oZg/default.jpg
"""


_DELIM = " -- "
music_lib = r"C:\Users\mihaly.kotiers\Desktop\trhow\yt-player\music_lib.txt"


def pull_as_df(columns=None):
    df = pd.DataFrame(columns=["title", "url", "duration", "add_date"])
    with open(music_lib) as r:
        for line in r:
            con = line.split(_DELIM)
            for i in range(4 - len(con)):
                con.append("")
            b = {
                "title": [con[0]],
                "url": [con[1]],
                "duration": [con[2]],
                "add_date": [con[3]],
            }
            tf = pd.DataFrame(b)
            df = pd.concat([df, tf], ignore_index=True)
    if columns is not None:
        return df[columns]
    return df


def inwriter(title_in, url, duration):
    title = title_in.encode("utf-8", errors="ignore").decode("utf-8")
    with open(music_lib, "r") as lib:
        text = lib.read()
    if title not in text:
        with open(music_lib, "r") as lib:
            content = lib.read()
        content = content.split("\n")[:-1]  # to remove last newline char
        line_to_add = _DELIM.join([title, url, duration, str(datetime.now())])
        print(url)
        content.append(line_to_add)
        content.sort()
        with open(music_lib, "w") as lib:
            for con in content:
                try:
                    if not con == "":
                        lib.write(con + "\n")
                except:
                    print("*" * 80)
                    print(" ")
                    title = re.sub(r"[^a-zA-Z0-9 ]", "", title)
                    line_to_add = _DELIM.join(
                        [title, url, duration, str(datetime.now())]
                    )
                    lib.write(line_to_add + "\n")
                    formatter.abc_rower("   ! WARNING !")
                    print(" ")
                    print("\n\nWasn't able to add\n" + ">> " + con + " <<")
                    print("try adding it manually\n\n")


def pull_songs():
    """
    Reads in the music library and returns a list of indeces, titles,
    duration-s, dates of added. Prints indeces and titles.
    """
    tab = []
    with open(music_lib) as lib:
        for i, line in enumerate(lib):
            print(str(i) + " " + line.split(_DELIM)[0])
            if "https" in line:
                tab.append(line.split(_DELIM))
    return tab


def pull_Music_tab():
    """
    Reads in the music library and returns a list of indeces, titles,
    duration-s, dates of added. Doesn't print.
    """
    tab = []
    with open(music_lib) as lib:
        for i, line in enumerate(lib):
            # if "https" in line:
            tab.append(line.split(_DELIM))
    return tab
