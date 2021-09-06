"""
This series of classes are used to represent albums, songs, and other
structures and their metadata in the LMS.
"""

class LMSPlayer:
    def __init__(self, name, player_id):
        self.name = name
        self.player_id = player_id

class Album:
    def __init__(self, album_id, artist, title, year, songs):
        self.album_id = album_id
        self.artist = artist
        self.title = title
        self.year = year
        self.songs = songs

    def __repr__(self):
        song_strings = []
        for song in self.songs:
            song_strings.append(repr(song))
        tracklist = "\n> ".join(song_strings)
        return f"{self.title} :: {self.artist} ({self.year})\n> {tracklist}"

class Song:
    def __init__(self, song_id, title, artist, artist_id, album_title, album_id, year, tracknum):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.artist_id = artist_id
        self.album_title = album_title
        self.album_id = album_id
        self.year = year
        self.tracknum = tracknum

    def __repr__(self):
        return f"{self.title} - {self.artist} - {self.album_title} ({self.year})"
