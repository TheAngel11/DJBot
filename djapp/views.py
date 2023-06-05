from django.shortcuts import render
from django.http import HttpResponse
import random
import uuid
import json
from djapp.models import Song, Genre
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.protobuf.json_format import MessageToJson
from api.views import search, get_access_token, get_artist_by_artist,get_artist_by_genre,get_album_by_artist,get_songs_by_playlist, get_artist_by_playlist
from djapp.nlg import generateSentence


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

    #json_response = MessageToJson(response._pb)
    #print(json_response)
    
    answer = getAnswer(request, response)

    return HttpResponse(answer)

# function that creates the answer
def getAnswer(request, response):
    intent = response.query_result.intent.display_name
    parameters = response.query_result.parameters

    answer = ""
    if intent == "music.get-song": # get song
        answer = getSongAnswer(request, parameters)
    elif intent == "music.get-artist": # get artist
        answer = getArtistAnswer(request, parameters)
    elif intent == "music.get-playlist": # get playlist
        answer = getPlaylistAnswer(request, parameters)
    elif intent == "music.get-album": # get album
        answer = getAlbumAnswer(request, parameters)
    else:
        answer = response.query_result.fulfillment_text

    return answer

# function that creates the answer for the get-song intent
def getSongAnswer(request, parameters):
    buildQuery = ""

    # check if the user has specified a mood or situation
    if parameters['atribute'] != [] or parameters['mood'] != []:
        if parameters['atribute'] != []:
            buildQuery += " " + random.choice(parameters['atribute'])
        else :
            buildQuery += " " + random.choice(parameters['mood'])

        aux = get_songs_by_playlist(request, buildQuery)
        if aux == None:
            return "I don't know what song you want to listen to"
        
        request.session['query'] = "mood:" + buildQuery
        return generateSentence('song', random.choice(aux))
    # create the query
    else: 
        if parameters['music-artist'] != "":
            buildQuery += "artist:" + parameters['music-artist'][0]
        if parameters['period'] != []:
            buildQuery += "year:" + random.choice(parameters['period'])
        if parameters['purpose'] != []:
            buildQuery += " " + random.choice(parameters['purpose'])
        if parameters['music-genre'] != []:        
            buildQuery += "genre:" + random.choice(parameters['music-genre'])
        if parameters['time'] != "":
            buildQuery += " " + parameters['time']


        #check in sesion if the user has already asked for a song 
        if buildQuery == "":
            if 'query' in request.session:
                buildQuery = request.session['query']
                if "mood:" in buildQuery:
                    mood = buildQuery.split(":")[1].strip()
                    aux = get_songs_by_playlist(request, mood)
                    return generateSentence('song', random.choice(aux))
            else:
                buildQuery += " songs"

        result = search(request, 'track', buildQuery) # search in spotify

        #check if result is not empty + max value for random
        if result['tracks']['total'] == 0:
            return "I don't know what song you want to listen to"
        elif result['tracks']['total'] <= result['tracks']['limit']:
            randomMax = result['tracks']['total'] - 1
        else:
            randomMax = result['tracks']['limit'] - 1
    
        request.session['query'] = buildQuery

        randInt = random.randint(0,randomMax)
        song = result['tracks']['items'][randInt]['name'] + " by " + result['tracks']['items'][randInt]['artists'][0]['name']

        return generateSentence('song', song)

