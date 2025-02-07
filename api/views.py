from django.shortcuts import render
import base64
import random
from requests import get, post
import random
from djbotEnvironment.settings import CLIENT_ID, CLIENT_SECRET, AUTH_URL, BASE_URL


# function to get the access token
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

# function to search for a song, artist, album, playlist, or genre
def search(request, type, query):
    params = {
        'q': query,
        'type': type,
        'limit': 10
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }
    print(headers)

    
    response = get(BASE_URL + '/search', headers=headers, params=params)
    

    if response.status_code == 200:
        return response.json()
    return None

# function to get the songs by a playlist
def get_songs_by_playlist(request, name):
    params = {
        'q': name,
        'type': 'playlist',
        'limit': 10
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    response = get(BASE_URL + '/search', headers=headers, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    if data['playlists']['total'] == 0:
        return None
    elif data['playlists']['total'] <= data['playlists']['limit']:
        id = data['playlists']['items'][random.randint(0,data['playlists']['total']-1)]['id']
    else:
        id = data['playlists']['items'][random.randint(0,data['playlists']['limit']-1)]['id']

    response = get(BASE_URL + '/playlists/' + id, headers=headers)

    if response.status_code == 200:
        result = response.json()
        songs = []
        if result['tracks']['total'] == 0:
            return None
        elif result['tracks']['total'] <= result['tracks']['limit']:
            for i in range(result['tracks']['total']):
                if result['tracks']['items'][i]['track'] != None:
                    songs.append(result['tracks']['items'][i]['track']['name'])
        else:
            for i in range(result['tracks']['limit']):
                if result['tracks']['items'][i]['track'] != None:
                    songs.append(result['tracks']['items'][i]['track']['album']['name'])
        return songs
    return None

# function to get the genre by artist
def get_genres_by_artist(artist):
    artist_id = search('artist', artist)['artists']['items'][0]['id']
    response = get(BASE_URL + '/artists/' + artist_id, headers=HEADER)
    if response.status_code == 200:   
        return response.json()['genres']
    return None

# function to get the lbum by another album
def get_album_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(BASE_URL + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()    
    return None

#function to get the songs by album
def get_songs_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    params = {
        'market': 'US'
    }
    response = get(BASE_URL + '/albums/' + album_id + '/tracks', headers=HEADER, params=params)
    if response.status_code == 200:
        return response.json()    
    return None

# function to get the genre by album
def get_genre_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(BASE_URL + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['genres']    
    return None

# function to get the artist by another artist
def get_artist_by_artist(request, artist):    
    data = search(request, 'artist', artist)
    if data == None:
        return None
    
    if data['artists']['total'] == 0:
        return None
    else:
        artist_id = data['artists']['items'][0]['id']
    
    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }
    print(headers)

    response = get(BASE_URL + '/artists/' + artist_id + '/related-artists', headers=headers)
    
    if response.status_code == 200:    
        result = response.json()
        print(response.url)
        artists = []

        total = len(result['artists'])

        if total == 0:
            return None
        else:
            for i in range(total):
                artists.append(result['artists'][i]['name']) 
        return artists
    return None

# function to get the artist by genre
def get_artist_by_genre(request, genre):   
    params = {
        'q': 'genre:"' + genre + '"',
        'type': 'artist',
        'limit': 20
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    response = get(BASE_URL + '/search', headers=headers, params=params)

    if response.status_code == 200:
        result = response.json()
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

# function to get the artist by playlist
def get_artist_by_playlist(request, name):
    params = {
        'q': name,
        'type': 'playlist',
        'limit': 10
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    response = get(BASE_URL + '/search', headers=headers, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    if data['playlists']['total'] == 0:
        return None
    elif data['playlists']['total'] <= data['playlists']['limit']:
        id = data['playlists']['items'][random.randint(0,data['playlists']['total']-1)]['id']
    else:
        id = data['playlists']['items'][random.randint(0,data['playlists']['limit']-1)]['id']

    response = get(BASE_URL + '/playlists/' + id, headers=headers)

    if response.status_code == 200:
        result = response.json()
        songs = []
        if result['tracks']['total'] == 0:
            return None
        elif result['tracks']['total'] <= result['tracks']['limit']:
            for i in range(result['tracks']['total']):
                if result['tracks']['items'][i]['track'] != None:
                    songs.append(result['tracks']['items'][i]['track']['album']['artists'][0]['name'])
        else:
            for i in range(result['tracks']['limit']):
                if result['tracks']['items'][i]['track'] != None:
                    songs.append(result['tracks']['items'][i]['track']['album']['artists'][0]['name'])
        return songs
    return None

# function to get the album by genre
def get_album_by_genre(request, genre):   
    params = {
        'q': 'genre:"' + genre + '"',
        'type': 'album',
        'limit': 10,
    }

    headers = { 'Authorization': 'Bearer ' + request.session['access_token'] }

    response = get(BASE_URL + '/search', headers=headers, params=params)

    if response.status_code == 200:
        result = response.json()
        albums = []
        for i in range(result['total'] - 1):
            albums.append(result['albums']['items'][i]['name'])
        return albums
    return None

# function to get the album by artist
def get_album_by_artist(request, artist):    
    artist_id = search(request, 'artist', artist)['artists']['items'][0]['id']
    response = get(BASE_URL + '/artists/' + artist_id + '/albums', headers={ 'Authorization': 'Bearer ' + request.session['access_token']})
    if response.status_code == 200:    
        result = response.json()
        albums = []
        for i in range(result['limit'] - 1):
            albums.append(result['items'][i]['name']) 
        return albums
    return None

# function to get the artist by album
def get_artist_by_album(album):
    album_id = search('album', album)['albums']['items'][0]['id']
    response = get(BASE_URL + '/albums/' + album_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['artists'][0]['name']    
    return None

# function to get the artist by song
def get_artist_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['artists'][0]['name']    
    return None

# function to get the genre by song
def get_genre_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['album']['genres']    
    return None

# function to get the album by song
def get_album_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['album']['name']    
    return None

# function to get the song by song
def get_song_by_song(song):
    song_id = search('track', song)['tracks']['items'][0]['id']
    response = get(BASE_URL + '/tracks/' + song_id, headers=HEADER)
    if response.status_code == 200:
        return response.json()['name']    
    return None

# index page
def index(request):
    # for printing all the songs of an artist
    #songs = get_songs_by_artist('Eminem')
    #for song in songs['tracks']:
    #    print(song['name'])

    # for printing all the genres of an artist
    #genres = get_genres_by_artist('Eminem')
    #for genre in genres:
     #   print(genre)


    # for printing all the albums of an artist
    #albums = get_albums_by_artist('Eminem')
    #for album in albums['items']:
    #    print(album['name'])
    return render(request, 'index.html')