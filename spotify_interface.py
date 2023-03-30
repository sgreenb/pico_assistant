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
    else:
        pass

def play_song(song_query, client_id=spotify_keys[0], client_secret=spotify_keys[1], device_id=spotify_keys[3]):
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

def play_top_result(query, client_id=spotify_keys[0], client_secret=spotify_keys[1], device_id=spotify_keys[3]):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri="http://localhost:3000",
                                                   scope="user-modify-playback-state,user-read-playback-state"))

    content_types = ["track", "album", "artist", "playlist"]
    top_results = {}

    # Search for each content type and store the top result
    for content_type in content_types:
        results = sp.search(q=query, limit=1, type=content_type)
        if results[content_type + 's']['items']:
            item = results[content_type + 's']['items'][0]
            if content_type == 'artist':
                score = item['followers']['total']
            elif content_type == 'playlist':
                score = item['tracks']['total']
            else:
                score = item.get('popularity', 0)  # Use default value of 0 if 'popularity' field is missing
            top_results[content_type] = (item, score)

    # Find the top result with the highest popularity
    top_content, _ = max(top_results.values(), key=lambda x: x[1])
    top_content_type = [k for k, v in top_results.items() if v[0] == top_content][0]
    top_content_uri = top_content['uri']

    try:
        sp.transfer_playback(device_id)
        time.sleep(1)
        if top_content_type == "track":
            sp.start_playback(device_id=device_id, uris=[top_content_uri])
        elif top_content_type == "artist":
            # Play the artist's top tracks
            top_tracks = sp.artist_top_tracks(top_content_uri)
            track_uris = [track['uri'] for track in top_tracks['tracks']]
            sp.start_playback(device_id=device_id, uris=track_uris)
        elif top_content_type in ["album", "playlist"]:
            sp.start_playback(device_id=device_id, context_uri=top_content_uri)
        else:
            print("Content type not supported for playback")
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
    if "volume" in reply_content:
        volume_data = reply_content.strip().split('|')
        volume_level = int(volume_data[1])
        control_playback("volume", volume_level)
    elif reply_content == "pause":
        control_playback("pause")
    elif reply_content == "next":
        control_playback("next")
    elif reply_content == "resume":
        control_playback("resume")
    else:
        play_top_result(reply_content)