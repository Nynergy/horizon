import curses
import json

class Point:
    def __init__(self, y, x):
        self.y = y
        self.x = x

def get_config():
    with open('config.json') as fp:
        data = json.load(fp)

    return data

def curses_color(color):
    color_dict = {
                  "black": curses.COLOR_BLACK,
                  "red": curses.COLOR_RED,
                  "green": curses.COLOR_GREEN,
                  "yellow": curses.COLOR_YELLOW,
                  "blue": curses.COLOR_BLUE,
                  "magenta": curses.COLOR_MAGENTA,
                  "cyan": curses.COLOR_CYAN,
                  "white": curses.COLOR_WHITE,
                  "transparent": -1
                 }

    return color_dict[color]

def get_color_pair(pair_name):
    pair_dict = {
                 "Foreground": curses.color_pair(1),
                 "Accent": curses.color_pair(2),
                 "Selection": curses.color_pair(3),
                 "Playbar": curses.color_pair(4),
                 "PlaylistSongTitle": curses.color_pair(5),
                 "PlaylistSongAlbum": curses.color_pair(6),
                 "PlaylistSongTracknum": curses.color_pair(7),
                 "PlaylistSongArtist": curses.color_pair(8),
                 "PlaylistSongYear": curses.color_pair(9),
                 "VolumeFill": curses.color_pair(10)
                }

    return pair_dict[pair_name]
