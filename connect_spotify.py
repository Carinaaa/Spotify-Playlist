# Connect to spotify
# 1. Load the client id and client secret
from dotenv import load_dotenv
import os
from retrived_data import songs
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "http://127.0.0.1:3001/"
scope = "playlist-modify-public"  # or "playlist-modify-private"

# 2. Initialize Spotify with the credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

# Get your Spotify user id
user_id = sp.me()["id"]

print(user_id)

# Create a new playlist
playlist = sp.user_playlist_create(
    user=user_id,
    name="2000's Playlist",
    public=True,
    description="Created with Spotipy!"
)

print("Playlist created:", playlist["external_urls"]["spotify"])


track_uris = []

for track in songs:
    entry = sp.search(q=track + songs[track], type='track', limit=1)
    track_uris.append(entry['tracks']['items'][0]['uri'])

sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)

print("Tracks added successfully!")


