"""
Boxes are like panels that take up smaller portions of the screen, and are
typically rendered over top of the actual screen panels. These take the form of
message boxes, prompts, lists, forms, etc.
"""

import curses

import draw
from util import Point

from classes.Form import Form
from classes.Panel import Panel

"""
An Infobox is a little popup on the screen that just delivers some info, such
as "Fetching Albums..." or "Loading Playlist...".
"""

BORDER_PADDING = 2
INNER_PADDING = 2
OUTER_PADDING = 2
FULL_PADDING = BORDER_PADDING + INNER_PADDING + OUTER_PADDING

class Infobox(Panel):
    def __init__(self, message, win, title=""):
        infobox_dimensions = self.generateDimensions(message, win)
        super().__init__(infobox_dimensions, title)

    def generateDimensions(self, message, win):
        (max_y, max_x) = win.getmaxyx()

        # Determine how many lines the message will be split across
        strings = message.split('\n')
        lines = []
        for s in strings:
            if(len(s) >= max_x - FULL_PADDING):
                # TODO: wrapAtLength is currently unimplemented
                wrapped_lines = self.wrapAtLength(s, max_x - FULL_PADDING)
                for w in wrapped_lines:
                    lines.append(w)
            else:
                lines.append(s)
        num_lines = len(lines)
        self.lines = lines

        # Determine how wide the box needs to be
        longest_string_length = 0
        for l in lines:
            if len(l) > longest_string_length:
                longest_string_length = len(l)

        # Determine the dimensions of the box and return them
        y = ((max_y // 2) - (num_lines // 2))
        x = ((max_x // 2) - (longest_string_length // 2))
        width = longest_string_length + (OUTER_PADDING + BORDER_PADDING)
        height = num_lines + (OUTER_PADDING + BORDER_PADDING)

        ul = Point(y, x)
        lr = Point(y + height, x + width)
        dimensions = (ul, lr)

        return dimensions

    def render(self):
        self.drawBorder()
        self.drawMessage()
        self.win.refresh()

    def drawBorder(self):
        self.win.box()

    def drawMessage(self):
        self.win.attron(curses.A_BOLD)
        counter = 0
        for line in self.lines:
            line_y = counter + (BORDER_PADDING + INNER_PADDING) // 2
            line_x = (self.width // 2) - (len(line) // 2)
            line_point = Point(line_y, line_x)
            draw.string(line_point, line, self.win)
            counter += 1
        self.win.attroff(curses.A_BOLD)

"""
A Prompt is a special kind of Infobox that, when rendered, asks the user for a
yes or no confirmation.
"""

class Prompt(Infobox):
    def __init__(self, message, win, title=""):
        self.prompt_string = "(y)es :: (n)o"
        super().__init__(message, win, title)

    def generateDimensions(self, message, win):
        (max_y, max_x) = win.getmaxyx()

        # Determine how many lines the message will be split across
        strings = message.split('\n')
        lines = []
        for s in strings:
            if(len(s) >= max_x - FULL_PADDING):
                # TODO: wrapAtLength is currently unimplemented
                wrapped_lines = self.wrapAtLength(s, max_x - FULL_PADDING)
                for w in wrapped_lines:
                    lines.append(w)
            else:
                lines.append(s)
        # NOTE: We add 2 to account for the yes/no prompt
        num_lines = len(lines) + 2
        self.lines = lines

        # Determine how wide the box needs to be
        longest_string_length = 0
        for l in lines:
            if len(l) > longest_string_length:
                longest_string_length = len(l)
        # In case the message is shorter than the prompt
        longest_string_length = max(longest_string_length, len(self.prompt_string))

        # Determine the dimensions of the box and return them
        y = ((max_y // 2) - (num_lines // 2))
        x = ((max_x // 2) - (longest_string_length // 2))
        width = longest_string_length + (OUTER_PADDING + BORDER_PADDING)
        height = num_lines + (OUTER_PADDING + BORDER_PADDING)

        ul = Point(y, x)
        lr = Point(y + height, x + width)
        dimensions = (ul, lr)

        return dimensions

    def drawMessage(self):
        self.win.attron(curses.A_BOLD)
        counter = 0
        for line in self.lines:
            line_y = counter + (BORDER_PADDING + INNER_PADDING) // 2
            line_x = (self.width // 2) - (len(line) // 2)
            line_point = Point(line_y, line_x)
            draw.string(line_point, line, self.win)
            counter += 1

        # Draw prompt as well
        counter += 1
        line = self.prompt_string
        line_y = counter + (BORDER_PADDING + INNER_PADDING) // 2
        line_x = (self.width // 2) - (len(line) // 2)
        line_point = Point(line_y, line_x)
        draw.string(line_point, line, self.win)
        self.win.attroff(curses.A_BOLD)

    def getConfirmation(self):
        self.render()
        key = None
        while(key not in [ord('y'), ord('Y'), ord('n'), ord('N')]):
            key = self.win.getch()
            if key == curses.KEY_RESIZE:
                # Tell the Engine to resize everything and then re-render this prompt
                return "RESIZE"
            elif key in [ord('y'), ord('Y')]:
                return True
            elif key in [ord('n'), ord('N')]:
                return False

"""
A Listbox is a special type of Infobox that takes a list of items and presents
them to the user. The user then usesa letter to choose from the list.
"""

class Listbox(Infobox):
    def __init__(self, message, items, win, title=""):
        self.items = items
        super().__init__(message, win, title)

    def generateDimensions(self, message, win):
        (max_y, max_x) = win.getmaxyx()

        # Determine how many lines the message will be split across
        self.message_strings = message.split('\n')
        item_strings = []
        for item in self.items:
            item_strings.append(repr(item))
        self.lines = self.message_strings + [" "] + item_strings
        num_lines = len(self.lines)

        # Determine how wide the box needs to be
        longest_string_length = 0
        for l in self.lines:
            if len(l) > longest_string_length:
                longest_string_length = len(l)

        # Determine the dimensions of the box and return them
        y = 0
        x = 0
        width = longest_string_length + (OUTER_PADDING + BORDER_PADDING)
        height = num_lines + (OUTER_PADDING + BORDER_PADDING)

        ul = Point(y, x)
        lr = Point(y + height, x + width)
        dimensions = (ul, lr)

        return dimensions

    def drawMessage(self):
        self.win.attron(curses.A_BOLD)
        counter = 0
        self.choices = []
        choice = 'a'
        for line in self.lines:
            if counter > len(self.message_strings):
                self.choices.append(choice)
                line = f"({choice}) {line}"
                choice = chr(ord(choice) + 1)
            line_y = counter + (BORDER_PADDING + INNER_PADDING) // 2
            line_x = (self.width // 2) - (len(line) // 2)
            line_point = Point(line_y, line_x)
            draw.string(line_point, line, self.win)
            counter += 1
        self.win.attroff(curses.A_BOLD)

    def getChoice(self):
        self.render()
        key = self.win.getkey()
        if key == curses.KEY_RESIZE:
            # Tell the Engine to resize everything and then re-render this prompt
            return "RESIZE"
        elif key in self.choices:
            choice = self.choices.index(key)
            return self.items[choice]

        return None

"""
An Editbox is a special kind of prompt that has an embedded form field for the
user to input a string.
"""

class Editbox(Infobox):
    def __init__(self, message, prompt, win, title=""):
        super().__init__(message, win, title)
        self.message = message
        self.constructForm(prompt)

    def generateDimensions(self, message, win):
        (max_y, max_x) = win.getmaxyx()

        # Determine the dimensions of the box and return them
        y = ((max_y // 2) - 2)
        x = max_x // 4
        width = (max_x // 2) + (OUTER_PADDING + BORDER_PADDING)
        height = 4 + (OUTER_PADDING + BORDER_PADDING)

        ul = Point(y, x)
        lr = Point(y + height, x + width)
        dimensions = (ul, lr)

        return dimensions

    def constructForm(self, prompt):
        # Origin is in reference to stdscr, so we need to offset it with our x, y
        y_offset = self.y
        x_offset = self.x
        y = self.height - (FULL_PADDING // 2)
        x = FULL_PADDING // 2
        origin = Point(y + y_offset, x + x_offset)
        self.form = Form(origin, self.width - FULL_PADDING, prompt)

    def getInput(self):
        self.drawBorder()
        self.drawMessage()
        self.drawQuitCommand()
        self.win.refresh()
        
        (user_input, ret_code) = self.form.edit()

        return (user_input, ret_code)

    def drawMessage(self):
        self.win.attron(curses.A_BOLD)
        y = (BORDER_PADDING + INNER_PADDING) // 2
        x = (self.width // 2) - (len(self.message) // 2)
        p = Point(y, x)
        draw.string(p, self.message, self.win)
        self.win.attroff(curses.A_BOLD)

    def drawQuitCommand(self):
        quit_command = "Press F1 to Cancel"

        self.win.attron(curses.A_BOLD)
        y = self.height - 1
        x = (self.width // 2) - (len(quit_command) // 2)
        p = Point(y, x)
        draw.string(p, quit_command, self.win)
        self.win.attroff(curses.A_BOLD)

    def injectString(self, string):
        self.form.injectString(string)
