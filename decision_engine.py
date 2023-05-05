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
    sdf = st.quick_sort(df, "dis", st.abc_leq)
    if cutoff is None:
        return sdf.head(cutoff)
    return sdf.head(cutoff)


def ser_lib():
    lib = ls.pull_as_df()
    s_word = input("Search: ")
    s_lib = sorted_by_word(s_word, lib, 6)
    print(s_lib[["title"]])


ser_lib()
