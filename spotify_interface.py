import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os

#spotify_keys.txt contains the Client ID, Client secret, path to Spotify exe, and device ID each on a newline.
spotify_keys = []
spotify_keys += open("spotify_keys.txt", "r").read().split("\n")

def open_spotify_windows():
    spotify_path = spotify_keys[2]
    os.startfile(spotify_path)
    time.sleep(1)

def play_song(song_query, client_id, client_secret):
    # Set up the Spotify API client
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri="http://localhost:3000",
                                                   scope="user-modify-playback-state,user-read-playback-state"))

    # Search for the song
    results = sp.search(q=song_query, limit=1, type='track')
    if not results['tracks']['items']:
        print("No song found")
        return

    # Get the song's URI
    song_uri = results['tracks']['items'][0]['uri']

    # Check if there is a device available for playback
    device_id = spotify_keys[3]
    try:
        sp.transfer_playback(device_id)
        time.sleep(1)  # Wait for the transfer to complete
        sp.start_playback(device_id=device_id, uris=[song_uri])
    except:
        print("No device found")

 
client_id = spotify_keys[0]
client_secret = spotify_keys[1]
open_spotify_windows()
song_query = "Manu Chao"
play_song(song_query, client_id, client_secret)

