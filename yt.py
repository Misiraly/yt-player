import vlc
from yt_dlp import YoutubeDL

import lib_sorter as lib_s
import side_functions as sf
import ui_first

# from random import randint

# OPTIONS = {"ser":sf.ser_lib, "default":init_player}


def divider():
    print("-" * 80)


def decision_tree(bu):
    prompt = "[>] URL or song Number /quit - 'q'/ [>]: "
    cmd_input = input(prompt)
    if cmd_input == "ser":
        divider()
        sf.ser_lib()
        divider()
    elif cmd_input == "del":
        divider()
        sf.del_a_song()
        divider()
    elif cmd_input == "tab":
        bu.show_article()
    else:
        init_player(bu, cmd_input)
        bu.show_article()


def playTheSong(url):
    ydl_opts = {"format": "bestaudio"}
    with YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(url, download=False)
    media = vlc.MediaPlayer(song_info["url"])
    media.play()
    return song_info, media


def init_player_ui(url, song_info, media):
    v_title = song_info["title"]
    v_duration = song_info["duration"]
    ui_first.cli_gui(v_title, v_duration, media)
    lib_s.inwriter(
        v_title, url, ui_first.formatted_time(v_duration)
    )  # use the original url, otherwise it writes in a sheit url


def init_player(bu, cmd_input):
    bu.url = sf.start_input(bu.prev_url, bu.tab, cmd_input)
    song_info, media = playTheSong(bu.url)
    init_player_ui(bu.url, song_info, media)
    bu.prev_url = bu.url
    bu.print_closer()


def main_loop():
    bu = ui_first.BaseInterface()
    bu.show_article()
    while True:
        decision_tree(bu)


if __name__ == "__main__":
    main_loop()
