"""
This series of classes are used to represent albums, songs, and other
structures and their metadata in the LMS.
"""

class LMSPlayer:
    def __init__(self, name, player_id):
        self.name = name
        self.player_id = player_id

    def __repr__(self):
        return self.name

class Playlist:
    def __init__(self, playlist_id, name, songs):
        self.playlist_id = playlist_id
        self.name = name
        self.songs = songs

    def addSong(self, song):
        self.songs.append(song)

    def __repr__(self):
        return self.name

class Artist:
    def __init__(self, artist_id, name, albums):
        self.artist_id = artist_id
        self.name = name
        self.albums = albums

    def addAlbum(self, album):
        index = 0
        for i in range(len(self.albums)):
            a = self.albums[i]
            if album.year < a.year:
                break
            index += 1
        self.albums.insert(index, album)

    def __repr__(self):
        return self.name

class Album:
    def __init__(self, album_id, artist, artist_id, title, year, songs):
        self.album_id = album_id
        self.artist = artist
        self.artist_id = artist_id
        self.title = title
        self.year = year
        self.songs = songs

    def addSong(self, song):
        index = min(len(self.songs), song.tracknum - 1)
        self.songs.insert(index, song)

    def __repr__(self):
        return self.title

class Song:
    def __init__(self, song_id, title, artist, artist_id, album_title, album_id, year, tracknum):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.artist_id = artist_id
        self.album_title = album_title
        self.album_id = album_id
        self.year = year
        self.tracknum = int(tracknum)

    def __repr__(self):
        return self.title
