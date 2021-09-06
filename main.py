#!/usr/bin/python3.8

import curses

from util import curses_color, get_config

from classes.Engine import Engine

def initialize_curses_environment(stdscr):
    stdscr.keypad(True)
    curses.curs_set(0)

def initialize_color_pairs(config):
    curses.use_default_colors()
    background = -1 # Transparent background
    curses.init_pair( 1, curses_color(config["ForegroundColor"]), background)
    curses.init_pair( 2, curses_color(config["AccentColor"]), background)
    curses.init_pair( 3, curses_color(config["SelectionColor"]), background)
    curses.init_pair( 4, curses_color(config["PlaybarColor"]), background)
    curses.init_pair( 5, curses_color(config["PlaylistSongTitleColor"]), background)
    curses.init_pair( 6, curses_color(config["PlaylistSongAlbumColor"]), background)
    curses.init_pair( 7, curses_color(config["PlaylistSongTracknumColor"]), background)
    curses.init_pair( 8, curses_color(config["PlaylistSongArtistColor"]), background)
    curses.init_pair( 9, curses_color(config["PlaylistSongYearColor"]), background)
    curses.init_pair(10, curses_color(config["VolumeFillColor"]), background)

def main(stdscr):
    config = get_config()
    initialize_curses_environment(stdscr)
    initialize_color_pairs(config)

    engine = Engine(config, stdscr)
    engine.run()

# Begin curses mode
curses.wrapper(main)
