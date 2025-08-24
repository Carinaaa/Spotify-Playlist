from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from CONSTANTS import PUBLIC_PLAYLIST, REDIRECT_URI
import json

class SpotifyPlaylistCreator:
    def __init__(self):
        self.user = None
        self.playlist = None
        self.scope = None
        self.uris = []

    def get_spotify_client(self, scope: str = PUBLIC_PLAYLIST):
        """Authenticate the Spotify user."""
        load_dotenv()
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        self.scope = scope
        self.user = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=REDIRECT_URI,
                scope=self.scope
            )
        )

    def create_playlist(self, name: str, description: str):
        """Create a new Spotify playlist for the current user."""
        self.playlist = self.user.user_playlist_create(
            user=self.user.me()["id"], name=name, public=True if self.scope == PUBLIC_PLAYLIST else False, description=description
        )
        print(f"Playlist created: {self.playlist['external_urls']['spotify']}")

    def get_track_uris(self, tracks: dict):
        """Search Spotify for each track and get a list of URIs."""
        for title, artist in tracks.items():
            try:
                query = f"{title} {artist}"
                result = self.user.search(q=query, type="track", limit=1)
                items = result["tracks"]["items"]
                if items:
                    self.uris.append(items[0]["uri"])
            except Exception as e:
                print(f"Failed to find track: {title} ({e})")


    def populate_playlist(self, songs: dict, name: str = "2000's Playlist 2", description: str = "Created with Spotipy!"):
        self.get_spotify_client()
        self.create_playlist(name=name, description=description)
        self.get_track_uris(songs)

        if self.uris:
            self.user.playlist_add_items(playlist_id=self.playlist["id"], items=self.uris)
            print("Tracks added successfully!")
        else:
            print("No tracks were added.")
