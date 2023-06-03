from django.shortcuts import render
import base64
from requests import get, post
from djbotEnvironment.settings import CLIENT_ID, CLIENT_SECRET, AUTH_URL, BASE_URL

def get_access_token():
    client_authorization = CLIENT_ID + ':' + CLIENT_SECRET
    client_authorization = base64.b64encode(client_authorization.encode())
    client_authorization = client_authorization.decode('utf-8')

    headers = {
        'Authorization': 'Basic ' + client_authorization,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = post(AUTH_URL, headers=headers, data=data)
    access_token = response.json()['access_token']

    return access_token

HEADER = { 'Authorization': 'Bearer ' + get_access_token() }

def search(request, type, query):
    params = {
        'q': query,
        'type': type,
        'limit': 10
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    print(headers)

    response = get(BASE_URL + '/search', headers=headers, params=params)
    print(response.url)

    if response.status_code == 200:
        return response.json()
    return None

def get_songs_by_artist(artist):
    artist_id = search('artist', artist)['artists']['items'][0]['id']
    params = {
        'market': 'US'
    }
    response = get(BASE_URL + '/artists/' + artist_id + '/top-tracks', headers=HEADER, params=params)
    if response.status_code == 200:    
        return response.json()
    return None

def get_genres_by_artist(artist):
    artist_id = search('artist', artist)['artists']['items'][0]['id']
    response = get(BASE_URL + '/artists/' + artist_id, headers=HEADER)
    if response.status_code == 200:   
        return response.json()['genres']
    return None

def get_albums_by_artist(artist):
    artist_id = search('artist', artist)['artists']['items'][0]['id']
    response = get(BASE_URL + '/artists/' + artist_id + '/albums', headers=HEADER)
    if response.status_code == 200:
        return response.json()    
    return None

def get_album_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(BASE_URL + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()    
    return None

def get_songs_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    params = {
        'market': 'US'
    }
    response = get(BASE_URL + '/albums/' + album_id + '/tracks', headers=HEADER, params=params)
    if response.status_code == 200:
        return response.json()    
    return None

def get_genre_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(BASE_URL + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['genres']    
    return None

def get_artist_by_artist(artist):
    artist_id = search('artist', artist)['artists']['items'][0]['id']
    response = get(BASE_URL + '/artists/' + artist_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['name']    
    return None

def get_artist_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(BASE_URL + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['artists'][0]['name']    
    return None

def get_artist_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['artists'][0]['name']    
    return None

def get_genre_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['album']['genres']    
    return None

def get_album_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['album']['name']    
    return None

def get_song_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['name']    
    return None


def index(request):
    # for printing all the songs of an artist
    #songs = get_songs_by_artist('Eminem')
    #for song in songs['tracks']:
    #    print(song['name'])

    # for printing all the genres of an artist
    genres = get_genres_by_artist('Eminem')
    for genre in genres:
        print(genre)


    # for printing all the albums of an artist
    #albums = get_albums_by_artist('Eminem')
    #for album in albums['items']:
    #    print(album['name'])
    return render(request, 'index.html')