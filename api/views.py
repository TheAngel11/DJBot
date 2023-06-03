from django.shortcuts import render
import environ
import base64
from requests import get, post

env = environ.Env()
environ.Env.read_env()


def get_access_token():
    client_authorization = env('CLIENT_ID') + ':' + env('CLIENT_SECRET')
    client_authorization = base64.b64encode(client_authorization.encode())
    client_authorization = client_authorization.decode('utf-8')

    headers = {
        'Authorization': 'Basic ' + client_authorization,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = post(env('AUTH_URL'), headers=headers, data=data)
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

    response = get(env('BASE_URL') + '/search', headers=headers, params=params)
    print(response.url)

    if response.status_code == 200:
        return response.json()
    return None




def get_songs_by_playlist(request, name):
    params = {
        'q': name,
        'type': 'playlist',
        'limit': 1
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    response = get(env('BASE_URL') + '/search', headers=headers, params=params)
    id = response.json()['playlists']['items'][0]['id']

    response = get(env('BASE_URL') + '/playlists/' + id, headers=headers)
    print(response.url)

    if response.status_code == 200:
        result = response.json()
        #print(result)
        songs = []
        if result['tracks']['total'] == 0:
            return None
        elif result['tracks']['total'] <= result['tracks']['limit']:
            for i in range(result['tracks']['total']):
                songs.append(result['tracks']['items'][i]['track']['name'])
        else:
            for i in range(result['tracks']['limit']):
                songs.append(result['tracks']['items'][i]['track']['album']['name'])
        return songs
    return None


def get_genres_by_artist(artist):
    artist_id = search('artist', artist)['artists']['items'][0]['id']
    response = get(env('BASE_URL') + '/artists/' + artist_id, headers=HEADER)
    if response.status_code == 200:   
        return response.json()['genres']
    return None


def get_album_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(env('BASE_URL') + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()    
    return None

def get_songs_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    params = {
        'market': 'US'
    }
    response = get(env('BASE_URL') + '/albums/' + album_id + '/tracks', headers=HEADER, params=params)
    if response.status_code == 200:
        return response.json()    
    return None

def get_genre_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(env('BASE_URL') + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['genres']    
    return None

def get_artist_by_artist(request, artist):    
    artist_id = search(request, 'artist', artist)['artists']['items'][0]['id']
    response = get(env('BASE_URL') + '/artists/' + artist_id + '/related-artists', headers={ 'Authorization': 'Bearer ' + request.session['access_token']})
    print(request.session['access_token'])
    print(response.url)
    if response.status_code == 200:    
        result = response.json()
        artists = []

        total = len(result['artists'])

        if total == 0:
            return None
        else:
            for i in range(total):
                artists.append(result['artists'][i]['name']) 
        return artists
    return None

def get_artist_by_genre(request, genre):   
    params = {
        'q': 'genre:"' + genre + '"',
        'type': 'artist',
        'limit': 20
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    response = get(env('BASE_URL') + '/search', headers=headers, params=params)
    print(response.url)

    if response.status_code == 200:
        result = response.json()
        print(result)
        artists = []
        if result['artists']['total'] == "0":
            return None
        elif result['artists']['total'] <= result['artists']['limit']:
            for i in range(result['artists']['total'] - 1):
                artists.append(result['artists']['items'][i]['name'])
        else:
            for i in range(result['artists']['limit']):
                artists.append(result['artists']['items'][i]['name'])
        return artists
    return None

def get_album_by_genre(request, genre):   
    params = {
        'q': 'genre:"' + genre + '"',
        'type': 'album',
        'limit': 10,
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    response = get(env('BASE_URL') + '/search', headers=headers, params=params)
    print(response.url)

    if response.status_code == 200:
        result = response.json()
        print(result)
        albums = []
        for i in range(result['total'] - 1):
            albums.append(result['albums']['items'][i]['name'])
        return albums
    return None

def get_album_by_artist(request, artist):    
    artist_id = search(request, 'artist', artist)['artists']['items'][0]['id']
    response = get(env('BASE_URL') + '/artists/' + artist_id + '/albums', headers={ 'Authorization': 'Bearer ' + request.session['access_token']})
    if response.status_code == 200:    
        result = response.json()
        print(result)
        albums = []
        for i in range(result['limit'] - 1):
            albums.append(result['items'][i]['name']) 
        return albums
    return None

def get_artist_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(env('BASE_URL') + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['artists'][0]['name']    
    return None

def get_artist_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(env('BASE_URL') + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['artists'][0]['name']    
    return None

def get_genre_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(env('BASE_URL') + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['album']['genres']    
    return None

def get_album_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(env('BASE_URL') + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['album']['name']    
    return None

def get_song_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(env('BASE_URL') + '/tracks/' + song_id, headers=HEADER)
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