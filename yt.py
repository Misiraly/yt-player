import vlc
from yt_dlp import YoutubeDL

import lib_sorter as ls
import side_functions as sf
import ui_first

# from random import randint

# OPTIONS = {"ser":sf.ser_lib, "default":init_player}

EXIT_CHARS = {"q", "exit"}


def divider():
    print("-" * 80)


def playTheSong(url):
    ydl_opts = {"format": "bestaudio"}
    with YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(url, download=False)
    media = vlc.MediaPlayer(song_info["url"])
    media.play()
    return song_info, media


def play_on_list(cmd_input, bu):
    cmd_num = int(cmd_input)
    if cmd_num not in bu.table.index:
        print("[TRY AGAIN], number not on list")
    else:
        bu.song = bu.table.iloc[cmd_num]
        song_info, media = playTheSong(bu.song["url"])
        ui_first.cli_gui(bu.song["title"], song_info["duration"], media)
        bu.print_closer()


def play_new(cmd_input, bu):
    if "https" not in cmd_input:
        print("[TRY AGAIN], cant comprehend")
    else:
        url = cmd_input
        song_info, media = playTheSong(url)
        v_title = song_info["title"]
        v_duration = song_info["duration"]
        bu.song = {"title": v_title, "url": url, "duration": v_duration}
        ui_first.cli_gui(v_title, v_duration, media)
        ls.write_table_to_csv(v_title, url, ui_first.formatted_time(v_duration))
        bu.print_closer()


def init_player(cmd_input, bu):
    if cmd_input.isnumeric():
        play_on_list(cmd_input, bu)
    else:
        play_new(cmd_input, bu)
    bu.show_article()


def replay(bu):
    init_player(bu.song["url"], bu)


def single_play(bu):
    cmd_input = input("[>] song URL [played only once]: ")
    if "https" not in cmd_input:
        print("[TRY AGAIN], cant comprehend")
    else:
        url = cmd_input
        song_info, media = playTheSong(url)
        v_title = song_info["title"]
        v_duration = song_info["duration"]
        bu.song = {
            "title": song_info["title"],
            "url": url,
            "duration": song_info["duration"],
        }
        ui_first.cli_gui(v_title, v_duration, media)
        bu.print_closer()
        bu.show_article()


def correct_title(bu):
    cmd_input = input("[>] index of title to correct: ")
    if cmd_input.isnumeric():
        cmd_num = int(cmd_input)
        if cmd_num not in bu.table.index:
            print("[TRY AGAIN], number not on list")
        else:
            song = bu.table.iloc[cmd_num]
            ls.del_from_csv(cmd_num)
            title = ls.correct_title(song["title"])
            ls.write_table_to_csv(title, song["url"], song["duration"])
            bu.show_article()


def decision_tree(bu):
    prompt = "[>] URL or song Number /quit - 'q'/ [>]: "
    cmd_input = input(prompt)
    if cmd_input in EXIT_CHARS:
        exit()
    elif cmd_input == "ser":
        divider()
        sf.ser_lib()
        divider()
    elif cmd_input == "del":
        divider()
        sf.del_a_song()
        divider()
    elif cmd_input == "tab":
        bu.show_article()
    elif cmd_input == "r":
        replay(bu)
    elif cmd_input == "single":
        single_play(bu)
    elif cmd_input == "correct title":
        correct_title(bu)
    elif cmd_input == "random":
        print("\n[RETARD WARNING] I disabled it, retard.\n")
        return
        # return table.iloc[randint(0,len(table.index))]['url']
    else:
        init_player(cmd_input, bu)


def main_loop():
    bu = ui_first.BaseInterface()
    bu.show_article()
    while True:
        decision_tree(bu)


if __name__ == "__main__":
    main_loop()
