"""
A Form is a single-line input field that can be embedded into a prompt-like
window, effectively creating a little editor to type strings into.

This is how we get the names of new/edited playlists from the user.
"""

import curses

import draw
from util import Point

class Form:
    def __init__(self, origin, length, prompt=""):
        self.origin = origin
        self.length = length
        self.prompt = prompt
        self.buffer = ""
        self.constructFormWindow()

    def constructFormWindow(self):
        self.win = curses.newwin(1, self.length, self.origin.y, self.origin.x)
        self.win.keypad(True)

    def render(self):
        self.clearScreen()
        self.drawPrompt()
        self.drawBuffer()

    def clearScreen(self):
        # We only have to clear the single line after the prompt
        left = Point(0, len(self.prompt))
        right = Point(0, self.length - 3)
        draw.h_line(left, right, ' ', self.win)

    def drawPrompt(self):
        p = Point(0, 0)
        draw.string(p, self.prompt, self.win)

    def drawBuffer(self):
        buffer_size = len(self.buffer)
        temp_buffer = ""
        form_length = self.length - (len(self.prompt) + 2)
        if buffer_size >= form_length:
            temp_buffer = self.buffer[buffer_size - form_length:buffer_size]
        else:
            temp_buffer = self.buffer

        p = Point(0, len(self.prompt) + 1)
        draw.string(p, temp_buffer, self.win)

    def injectString(self, string):
        for ch in string:
            self.addCharToBuffer(ch)

    def addCharToBuffer(self, ch):
        self.buffer += ch

    def removeCharFromBuffer(self):
        self.buffer = self.buffer[:len(self.buffer) - 1]

    def edit(self):
        # Make the cursor visible while typing
        curses.curs_set(1)

        while True:
            self.render()
            ch = self.win.getch()
            if ch == 10: # Enter
                # Submit the current buffer
                curses.curs_set(0)
                return (self.trimWhitespace(self.buffer), 1)
            elif ch == curses.KEY_F1:
                # Cancel the edit
                curses.curs_set(0)
                return ("Cancelled", -1)
            elif ch == curses.KEY_RESIZE:
                # Return the resize code with the buffer as it exists
                return (self.buffer, 0)
            else:
                # Handle characters as input
                self.handleInput(ch)

    def handleInput(self, ch):
        if ch == 127: # Backspace key
            self.removeCharFromBuffer()
        else:
            ch = convert_int_to_char(ch)
            self.addCharToBuffer(ch)

    def trimWhitespace(self, string):
        return string.strip()

def convert_int_to_char(num):
    return chr(num)
