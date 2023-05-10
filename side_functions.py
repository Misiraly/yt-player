import pandas as pd

import lib_sorter as ls
from modules import search_text as st

TREE = {
    "ser": "search for a text",
    "edit": "edit the library",
    "single": "play a video but don't add to library",
}


def sorted_by_word(s_word: str, lib: pd.DataFrame, cutoff: int = 5) -> pd.DataFrame:
    df = lib
    df["dis"] = lib.apply(
        lambda row: st.token_distance_list(s_word, row["title"]), axis=1
    )
    sdf = st.qs_df(df, "dis", st.abc_leq)
    print(sdf)
    return sdf


def ser_lib():
    lib = ls.pull_as_df()
    s_word = input("Search: ")
    s_lib = sorted_by_word(s_word, lib, 6)
    print(s_lib[["title"]])


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


def start_input(prev_url, tab):
    cont = True
    prompt = "[>] URL or song Number /quit - 'q'/ [>]: "
    while cont:
        cmd_input = exit_check(input(prompt))
        url, cont = check_if_num(cmd_input, tab, prev_url)
    return url
