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
        """Search Billboard for timeline for top songs."""
        user_prompt = input("Which year do you want to travel to? Type the date YYYY-MM-DD: ")
        base_url = BILLBOARD_URL + user_prompt
        response = requests.get(base_url)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def set_titles(self):
        """Search Billboard for titles of top songs."""
        # Get Titles
        all_titles_tag = self.soup.find_all("h3", id="title-of-a-story")
        # Clean the list to get only titles
        keywords_to_exclude = ["Songwriter(s)", "Producer(s)", "Imprint/Label"]
        all_titles_list = [entry.getText() for entry in all_titles_tag[2:-13]
                           if not any(keyword in entry.getText() for keyword in keywords_to_exclude)]
        self.only_titles_list = [re.sub(r"[\n\t]", "", title) for title in all_titles_list]

    def set_artists(self):
        """Search Billboard for top songs artists."""
        # Get artists
        all_artists_tag = self.soup.select(selector="div li ul li span")
        # Filer to get only indexes 0 then 10, 20, 30... to have only artist's name
        all_artists_list = [entry.getText() for entry in all_artists_tag[::10]]
        self.only_artists_list = [re.sub(r"[\n\t]", "", name) for name in all_artists_list]

    def write_non_relational_db(self):
        """Create a new file with a dictionary for the current songs."""
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
