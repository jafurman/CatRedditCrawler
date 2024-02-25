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

import numpy as np
from keras.preprocessing import image
from keras.applications import vgg16
import os
from PIL import Image
import requests
from io import BytesIO
from urllib.parse import urlparse, parse_qs


processed_images = set()


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # database connection is localhost client.[databaseName]
        db = client.CatDB
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


def getExcessData(dictionary):
    found_words_list = dictionary.get('cat-like_words', [])

    # Bonuses
    catBonus = len(dictionary.get('cat-like_words', ['cat']))
    catBonus += len(dictionary.get('cat-like_words', ['cats']))
    catBonus += len(dictionary.get('cat-like_words', ['kitten']))
    catBonus += len(dictionary.get('cat-like_words', ['kitty']))
    catBonus += len(dictionary.get('cat-like_words', ['kittens']))
    catBonus += len(dictionary.get('cat-like_words', ['kitties']))
    catBonus += len(dictionary.get('cat-like_words', ['meow']))
    catBonus += len(dictionary.get('cat-like_words', ['meows']))
    catBonus += len(dictionary.get('cat-like_words', ['purr']))
    catBonus += len(dictionary.get('cat-like_words', ['purrs']))
    catBonus += len(dictionary.get('cat-like_words', ['prr']))
    catBonus *= 1.5

    memeBonus = len(dictionary.get('cat-like_words', [':3']))
    memeBonus += len(dictionary.get('cat-like_words', ['XD']))
    memeBonus *= 1.25

    felineBonus = len(dictionary.get('cat-like_words', ['feline']))
    felineBonus += len(dictionary.get('cat-like_words', ['furball']))

    score = len(found_words_list)

    bonusScore = 0
    bonusScore += catBonus
    bonusScore += memeBonus
    bonusScore += felineBonus

    dictionary['Cat Related Words'] = str(score)
    dictionary['Total CatBonus'] = str(bonusScore)
    dictionary['Cat Document Score'] = str(score + bonusScore)
    return dictionary


def storeInDatabase(db, content, CurrentUrl):
    try:
        # new collection
        col = db.OrganizedCatWords
        if content != '':
            doc = getSubredditInfo(CurrentUrl)
            doc = getExcessData(doc)
            addition = col.insert_one(doc)
        else:
            print('No need to store this garbage')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False


def convertToJPGAndDeleteOldFile(image_path):
    # Check if the image_path is a URL
    if image_path.startswith("http"):
        response = requests.get(image_path)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(image_path)

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Extract filename and extension from the URL or local path
    if image_path.startswith("http"):
        parsed_url = urlparse(image_path)
        query_params = parse_qs(parsed_url.query)
        filename = os.path.basename(parsed_url.path)
        filename_without_extension, _ = os.path.splitext(filename)
        jpg_path = filename_without_extension + ".jpg"
    else:
        jpg_path = os.path.splitext(image_path)[0] + ".jpg"

    img.save(jpg_path, "JPEG")

    # Delete the old file if it's a local file
    if not image_path.startswith("http") and os.path.exists(image_path):
        os.remove(image_path)

    return jpg_path


def printOutImagePredictions(imagesList, srName):
    global processed_images  # Use the global set

    result_list = []  # Initialize an empty list to store dictionaries

    for image_file in imagesList:
        # Skip if already processed
        if image_file in processed_images:
            print(f"Skipping {image_file}. Already processed.")
            continue

        # Convert image to JPG if needed
        jpg_path = convertToJPGAndDeleteOldFile(image_file)

        print(f"Processing {image_file} in {srName}")

        model = vgg16.VGG16()

        # Use the converted JPG image
        img = image.load_img(jpg_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = vgg16.preprocess_input(x)
        predictions = model.predict(x)
        predicted_classes = vgg16.decode_predictions(predictions, top=5)

        print("Top predictions for this image:")

        # Create a list to store predictions for the current image
        predictions_list = []
        for _, name, likelihood in predicted_classes[0]:
            prediction_info = {
                "Prediction": name,
                "Likelihood": likelihood * 100,
            }
            predictions_list.append(prediction_info)
            print(f"{name}: {likelihood * 100}%")

        # Add the processed image to the set
        processed_images.add(image_file)

        # Add the predictions list to the result list
        result_list.append({
            "Image_File": image_file,
            "Predictions": predictions_list
        })

    return result_list


def getSubredditInfo(subreddit_url):
    global processed_images
    try:
        driver = webdriver.Chrome()
        driver.get(subreddit_url)

        # Wait for the page to load
        driver.implicitly_wait(20)

        # Fetch information from the shreddit-subreddit-header
        try:
            subreddit_header = driver.find_element(By.TAG_NAME, 'shreddit-subreddit-header')
            display_name = subreddit_header.get_attribute('display-name')
            display_name = catLike(str(display_name))
            descrip = subreddit_header.get_attribute('description')
            descrip = catLike(str(descrip))
            subscribers = subreddit_header.get_attribute('subscribers')
            active_users = subreddit_header.get_attribute('active')

            # Wait for images to load
            images = driver.find_elements(By.TAG_NAME, 'img')
            images = list(images)

            image_urls = [image.get_attribute('src') for image in images]

        except NoSuchElementException:
            print("Subreddit header not found")
            return None

        finally:
            html = driver.page_source
            soup = bs(html, 'html.parser')
            img_tags = soup.find_all('img')
            img_srcs = [img['src'] for img in img_tags if 'src' in img.attrs]
            all_image_urls = image_urls + img_srcs
            count = 0
            for item in all_image_urls:
                count += 1

            dictionaryReturn = printOutImagePredictions(all_image_urls, display_name)

            # Close the browser window
            driver.quit()

        return {
            'display_name': str(display_name),
            'CatDescription': str(descrip),
            'subscribers': str(subscribers),
            'active_users': str(active_users),
            'images': str(image_urls),
            'cat-like_words': list(foundWords),
            'complete_html': html,
            'all_image_urls': all_image_urls,
            "UniqueImagesAndPredictions": dictionaryReturn
        }

    except Exception as e:
        print(f"Error: {e}")
        return None


# This method changes the text string given in to be a "cat-like" phrase
def catLike(des):
    catifiedString = ""
    for letter in des:
        randomChance = random.randint(0, 30)
        if randomChance == 15 and letter == " ":
            catifiedString += " :3 "
        if randomChance == 20 and letter == " ":
            catifiedString += " >:3 "
        if randomChance == 25 and letter == " ":
            catifiedString += " *lick lick* "
        if randomChance == 5 and letter == " ":
            catifiedString += " *lick*"
        if randomChance == 10 and letter == " ":
            catifiedString += " ;3 "
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
    "shadow", "softness", "dainty", "cozy", "regal",
    ":3", "uwu", "cuddles", "memes", "kitty", "cats", "kitties", "meows", "xd", "prr", "furball", "feline"
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
                print(f"{totalWords} total related words words : {foundWords}")

                storeInDb = storeInDatabase(datab, foundWords, url)
        else:
            print(f"{num} : NULL")

    except Exception as e:
        print(f"Error parsing HTML: {e}")