# function that creates the answer for the get-artist intent
def getArtistAnswer(request, parameters):
    buildQuery = ""

    # check if the user has specified another artist
    if parameters['music-artist'] != "":
        result = get_artist_by_artist(request, parameters['music-artist'])
        if result == None:
            return "I don't know what artist you want to listen to"
        return generateSentence('artist', random.choice(result))        
    # check if the user has specified a genre
    if parameters['music-genre'] != "":
        result = get_artist_by_genre(request, parameters['music-genre'])
        if result == None:
            return "I don't know what artist you want to listen to"
        return generateSentence('artist', random.choice(result))
    # create the query
    if parameters['atribute'] != []:
        buildQuery += " " + random.choice(parameters['atribute'])
    if parameters['period'] != "":
        buildQuery += " " + parameters['period']
    if parameters['mood'] != "":
        buildQuery += " " + parameters['mood']

    if buildQuery == "":
        buildQuery += " artists"
    else:
        result = get_artist_by_playlist(request, buildQuery)
        return generateSentence('artist', random.choice(result))

    result = search(request, 'artist', buildQuery) # search in spotify

    #check if result is not empty + max value for random
    if result['artists']['total'] == 0:
        return "I don't know what artist you want to listen to"
    elif result['artists']['total'] <= result['artists']['limit']:
        randomMax = result['artists']['total'] - 1
    else:
        randomMax = result['artists']['limit'] - 1

    artist = result['artists']['items'][random.randint(0,randomMax)]['name']
   
    return generateSentence('artist', artist)

# function that creates the answer for the get-album intent
def getAlbumAnswer(request, parameters):
    buildQuery = ""
    result = []
    
    # check if the user has specified an artist
    if parameters['music-artist'] != "":
        result = get_album_by_artist(request, parameters['music-artist'])
        if result == None:
            return "I don't know what album you want to listen to"
        randomMax = len(result)
    # create the query
    else:  
        if parameters['music-genre'] != []:
            buildQuery += " " + random.choice(parameters['music-genre'])  
        if parameters['period'] != "":
            buildQuery += " " + parameters['period']
        if parameters['mood'] != "":
            buildQuery += " " + parameters['mood']
        if parameters['atribute'] != []:
            buildQuery += " " + random.choice(parameters['atribute'])

        if buildQuery == "":
            buildQuery += " albums"

        aux = search(request, 'album', buildQuery) # search in spotify

        #check if result is not empty + max value for random
        if aux == None:
            return "I don't know what album you want to listen to"        
        if aux['albums']['total'] == 0:
            return "I don't know what album you want to listen to"
        elif aux['albums']['total'] <= aux['albums']['limit']:
            randomMax = aux['albums']['total']
        else:
            randomMax = aux['albums']['limit']
        
        for i in range(randomMax):
            result.append(aux['albums']['items'][i]['name'])
    
    # check if the user has specified a number of albums
    if parameters['number-integer'] != "":
        if parameters['number-integer'] != 1:    
            numbers = generate_random_numbers(parameters['number-integer'], randomMax)
            sentence = "You should listen:\n\n"
            for i in range(len(numbers)):
                index = numbers[i]
                sentence += "\u2022 " + result[index] + "\n\n"
            return sentence                    

    return generateSentence('album', random.choice(result))

# function that creates the answer for the get-playlist intent
def getPlaylistAnswer(request, parameters):
    buildQuery = ""

    # create the query
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

    if buildQuery == "":
        buildQuery += " playlists"

    result = search(request, 'playlist', buildQuery) # search in spotify

    #check if result is not empty + max value for random
    if result == None:
            return "I don't know what playlist you want to listen to"    
    if result['playlists']['total'] == 0:
        return "I don't know what playlist you want to listen to"
    elif result['playlists']['total'] <= result['playlists']['limit']:
        randomMax = result['playlists']['total']
    else:
        randomMax = result['playlists']['limit']

    # check if the user has specified a number of playlists
    if parameters['number-integer'] != "":
        if parameters['number-integer'][0] != "1.0":            
            numbers = generate_random_numbers(parameters['number-integer'][0], randomMax)
            sentence = "You should listen this playlists:\n\n"
            for i in range(len(numbers)):
                index = numbers[i]
                sentence += "\u2022 " + result['playlists']['items'][index]['name'] + "\n\n"
            return sentence                    

    randInt = random.randint(0, randomMax - 1)
    playlist = result['playlists']['items'][randInt]['name']
    return generateSentence('playlist',playlist)

# function that generates random numbers based on user specifications and max value of the list
def generate_random_numbers(paramters, max):
    if type(paramters) == str:
        end = int(paramters)
    else:
        end = round(paramters)
  
    if max <= end:
        numbers = random.sample(range(0, max), max)
    else:     
        numbers = random.sample(range(0, max), end)
    return numbers