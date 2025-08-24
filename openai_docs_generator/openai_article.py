import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import base64
from openai import OpenAI
from CONSTANTS import OWNER, REPO, BRANCH, SITE

class ContentWriter:
    def __init__(self):
        self.urls_all_files = []
        self.contents = {}
        self.prompts = []
        self.openai = None

    def set_target_files_urls(self):
        # Get target repo
        response = requests.get(SITE + OWNER + '/' + REPO)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Get all the files in the project
        all_files_tag = soup.find_all("div", class_="react-directory-truncate")
        all_files_set = set(files.getText() for files in all_files_tag)
        # Create URLs for each file
        self.urls_all_files = [f"https://api.github.com/repos/{OWNER}/{REPO}/contents/" + names + f"?ref={BRANCH}" for names
                          in all_files_set]
        #print(self.urls_all_files)

    def write_code(self):
        for url in self.urls_all_files:
            code_response = requests.get(url)
            code_response.raise_for_status()
            data = code_response.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            self.contents[data["name"]] = content
        del self.contents["README.md"]

    def write_prompts(self):
        self.set_target_files_urls()
        self.write_code()

        # Define system prompt
        system_prompt = ("You are a content writer using Medium.com that writes explicative /"
                         "and concise tutorials of code sources for beginner-intermediate software developers.")
        self.prompts.append(
            {"role": "system", "content": system_prompt})
        # Define user prompt
        user_prompt = ''
        for key, value in self.contents.items():
            user_prompt += f"The file is called {key}. "
            user_prompt += f"The content (code) is the following: {value} \n"
        self.prompts.append(
            {"role": "user", "content": user_prompt})

    def enable_model_OpenAI(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        self.openai = OpenAI()  # create model using the env var
        self.write_prompts()

    def create_article(self):
        self.enable_model_OpenAI()
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.prompts
        )
        return response.choices[0].message.content


cw = ContentWriter()
article = cw.create_article()
print(article)

with open("README.md", "w", encoding="utf-8") as chat_response:
    chat_response.write(article)
