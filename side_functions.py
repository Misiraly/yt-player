import pandas as pd

import lib_sorter as ls
from modules import search_text as st

TREE = {
    "ser": "search for a text",
    "edit": "edit the library",
    "single": "play a video but don't add to library",
}

EXIT_CHARS = {"q", "exit"}


def del_a_song():
    lines = ls.pull_as_lines()
    cmd_input = input("Song to delete (via index): ")
    if not cmd_input.isnumeric():
        print(f"[ERROR] wrong index ({cmd_input}), use only integers.")
        return
    if not int(cmd_input) in range(len(lines)):
        print(f"[ERROR] index ({cmd_input}) out of bounds.")
        return
    cmd_num = int(cmd_input)
    title = lines[cmd_num].split(ls._DELIM)[0]
    print("Are you sure to delete the song: ")
    print(" > " + title)
    make_sure = input("? [y/N]")
    if make_sure not in {"y", "Y"}:
        print("[INFO] deletion aborted")
        return
    ls.del_music_line(lines[cmd_num])
    print(f"[INFO] deleted song: {title}")


def sorted_by_word(s_word: str, lib: pd.DataFrame, cutoff: int = 5) -> pd.DataFrame:
    df = lib
    df["dis"] = lib.apply(
        lambda row: st.token_distance_list(s_word, row["title"]), axis=1
    )
    if cutoff > len(df.index):
        print(
            f"[WARNING] Cutoff value ({cutoff}) larger than library length, defaulting to 5"
        )
        cutoff = 5
    sdf = st.qs_df(df, "dis", st.abc_leq, cutoff=cutoff)
    return sdf


def find_options(cmd_input):
    op_STR = " --"
    if op_STR in cmd_input:
        return tuple(cmd_input.split(op_STR))
    return cmd_input, 5


def ser_lib():
    lib = ls.pull_as_df()
    cmd_input = input("Search [optional: --cutoff=int]: ")
    s_word, cutoff = find_options(cmd_input)
    s_lib = sorted_by_word(s_word, lib, int(cutoff))
    print(s_lib[["title"]])


def exit_check(cmd_input):
    if cmd_input.lower() in EXIT_CHARS:
        print()
        exit()


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


def start_input(prev_url, tab, cmd_input):
    cont = True
    url = prev_url
    while cont:
        exit_check(cmd_input)
        url, cont = check_if_num(cmd_input, tab, prev_url)
    return url
