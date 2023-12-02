# I don't know why I created this. I now have a database with much more cat data than I intended. I think now I'll
# create a website that posts photos of cats on specific pages

from urllib.error import HTTPError
from urllib.parse import urlparse

from bs4 import BeautifulSoup as bs
import pymongo
import traceback

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

import random


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


def storeInDatabase(db, content, CurrentUrl):
    try:
        # new collection
        col = db.OrganizedCatWords
        if content != '':
            doc = getSubredditInfo(CurrentUrl)
            addition = col.insert_one(doc)
            print(addition)
        else:
            print('No need to store this garbage')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False


def getSubredditInfo(subreddit_url):
    try:
        driver = webdriver.Chrome()
        driver.get(subreddit_url)

        driver.implicitly_wait(3)

        # Fetch information from the shreddit-subreddit-header
        try:
            subreddit_header = driver.find_element(By.TAG_NAME, 'shreddit-subreddit-header')

            display_name = subreddit_header.get_attribute('display-name')
            descrip = subreddit_header.get_attribute('description')
            descrip = catLike(str(descrip))
            subscribers = subreddit_header.get_attribute('subscribers')
            active_users = subreddit_header.get_attribute('active')

        except NoSuchElementException:
            print("Subreddit header not found")
            return None

        return {
            'display_name': str(display_name),
            'CatDescription': str(descrip),
            'subscribers': str(subscribers),
            'active_users': str(active_users),
            'cat-like_words': str(foundWords)
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        # Close the browser window
        driver.quit()


# This method changes the text string given in to be a "cat-like" phrase
def catLike(des):
    catifiedString = ""
    for letter in des:
        randomChance = random.randint(0, 30)
        if randomChance == 15 and letter == " ":
            catifiedString += " :3 "
        if randomChance == 20 and letter == " ":
            catifiedString += " >:0 "
        if randomChance == 25 and letter == " ":
            catifiedString += " *lick lick* "
        if randomChance == 5 and letter == " ":
            catifiedString += " HISSSSSSSSSS...  "
        catifiedString += letter
        if letter == "m":
            randNum = random.randint(0, 3)
            if randNum == 2:
                catifiedString += "oeow"
        if letter == "p":
            catifiedString += "rr"

    return catifiedString


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
    "companion", "lapcat", "purr", "nurturing", "meow",
    "feline", "whiskers", "kitty", "purring", "tailless",
    "playful", "napping", "velvet", "fluff", "curled",
    "clawing", "whisking", "sleek", "lounging", "gaze",
    "fuzzy", "naptime", "pawprints", "snooze", "prowling",
    "stealthy", "tuxedo", "curled", "curious", "graceful",
    "stealth", "prowler", "snug", "agile", "charming",
    "eyes", "prowess", "curious", "slumber", "agile",
    "tails", "sleek", "poised", "nimble", "luminary",
    "gaze", "frolic", "comfort", "trill", "vigilant",
    "shadow", "softness", "dainty", "cozy", "regal"
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
        description = ' '.join([paragraph.get_text(strip=True) for paragraph in paragraphs])
        if description:
            text_content = description
            foundWords = findSpecificWords(text_content)
            totalWords = 0
            for word in list(foundWords):
                totalWords += 1
            if foundWords:
                print(f"{foundWords}")
                print(f"DocNum:{num} : TotalWords: {totalWords}")

                storeInDb = storeInDatabase(datab, foundWords, url)
        else:
            print(f"{num} : NULL")

    except Exception as e:
        print(f"Error parsing HTML: {e}")
