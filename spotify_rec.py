import csv
import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

import spotipy
import spotipy.util as util

spotify_playlist_id = '37i9dQZEVXcHLzzqRkcgrd'

username = '21jytlvp5orepkujthaapp7cy'
scope = 'user-library-read user-library-modify playlist-read-private playlist-modify-private playlist-modify-public'
client_id = '13113033cada447986869fcda8b4a6f0'
client_secret = 'c7b8dcecc92b4a06abbb93ababa83e08'
redirect_uri = 'http://localhost:8080/'

token = util.prompt_for_user_token(
    username,
    scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri)


def writePlaylistToCSV(csv_file, csv_columns, dict_data):
    try:
        with open('playlists.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, lineterminator='\n')
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError as e:
        print("IOError:" + e)


# def show_tracks(results):
#     for i, item in enumerate(results['items']):
#         track = item['track']
#         print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))


csv_columns = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
               'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'type',
               'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature', 'like']

features = []  # list to contain the audio features of playlists
spotify_playlist_features = []  # list to contain the AF of selected spotify playlist

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    playlists = sp.user_playlists(username)

    # for each playlist in user's library
    for playlist in playlists['items']:
        # if user owns playlist
        if playlist['owner']['id'] == username:
            # get the playlist
            curr = sp.user_playlist(username, playlist['id'])
            tracks = curr['tracks']

            while tracks['next']:
                songs = tracks['items']

                # add fav song ids and names to list
                for i in range(0, len(songs)):
                    if songs[i]['track']['id'] is not None:
                        audio_features = sp.audio_features(songs[i]['track']['id'])
                        for feature in audio_features:
                            if feature is not None:
                                if playlist['name'] == 'NotFavourite':
                                    feature['like'] = 0
                                else:
                                    feature['like'] = 1
                                features.append(feature)
                tracks = sp.next(tracks)

    currentPath = os.getcwd()
    csv_file = currentPath + "playlists.csv"
    writePlaylistToCSV(csv_file, csv_columns, features)

    spotify_playlist = sp.user_playlist(username, spotify_playlist_id, fields='tracks,next')
    tracks = spotify_playlist['tracks']
    songs = tracks['items']
    for i in range(0, len(songs)):
        if songs[i]['track']['id'] is not None:
            audio_features = sp.audio_features(songs[i]['track']['id'])
            for feature in audio_features:
                if feature is not None:
                    spotify_playlist_features.append(feature)

    # actual machine learning

    recommended_ids = []  # list to contain ids of recommended songs

    # df for playlists
    df = pd.DataFrame(data=spotify_playlist_features, columns=csv_columns)
    testData = df.drop(['type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature', 'like'], axis=1)
    # print(testData.head())

    # df for data of user playlists
    dataset = pd.read_csv('playlists.csv')
    dataset = dataset.drop(['type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature'], axis=1)
    # print(dataset.head())

    X = dataset.iloc[:, :11]
    y = dataset.iloc[:, [-1]]

    classifier = DecisionTreeClassifier(criterion='entropy')
    classifier.fit(X, y)

    # predict which songs you might like
    pred = classifier.predict(testData)
    for i, recommend in enumerate(pred):
        if recommend == 1:
            recommended_ids.append(df.loc[i]['id'])

    # is there already a recommended playlist?
    recommended_playlist_id = ''
    my_playlists = sp.current_user_playlists(limit=50)
    for playlist in my_playlists['items']:
        if playlist['name'] == 'Recommended':
            recommended_playlist_id = playlist['id']

    if recommended_playlist_id == '':
        # create RECOMMENDED Playlist
        recommend_playlist = sp.user_playlist_create(username,
                                                     'Recommended')
        recommended_playlist_id = recommend_playlist['id']

    results = sp.user_playlist_add_tracks(username,
                                          recommended_playlist_id,
                                          recommended_ids)
else:
    print("Can't get token for", username)
