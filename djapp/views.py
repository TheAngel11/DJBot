from django.shortcuts import render
from django.http import HttpResponse
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import random
from djapp.models import Song, Genre
from google.cloud import dialogflow_v2beta1 as dialogflow

def index(request):
    return render(request, 'index.html')


def get_message(request):
    # Get the message from the user
    message = request.GET.get('message')
    # Process and return the response
    response = chatbot(message)

    return HttpResponse(response)


genre = {"pop", "rock", "rap", "classic"}
mood = {"happi", "angry", "sad", "calm"}

responses_artist = ["%s is great!",
                    "You can listen to %s",
                    "I think you would like %s's songs",
                    "%s is what you are looking for",
                    "Haven't listened to %s yet? You'll love it",
                    "The artist %s it is really great",
                    "You'll love the artist %s, it is extraordinary"]

responses_song = ["You should listen to %s",
                  "I recommend you listen to %s",
                  "I think you would like %s",
                  "The song that suits better is %s",
                  "%s is the song you are looking for",
                  "The song %s it is the best choice for you",
                  "You are looking for %s, it is really great",
                  "You'll love the song %s, it is huge"]





def generate_artist(songs):
    artists = []
    for word in songs:
        artists.append(word.getArtist())
    return artists


def filter_stop_words(sentence, stop_words):
    filtered = []
    for word in sentence:
        if word not in stop_words:
            filtered.append(word)
    return filtered


def get_song_genre(genre, database):
    songs_in_genre = [s for s in database if genre in s.getGenre()]
    if songs_in_genre:
        return random.choice(songs_in_genre)
    else:
        return None


def get_song_artist(artist, database):
    songs_in_artist = [s for s in database if artist in s.getArtist()]
    if songs_in_artist:
        return random.choice(songs_in_artist)
    else:
        return None


def song_by_mood(mood, database):
    songs_in_mood = [s for s in database if mood in s.getMood()]
    if songs_in_mood:
        return random.choice(songs_in_mood)
    else:
        return None


def get_artist_from_artist(artist, database):
    song_v1 = get_song_artist(artist, database)
    songs_in_genre = [s for s in database if song_v1.getGenre() == s.getGenre()]
    song = random.choice(songs_in_genre)
    while (song.getArtist() == artist):
        song = random.choice(songs_in_genre)
    return song

g1 = Genre("rap", "sad")  # Rap sad
g2 = Genre("rock", "angry")  # Rock angry
g3 = Genre("pop", "happi")  # Pop happy
g4 = Genre("classic", "calm")  # Classic calm

s1 = Song("God's Plan", "Drake", g1)
s2 = Song("Thunderstruck", "AC/DC", g2)
s3 = Song("Lose Yourself", "Eminem", g1)
s4 = Song("Bohemian Rhapsody", "Queen", g2)
s5 = Song("Hey Jude", "Beatles", g2)
s6 = Song("The Four Seasons", "Vivaldi", g4)
s7 = Song("9th Symphony", "Beethoven", g4)
s8 = Song("Für Elise", "Mozart", g4)
s9 = Song("Dancing queen", "ABBA", g3)
s10 = Song("Skyline", "Khalid", g3)
s11 = Song("SAOKO", "Rosalía", g3)
s12 = Song("Agua pasá", "SFDK", g1)
s13 = Song("Don't Stop Believin'", "Journey", g2)
s14 = Song("Umbrella", "Rihanna", g3)
s15 = Song("Hotel California", "Eagles", g2)
s16 = Song("Smells Like Teen Spirit", "Nirvana", g2)

S = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16]

def chatbot(message):
    database = S
    artist_list = generate_artist(S)

    user_input = message
    user_input_tokens = word_tokenize(user_input)
    user_input_tokens = [PorterStemmer().stem(token) for token in user_input_tokens]
    stop_words = stopwords.words('english')
    filtered = filter_stop_words(user_input_tokens, stop_words)
    # print(filtered)

    if "bye" in filtered:
        return "Goodbye! Have a nice day."

    for word in filtered:
        if word in genre:
            song = get_song_genre(word, database)
            if "song" in filtered:
                sentence = random.choice(responses_song)
                return sentence % song.getInfo()
                break
            elif "artist" in filtered:
                sentence = random.choice(responses_artist)
                return sentence % song.getArtistInfo()
                break
        if word in mood:
            song = song_by_mood(word, database)
            if "song" in filtered:
                sentence = random.choice(responses_song)
                return sentence % song.getInfo()
                break
            elif "artist" in filtered:
                sentence = random.choice(responses_artist)
                return sentence % song.getArtistInfo()
                break
        if word in artist_list:
            if "song" in filtered:
                song = get_song_artist(word, database)
                sentence = random.choice(responses_song)
                return sentence % song.getInfo()
                break
            elif "artist" in filtered:
                song = get_artist_from_artist(word, database)
                sentence = random.choice(responses_artist)
                return sentence % song.getArtistInfo()
                break


    else:
        return "I'm sorry, I didn't understand your question. Please try again."






