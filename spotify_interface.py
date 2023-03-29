import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
import psutil

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

#spotify_keys.txt contains the Client ID, Client secret, path to Spotify exe, and device ID each on a newline.
spotify_keys = []
spotify_keys += open("spotify_keys.txt", "r").read().split("\n")

def is_spotify_running():
    for process in psutil.process_iter():
        try:
            if 'spotify' in process.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def open_spotify_windows():
    if not is_spotify_running():
        spotify_path = spotify_keys[2]
        os.startfile(spotify_path)
        time.sleep(1)

def play_song(song_query, client_id=spotify_keys[0], client_secret=spotify_keys[1], device_id = spotify_keys[3]):
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
    try:
        sp.transfer_playback(device_id)
        time.sleep(1)  # Wait for the transfer to complete
        sp.start_playback(device_id=device_id, uris=[song_uri])
    except:
        print("No device found")

def control_playback(action, value=None,client_id=spotify_keys[0], client_secret=spotify_keys[1], device_id=spotify_keys[3]):
    # Set up the Spotify API client
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri="http://localhost:3000",
                                                   scope="user-modify-playback-state,user-read-playback-state"))
    if action == 'volume':
        if value is not None and 0 <= value <= 100:
            sp.volume(value, device_id=device_id)
        else:
            print("Invalid volume value. It should be between 0 and 100.")
    elif action == 'pause':
        sp.pause_playback(device_id=device_id)
    elif action == 'next':
        sp.next_track(device_id=device_id)
    else:
        print("Invalid action. Please provide a valid action: 'volume', 'pause', or 'next'.")

def spotify_agent(prompt):
    completion = openai.ChatCompletion.create(
    model = "gpt-4",
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You identify a song, playlist, or artist based on a user request. The output must be in the format: 'Song name - Artist' or 'Artist'"},
                    {"role":"user", "content": prompt},
                    ] 
        )
    spotify_query = completion.choices[0].message.content
    open_spotify_windows()
    play_song(spotify_query)