"""
This module aims to fill some holes in the lmsquery library, including adding
my own query wrappers for common functions and server commands.
"""

from classes.Music import Album, Artist, Song

"""
Songinfo queries return a list of dictionaries, so we use this function to
collapse the list into a single dictionary with each key/value pair.
"""
def collapse_songinfo(songinfo):
    return {key: value for d in songinfo for key, value in d.items()}

def get_current_playlist(lms, player):
    player_id = player.player_id
    playlist = []

    # Determine how many tracks there are in the playlist
    num_tracks = lms.query(player_id, "playlist", "tracks", "?")['_tracks']

    # For every track, get its path, and use the path to get the metadata
    for i in range(num_tracks):
        paths = lms.query(player_id, "playlist", "path", i, "?")
        songinfo = lms.query("", "songinfo", 0, 9999, "url:" + paths['_path'], "tags:aelsty")['songinfo_loop']
        s = collapse_songinfo(songinfo)

        song = Song(s['id'], s['title'], s['artist'], s['artist_id'],
                    s['album'], s['album_id'], s['year'], s['tracknum'])
        playlist.append(song)

    return playlist

def get_now_playing(lms, player):
    player_id = player.player_id

    # Query the status of the player to get the playing track's index in the playlist
    status = lms.query(player_id, 'status')
    try:
        playing_index = int(status['playlist_cur_index'])
    except KeyError:
        # There is nothing in the playlist to grab
        return {}

    # Query the status again, but now with the specific index, and get the track_id
    playing_track = lms.query(player_id, 'status', playing_index, 1, '-')['playlist_loop'][0]
    track_id = playing_track['id']

    # Now that we have the ID, do a songinfo query on the track
    songinfo = lms.query(player_id, 'songinfo', 0, 9999, 'track_id:' + str(track_id),
                         'tags:adly')['songinfo_loop']
    track_info = collapse_songinfo(songinfo)

    # Query the elapsed time of the playing track
    timeinfo = lms.query(player_id, 'time', '?')
    track_info['elapsed_time'] = timeinfo['_time']

    return track_info

def get_player_info(lms, player):
    player_id = player.player_id
    status = lms.query(player_id, 'status', 0, 9999)

    return status

def get_media_library(lms):
    # Get all songs, then organize them into albums
    songs = lms.query("", "songs", 0, 9999, "tags:ACelSty")['titles_loop']
    albums = {}

    for song in songs:
        if song['compilation'] == '1':
            artist = "Various Artists"
        else:
            artist = song['albumartist'] if 'albumartist' in song else song['artist']
        artist_id = song['albumartist_ids'] if 'albumartist_ids' in song else song['artist_ids']
        if song['album_id'] not in albums:
            # Create album if it doesn't already exist
            album = Album(song['album_id'], artist, artist_id, song['album'], song['year'], [])
            albums[album.album_id] = album
        # Put song obj into album tracklist
        song_obj = Song(song['id'], song['title'], artist, artist_id,
                        song['album'], song['album_id'], song['year'], song['tracknum'])
        album = albums[song['album_id']]
        album.addSong(song_obj)

    artists = {}
    for album in albums.values():
        if album.artist_id not in artists:
            # Create artist if it doesn't already exist
            artist = Artist(album.artist_id, album.artist, [])
            artists[artist.artist_id] = artist
        artist = artists[album.artist_id]
        artist.addAlbum(album)

    sorted_artists = dict(sorted(artists.items(), key = lambda item: item[1].name.upper()))

    return sorted_artists

def control_playlist(lms, player, command, selected_item):
    player_id = player.player_id

    # Determine which query to use based on the type of item selected
    if isinstance(selected_item, Artist):
        lms.query(player_id, "playlistcontrol", f"cmd:{command}", f"artist_id:{selected_item.artist_id}")
    elif isinstance(selected_item, Album):
        lms.query(player_id, "playlistcontrol", f"cmd:{command}", f"album_id:{selected_item.album_id}")
    elif isinstance(selected_item, Song):
        lms.query(player_id, "playlistcontrol", f"cmd:{command}", f"track_id:{selected_item.song_id}")
    else:
        raise ValueError(selected_item)

def clear_playlist(lms, player):
    player_id = player.player_id

    lms.query(player_id, "playlist", "clear")