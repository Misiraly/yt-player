from datetime import datetime

import pandas as pd
import regex as re

_DELIM = " -- "
music_table = "data/music_table.csv"
# should have format as in "data/test-table.csv"


def divider():
    """
    Use it to visually divide blocks on the terminal.
    """
    print("-" * 80)


def pull_csv_as_df():
    df = pd.read_csv(music_table, index_col=[0])
    return df


def write_table_to_csv(title_in, url, duration):
    """
    Given the title, url and duration of a song, writes it into the library.
    The library is saved after sorting by titles.
    """
    df = pull_csv_as_df()
    if title_in not in df["title"].values:
        df.loc[len(df.index)] = [title_in, url, duration, str(datetime.now())]
        # sort_values sorts all capital letters before lowercase letters...
        # we do not want this.
        out_df = df.sort_values(
            by=["title"], key=lambda col: col.str.lower(), ignore_index=True
        )
        out_df.to_csv(music_table)


def correct_title(title_in):
    """
    Returns a title-string stripped of non-standard characters.
    """
    title = re.sub(r"[^a-zA-Z0-9 ]", "", title_in)
    title = title.lstrip()
    return title


def del_from_csv(row_index):
    """
    Removes a row from the library given the row index.
    """
    df = pull_csv_as_df()
    new_df = df.drop([row_index]).reset_index(drop=True)
    new_df.to_csv(music_table)


# Retained for developer uses, sensibility checks.


def pull_as_df(columns=None):
    df = pd.DataFrame(columns=["title", "url", "duration", "add_date"])
    music_lib = r"data\music_lib.txt"
    with open(music_lib) as r:
        for line in r:
            con = line.split(_DELIM)
            for i in range(4 - len(con)):
                con.append("")
            b = {
                "title": [con[0]],
                "url": [con[1].replace("\n", "")],
                "duration": [con[2].replace("\n", "")],
                "add_date": [con[3].replace("\n", "")],
            }
            tf = pd.DataFrame(b)
            df = pd.concat([df, tf], ignore_index=True)
    if columns is not None:
        return df[columns]
    return df


def inwriter(title_in, url, duration):
    title = title_in.encode("utf-8", errors="ignore").decode("utf-8")
    music_lib = r"data\music_lib.txt"
    with open(music_lib, "r") as lib:
        text = lib.read()
    if title not in text:
        content = text.split("\n")[:-1]  # to remove last newline char
        line_to_add = _DELIM.join([title, url, duration, str(datetime.now())])
        content.append(line_to_add)
        content.sort()
        with open(music_lib, "w") as lib:
            for con in content:
                try:
                    if not con == "":
                        lib.write(con + "\n")
                except Warning:
                    divider()
                    title = correct_title(title)
                    line_to_add = _DELIM.join(
                        [title, url, duration, str(datetime.now())]
                    )
                    lib.write(line_to_add + "\n")
                    input("[WARNING] title bad. Still added.")
                    divider()


def pull_songs():
    """
    Reads in the music library and returns a list of indeces, titles,
    duration-s, dates of added. Prints indeces and titles.
    """
    tab = []
    music_lib = r"data\music_lib.txt"
    with open(music_lib) as lib:
        for i, line in enumerate(lib):
            print(str(i) + " " + line.split(_DELIM)[0])
            if "https" in line:
                tab.append(line.split(_DELIM))
    return tab


def pull_music_tab_KILL():
    """
    Reads in the music library and returns a list of indices, titles,
    duration-s, dates of added. Doesn't print.
    """
    tab = []
    music_lib = r"data\music_lib.txt"
    with open(music_lib) as lib:
        for i, line in enumerate(lib):
            # if "https" in line:
            tab.append(line.split(_DELIM))
    return tab


def pull_as_lines():
    music_lib = r"data\music_lib.txt"
    with open(music_lib, "r") as lib:
        lines = lib.readlines()
    return lines


def del_music_line(line_to_del):
    lines = pull_as_lines()
    music_lib = r"data\music_lib.txt"
    with open(music_lib, "w") as lib:
        for line in lines:
            if line_to_del != line:
                lib.write(line)
