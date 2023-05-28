from django.db import models

# Create your models here.

class Song:
    def __init__(self, title, artist, genre):
        self.title = title
        self.artist = artist
        self.genre = genre

    def getGenre(self):
        return self.genre.getName().lower()

    def getTitle(self):
        return self.title.lower()

    def getArtist(self):
        return self.artist.lower()

    def getArtistInfo(self):
        return self.artist

    def getMood(self):
        return self.genre.getMood().lower()

    def getInfo(self):
        return self.title + " by " + self.artist
    


class Genre:
    def __init__(self, name, mood):
        self.name = name
        self.mood = mood

    def getName(self):
        return self.name

    def getMood(self):
        return self.mood
