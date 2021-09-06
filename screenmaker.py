"""
This module is responsible for taking a screen name and constructing the
appropriate Screen object, including populating it with the appropriate Panels.
"""

from util import Point

from classes.Panel import DummyPanel, Panel, PlaylistPanel
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
        return _makePlaylist_screen
    elif screen_name == 'Test':
        return _makeTest_screen
    else:
        raise ValueError(screen_name)

def _makePlaylist_screen(screen_dimensions):
    # Playlist consists of a single Panel showing the current play queue
    screen = Screen(screen_dimensions, "Playlist")
    panel = PlaylistPanel(screen_dimensions, "Playlist")
    screen.addPanel(panel)

    return screen

def _makeTest_screen(screen_dimensions):
    # Test screen is just a single empty panel
    screen = Screen(screen_dimensions, "Test")
    panel = DummyPanel(screen_dimensions, "Test")
    screen.addPanel(panel)

    return screen

def get_screen_resizer(screen_name):
    if screen_name == 'Playlist':
        return _resizePlaylist_screen
    elif screen_name == 'Test':
        return _resizeTest_screen
    else:
        raise ValueError(screen_name)

def _resizePlaylist_screen(screen, screen_dimensions):
    screen.setDimensions(screen_dimensions)
    for panel in screen.panels:
        panel.resize(screen_dimensions)

def _resizeTest_screen(screen, screen_dimensions):
    screen.setDimensions(screen_dimensions)
    for panel in screen.panels:
        panel.resize(screen_dimensions)
