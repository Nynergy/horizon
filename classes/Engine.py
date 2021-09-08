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
        # Upon startup, default to the first player we can find
        player_choice = players[0]
        player = LMSPlayer(player_choice['name'], player_choice['playerid'])

        return player

    def constructScreens(self):
        screen_dimensions = self.getWindowDimensions()
        self.screens = [
                         screenmaker.make_screen("Playlist", screen_dimensions),
                         screenmaker.make_screen("Media Library", screen_dimensions),
                         screenmaker.make_screen("Test", screen_dimensions)
                       ]

        # We want to load the media library when the program starts
        self.reloadMediaLibrary()
        self.win.clear()
        self.win.refresh()

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

    def reloadMediaLibrary(self):
        # Tell the user we are doing work
        infobox = Infobox("Fetching Media Library...\n\nThis may take a minute", self.win)
        infobox.render()

        # Clear the old media library
        media_library_screen = self.screens[1]
        media_library_panels = media_library_screen.panels
        for panel in media_library_panels:
            panel.clearItems()
        
        # Fetch the new media library from LMS
        media_library = lmswrapper.get_media_library(self.server)
        for artist in media_library.values():
            media_library_panels[0].addItem(artist)

        media_library_screen.setCurrentPanel(0)

        paneldriver.change_media_panels(self.screens[1])

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
            elif(key == ord('j')):
                # Move current panel's highlight down 1
                panel = self.screens[0].getCurrentPanel()
                paneldriver.move_down(panel, 1)
            elif(key == ord('k')):
                # Move current panel's highlight up 1
                panel = self.screens[0].getCurrentPanel()
                paneldriver.move_up(panel, 1)
            else:
                pass # Do nothing

        """ MEDIA LIBRARY COMMANDS """
        # These commands should only work while on the Media Library screen
        if self.currentScreenIndex == 1:
            if(key == ord('r')):
                # If we hit 'r' on the Media Library screen, reload the media library
                self.reloadMediaLibrary()
            elif(key == ord('j')):
                # Move current panel's highlight down 1
                panel = self.screens[1].getCurrentPanel()
                paneldriver.move_down(panel, 1)
                paneldriver.change_media_panels(self.screens[1])
            elif(key == ord('k')):
                # Move current panel's highlight up 1
                panel = self.screens[1].getCurrentPanel()
                paneldriver.move_up(panel, 1)
                paneldriver.change_media_panels(self.screens[1])
            elif(key == ord('h')):
                # Move focused panel to the left
                self.screens[1].decrementCurrentPanel()
            elif(key == ord('l')):
                # Move focused panel to the right
                self.screens[1].incrementCurrentPanel()
            else:
                pass # Do nothing

        """ GENERIC COMMANDS """
        # These commands should be run regardless of what screen is being shown
        if(key == ord('q')):
            self.quit = True
        elif(key in TAB_NUMBERS):
            if key == ord('1'):
                # If switching to the playlist screen, reload the playlist first
                self.reloadPlaylist()
            self.changeTab(key)
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
