"""
The Engine is the heart of the application. It handles inputs, renders screens
and panels, delegates fetching from the LMS, etc.
"""

import lmsquery

import inputhandler
import lmswrapper
import paneldriver
import screenmaker
from util import Mode, Point

from classes.Box import Infobox
from classes.Music import LMSPlayer
from classes.Panel import Playbar, Statusline
from classes.Screen import Screen

class Engine:
    def __init__(self, config, win):
        self.quit = False
        self.config = config
        self.server = lmsquery.LMSQuery(config["ServerIP"], config["ServerPort"])
        self.player = self.getPlayers()
        self.win = win
        (self.height, self.width) = self.win.getmaxyx()
        self.mode = Mode.NORMAL # Start in normal mode
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
                         screenmaker.make_screen("Saved Playlists", screen_dimensions),
                         screenmaker.make_screen("Test", screen_dimensions)
                       ]

        # We want to load the media library when the program starts
        self.reloadMediaLibrary()
        self.win.clear()
        self.win.refresh()

        # We want to load the user's saved playlists as well
        self.reloadSavedPlaylists()
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
        infobox = Infobox("Fetching Media Library...", self.win)
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

    def reloadSavedPlaylists(self):
        # Tell the user we are doing work
        infobox = Infobox("Fetching Saved Playlists...", self.win)
        infobox.render()

        # Clear the old list of saved playlists
        saved_playlists_screen = self.screens[2]
        saved_playlists_panels = saved_playlists_screen.panels
        for panel in saved_playlists_panels:
            panel.clearItems()

        # Fetch the new saved playlists from LMS
        saved_playlists = lmswrapper.get_saved_playlists(self.server)
        for playlist in saved_playlists:
            saved_playlists_panels[0].addItem(playlist)

        saved_playlists_screen.setCurrentPanel(0)

        paneldriver.change_saved_playlist_panel(self.screens[2])

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
            self.renderAll()
            key = self.getInput()
            self.handleInput(key)

    def renderAll(self):
        self.renderStatusline()
        self.renderCurrentScreen()
        self.renderPlaybar()

    def renderStatusline(self):
        # Fetch status info for current player
        player_info = lmswrapper.get_player_info(self.server, self.player)
        # Statusline needs player info, as well as our current mode
        self.statusline.render(player_info, self.mode)

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
        if self.mode == Mode.NORMAL:
            """ PLAYLIST COMMANDS """
            if self.currentScreenIndex == 0:
                inputhandler.handle_playlist_commands(self, key)

            """ MEDIA LIBRARY COMMANDS """
            if self.currentScreenIndex == 1:
                inputhandler.handle_media_library_commands(self, key)

            """ SAVED PLAYLISTS COMMANDS """
            if self.currentScreenIndex == 2:
                inputhandler.handle_saved_playlist_commands(self, key)

            """ GENERIC COMMANDS """
            inputhandler.handle_generic_commands(self, key)
        elif self.mode == Mode.MOVE:
            """ MOVE MODE COMMANDS """
            inputhandler.handle_move_mode_commands(self, key)
        elif self.mode == Mode.DELETE:
            """ DELETE MODE COMMANDS """
            inputhandler.handle_delete_mode_commands(self, key)

    def resizeAll(self):
        # First, reset the Engine's internal sizes
        (self.height, self.width) = self.win.getmaxyx()
        # Next, resize each Screen with the screenmaker
        screen_dimensions = self.getWindowDimensions()
        for screen in self.screens:
            screenmaker.resize_screen(screen, screen_dimensions)
        # Next, resize the Playbar and Statusline
        self.resizePlaybar()
        self.resizeStatusline()

        self.renderAll()

    def changeTab(self, key):
        tab_index = int(chr(key)) - 1
        if(tab_index < len(self.screens)):
            self.currentScreenIndex = tab_index
