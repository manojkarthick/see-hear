from pymongo import MongoClient
import requests
import urllib
import json
from watson_developer_cloud import ToneAnalyzerV3
import os
import csv

# Global Params

# APP IDS & KEYS
client_id = '6858ab75d972444f8ffe42b2014e5919'
client_secret = '2873d66f9af54d5d8930b2681c73b6ea'
last_fm_api_key = 'e0f98881b038181c5a231d9d96355d22'
watson_username = 'f6f09fec-0cb6-49d9-8e20-7f72074df11a'
watson_password = 'zohAscsqYXQl'
watson_version = '2017-09-26'

# URLs
access_token_url = 'https://accounts.spotify.com/api/token'
search_url = 'https://api.spotify.com/v1/search?{}'
audio_features_url = 'https://api.spotify.com/v1/audio-features/'
last_fm_url = 'http://ws.audioscrobbler.com/2.0/?method=track.getinfo&artist={}&track={}&api_key={}&format=json'

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
    record['Title'] = title.rstrip()
    record['Artist'] = track_artist
    i = 3
    for audio_feature in audio_features:
        record[data_features[i]] = audio_details[audio_feature]
        i += 1
    return record


def get_last_fm_data(record):
    artist = record['Artist']
    track = record['Title']
    turl = last_fm_url.format(artist, track, last_fm_api_key)
    response = requests.get(turl)

    fm_data = response.json()
    try:
        record['Thumbnail'] = fm_data['track']['album']['image'][2]['#text']
    except KeyError:
        record['Thumbnail'] = ''
    except IndexError:
        record['Thumbnail'] = ''
    try:
        record['Genre'] = fm_data['track']['toptags']['tag'][0]['name']
    except KeyError:
        record['Genre'] = ''
    except IndexError:
        record['Genre'] = ''
    try:
        record['Listeners'] = fm_data['track']['listeners']
    except KeyError:
        record['Listeners'] = -1
    try:
        record['Playcount'] = fm_data['track']['playcount']
    except KeyError:
        record['Playcount'] = -1
    return record


def analyze_tone_over_lyrics():
    tone_analyzer = ToneAnalyzerV3(version='2017-09-26', username='f6f09fec-0cb6-49d9-8e20-7f72074df11a',
                                   password='zohAscsqYXQl')
    songs = see_hear_db.Rock.find()
    for song in songs:
        song_id = song['ID']
        print song_id
        lyrics = song['Lyrics']
        tone = tone_analyzer.tone(lyrics, tones='emotion', content_type='text/plain')
        see_hear_db.Rock.update({'ID': song_id}, {'$set': {'Tone': tone}})


def insert_tweet_sentiment():
    for filename in os.listdir('../datasets/hot100-tweets/'):
        with open('../datasets/hot100-tweets/' + filename, 'rb') as csv_file:
            song_id = filename.split('.txt')[0]
            print song_id
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                record = dict()
                record['ID'] = song_id
                record['Compound'] = float(row[-1][:-1])
                record['Neutral'] = float(row[-2])
                record['Negative'] = float(row[-3])
                record['Positive'] = float(row[-4])
                record['Coordinates'] = row[-5]
                record['Places'] = row[-6]
                tweet = ''
                for i in range(0, len(row)-6):
                    tweet = tweet + row[i]
                record['Tweet'] = tweet[2:len(tweet)-1]
                see_hear_db.Tweets.insert_one(record)


if __name__ == '__main__':
    access_token = get_access_token()
    track_file = open('../extras/Country.txt', 'r')
    for track_title in track_file:
        data = get_spotify_data(track_title)
        data = get_last_fm_data(data)
        print data['ID']
        see_hear_db.Country.insert_one(data)
    analyze_tone_over_lyrics()
    insert_tweet_sentiment()
