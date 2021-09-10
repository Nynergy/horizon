"""
This module aims to provide a nice suite of wrappers for drawing on curses
windows. Window must be provided to each function.
"""

import curses

from util import Point

def char(p, ch, win):
    win.addch(p.y, p.x, ch)

def string(p, s, win):
    win.addstr(p.y, p.x, s)

def h_line(p1, p2, ch, win):
    if (p1.y != p2.y) or (p1.x == p2.x):
        raise ValueError((p1, p2))

    left = min(p1.x, p2.x)
    right = max(p1.x, p2.x)
    for i in range(left, right + 1):
        char(Point(p1.y, i), ch, win)

def v_line(p1, p2, ch, win):
    if (p1.x != p2.x) or (p1.y == p2.y):
        raise ValueError((p1, p2))

    top = min(p1.y, p2.y)
    bottom = max(p1.y, p2.y)
    for i in range(top, bottom + 1):
        char(Point(i, p1.x), ch, win)
