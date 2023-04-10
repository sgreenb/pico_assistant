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
        time.sleep(1) #unnecessary?
    else:
        pass

def play_song(song_query, client_id=spotify_keys[0], client_secret=spotify_keys[1], device_id=spotify_keys[3]):
    # Set up the Spotify API client
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri="http://localhost:3000",
                                                   scope="user-modify-playback-state,user-read-playback-state"))
    # Search for the song
    results = sp.search(q=song_query, limit=3, type='track')  # Increase the limit to get more results
    if not results['tracks']['items']:
        print("No song found")
        return
    # Filter the results based on popularity
    popular_songs = sorted(results['tracks']['items'], key=lambda x: x['popularity'], reverse=True)
    song_uri = popular_songs[0]['uri']  # Get the URI of the most popular song
    
    # Get the song's URI
    song_uri = results['tracks']['items'][0]['uri']
    # Check if there is a device available for playback
    try:
        sp.transfer_playback(device_id)
        time.sleep(1)  # Wait for the transfer to complete
        sp.start_playback(device_id=device_id, uris=[song_uri])
    except:
        print("No device found")

def play_item(search_query, search_type='track', client_id=spotify_keys[0], client_secret=spotify_keys[1], device_id=spotify_keys[3]):
    # Set up the Spotify API client
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri="http://localhost:3000",
                                                   scope="user-modify-playback-state,user-read-playback-state"))

    # Search for the item
    results = sp.search(q=search_query, limit=1, type=search_type)
    if not results[search_type + 's']['items']:
        print(f"No {search_type} found")
        return

    # Get the item's URI
    item_uri = results[search_type + 's']['items'][0]['uri']

    # Check if there is a device available for playback
    try:
        sp.transfer_playback(device_id)
        time.sleep(1)  # Wait for the transfer to complete

        if search_type == 'track':
            sp.start_playback(device_id=device_id, uris=[item_uri])
        elif search_type == 'artist':
            top_tracks = sp.artist_top_tracks(item_uri)
            track_uris = [track['uri'] for track in top_tracks['tracks']]
            sp.start_playback(device_id=device_id, uris=track_uris)
        else:
            print("Invalid search type")
            return
    except Exception as e:
        print(f"Error during playback: {e}")

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
    elif action == 'resume':
        sp.start_playback(device_id=device_id)
    else:
        print("Invalid action. Please provide a valid action: 'volume', 'pause', 'resume, or 'next'.")

def spotify_agent(prompt):
    completion = openai.ChatCompletion.create(
    model = "gpt-4",
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You control a music app based on a user request.\
                     You reply with a song name or artist to be played, or an action to be taken.\
                     If the user wants to play a song or artist reply in the format: 'Song name - Artist' or 'Artist'.\
                     If the user wants to change the volume reply in the format: 'volume | volume level' where the volume level is a number between 1 and 100.\
                     If the user wants to pause the song reply: 'pause'.\
                     If the user wants to resume or unpause a song reply: 'resume'.\
                     If the user wants to play the next song reply: 'next'" 
                    },
                    {"role":"user", "content": prompt},
                    ] 
        )
    reply_content = completion.choices[0].message.content
    open_spotify_windows()
    if "|" in reply_content:
        volume_data = reply_content.strip().split('|')
        volume_level = int(volume_data[1])
        control_playback("volume", volume_level)
    elif reply_content == "pause":
        control_playback("pause")
    elif reply_content == "next":
        control_playback("next")
    elif reply_content == "resume":
        control_playback("resume")
    elif "-" in reply_content:
        play_song(reply_content)
        return "Playing " + reply_content
    else:
        play_item(reply_content, search_type="artist")
        return "Playing " + reply_content