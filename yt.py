from random import randint

import vlc
from yt_dlp import YoutubeDL

import lib_sorter as ls
import side_functions as sf
import ui_first

EXIT_CHARS = {"q", "exit"}


def divider():
    """
    Use it to visually divide blocks on the terminal.
    """
    print("-" * 80)


def playTheSong(url):
    """
    Play a video from a given url, and return it as as an object with some
    info about the video.
    """

    ydl_opts = {"format": "bestaudio"}
    with YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(url, download=False)
    media = vlc.MediaPlayer(song_info["url"])
    media.play()
    return song_info, media


def play_on_list(cmd_input, bu):
    """
    Plays a song that is tracked by our library.
    """
    cmd_num = int(cmd_input)
    if cmd_num not in bu.table.index:
        print("[TRY AGAIN], number not on list")
    else:
        bu.song = bu.table.iloc[cmd_num]
        song_info, media = playTheSong(bu.song["url"])
        ui_first.cli_gui(bu.song["title"], song_info["duration"], media)
        bu.print_closer()


def play_random(bu):
    """
    Plays a song that is tracked by our library.
    """
    r = randint(0, len(bu.table.index) - 1)
    bu.song = bu.table.iloc[r]
    print("\nPlaying a random song...\n")
    song_info, media = playTheSong(bu.song["url"])
    ui_first.cli_gui(bu.song["title"], song_info["duration"], media)
    bu.print_closer()
    bu.show_article()


def play_new(cmd_input, bu):
    """
    Play a song not yet tracked by our library.
    """
    if "https" not in cmd_input:
        print("[TRY AGAIN], can't comprehend")
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
    """
    If we get an integer input, we assume it refers to a song already in our
    library. Otherwise we handle it as a new song that needs to be added to
    the library.
    """
    if cmd_input.isnumeric():
        play_on_list(cmd_input, bu)
    else:
        play_new(cmd_input, bu)
    bu.show_article()


def replay(bu):
    """
    Replays the song saved in the `BaseInterface` object (bu). If it wasn't
    added to the library yet, it means it will be added.
    """
    init_player(bu.song["url"], bu)


def search_table():
    divider()
    sf.ser_lib()
    divider()


def delete_song():
    divider()
    sf.del_a_song()
    divider()


def single_play(bu):
    """
    Plays a song but doesn't add it to the list of songs. However it is
    recorded in the `BaseInterface` object (bu), thus will be tracked after
    replay.
    """

    cmd_input = input("[>] song URL [played only once]: ")
    if "https" not in cmd_input:
        print("[TRY AGAIN], can't comprehend")
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
    """
    Uses the `correct_title()` function from `side_functions`. Makes sure
    the user corrects the title it actually wants to correct as it is final.
    """
    cmd_input = input("[>] index of title to correct: ")
    if cmd_input.isnumeric():
        cmd_num = int(cmd_input)
        if input("Are you sure? [y/N]") not in {"y", "Y"}:
            return
        if cmd_num not in bu.table.index:
            print("[TRY AGAIN], number not on list")
        else:
            song = bu.table.iloc[cmd_num]
            ls.del_from_csv(cmd_num)
            title = ls.correct_title(song["title"])
            ls.write_table_to_csv(title, song["url"], song["duration"])
            bu.show_article()


def command_help():
    print("Command list: ")
    print("  - ser :: search for song")
    print("  - del :: delete a song")
    print("  - correct title :: remove unusual characters from title")
    print("  - tab :: print the list of songs")
    print("  - date :: print a list where the songs are arranged by date, descending")
    print("  - r :: replay a song")
    print("  - single :: play a url without adding it to the library")
    print("  - help :: prints this list")
    print("  - random :: doesn't work, don't use")


def decision_tree(bu):
    """
    Decides what to execute given an input from the terminal.
    """
    print("[ser : del : correct title : tab : date : r : single : help]")
    prompt = "[>] URL or song Number /quit - 'q'/ [>]: "
    cmd_input = input(prompt)
    if cmd_input in EXIT_CHARS:
        exit()
    elif cmd_input == "ser":
        search_table()
    elif cmd_input == "del":
        delete_song()
    elif cmd_input == "correct title":
        correct_title(bu)
    elif cmd_input == "tab":
        bu.show_article()
    elif cmd_input == "date":
        bu.show_article_by_date()
    elif cmd_input == "r":
        replay(bu)
    elif cmd_input == "single":
        single_play(bu)
    elif cmd_input == "help":
        command_help()
    elif cmd_input == "random":
        play_random(bu)
    else:
        init_player(cmd_input, bu)


def main_loop():
    bu = ui_first.BaseInterface()
    bu.show_article()
    while True:
        decision_tree(bu)


if __name__ == "__main__":
    main_loop()
