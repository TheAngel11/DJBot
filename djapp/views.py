from django.shortcuts import render
from django.http import HttpResponse
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import random
import uuid
import json
from djapp.models import Song, Genre
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.protobuf.json_format import MessageToJson
from api.views import search, get_songs_by_artist, get_genres_by_artist, get_albums_by_artist, get_access_token


def index(request):
    if 'uuid' not in request.session:
        request.session['uuid'] = str(uuid.uuid4())

    request.session['access_token'] = get_access_token()

    return render(request, 'index.html')


def get_message(request):
    # Get the message from the user
    message = request.GET.get('message')

    session_client = dialogflow.SessionsClient()

    session_path = session_client.session_path("djbot-388016", request.session['uuid'])

    text_input = dialogflow.TextInput(text=message, language_code="en-US")

    query_input = dialogflow.QueryInput(text=text_input)

    # Enable sentiment analysis
    sentiment_config = dialogflow.SentimentAnalysisRequestConfig(
        analyze_query_text_sentiment=True
    )

    # Set the query parameters with sentiment analysis
    query_params = dialogflow.QueryParameters(
        sentiment_analysis_request_config=sentiment_config
    )

    response = session_client.detect_intent(
        request={
            "session": session_path,
            "query_input": query_input,
            "query_params": query_params,
        }
    )

    #response = session_client.detect_intent(session=session_path, query_input=query_input, query_params=query_params)

    json_response = MessageToJson(response._pb)
    print(json_response)

    print(response.query_result.fulfillment_text)

    # TODO: Get intent and parameters from the response and execute API call to spotify

    answer = getAnswer(request, response)

    return HttpResponse(answer)


def getAnswer(request, response):
    intent = response.query_result.intent.display_name
    parameters = response.query_result.parameters

    #request.session['mood'] = parameters['mood']

    answer = ""
    if intent == "music.get-song":
        song = getSongAnswer(request, parameters)
        with open('recomendations.json', 'r') as file:
            data = json.load(file)
        # Generate a random song recommendation
        songs_response = data['songs']
        answer = random.choice(songs_response).replace("<song>", "Hola")

    elif intent == "music.get-artist":
        artist = getArtistAnswer(request, parameters)
        answer = random.choice(data['artist']).replace("<artist>", artist)
        
    elif intent == "music.get-playlist":
        answer = getPlaylistAnswer(request, parameters)
    elif intent == "music.get-album":
        answer = "Sure, I'll find you an album"
    else:
        answer = response.query_result.fulfillment_text

    return answer

def getSongAnswer(request, parameters):
    buildQuery = ""

    if parameters['music-artist'] != "":
        buildQuery += parameters['music-artist']
    if parameters['period'] != []:
        buildQuery += " " + random.choice(parameters['period'])
    if parameters['purpose'] != []:
        buildQuery += " " + random.choice(parameters['purpose'])
    if parameters['music-genre'] != "":
        buildQuery += " " + parameters['music-genre']
    if parameters['time'] != "":
        buildQuery += " " + parameters['time']
    if parameters['atribute'] != []:
        buildQuery += " " + random.choice(parameters['atribute'])
    if parameters['mood'] != []:
        buildQuery += " " + random.choice(parameters['mood'])
    
    #if buildQuery == "":
    #    buildQuery += request.session['mood']

    buildQuery += " songs"

    result = search(request, 'track', buildQuery)
    songs = []
    randInt = random.randint(0, result['tracks']['limit'] - 1)
    for i in range(randInt):
        songs.append(result['tracks']['items'][i]['name'] + " by " + result['tracks']['items'][i]['artists'][0]['name'])
    
    # Build a pretty string with the songs
    filtered = "I found these songs: \n"
    for song in songs:
        # Dot in UTF-8 is \u2022
        filtered += "\u2022 " + song + "\n"

    print(filtered)

    song = random.choice(songs)
    return song

def getArtistAnswer(request, parameters):
    buildQuery = ""

    if parameters['music-artist'] != "":
        if parameters['atribute'] != []:
            buildQuery += parameters['atribute'][0] + " to "
        buildQuery += parameters['music-artist']
    elif parameters['atribute'] != []:
        buildQuery += " " + random.choice(parameters['atribute'])
    if parameters['music-genre'] != "":
        buildQuery += " " + parameters['music-genre']
    if parameters['period'] != "":
        buildQuery += " " + parameters['period']
    if parameters['mood'] != "":
        buildQuery += " " + parameters['mood']

    buildQuery += " artists"

    result = search(request, 'artist', buildQuery)
    
    songs = []
    randInt = random.randint(0, result['artists']['limit'] - 1)
    for i in range(randInt):
        songs.append(result['artists']['items'][i]['name'])
    
    # Build a pretty string with the songs
    filtered = "I found these artists: \n"
    for song in songs:
        # Dot in UTF-8 is \u2022
        filtered += "\u2022 " + song + "\n"

    print(filtered)

    return filtered

def getAlbumAnswer(request, parameters):
    buildQuery = ""

    if parameters['music-genre'] != []:
        for genre in parameters['music-genre']:
            buildQuery += genre + " "
    if parameters['music-artist'] != "":
        buildQuery += " " + parameters['music-artist']
    if parameters['purpose'] != []:
        buildQuery += " " + random.choice(parameters['purpose'])
    if parameters['mood'] != "":
        buildQuery += " " + parameters['mood']

    buildQuery += " albums"

    result = search(request, 'album', buildQuery)
    songs = []
    randInt = random.randint(0, result['albums']['limit'] - 1)
    for i in range(randInt):
        songs.append(result['albums']['items'][i]['name'])
    
    # Build a pretty string with the songs
    filtered = "I found these albums: \n"
    for song in songs:
        # Dot in UTF-8 is \u2022
        filtered += "\u2022 " + song + "\n"

    print(filtered)
    return filtered

def getPlaylistAnswer(request, parameters):
    buildQuery = ""

    if parameters['music-genre'] != []:
        for genre in parameters['music-genre']:
            buildQuery += genre + " "
    if parameters['music-artist'] != "":
        buildQuery += " " + parameters['music-artist']
    if parameters['purpose'] != []:
        buildQuery += " " + random.choice(parameters['purpose'])
    if parameters['mood'] != []:
        for mood in parameters['mood']:
            buildQuery += " " + mood
    if parameters['period'] != []:
        for period in parameters['period']:
            buildQuery += " " + period
    if parameters['atribute'] != []:
        for atribute in parameters['atribute']:
            buildQuery += " " + atribute
    if parameters['music-album'] != "":
        buildQuery += " " + parameters['music-album']

    buildQuery += " playlists"

    result = search(request, 'playlist', buildQuery)
    songs = []
    randInt = random.randint(0, result['playlists']['limit'] - 1)
    for i in range(randInt):
        songs.append(result['playlists']['items'][i]['name'])
    
    # Build a pretty string with the songs
    filtered = "I found these playlists: \n"
    for song in songs:
        # Dot in UTF-8 is \u2022
        filtered += "\u2022 " + song + "\n"

    print(filtered)
    return filtered

  