from pymongo import MongoClient
import requests
import json
import urllib

# Global Params

# APP IDS
client_id = '6858ab75d972444f8ffe42b2014e5919'
client_secret = '2873d66f9af54d5d8930b2681c73b6ea'

# URLs
access_token_url = 'https://accounts.spotify.com/api/token'
search_url = 'https://api.spotify.com/v1/search?{}'
audio_features_url = 'https://api.spotify.com/v1/audio-features/'

# Features
data_features = ['ID', 'Title', 'Artist', 'Danceability', 'Energy', 'Key', 'Loudness', 'Mode', 'Speechiness',
                 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 'Duration']

audio_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                  'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']

client = MongoClient()
see_hear_db = client.SEEHEAR


# Function to check the received response
def check_response_message(response):
    if response.status_code == 200:
        return
    else:
        j_resp = json.loads(response.text)
        raise Exception(j_resp['error']['message'])


# Function to get the short lived access token
def get_access_token():
    body_params = {'grant_type': 'client_credentials'}
    response = requests.post(access_token_url, data=body_params, auth=(client_id, client_secret))
    j_resp = json.loads(response.text)
    return str(j_resp['access_token'])


def get_track_id(title):
    args = {"q": title, "type": "track"}
    request = search_url.format(urllib.urlencode(args))
    header = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(request, headers=header)
    check_response_message(response)
    return json.loads(response.text)
    return str(j_resp['tracks']['items'][0]['id'])


def get_track_audio_features(tr_id):
    url = audio_features_url + tr_id
    header = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=header)
    check_response_message(response)
    return json.loads(response.text)


def get_spotify_data(title):

    track_details = get_track_id(title)
    track_id = str(track_details['tracks']['items'][0]['id'])
    track_artist = str(track_details['tracks']['items'][0]['artists'][0]['name'])

    audio_details = get_track_audio_features(track_id)
    record = dict()
    record['ID'] = track_id
    record['Title'] = track_title
    record['Artist'] = track_artist
    i = 3
    for audio_feature in audio_features:
        record[data_features[i]] = audio_details[audio_feature]
        i += 1
    return record

if __name__ == '__main__':
    access_token = 'BQATb_Bxf8UCFKJeTFl8OD3-jqd0Xaw-JcnBrG3hQ_7r4rsLYBHW9HMDmK18nTyzflyZh-kpaR84diS2FV0'  # get_access_token()
    track_title = 'Havana'
    spotify_data = get_spotify_data(track_title.rstrip())
    see_hear_db.songs.insert_one(spotify_data)