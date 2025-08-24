# A Practical Guide to Billboard Scraping and Spotify Playlist Creation

In this tutorial, we'll learn how to scrape the Billboard Hot 100 chart for specific date listings of top songs and their artists, then create a Spotify playlist based on this data using Python. We'll break the task down into several files for better organization.

## Prerequisites

Before we start, make sure you have the following installed:

1. Python (version 3.x)
2. Required Python packages:
   - `requests`
   - `beautifulsoup4`
   - `spotipy`
   - `python-dotenv`

You can install these packages using pip:

```bash
pip install requests beautifulsoup4 spotipy python-dotenv
```

### File Structure

Here's how the project structure looks:

```
/project_directory/
│
├── CONSTANTS.py
├── scrap_billboard.py
├── connect_spotify.py
├── main.py
└── .gitignore
```

### The `CONSTANTS.py` File

This file holds constant values that are used throughout the project.

```python
# scope
PUBLIC_PLAYLIST = "playlist-modify-public"

# URI
REDIRECT_URI = "http://127.0.0.1:3001/"

# URL
BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"
```

### The scrap_billboard.py File

This is the core of our project where we scrape Billboard's Hot 100 chart.

Key Methods:
- set_time_period(): Prompts the user for a date and fetches the respective Billboard chart.
- set_titles(): Extracts song titles from the chart.
- set_artists()`: Extracts artist names.
- write_non_relational_db(): Coordinates the data collection process and checks for consistency between titles and artists.

Here's the complete code for scrap_billboard.py:

```python
import requests
from bs4 import BeautifulSoup
import re
from CONSTANTS import BILLBOARD_URL

class BillboardScrap:
    def __init__(self):
        self.soup = None
        self.only_titles_list = []
        self.only_artists_list = []
        self.titles_and_artists = {}

    def set_time_period(self):
        user_prompt = input("Which year do you want to travel to? Type the date YYYY-MM-DD: ")
        base_url = BILLBOARD_URL + user_prompt
        response = requests.get(base_url)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def set_titles(self):
        all_titles_tag = self.soup.find_all("h3", id="title-of-a-story")
        keywords_to_exclude = ["Songwriter(s)", "Producer(s)", "Imprint/Label"]
        all_titles_list = [entry.getText() for entry in all_titles_tag[2:-13]
                           if not any(keyword in entry.getText() for keyword in keywords_to_exclude)]
        self.only_titles_list = [re.sub(r"[\n\t]", "", title) for title in all_titles_list]

    def set_artists(self):
        all_artists_tag = self.soup.select(selector="div li ul li span")
        all_artists_list = [entry.getText() for entry in all_artists_tag[::10]]
        self.only_artists_list = [re.sub(r"[\n\t]", "", name) for name in all_artists_list]

    def write_non_relational_db(self):
        self.set_time_period()
        self.set_titles()
        self.set_artists()

        try:
            assert len(self.only_titles_list) == len(self.only_artists_list)
            for i in range(len(self.only_titles_list)):
                self.titles_and_artists[self.only_titles_list[i]] = self.only_artists_list[i]
            print("Ok, got all titles and all artists")
        except AssertionError:
            print("Approach needs to be changed, lists are not aligned...")

    def get_data(self) -> dict:
        return self.titles_and_artists
```

### The `connect_spotify.py` File

This file handles the Spotify OAuth authentication process and playlist creation.

**Key Methods**:
- `get_spotify_client()`: Authenticates the user using credentials stored in an `.env` file.
- `create_playlist()`: Creates a new playlist on the user's account.
- `get_track_uris()`: Searches for each song in Spotify and retrieves its URI.
- `populate_playlist()`: Combines all functionalities to create a playlist with the selected top songs.

Here’s the complete code for `connect_spotify.py`:

```python
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from CONSTANTS import PUBLIC_PLAYLIST, REDIRECT_URI

class SpotifyPlaylistCreator:
    def __init__(self):
        self.user = None
        self.playlist = None
        self.scope = None
        self.uris = []

    def get_spotify_client(self, scope: str = PUBLIC_PLAYLIST):
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
        self.playlist = self.user.user_playlist_create(
            user=self.user.me()["id"], name=name, public=True if self.scope == PUBLIC_PLAYLIST else False, description=description
        )
        print(f"Playlist created: {self.playlist['external_urls']['spotify']}")

    def get_track_uris(self, tracks: dict):
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
```

### The `main.py` File

This is the entry point for our program, which combines both the scraping and Spotify functionalities.

```python
from scrap_billboard import BillboardScrap
from connect_spotify import SpotifyPlaylistCreator

if __name__ == "__main__":
    bill = BillboardScrap()
    bill.write_non_relational_db()
    data = bill.get_data()

    spc = SpotifyPlaylistCreator()
    spc.populate_playlist(data)
```

### The `.gitignore` File

The `.gitignore` file is used to specify files and directories that should be ignored by version control (like sensitive environment settings).

```
.env
```

### Configuration

Make sure to create a `.env` file in your project directory containing your Spotify API credentials:

```
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
```

### Running the Project

1. Enter the desired date when prompted (in the format YYYY-MM-DD).
2. The program will scrape the Billboard data and create a Spotify playlist with the titles and artists found.

### Conclusion

By following this guide, you've learned how to integrate web scraping with an API to create a dynamic music playlist based on real-time data. This approach can serve as a foundation for various applications, such as music analytics or personalized playlist creation. Happy coding!