"""
The Engine is the heart of the application. It handles inputs, renders screens
and panels, delegates fetching from the LMS, etc.
"""

import curses
import lmsquery
import time

import lmswrapper
import paneldriver
import screenmaker
from util import Point

from classes.Music import LMSPlayer
from classes.Panel import Infobox, Playbar, Statusline
from classes.Screen import Screen

TAB_NUMBERS = [
                ord('1'), ord('2'), ord('3'),
                ord('4'), ord('5'), ord('6'),
                ord('7'), ord('8'), ord('9')
              ]

class Engine:
    def __init__(self, config, win):
        self.quit = False
        self.config = config
        self.server = lmsquery.LMSQuery(config["ServerIP"], config["ServerPort"])
        self.player = self.getPlayers()
        self.win = win
        (self.height, self.width) = self.win.getmaxyx()
        self.constructScreens()
        self.constructStatusline()
        self.constructPlaybar()

    def getPlayers(self):
        players = self.server.get_players()
        # FIXME: For now, just default to the first player we find
        player_choice = players[0]
        player = LMSPlayer(player_choice['name'], player_choice['playerid'])

        return player

    def constructScreens(self):
        screen_dimensions = self.getWindowDimensions()
        self.screens = [
                         screenmaker.make_screen("Playlist", screen_dimensions),
                         screenmaker.make_screen("Test", screen_dimensions)
                       ]
        # NOTE: As long as we start on Playlist, load it here
        self.currentScreenIndex = 0
        self.reloadPlaylist()


    def getWindowDimensions(self):
        ul = Point(0, 0)
        lr = Point(self.height, self.width)
        dimensions = (ul, lr)

        return dimensions

    def reloadPlaylist(self):
        # Tell the user we are doing work
        infobox = Infobox("Fetching Current Playlist...", self.win)
        infobox.render()

        # Clear the old playlist
        playlist_screen = self.screens[0]
        playlist_panel = playlist_screen.getCurrentPanel()
        playlist_panel.clearItems()

        # Fetch the new playlist from LMS
        current_playlist = lmswrapper.get_current_playlist(self.server, self.player)
        for song in current_playlist:
            playlist_panel.addItem(song)

    def getCurrentScreen(self):
        return self.screens[self.currentScreenIndex]

    def constructStatusline(self):
        dimensions = self.getStatuslineDimensions()
        self.statusline = Statusline(dimensions)

    def getStatuslineDimensions(self):
        ul = Point(0, 0)
        lr = Point(0, self.width)
        dimensions = (ul, lr)

        return dimensions

    def resizeStatusline(self):
        new_dimensions = self.getStatuslineDimensions()
        self.statusline.resize(new_dimensions)

    def constructPlaybar(self):
        dimensions = self.getPlaybarDimensions()
        self.playbar = Playbar(dimensions)

    def getPlaybarDimensions(self):
        ul = Point(self.height - 3, 0)
        lr = Point(self.height, self.width)
        dimensions = (ul, lr)

        return dimensions

    def resizePlaybar(self):
        new_dimensions = self.getPlaybarDimensions()
        self.playbar.resize(new_dimensions)

    def run(self):
        while(not self.quit):
            self.renderStatusline()
            self.renderCurrentScreen()
            self.renderPlaybar()
            key = self.getInput()
            self.handleInput(key)

    def renderStatusline(self):
        # Fetch status info for current player
        player_info = lmswrapper.get_player_info(self.server, self.player)
        self.statusline.render(player_info)

    def renderCurrentScreen(self):
        current_screen = self.getCurrentScreen()
        current_screen.render()

    def renderPlaybar(self):
        # Fetch info for the currently playing track
        track_info = lmswrapper.get_now_playing(self.server, self.player)
        self.playbar.render(track_info)

    def getInput(self):
        current_panel = self.getCurrentScreen().getCurrentPanel()
        # getch() on the playbar to keep it rendering properly
        key = self.playbar.win.getch()
        return key

    def handleInput(self, key):
        """ PLAYLIST COMMANDS """
        # These commands should only work while on the Playlist screen
        if self.currentScreenIndex == 0:
            if(key == ord('r')):
                # If we hit 'r' on the Playlist screen, reload the playlist
                self.reloadPlaylist()
            else:
                pass # Do nothing

        """ GENERIC COMMANDS """
        # These commands should be run regardless of what screen is being shown
        if(key == ord('q')):
            self.quit = True
        elif(key in TAB_NUMBERS):
            # If switching to the playlist screen, reload the playlist first
            if key == ord('1'):
                self.reloadPlaylist()
            self.changeTab(key)
        elif(key == ord('j')):
            # Move current panel's highlight down 1
            panel = self.getCurrentScreen().getCurrentPanel()
            paneldriver.move_down(panel, 1)
        elif(key == ord('k')):
            # Move current panel's highlight up 1
            panel = self.getCurrentScreen().getCurrentPanel()
            paneldriver.move_up(panel, 1)
        elif(key == curses.KEY_RESIZE):
            # Begin a cascading call to resize all screens/panels/windows/etc
            # First, reset the Engine's internal sizes
            (self.height, self.width) = self.win.getmaxyx()
            # Next, resize each Screen with the screenmaker
            screen_dimensions = self.getWindowDimensions()
            for screen in self.screens:
                screenmaker.resize_screen(screen, screen_dimensions)
            # Next, resize the Playbar and Statusline
            self.resizePlaybar()
            self.resizeStatusline()
        else:
            pass # Do nothing

    def changeTab(self, key):
        tab_index = int(chr(key)) - 1
        if(tab_index < len(self.screens)):
            self.currentScreenIndex = tab_index
