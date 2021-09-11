"""
This module houses all the input handling that the Engine performs.
"""

import curses

import lmswrapper
import paneldriver
from util import Mode

from classes.Box import Editbox, Infobox, Listbox, Prompt
from classes.Music import LMSPlayer
from classes.Panel import PlaylistPanel

TAB_NUMBERS = [
                ord('1'), ord('2'), ord('3'),
                ord('4'), ord('5'), ord('6'),
                ord('7'), ord('8'), ord('9')
              ]

def handle_playlist_commands(engine, key):
    if(key == ord('f')):
        # Reload the playlist
        engine.reloadPlaylist()
    elif(key == ord('j')):
        # Move current panel's highlight down 1
        panel = engine.screens[0].getCurrentPanel()
        paneldriver.move_down(panel, 1)
    elif(key == ord('J')):
        # Move current panel's highlight down half the panel height
        panel = engine.screens[0].getCurrentPanel()
        paneldriver.move_down(panel, panel.height // 2)
    elif(key == ord('G')):
        # Move current panel's highlight down to the bottom
        panel = engine.screens[0].getCurrentPanel()
        paneldriver.move_down(panel, len(panel.items))
    elif(key == ord('k')):
        # Move current panel's highlight up 1
        panel = engine.screens[0].getCurrentPanel()
        paneldriver.move_up(panel, 1)
    elif(key == ord('K')):
        # Move current panel's highlight up half the panel height
        panel = engine.screens[0].getCurrentPanel()
        paneldriver.move_up(panel, panel.height // 2)
    elif(key == ord('g')):
        # Move current panel's highlight up to the top
        panel = engine.screens[0].getCurrentPanel()
        paneldriver.move_up(panel, len(panel.items))
    elif(key == ord(' ')):
        # Toggle play/pause
        lmswrapper.toggle_play_mode(engine.server, engine.player)
    elif(key == ord('/')):
        # Stop playing
        lmswrapper.stop_playing(engine.server, engine.player)
    elif((key == ord('`')) or (key == ord('~'))): # Shift is optional
        # Toggle player's mute state
        lmswrapper.toggle_mute_state(engine.server, engine.player)
    elif(key == 10): # Key 10 is ENTER
        # Grab the selected item's index and start playback from that index
        panel = engine.screens[0].getCurrentPanel()
        index = panel.getCurrentItemIndex()
        lmswrapper.play_song_at_playlist_index(engine.server, engine.player, index)
    elif(key == ord('<')):
        # Play the previous track in the playlist
        lmswrapper.play_song_at_playlist_index(engine.server, engine.player, '-1')
    elif(key == ord('>')):
        # Play the next track in the playlist
        lmswrapper.play_song_at_playlist_index(engine.server, engine.player, '+1')
    elif(key == ord(',')):
        # Seek backward in the current track
        lmswrapper.seek_track(engine.server, engine.player, '-5')
    elif(key == ord('.')):
        # Seek forward in the current track
        lmswrapper.seek_track(engine.server, engine.player, '+5')
    elif(key == ord('r')):
        # Toggle repeat mode
        lmswrapper.toggle_playlist_mode(engine.server, engine.player, 'repeat')
    elif(key == ord('z')):
        # Toggle shuffle mode
        lmswrapper.toggle_playlist_mode(engine.server, engine.player, 'shuffle')
        # When we shuffle, playlist order may change, so reload it
        engine.reloadPlaylist()
    elif(key == ord('n')):
        # Rename currently connected player
        editbox = Editbox(f"Enter a New Name for Player '{engine.player.name}'", "Name:", engine.win)
        editbox.injectString(engine.player.name)
        (new_name, ret_code) = editbox.getInput()
        while ret_code == 0:
            # Handle resizing
            engine.resizeAll()
            editbox = Editbox(f"Enter a New Name for Player '{engine.player.name}'", "Name:", engine.win)
            editbox.injectString(new_name)
            (new_name, ret_code) = editbox.getInput()
        
        if ret_code != -1:
            lmswrapper.rename_player(engine.server, engine.player, new_name)
    elif(key == ord('S')):
        # TODO: Implement handling for name collisions with existing playlists
        # TODO: Implement handling for user hitting enter on empty string
        # Save play queue contents to a new playlist
        editbox = Editbox(f"Enter a Name for the New Playlist", "Name:", engine.win)
        (new_name, ret_code) = editbox.getInput()
        while ret_code == 0:
            # Handle resizing
            engine.resizeAll()
            editbox = Editbox(f"Enter a Name for the New Playlist", "Name:", engine.win)
            (new_name, ret_code) = editbox.getInput()
        
        if ret_code != -1:
            lmswrapper.save_new_playlist(engine.server, engine.player, new_name)

            # We'll have to fetch the new list of saved playlists to get it
            engine.renderAll()
            engine.reloadSavedPlaylists()
    else:
        pass # Do nothing

def handle_media_library_commands(engine, key):
    if(key == ord('f')):
        # Reload the media library
        engine.reloadMediaLibrary()
    elif(key == ord('j')):
        # Move current panel's highlight down 1
        panel = engine.screens[1].getCurrentPanel()
        paneldriver.move_down(panel, 1)
        paneldriver.change_media_panels(engine.screens[1])
    elif(key == ord('J')):
        # Move current panel's highlight down half the panel size
        panel = engine.screens[1].getCurrentPanel()
        paneldriver.move_down(panel, panel.height // 2)
        paneldriver.change_media_panels(engine.screens[1])
    elif(key == ord('G')):
        # Move current panel's highlight down to the bottom
        panel = engine.screens[1].getCurrentPanel()
        paneldriver.move_down(panel, len(panel.items))
        paneldriver.change_media_panels(engine.screens[1])
    elif(key == ord('k')):
        # Move current panel's highlight up 1
        panel = engine.screens[1].getCurrentPanel()
        paneldriver.move_up(panel, 1)
        paneldriver.change_media_panels(engine.screens[1])
    elif(key == ord('K')):
        # Move current panel's highlight up half the panel size
        panel = engine.screens[1].getCurrentPanel()
        paneldriver.move_up(panel, panel.height // 2)
        paneldriver.change_media_panels(engine.screens[1])
    elif(key == ord('g')):
        # Move current panel's highlight up to the top
        panel = engine.screens[1].getCurrentPanel()
        paneldriver.move_up(panel, len(panel.items))
        paneldriver.change_media_panels(engine.screens[1])
    elif(key == ord('h')):
        # Move focused panel to the left
        engine.screens[1].decrementCurrentPanel()
    elif(key == ord('l')):
        # Move focused panel to the right
        engine.screens[1].incrementCurrentPanel()
    elif(key == 10): # Key 10 is ENTER
        # Grab the selected item and pass it to the LMS to load into the playlist
        panel = engine.screens[1].getCurrentPanel()
        selected_item = paneldriver.get_selected_item(panel)
        
        # Let the user know we are doing work
        infobox = Infobox("Loading Media Selection...", engine.win)
        infobox.render()
        lmswrapper.control_playlist(engine.server, engine.player, 'load', selected_item)
    elif(key == ord(' ')):
        # Grab the selected item and pass it to the LMS to append to the playlist
        panel = engine.screens[1].getCurrentPanel()
        selected_item = paneldriver.get_selected_item(panel)
        
        # Let the user know we are doing work
        infobox = Infobox("Adding Media Selection to Current Playlist...", engine.win)
        infobox.render()
        lmswrapper.control_playlist(engine.server, engine.player, 'add', selected_item)
    else:
        pass # Do nothing


def handle_saved_playlist_commands(engine, key):
    if(key == ord('f')):
        # Reload the saved playlists
        engine.reloadSavedPlaylists()
    elif(key == ord('j')):
        # Move current panel's highlight down 1
        panel = engine.screens[2].getCurrentPanel()
        paneldriver.move_down(panel, 1)
        paneldriver.change_saved_playlist_panel(engine.screens[2])
    elif(key == ord('J')):
        # Move current panel's highlight down half the panel size
        panel = engine.screens[2].getCurrentPanel()
        paneldriver.move_down(panel, panel.height // 2)
        paneldriver.change_saved_playlist_panel(engine.screens[2])
    elif(key == ord('G')):
        # Move current panel's highlight down to the bottom
        panel = engine.screens[2].getCurrentPanel()
        paneldriver.move_down(panel, len(panel.items))
        paneldriver.change_saved_playlist_panel(engine.screens[2])
    elif(key == ord('k')):
        # Move current panel's highlight up 2
        panel = engine.screens[2].getCurrentPanel()
        paneldriver.move_up(panel, 1)
        paneldriver.change_saved_playlist_panel(engine.screens[2])
    elif(key == ord('K')):
        # Move current panel's highlight up half the panel size
        panel = engine.screens[2].getCurrentPanel()
        paneldriver.move_up(panel, panel.height // 2)
        paneldriver.change_saved_playlist_panel(engine.screens[2])
    elif(key == ord('g')):
        # Move current panel's highlight up to the top
        panel = engine.screens[2].getCurrentPanel()
        paneldriver.move_up(panel, len(panel.items))
        paneldriver.change_saved_playlist_panel(engine.screens[2])
    elif(key == ord('h')):
        # Move focused panel to the left
        engine.screens[2].decrementCurrentPanel()
    elif(key == ord('l')):
        # Move focused panel to the right
        engine.screens[2].incrementCurrentPanel()
    elif(key == 10): # Key 10 is ENTER
        # Grab the selected item and pass it to the LMS to play immediately
        panel = engine.screens[2].getCurrentPanel()
        selected_item = paneldriver.get_selected_item(panel)
        
        # Let the user know we are doing work
        infobox = Infobox("Loading Media Selection...", engine.win)
        infobox.render()
        lmswrapper.load_saved_playlist(engine.server, engine.player, 'play', selected_item)
    elif(key == ord(' ')):
        # Grab the selected item and pass it to the LMS to append to the playlist
        panel = engine.screens[2].getCurrentPanel()
        selected_item = paneldriver.get_selected_item(panel)
        
        # Let the user know we are doing work
        infobox = Infobox("Loading Media Selection...", engine.win)
        infobox.render()
        lmswrapper.load_saved_playlist(engine.server, engine.player, 'add', selected_item)
    elif(key == ord('n')):
        # TODO: Handle case where user hits 'n' while highlighting a track instead of a playlist
        # Rename highlighted saved playlist
        panel = engine.screens[2].getCurrentPanel()
        playlist = paneldriver.get_selected_item(panel)

        editbox = Editbox(f"Enter a New Name for Playlist '{playlist.name}'", "Name:", engine.win)
        editbox.injectString(playlist.name)
        (new_name, ret_code) = editbox.getInput()
        while ret_code == 0:
            # Handle resizing
            engine.resizeAll()
            editbox = Editbox(f"Enter a New Name for Playlist '{playlist.name}'", "Name:", engine.win)
            editbox.injectString(new_name)
            (new_name, ret_code) = editbox.getInput()
        
        if ret_code != -1:
            # We have to dry-run first to see if there is a name collision
            conflict = lmswrapper.rename_playlist(engine.server, playlist.playlist_id, new_name, True)
            if conflict:
                engine.renderAll()

                # Prompt the user if they actually want to overwrite the playlist
                prompt = Prompt("A playlist with this name already exists. Overwrite it?", engine.win)
                confirmed = prompt.getConfirmation()
                while confirmed == "RESIZE":
                    engine.resizeAll()
                    prompt = Prompt("A playlist with this name already exists. Overwrite it?", engine.win)
                    confirmed = prompt.getConfirmation()
                if confirmed:
                    # Clear the playlist
                    engine.renderAll()

                    # Let the user know we are doing work
                    infobox = Infobox("Renaming Saved Playlist...", engine.win)
                    infobox.render()
                    lmswrapper.rename_playlist(engine.server, playlist.playlist_id, new_name, False)

                    engine.reloadSavedPlaylists()
            else: # No conflict, go right ahead
                # Clear the playlist
                engine.renderAll()

                # Let the user know we are doing work
                infobox = Infobox("Renaming Saved Playlist...", engine.win)
                infobox.render()
                lmswrapper.rename_playlist(engine.server, playlist.playlist_id, new_name, False)

                engine.reloadSavedPlaylists()
    elif(key == ord('D')):
        # Prompt the user if they actually want to delete the playlist
        playlist = engine.screens[2].panels[0].getCurrentItem()
        prompt = Prompt(f"Really delete the playlist? ({playlist.name})", engine.win)
        confirmed = prompt.getConfirmation()
        while confirmed == "RESIZE":
            engine.resizeAll()
            prompt = Prompt("Really delete the playlist? ({playlist.name})", engine.win)
            confirmed = prompt.getConfirmation()
        if confirmed:
            # Clear the playlist
            engine.renderAll()

            # Let the user know we are doing work
            infobox = Infobox("Deleting Playlist...", engine.win)
            infobox.render()
            lmswrapper.delete_saved_playlist(engine.server, playlist.playlist_id)

            engine.reloadSavedPlaylists()
    else:
        pass # Do nothing

def handle_generic_commands(engine, key):
    if(key == ord('q')):
        engine.quit = True
    elif(key in TAB_NUMBERS):
        if key == ord('1'):
            # If switching to the playlist screen, reload the playlist first
            engine.reloadPlaylist()
        engine.changeTab(key)
    elif(key == ord('c')):
        # Prompt the user if they actually want to clear the playlist
        prompt = Prompt("Really clear the current playlist?", engine.win)
        confirmed = prompt.getConfirmation()
        while confirmed == "RESIZE":
            engine.resizeAll()
            prompt = Prompt("Really clear the current playlist?", engine.win)
            confirmed = prompt.getConfirmation()
        if confirmed:
            # Clear the playlist
            engine.renderAll()

            # Let the user know we are doing work
            infobox = Infobox("Clearing Current Playlist...", engine.win)
            infobox.render()
            lmswrapper.clear_playlist(engine.server, engine.player)

            # If currently on the Playlist screen, refresh it to show changes
            if engine.currentScreenIndex == 0:
                engine.reloadPlaylist()
    elif(key == ord('-')):
        # Volume down
        lmswrapper.change_volume(engine.server, engine.player, '-5')
    elif((key == ord('=')) or (key == ord('+'))): # Shift is optional
        # Volume up
        lmswrapper.change_volume(engine.server, engine.player, '+5')
    elif(key == ord('o')):
        # Toggle the player ON and OFF
        lmswrapper.toggle_power(engine.server, engine.player)
    elif(key == ord('p')):
        # Present a list of players found, and choose one to connect to
        players = []
        player_list = engine.server.get_players()
        for player in player_list:
            p = LMSPlayer(player['name'], player['playerid'])
            players.append(p)
        listbox = Listbox("Please Select a Player", players, engine.win)
        choice = listbox.getChoice()
        while choice == "RESIZE":
            engine.resizeAll()
            listbox = Listbox("Please Select a Player", players, engine.win)
            choice = listbox.getChoice()
        if choice != None:
            engine.player = choice

            # If the user is on the Playlist screen, reload it
            if engine.currentScreenIndex == 0:
                engine.reloadPlaylist()
    elif(key == ord('m')):
        # Only enter move mode if focused on a PlaylistPanel
        panel = engine.getCurrentScreen().getCurrentPanel()
        if isinstance(panel, PlaylistPanel):
            engine.mode = Mode.MOVE
            # Tell the panel to store the start index
            panel.setMoveStart()
    elif(key == ord('d')):
        # Only enter delete mode if focused on a PlaylistPanel
        panel = engine.getCurrentScreen().getCurrentPanel()
        if isinstance(panel, PlaylistPanel):
            engine.mode = Mode.DELETE
    elif(key == ord('R')):
        # Prompt user if they want to start a database rescan
        prompt = Prompt("Rescan the Music Database?", engine.win)
        confirmed = prompt.getConfirmation()
        while confirmed == "RESIZE":
            engine.resizeAll()
            prompt = Prompt("Rescan the Music Database?", engine.win)
            confirmed = prompt.getConfirmation()
        if confirmed:
            lmswrapper.trigger_rescan(engine.server)
    elif(key == curses.KEY_RESIZE):
        # Begin a cascading call to resize all screens/panels/windows/etc
        engine.resizeAll()
    else:
        pass # Do nothing

def handle_move_mode_commands(engine, key):
    if(key == ord('q')):
        # Exit move mode without serializing changes
        panel = engine.getCurrentScreen().getCurrentPanel()
        panel.getMoveIndices()
        engine.mode = Mode.NORMAL
    elif(key == ord('m')):
        # Only enter move mode if focused on a PlaylistPanel
        panel = engine.getCurrentScreen().getCurrentPanel()
        if isinstance(panel, PlaylistPanel):
            engine.mode = Mode.NORMAL
            (start, end) = panel.getMoveIndices()
            if start != end:
                # Use different queries based on the current screen
                if engine.currentScreenIndex == 0:
                    lmswrapper.move_track_in_play_queue(engine.server, engine.player, start, end)
                    engine.reloadPlaylist()
                elif engine.currentScreenIndex == 2:
                    playlist = engine.screens[2].panels[0].getCurrentItem()
                    lmswrapper.move_track_in_saved_playlist(engine.server, playlist.playlist_id, start, end)
                    engine.reloadSavedPlaylists()
                    # Move focused panel back to the playlist tracks
                    engine.screens[2].incrementCurrentPanel()
    elif(key == ord('j')):
        # Move current panel's highlight down 1
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_down(panel, 1)
    elif(key == ord('J')):
        # Move current panel's highlight down half the panel height
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_down(panel, panel.height // 2)
    elif(key == ord('G')):
        # Move current panel's highlight down to the bottom
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_down(panel, len(panel.items))
    elif(key == ord('k')):
        # Move current panel's highlight up 1
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_up(panel, 1)
    elif(key == ord('K')):
        # Move current panel's highlight up half the panel height
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_up(panel, panel.height // 2)
    elif(key == ord('g')):
        # Move current panel's highlight up to the top
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_up(panel, len(panel.items))
    elif(key == curses.KEY_RESIZE):
        # Begin a cascading call to resize all screens/panels/windows/etc
        engine.resizeAll()
    else:
        pass # Do nothing

def handle_delete_mode_commands(engine, key):
    if(key == ord('q')):
        # Exit delete mode without serializing changes
        panel = engine.getCurrentScreen().getCurrentPanel()
        panel.getMarkedItems()
        engine.mode = Mode.NORMAL
    elif(key == ord(' ')):
        # Mark an item for deletion
        panel = engine.getCurrentScreen().getCurrentPanel()
        panel.markItem()
    elif(key == ord('d')):
        # Only enter delete mode if focused on a PlaylistPanel
        panel = engine.getCurrentScreen().getCurrentPanel()
        if isinstance(panel, PlaylistPanel):
            engine.mode = Mode.NORMAL
            marked_items = panel.getMarkedItems()
            if marked_items != []:
                prompt = Prompt(f"Really delete tracks?", engine.win)
                confirmed = prompt.getConfirmation()
                while confirmed == "RESIZE":
                    engine.resizeAll()
                    prompt = Prompt("Really delete tracks?", engine.win)
                    confirmed = prompt.getConfirmation()
                if confirmed:
                    # Clear the playlist
                    engine.renderAll()

                    # Let the user know we are doing work
                    infobox = Infobox("Deleting Tracks...", engine.win)
                    infobox.render()
                    # Use different queries based on the current screen
                    if engine.currentScreenIndex == 0:
                        lmswrapper.delete_tracks_from_play_queue(engine.server, engine.player, marked_items)
                        engine.reloadPlaylist()
                    elif engine.currentScreenIndex == 2:
                        playlist = engine.screens[2].panels[0].getCurrentItem()
                        lmswrapper.delete_tracks_from_saved_playlist(engine.server,
                                                                     playlist.playlist_id,
                                                                     marked_items)
                        engine.reloadSavedPlaylists()
    elif(key == ord('j')):
        # Move current panel's highlight down 1
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_down(panel, 1)
    elif(key == ord('J')):
        # Move current panel's highlight down half the panel height
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_down(panel, panel.height // 2)
    elif(key == ord('G')):
        # Move current panel's highlight down to the bottom
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_down(panel, len(panel.items))
    elif(key == ord('k')):
        # Move current panel's highlight up 1
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_up(panel, 1)
    elif(key == ord('K')):
        # Move current panel's highlight up half the panel height
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_up(panel, panel.height // 2)
    elif(key == ord('g')):
        # Move current panel's highlight up to the top
        panel = engine.getCurrentScreen().getCurrentPanel()
        paneldriver.move_up(panel, len(panel.items))
    elif(key == curses.KEY_RESIZE):
        # Begin a cascading call to resize all screens/panels/windows/etc
        engine.resizeAll()
    else:
        pass # Do nothing
