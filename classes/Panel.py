"""
This is where we keep all our Panel classes/subclasses.
"""

import curses
import unicodedata

import draw
from util import Mode, Point, get_color_pair

"""
A Panel is a container for an arbitrary set of information. Since this will
serve as the "abstract" baseclass, it has no idea how to render itself, though
it does have some basic draw functions that subclasses will call on if they
don't implement their own.
"""

class Panel:
    def __init__(self, panel_dimensions, title=""):
        self.constructPanelWindow(panel_dimensions)
        self.title = title

    def constructPanelWindow(self, panel_dimensions):
        (ul, lr) = panel_dimensions
        self.y = ul.y
        self.x = ul.x
        self.width = lr.x - ul.x
        self.height = lr.y - ul.y
        self.win = curses.newwin(self.height, self.width, self.y, self.x)

    def clearScreen(self):
        # Fill each cell with the empty character
        for i in range(self.height - 1):
            for j in range(self.width):
                p = Point(i, j)
                draw.char(p, " ", self.win)

    def drawTitleLine(self):
        ul = Point(0, 0)
        lr = Point(0, self.width - 1)
        self.drawTeeLine(ul, lr)

    def drawBottomLine(self):
        ul = Point(self.height - 2, 0)
        lr = Point(self.height - 2, self.width - 1)
        self.drawTeeLine(ul, lr)

    def drawTeeLine(self, left, right):
        # Horizontal line with tees on the ends
        self.win.attron(curses.A_ALTCHARSET)
        draw.h_line(left, right, curses.ACS_HLINE, self.win)
        draw.char(left, curses.ACS_LTEE, self.win)
        draw.char(right, curses.ACS_RTEE, self.win)
        self.win.attroff(curses.A_ALTCHARSET)

    def drawTitle(self):
        title_x = (self.width // 2) - (len(self.title) // 2)

        # First blank the area around the title
        ul = Point(0, title_x - 1)
        lr = Point(0, title_x + len(self.title))
        draw.h_line(ul, lr, " ", self.win)

        # Then draw the title string itself
        self.win.attron(curses.A_BOLD)
        draw.string(Point(0, title_x), self.title, self.win)
        self.win.attroff(curses.A_BOLD)

    def resize(self, new_dimensions):
        self.constructPanelWindow(new_dimensions)

"""
A DummyPanel is a test panel that just renders a basic Panel with no data.
"""

class DummyPanel(Panel):
    def __init__(self, panel_dimensions, title=""):
        super().__init__(panel_dimensions, title)

    def render(self):
        self.clearScreen()
        self.drawTitleLine()
        self.drawTitle()
        self.drawBottomLine()
        self.win.refresh()

"""
The Playbar is the constant panel of information about the currently playing
track, including title, artist, album, duration, elapsed time, etc.

This panel exists beneath every screen.
"""

INPUT_TIMEOUT = 750

class Playbar(Panel):
    def __init__(self, playbar_dimensions, title=""):
        super().__init__(playbar_dimensions, title)
        """
        This one is important: Make this window non-blocking so getch doesn't
        keep it from rendering, _but_ we also don't want it to be completely
        non-blocking because then the CPU tries to kill itself. Instead, we opt
        for a modest timeout of a fraction of a second.
        """
        self.win.timeout(INPUT_TIMEOUT)

    def render(self, track_info):
        self.clearScreen()
        if track_info != {}:
            self.drawProgressBar(track_info['duration'], track_info['elapsed_time'])
        self.drawBottomLine()
        if track_info != {}:
            self.drawTrackInfo(track_info)
        self.win.refresh()

    def clearScreen(self):
        # Fill each cell with the empty character
        for i in range(self.height):
            for j in range(self.width - 1):
                p = Point(i, j)
                draw.char(p, " ", self.win)

    def drawProgressBar(self, total_time, elapsed_time):
        percentage = elapsed_time / max(1, total_time)
        full_width = self.width - 2
        num_blocks = min(full_width, round(full_width * percentage))
        num_spaces = full_width - (num_blocks + 1) # Leave room for playhead

        attr = curses.A_ALTCHARSET | get_color_pair("Playbar")
        self.win.attron(attr)

        # Draw blocks
        for i in range(num_blocks):
            p = Point(0, i + 1)
            draw.char(p, curses.ACS_CKBOARD, self.win)

        # Draw playhead
        p = Point(0, min(full_width + 1, num_blocks))
        draw.char(p, curses.ACS_CKBOARD, self.win)

        # Draw spaces
        for i in range(num_spaces):
            p = Point(0, min(full_width + 1, num_blocks + i))
            draw.char(p, " ", self.win)

        self.win.attroff(attr)

    def drawTrackInfo(self, track_info):
        leader = "Now Playing: "
        title = track_info['title']
        artist = track_info['artist']
        album = track_info['album']
        year = track_info['year']
        total_time = convert_to_time(track_info['duration'])
        elapsed_time = convert_to_time(track_info['elapsed_time'])

        # Draw leader
        self.win.attron(curses.A_BOLD)
        leader_point = Point(self.height - 1, 0)
        draw.string(leader_point, leader, self.win)
        self.win.attroff(curses.A_BOLD)

        # Draw time info
        time_string = f"({elapsed_time}/{total_time})"
        time_point = Point(self.height - 1, self.width - (len(time_string) + 1))
        draw.string(time_point, time_string, self.win)

        # Draw track info
        # This gets truncated if it is too long
        info_string = f"{title} - {artist} - {album} ({year})"
        if len(info_string) >= self.width - (len(leader) + len(time_string) + 2):
            info_string = info_string[:self.width - (len(leader) + len(time_string) + 5)]
            info_string += "..."
        info_point = Point(self.height - 1, len(leader))
        draw.string(info_point, info_string, self.win)

    def resize(self, new_dimensions):
        self.constructPanelWindow(new_dimensions)
        # Don't forget to re-enable the non-blocking call!
        self.win.timeout(INPUT_TIMEOUT)

def convert_to_time(time):
    time = round(time)
    seconds = time % 60
    minutes = (time - seconds) // 60

    return f"{minutes}:{seconds:02d}"

"""
The Statusline is the line at the top of the screen that constantly displays
info about the player currently connected to. For example, it will show the
user its name, powered status, volume, etc.
"""

VOLUME_BLOCKS = 20

class Statusline(Panel):
    def __init__(self, statusline_dimensions, title=""):
        super().__init__(statusline_dimensions, title)

    def render(self, player_info, engine_mode):
        self.clearScreen()
        self.drawPlayerInfo(player_info)
        self.drawModeIndicator(engine_mode)
        self.win.refresh()

    def clearScreen(self):
        # Fill each cell with the empty character
        left = Point(0, 0)
        right = Point(0, self.width - 1)
        draw.h_line(left, right, " ", self.win)

    def drawPlayerInfo(self, player_info):
        """
        Things I'm interested in:
        - player_name
        - power (is the player powered on?)
        - rescan status (is the server rescanning?)
        *These next ones only return if the player is powered*
        - mixer_volume (render a volume bar)
        - mode (play, pause, etc)
        - playlist_repeat (is it set to repeat?)
        - playlist_shuffle (is it set to shuffle?)
        - playlist_tracks (number of tracks in the playlist)
        """
        player_name = player_info['player_name']
        power_state = translate_power(player_info['power'])

        # Draw name and power state
        self.status_string = ""

        self.win.attron(curses.A_BOLD)
        self.drawStatusPiece("Connected:")
        self.win.attroff(curses.A_BOLD)
        self.drawStatusPiece(player_name)

        self.drawStatusPiece('-')

        self.win.attron(curses.A_BOLD)
        self.drawStatusPiece("Power:")
        self.win.attroff(curses.A_BOLD)
        self.drawStatusPiece(power_state)

        if player_info['scan_status']:
            # Server is rescanning, render it next to power state
            self.drawStatusPiece('-')

            self.win.attron(curses.A_BOLD)
            self.drawStatusPiece("RESCANNING...")
            self.win.attroff(curses.A_BOLD)

        if power_state == "ON":
            mixer_volume = player_info['mixer volume']
            playback_mode = player_info['mode']
            playlist_repeat = translate_repeat(player_info['playlist repeat'])
            playlist_shuffle = translate_shuffle(player_info['playlist shuffle'])
            playlist_tracks = player_info['playlist_tracks']

            # Draw the rest of the info right to left
            # TODO: Add dividers where necessary
            self.playback_string = ""

            repshuf_string = "[" + playlist_repeat + playlist_shuffle + "]"
            self.drawPlaybackPiece(repshuf_string)

            (volume_fill_string, volume_head_string, volume_empty_string) = get_volume_strings(mixer_volume)
            self.drawPlaybackPiece(volume_empty_string)
            self.playback_string = self.playback_string.rstrip()
            self.drawPlaybackPiece(volume_head_string)
            self.playback_string = self.playback_string.rstrip()
            self.win.attron(get_color_pair("VolumeFill"))
            self.drawPlaybackPiece(volume_fill_string)
            self.win.attroff(get_color_pair("VolumeFill"))
            self.win.attron(curses.A_BOLD)
            self.drawPlaybackPiece("Volume:")
            self.win.attroff(curses.A_BOLD)

            self.drawPlaybackPiece('-')

            tracks_string = f"({playlist_tracks} Tracks)"
            self.drawPlaybackPiece(tracks_string)

            self.drawPlaybackPiece('-')

            mode_string = translate_mode(playback_mode)
            self.win.attron(curses.A_BOLD)
            self.drawPlaybackPiece(mode_string)
            self.win.attroff(curses.A_BOLD)

    def drawStatusPiece(self, info):
        p = Point(0, len(self.status_string))
        draw.string(p, info, self.win)
        self.status_string += info + " "

    def drawPlaybackPiece(self, info):
        p = Point(0, self.width - (len(info) + len(self.playback_string)))
        draw.string(p, info, self.win)
        self.playback_string = info + self.playback_string + " "

    def drawModeIndicator(self, engine_mode):
        if engine_mode == Mode.NORMAL:
            return
        elif engine_mode == Mode.MOVE:
            mode_string = " * MOVE MODE * "
        elif engine_mode == Mode.DELETE:
            mode_string = " * DELETE MODE * "

        y = 0
        x = (self.width // 2) - (len(mode_string) // 2)
        p = Point(y, x)
        attr = curses.A_REVERSE | curses.A_BOLD
        self.win.attron(attr)
        draw.string(p, mode_string, self.win)
        self.win.attroff(attr)

def translate_power(state):
    if state == 0:
        return "OFF"
    elif state == 1:
        return "ON"
    else:
        raise ValueError(state)

def translate_repeat(state):
    if state == 0:
        return '-'
    elif state == 1:
        return 'r'
    elif state == 2:
        return 'R'
    else:
        raise ValueError(state)

def translate_shuffle(state):
    if state == 0:
        return '-'
    elif state == 1:
        return 'z'
    elif state == 2:
        return 'Z'
    else:
        raise ValueError(state)

def get_volume_strings(volume):
    # Check if player is muted (mixer volume is negative)
    if volume < 0:
        line_char = '#'
        head_char = '#'
    else:
        line_char = '-'
        head_char = '|'

    percentage = volume / 100
    num_fill = max(1, round(abs(VOLUME_BLOCKS * percentage)))
    num_empty = VOLUME_BLOCKS - num_fill

    fill_string = line_char * (num_fill - 1)
    empty_string = line_char * num_empty

    return (fill_string, head_char, empty_string)

def translate_mode(mode):
    if mode == 'play':
        return "PLAYING"
    elif mode == 'pause':
        return "PAUSED"
    elif mode == 'stop':
        return "STOPPED"
    else:
        raise ValueError(mode)

"""
A ListPanel is a panel that specifically contains some list of information, and
will display/interact with that list via the user's commands.
"""

class ListPanel(Panel):
    def __init__(self, panel_dimensions, title=""):
        super().__init__(panel_dimensions, title)
        self.items = []
        self.f_item = 0
        self.l_item = min(len(self.items), self.height - 1)
        self.curr_item = 0
        self.focused = False

    def render(self):
        self.clearScreen()
        self.drawTitleLine()
        self.drawTitle()
        self.drawItems()
        self.clearSides()
        self.drawIndicators()
        self.drawBottomLine()
        self.win.refresh()

    def drawItems(self):
        # Translate any non-strings into strings
        strings = []
        for item in self.items:
            strings.append(repr(item))

        # Draw items within moving frame
        attr = 0
        counter = 0
        bound = min(self.l_item, len(self.items))
        for i in range(self.f_item, bound):
            # Specify applicable attributes
            if(counter + self.f_item == self.curr_item):
                attr = (attr | curses.A_REVERSE)
                if self.focused:
                    attr = (attr | get_color_pair("Accent"))
            item = strings[i][:self.width - 2] # Truncate strings longer than panel width
            fill_spaces = (self.width - calc_string_width(item)) - 2
            itemline = str(item) + (" " * fill_spaces)
            item_point = Point(counter + 1, 1)
            self.win.attron(attr)
            draw.string(item_point, itemline, self.win)
            self.win.attroff(attr)
            counter += 1
            attr = 0

    def drawIndicators(self):
        if(self.f_item > 0):
            self.drawUpperIndicators()

        if(self.l_item < len(self.items)):
            self.drawLowerIndicators()

    def drawUpperIndicators(self):
        left = Point(1, 0)
        right = Point(1, self.width - 1)

        self.win.attron(curses.A_ALTCHARSET)
        draw.char(left, curses.ACS_UARROW, self.win)
        draw.char(right, curses.ACS_UARROW, self.win)
        self.win.attroff(curses.A_ALTCHARSET)

    def drawLowerIndicators(self):
        left = Point(self.height - 3, 0)
        right = Point(self.height - 3, self.width - 1)

        self.win.attron(curses.A_ALTCHARSET)
        draw.char(left, curses.ACS_DARROW, self.win)
        draw.char(right, curses.ACS_DARROW, self.win)
        self.win.attroff(curses.A_ALTCHARSET)

    def clearSides(self):
        # Clear any mis-rendered item artifacts off the sides of the panel
        left_ul = Point(1, 0)
        left_lr = Point(self.height - 3, 0)
        draw.v_line(left_ul, left_lr, ' ', self.win)

        right_ul = Point(1, self.width - 1)
        right_lr = Point(self.height - 3, self.width - 1)
        draw.v_line(right_ul, right_lr, ' ', self.win)

    def getCurrentItemIndex(self):
        return self.curr_item

    def getCurrentItem(self):
        return self.items[self.curr_item]

    def setItems(self, new_items):
        self.items = new_items
        self.resetMovingFrame()

    def addItem(self, item):
        self.items.append(item)
        self.resetMovingFrame()

    def clearItems(self):
        self.items = []
        self.resetMovingFrame()

    def resize(self, new_dimensions):
        self.constructPanelWindow(new_dimensions)
        self.resetMovingFrame()

    def resetMovingFrame(self):
        self.curr_item = min(self.curr_item, self.height - 3, max(0, len(self.items) - 1))
        if len(self.items) < self.height - 1:
            self.f_item = 0
        self.l_item = min(len(self.items), self.f_item + (self.height - 3))

    def focus(self):
        self.focused = True

    def unfocus(self):
        self.focused = False

def calc_string_width(text):
    fake_length = len(text.replace(u'???', u"'").encode('utf-8'))
    num_wide = sum(unicodedata.east_asian_width(c) in 'WF' for c in text)
    return fake_length - num_wide

"""
The PlaylistPanel is the main panel of the Playlist screen, and shows
information about the tracks in the current playlist (a.k.a the now-playing
queue).

This panel is also used to show the user their saved playlists.
"""

PLAYLIST_TOP_BAR_HEIGHT = 1
PLAYLIST_HEADERS_HEIGHT = 2

class PlaylistPanel(ListPanel):
    def __init__(self, panel_dimensions, title=""):
        super().__init__(panel_dimensions, title)
        self.l_item = min(len(self.items), self.height - (PLAYLIST_HEADERS_HEIGHT + 3))
        self.constructColumnWidths()
        self.moveStart = -1
        self.markedItems = []

    def constructColumnWidths(self):
        # Column names:      Title,  Album, Track,   Artist, Year
        # Relative lengths:  Longest Second Smallest Third   Fourth
        # Relative %:        31%     31%    2%       31%     4%
        self.columnWidths = {}

        # Calculate how many cells wide each column needs to be
        title_x = round(self.width * 0.31)
        album_x = round(self.width * 0.31)
        track_x = max(7, round(self.width * 0.02))
        artist_x = round(self.width * 0.31)
        year_x = max(4, round(self.width * 0.04))

        self.columnWidths['title'] = title_x
        self.columnWidths['album'] = album_x
        self.columnWidths['track'] = track_x
        self.columnWidths['artist'] = artist_x
        self.columnWidths['year'] = year_x

    def render(self):
        self.clearScreen()
        self.drawTitleLine()
        self.drawTitle()
        self.drawColumnHeaders()
        self.drawHeadersUnderline()
        self.drawItems()
        self.clearSides()
        self.drawIndicators()
        self.drawBottomLine()
        self.win.refresh()

    def drawColumnHeaders(self):
        # Since headers aren't reversed, we don't need to worry about padding with spaces
        self.win.attron(curses.A_BOLD)

        # Title
        p = Point(PLAYLIST_TOP_BAR_HEIGHT, 1)
        draw.string(p, "Title", self.win)

        # Album
        p = Point(PLAYLIST_TOP_BAR_HEIGHT, p.x + self.columnWidths['title'])
        draw.string(p, "Album", self.win)

        # Tracknum
        p = Point(PLAYLIST_TOP_BAR_HEIGHT, p.x + self.columnWidths['album'])
        draw.string(p, "Track", self.win)

        # Artist
        p = Point(PLAYLIST_TOP_BAR_HEIGHT, p.x + self.columnWidths['track'])
        draw.string(p, "Artist", self.win)

        # Year
        p = Point(PLAYLIST_TOP_BAR_HEIGHT, self.width - 5)
        draw.string(p, "Year", self.win)

        self.win.attroff(curses.A_BOLD)

    def drawHeadersUnderline(self):
        ul = Point(PLAYLIST_HEADERS_HEIGHT, 0)
        lr = Point(PLAYLIST_HEADERS_HEIGHT, self.width - 1)

        # Horizontal line with tees on the ends
        self.win.attron(curses.A_ALTCHARSET)
        draw.h_line(ul, lr, curses.ACS_HLINE, self.win)
        draw.char(ul, curses.ACS_LTEE, self.win)
        draw.char(lr, curses.ACS_RTEE, self.win)
        self.win.attroff(curses.A_ALTCHARSET)

    def drawItems(self):
        # Draw items within moving frame
        attr = 0
        counter = 0
        bound = min(self.l_item, len(self.items))
        for i in range(self.f_item, bound):
            # Specify applicable attributes
            if(counter + self.f_item == self.curr_item):
                attr = (attr | curses.A_REVERSE)
            item = self.items[i]
            item_y = counter + PLAYLIST_HEADERS_HEIGHT + PLAYLIST_TOP_BAR_HEIGHT
            self.win.attron(attr)
            self.drawItem(item, item_y)
            self.win.attroff(attr)
            counter += 1
            attr = 0

    def drawItem(self, item, item_y):
        # Get our column values from the song object, truncating when necessary
        title = item.title[:self.columnWidths['title']]
        album = item.album_title[:self.columnWidths['album']]
        track = str(item.tracknum)[:self.columnWidths['track']]
        artist = item.artist[:self.columnWidths['artist']]
        year = str(item.year)[:self.columnWidths['year']]

        # Fill spaces for each value, based on the width of the column
        # Keep track of the string so far, to compare length
        self.song_string = " "
        absolute_offset = item_y - (PLAYLIST_HEADERS_HEIGHT + PLAYLIST_TOP_BAR_HEIGHT) + self.f_item

        attr = get_color_pair("PlaylistSongTitle")
        if absolute_offset == self.moveStart or absolute_offset in self.markedItems:
            attr = curses.A_BOLD | curses.A_REVERSE
        self.win.attron(attr)
        self.drawColumn('title', title, item_y)
        self.win.attroff(attr)

        attr = get_color_pair("PlaylistSongAlbum")
        if absolute_offset == self.moveStart or absolute_offset in self.markedItems:
            attr = curses.A_BOLD | curses.A_REVERSE
        self.win.attron(attr)
        self.drawColumn('album', album, item_y)
        self.win.attroff(attr)

        attr = get_color_pair("PlaylistSongTracknum")
        if absolute_offset == self.moveStart or absolute_offset in self.markedItems:
            attr = curses.A_BOLD | curses.A_REVERSE
        self.win.attron(attr)
        self.drawColumn('track', track, item_y)
        self.win.attroff(attr)

        attr = get_color_pair("PlaylistSongArtist")
        if absolute_offset == self.moveStart or absolute_offset in self.markedItems:
            attr = curses.A_BOLD | curses.A_REVERSE
        self.win.attron(attr)
        self.drawColumn('artist', artist, item_y)
        self.win.attroff(attr)

        attr = get_color_pair("PlaylistSongYear")
        if absolute_offset == self.moveStart or absolute_offset in self.markedItems:
            attr = curses.A_BOLD | curses.A_REVERSE
        self.win.attron(attr)
        p = Point(item_y, self.width - 5)
        draw.string(p, year, self.win)
        self.win.attroff(attr)

    def drawColumn(self, name, value, v_offset):
        fill_spaces = (self.columnWidths[name] - len(value))
        line = value + (" " * fill_spaces)
        while len(line) >= self.width - len(self.song_string):
            line = line.rstrip()
        while name == 'artist' and len(line) < (self.width - 1) - len(self.song_string):
            line += " "
        p = Point(v_offset, len(self.song_string))
        draw.string(p, line, self.win)
        self.song_string += line

    def drawUpperIndicators(self):
        left = Point(PLAYLIST_TOP_BAR_HEIGHT + PLAYLIST_HEADERS_HEIGHT, 0)
        right = Point(PLAYLIST_TOP_BAR_HEIGHT + PLAYLIST_HEADERS_HEIGHT, self.width - 1)

        self.win.attron(curses.A_ALTCHARSET)
        draw.char(left, curses.ACS_UARROW, self.win)
        draw.char(right, curses.ACS_UARROW, self.win)
        self.win.attroff(curses.A_ALTCHARSET)

    def drawLowerIndicators(self):
        left = Point(self.height - 3, 0)
        right = Point(self.height - 3, self.width - 1)

        self.win.attron(curses.A_ALTCHARSET)
        draw.char(left, curses.ACS_DARROW, self.win)
        draw.char(right, curses.ACS_DARROW, self.win)
        self.win.attroff(curses.A_ALTCHARSET)

    def clearSides(self):
        # Clear any mis-rendered item artifacts off the sides of the panel
        left_ul = Point(PLAYLIST_TOP_BAR_HEIGHT + PLAYLIST_HEADERS_HEIGHT, 0)
        left_lr = Point(self.height - 3, 0)
        draw.v_line(left_ul, left_lr, ' ', self.win)

        right_ul = Point(PLAYLIST_TOP_BAR_HEIGHT + PLAYLIST_HEADERS_HEIGHT, self.width - 1)
        right_lr = Point(self.height - 3, self.width - 1)
        draw.v_line(right_ul, right_lr, ' ', self.win)

    def resize(self, newDimensions):
        self.constructPanelWindow(newDimensions)
        self.constructColumnWidths()
        self.resetMovingFrame()

    def addItem(self, item):
        self.items.append(item)
        self.resetMovingFrame()

    def clearItems(self):
        self.items = []
        self.resetMovingFrame()

    def resetMovingFrame(self):
        self.curr_item = min(self.curr_item, self.height - (PLAYLIST_HEADERS_HEIGHT + 3),
                             max(0, len(self.items) - 1))
        if len(self.items) < self.height - (PLAYLIST_HEADERS_HEIGHT + 3):
            self.f_item = 0
        self.l_item = min(len(self.items), self.f_item + (self.height - (PLAYLIST_HEADERS_HEIGHT + 3)))

    def setMoveStart(self):
        self.moveStart = self.curr_item

    def getMoveIndices(self):
        move_start = self.moveStart
        self.moveStart = -1
        move_end = self.curr_item
        
        return (move_start, move_end)

    def markItem(self):
        if self.curr_item not in self.markedItems:
            self.markedItems.append(self.curr_item)
        else:
            self.markedItems.remove(self.curr_item)

    def getMarkedItems(self):
        marked = self.markedItems
        self.markedItems = []

        return marked
