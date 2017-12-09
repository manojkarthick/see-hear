import requests

track = 'Havana'
artist = 'Camila Cabello'
api_key = 'e0f98881b038181c5a231d9d96355d22'

turl = "http://ws.audioscrobbler.com/2.0/?method=track.getinfo&artist={}&track={}&api_key={}&format=json".format(artist, track, api_key)
response = requests.get(turl)

data = response.json()

thumbnail = data['track']['album']['image'][2]['#text']
genre = data['track']['toptags']['tag'][0]['name']
listeners = data['track']['listeners']
playcount = data['track']['playcount']

print(thumbnail, genre, listeners, playcount)
