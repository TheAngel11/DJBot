import json
import random


data = json.load(open('recomendations.json'))
usedSongs = []
usedArtists = []
usedAlbum = []
usedPlaylist = []

def generateSentence(type, word):
    global usedSongs
    global usedArtists
    global usedAlbum
    global usedPlaylist

    sentences = data[type]

    if type == "song":
        if len(usedSongs) == len(sentences):
            usedSongs = [] 
        final_sentence = returnSentence(usedSongs, sentences) 
        usedSongs.append(final_sentence)
    elif type == "artist":
        if len(usedArtists) == len(sentences):
            usedArtists = [] 
        final_sentence = returnSentence(usedArtists, sentences) 
        usedArtists.append(final_sentence)
    elif type == "album":
        if len(usedAlbum) == len(sentences):
            usedAlbum = [] 
        final_sentence = returnSentence(usedAlbum, sentences) 
        usedAlbum.append(final_sentence)
    elif type == "playlist":
        if len(usedPlaylist) == len(sentences):
            usedPlaylist = [] 
        final_sentence = returnSentence(usedPlaylist, sentences) 
        usedPlaylist.append(final_sentence)
    else:
        return "I don't know what you want to listen to"

    print(final_sentence)
    return final_sentence.replace("<"+ type + ">", word)

def returnSentence(usedArray, sentences):
    final_sentence = random.choice(sentences)
    while final_sentence in usedArray:
        final_sentence = random.choice(sentences)
    return final_sentence
