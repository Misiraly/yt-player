import time

import pandas as pd
import search_text as st

import lib_sorter as ls

_DELIM = " -- "
music_lib = (
    r"C:\Users\mihaly.kotiers\Desktop\trhow\yt-player\search_trial\music_lib - arch.txt"
)


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


def dimain():
    df = ls.pull_as_df()
    csv = "s_test_results.csv"
    # df.to_csv(csv, encoding='utf8')
    with open(csv, "w") as w:
        w.write("filters,title,url,duration,add_date,dis,batch\n")
    s_file = "s_words.txt"
    s_words = []
    with open(s_file) as r:
        for line in r:
            s_words.append(line.replace("\n", ""))
            print(line)
    for i, sw in enumerate(s_words):
        df["dis"] = df.apply(
            lambda row: st.token_distance_list(sw, row["title"]), axis=1
        )
        df["batch"] = df.apply(lambda row: i, axis=1)
        with open(csv, "a") as a:
            a.write("WORD:," + sw + ",,,,," + str(i) + "\n")
        sdf = st.quick_sort(df, "dis", st.abc_leq)
        sdf.head(5).to_csv("s_test_results.csv", mode="a")
    print()


def dis_test(sw, df):
    df["dis"] = df.apply(lambda row: st.token_distance_list(sw, row["title"]), axis=1)
    sdf = st.qs_df(df, "dis", st.abc_leq)
    return sdf


def dis_test_2(sw, df):
    df["dis"] = df.apply(lambda row: st.token_distance_list_2(sw, row["title"]), axis=1)
    sdf = st.qs_df(df, "dis", st.abc_leq)
    return sdf


def dis_test_3(sw, df):
    df["dis"] = df.apply(lambda row: st.token_distance_list_3(sw, row["title"]), axis=1)
    sdf = st.qs_df(df, "dis", st.abc_leq)
    return sdf


def sorted_by_word(sw):
    df = pull_as_df()
    df["dis"] = df.apply(lambda row: st.token_distance_list(sw, row["title"]), axis=1)
    sdf = st.quick_sort(df, "dis", st.abc_leq)
    return sdf.head(5)


def time_wrap(sorttype, sw, df):
    startime = time.time()
    sdf = sorttype(sw, df)
    delta = time.time() - startime
    # print(sdf)
    return delta


def main():
    sws = []
    s_file = "s_words.txt"
    with open(s_file) as r:
        for line in r:
            sws.append(line.replace("\n", ""))
            # print(line)
    funcs = {dis_test, dis_test_2, dis_test_3}  # , sorted_by_word}
    dlist = {}
    df = pull_as_df()
    for func in funcs:
        dlist[func.__name__] = []
    print("Initializing testing... please be patient...")
    for func in funcs:
        temp = []
        print()
        print(func.__name__)
        for i, sw in enumerate(sws):
            # print(sw.upper())
            delta = time_wrap(func, sw, df)
            # print(">> " + func.__name__ + "("+sw+"): "+str(delta))
            temp.append(delta)
            print(
                str((100 * i) // (len(sws) - 1)).rjust(3)
                + "%"
                + "." * ((i // 24) % 120),
                end="\r",
            )
        dlist[func.__name__] = temp
    print()
    for key in dlist:
        print(key.ljust(10) + " " + str(sum(dlist[key]) / len(dlist[key])))


if __name__ == "__main__":
    # df = ls.pull_as_df()
    main()
    # for i in range(10): main()
