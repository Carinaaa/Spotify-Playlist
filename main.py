import requests
from bs4 import BeautifulSoup
import re


# Web headers
headers = {
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"}

# Ask user about the time period
user_prompt = input("Which year do you want to travel to? Type the date YYYY-MM-DD: ")
# Construct url
base_url = "https://www.billboard.com/charts/hot-100/"+user_prompt

response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Get Titles
all_titles_tag = soup.find_all("h3",id="title-of-a-story")
#print(all_titles)

# Clean the list to get only titles
keywords_to_exclude = ["Songwriter(s)", "Producer(s)", "Imprint/Label"]
all_titles_list = [entry.getText() for entry in all_titles_tag[2:-13]
                   if not any(keyword in entry.getText() for keyword in keywords_to_exclude)]
only_titles_list = [re.sub(r"[\n\t]", "", title) for title in all_titles_list]
# print(only_titles_list)

# Get artists
all_artists_tag = soup.select(selector="div li ul li span")
# print(all_artists_tag)

# Filer to get only indexes 0 then 10, 20, 30... to have only artist's name
all_artists_list = [entry.getText() for entry in all_artists_tag[::10]]
only_artists_list = [re.sub(r"[\n\t]", "", name) for name in all_artists_list]
# print(only_artists_list)

if len(only_titles_list) == len(only_artists_list):
    print("Ok, got all titles and all artists")
else:
    print("Approach needs to be changed, lists are not aligned...")

# Create a dictionary with title and artist name and save it in another file
# This file I will use in the spotify query
with open("retrived_data.py", "a") as ret_data:
    ret_data.write("songs = {\n")
    for i in range(len(only_titles_list)):
        ret_data.write('"' + only_titles_list[i] + '" : "' + only_artists_list[i] + '",\n')
    ret_data.write("}")

