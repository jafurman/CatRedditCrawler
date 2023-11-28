# I don't know why I created this. I now have a database with much more cat data than I intended. I think now I'll
# create a website that posts photos of cats on specific pages

from urllib.error import HTTPError
from urllib.parse import urlparse

from bs4 import BeautifulSoup as bs
import pymongo
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # database connection is localhost client.[databaseName]
        db = client.CatDB
        print(f"DB : CONNECTED")
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


def getAllPages(db):
    try:
        # Collection
        col = db.Subreddits
        # Find all documents and project only the 'html' field
        html_cursor = col.find({}, {'html': 1, 'Url': 1})
        return list(html_cursor)
    except Exception as error:
        print("Mongo DB Error")
        return None


def findSpecificWords(paragraph):
    paragraph = paragraph.lower()
    sourcedWords = [word for word in searchWords if word in paragraph]
    return sourcedWords


def storeInDatabase(db, title ,content):
    try:
        # new collection
        col = db.OrganizedCatWords
        if content != '':
            doc = {
                "subreddit": str(title),
                "content": str(content),
            }
            addition = col.insert_one(doc)
        else:
            print('No need to store this garbage')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False


def extractSubredditName(url):
    try:
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        if len(path_parts) >= 2 and path_parts[0] == 'r':
            return path_parts[1]
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def getTitleWithUrl(subreddit_url):
    try:
        driver = webdriver.Chrome()
        driver.get(subreddit_url)

        driver.implicitly_wait(3)

        # Fetch the title directly
        title = driver.title
        return title.strip() if title else None

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        # Close the browser window
        driver.quit()


# ---------------------------- VV main method essentially VV----------------------------------#

# Get DB Connection
datab = connectDataBase()

# Establish a list of words the user is trying to find from the crawled subreddits
searchWords = [
    "cat", "kitten", "tabby", "whisker", "purr",
    "meow", "furball", "claw", "fur",
    "tail", "nap", "litter", "scratch", "paw",
    "whisker", "persian", "mane", "hiss", "cute",
    "little",
    "playful", "cuddle", "knead", "curious", "play",
    "soft", "cozy", "siamese", "mouse", "box",
    "cozy", "furry", "stretch", "domestic", "ginger",
    "calico", "pounce", "slinky", "balinese", "bobtail",
    "hug", "friendly", "sphynx", "playful", "food",
    "cuddly", "talk", "snuggle", "nip", "mewl",
    "slink", "tailor", "sleep", "cute", "hiss",
    "attitude", "tabby", "lick", "play", "tomcat",
    "food", "striped", "purr", "walk", "nap",
    "manecoon", "playpen", "nap", "fuzzy", "positive",
    "cat", "home", "whiskers", "playful", "nap",
    "cute", "paw", "tail", "fur", "meow",
    "stretch", "cuddle", "kitty", "purr", "cat",
    "tabby", "nap", "play", "purr", "knead",
    "play", "hiss", "lick", "snuggle", "pounce",
    "adorable", "kitten", "curious", "soft", "sleek",
    "mysterious", "soft", "pawprint", "cuddly", "fuzzy",
    "serene", "sly", "regal", "majestic", "hunter",
    "sweet", "charming", "playful", "sneaky", "sleepy",
    "alert", "sassy", "graceful", "loving", "independent",
    "companion", "lapcat", "purr", "nurturing", "meow"
]

# Open Documents and parse
try:
    pages = getAllPages(datab)
except HTTPError as e:
    print(e)


num = 0
for entry in pages:
    try:
        num += 1
        url = entry.get("Url")
        pageHtml = entry.get("html")
        soupy = bs(pageHtml, "html.parser")
        paragraphs = soupy.find_all('p')
        pageTitle = getTitleWithUrl(url)
        description = ' '.join([paragraph.get_text(strip=True) for paragraph in paragraphs])
        if description:
            text_content = description
            foundWords = findSpecificWords(text_content)
            if foundWords:
                print(f"{num} : {foundWords}")

                storeInDb = storeInDatabase(datab, pageTitle,foundWords)
        else:
            print(f"{num} : NULL")

    except Exception as e:
        print(f"Error parsing HTML: {e}")
