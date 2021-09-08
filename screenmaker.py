"""
This module is responsible for taking a screen name and constructing the
appropriate Screen object, including populating it with the appropriate Panels.
"""

from util import Point

from classes.Panel import DummyPanel, ListPanel, Panel, PlaylistPanel
from classes.Screen import Screen

def make_screen(screen_name, screen_dimensions):
    new_dimensions = truncate_dimensions(screen_dimensions)
    maker = get_screen_maker(screen_name)
    screen = maker(new_dimensions)

    return screen

def resize_screen(screen, screen_dimensions):
    new_dimensions = truncate_dimensions(screen_dimensions)
    screen_name = screen.title
    resizer = get_screen_resizer(screen_name)
    resizer(screen, new_dimensions)

def truncate_dimensions(dimensions):
    # Remove top line from dimensions for player info
    # Remove bottom lines from dimensions for playbar info
    (old_ul, old_lr) = dimensions
    ul = Point(old_ul.y + 1, old_ul.x)
    lr = Point(old_lr.y - 2, old_lr.x)
    new_dimensions = (ul, lr)

    return new_dimensions

def get_screen_maker(screen_name):
    if screen_name == 'Playlist':
        return _make_playlist_screen
    elif screen_name == 'Media Library':
        return _make_media_library_screen
    elif screen_name == 'Test':
        return _make_test_screen
    else:
        raise ValueError(screen_name)

def _make_playlist_screen(screen_dimensions):
    # Playlist consists of a single Panel showing the current play queue
    screen = Screen(screen_dimensions, "Playlist")
    panel = PlaylistPanel(screen_dimensions, "Playlist")
    screen.addPanel(panel)

    return screen

def _make_media_library_screen(screen_dimensions):
    # Media Library is three vertical panels (artist, album, songs)
    screen = Screen(screen_dimensions, "Media Library")

    artist_panel_dimensions = get_vertical_third_dimensions(screen_dimensions, 1)
    album_panel_dimensions = get_vertical_third_dimensions(screen_dimensions, 2)
    song_panel_dimensions = get_vertical_third_dimensions(screen_dimensions, 3)

    artist_panel = ListPanel(artist_panel_dimensions, "Artists")
    album_panel = ListPanel(album_panel_dimensions, "Albums")
    song_panel = ListPanel(song_panel_dimensions, "Songs")

    screen.addPanel(artist_panel)
    screen.addPanel(album_panel)
    screen.addPanel(song_panel)

    return screen

def get_vertical_third_dimensions(screen_dimensions, panel_num):
    (screen_ul, screen_lr) = screen_dimensions
    third = round(screen_lr.x / 3)
    panel_ul = Point(screen_ul.y, third * (panel_num - 1))
    panel_lr = Point(screen_lr.y, min(screen_lr.x, third * panel_num))
    panel_dimensions = (panel_ul, panel_lr)

    return panel_dimensions

def _make_test_screen(screen_dimensions):
    # Test screen is just a single empty panel
    screen = Screen(screen_dimensions, "Test")
    panel = DummyPanel(screen_dimensions, "Test")
    screen.addPanel(panel)

    return screen

def get_screen_resizer(screen_name):
    if screen_name == 'Playlist':
        return _resize_playlist_screen
    elif screen_name == 'Media Library':
        return _resize_media_library_screen
    elif screen_name == 'Test':
        return _resize_test_screen
    else:
        raise ValueError(screen_name)

def _resize_playlist_screen(screen, screen_dimensions):
    screen.setDimensions(screen_dimensions)
    for panel in screen.panels:
        panel.resize(screen_dimensions)

def _resize_media_library_screen(screen, screen_dimensions):
    screen.setDimensions(screen_dimensions)

    artist_panel_dimensions = get_vertical_third_dimensions(screen_dimensions, 1)
    album_panel_dimensions = get_vertical_third_dimensions(screen_dimensions, 2)
    song_panel_dimensions = get_vertical_third_dimensions(screen_dimensions, 3)

    screen.panels[0].resize(artist_panel_dimensions)
    screen.panels[1].resize(album_panel_dimensions)
    screen.panels[2].resize(song_panel_dimensions)

def _resize_test_screen(screen, screen_dimensions):
    screen.setDimensions(screen_dimensions)
    for panel in screen.panels:
        panel.resize(screen_dimensions)
