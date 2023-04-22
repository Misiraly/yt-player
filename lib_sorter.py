from datetime import datetime

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
music_lib = r"music_lib.txt"


def inwriter(title_in, url, duration):
    title = title_in.encode("utf-8", errors="ignore").decode("utf-8")
    with open(music_lib, "r") as lib:
        text = lib.read()
    if title not in text:
        with open(music_lib, "r") as lib:
            content = lib.read()
        content = content.split("\n")[:-1]  # to remove last newline char
        line_to_add = _DELIM.join([title, url, duration, str(datetime.now())])
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
                    formatter.abc_rower("   ! WARNING !")
                    print(" ")
                    print("\n\nWasn't able to add\n" + ">> " + con + " <<")
                    print("try adding it manually\n\n")


def pull_songs():
    tab = []
    with open(music_lib) as lib:
        for i, line in enumerate(lib):
            print(str(i) + " " + line.split(_DELIM)[0])
            if "https" in line:
                tab.append(line.split(_DELIM))
    return tab
