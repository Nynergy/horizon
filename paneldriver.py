"""
This module handles moving around and modifying the inner bits and bobs of
Panels, that way they don't need to know how to modify themselves.
"""

def move_down(panel, amount):
    # Validate that there are items
    if(len(panel.items) == 0):
        return

    # Set new curr_item and shift frame if necessary
    panel.curr_item = min(panel.curr_item + amount, len(panel.items) - 1)
    while(panel.curr_item >= panel.l_item):
        panel.f_item += 1
        panel.l_item += 1

def move_up(panel, amount):
    # Validate that there are items
    if(len(panel.items) == 0):
        return

    # Set new curr_item and shift frame if necessary
    panel.curr_item = max(panel.curr_item - amount, 0)
    while(panel.curr_item < panel.f_item):
        panel.f_item -= 1
        panel.l_item -= 1
