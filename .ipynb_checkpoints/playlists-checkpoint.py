import csv
import os

import spotipy
import spotipy.util as util

scope = 'user-library-read user-library-modify playlist-read-private'
username = '21jytlvp5orepkujthaapp7cy'
token = util.prompt_for_user_token(
    username,
    scope,
    client_id='13113033cada447986869fcda8b4a6f0',
    client_secret='c7b8dcecc92b4a06abbb93ababa83e08',
    redirect_uri='http://localhost:8080/')


def writePlaylistToCSV(csv_file, csv_columns, dict_data):
    try:
        with open('playlists.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, lineterminator='\n')
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError as e:
        print("IOError:" + e)


csv_columns = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
               'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'type',
               'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature']
features = []

if token:
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username)

    # for each playlist in user's library
    for playlist in playlists['items']:
        # if user owns playlist
        if playlist['owner']['id'] == username:
            # get the playlist
            curr = sp.user_playlist(username, playlist['id'])
            tracks = curr['tracks']
            songs = tracks['items']

            # add song ids and names to list
            for i in range(0, len(songs)):
                if songs[i]['track']['id'] is not None:
                    song_id = songs[i]['track']['id']
                    audio_features = sp.audio_features(song_id)
                    for feature in audio_features:
                        features.append(feature)

    currentPath = os.getcwd()
    csv_file = currentPath + "playlists.csv"
    writePlaylistToCSV(csv_file, csv_columns, features)

else:
    print("Can't get token for", username)
