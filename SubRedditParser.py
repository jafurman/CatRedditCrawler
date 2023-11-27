# I don't know why I created this. I now have a database with much more cat data than I intended. I think now I'll
# create a website that posts photos of cats on specific pages

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import traceback
import datetime
from urllib.parse import urlparse


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
        col = db.CatSr
        # Find all documents and project only the 'html' field
        html_cursor = col.find({}, {'html': 1})
        # Return a list of all HTML
        return list(html_cursor)
    except Exception as error:
        print("Mongo DB Error")
        return None


# ---------------------------- VV main method essentially VV----------------------------------#

# Get DB Connection
db = connectDataBase()

# Open Documents and parse
try:
    pages = getAllPages(db)
except HTTPError as e:
    print(e)

num = 0
for page in pages:
    try:
        num += 1
        pageHtml = page.get("html", "")
        if num == 89456:
            print(pageHtml)
        soupy = bs(pageHtml, "html.parser")
        #description = soupy.find('div', {'id': 'description'})
        paragraphs = soupy.find_all('p')
        description = ' '.join([paragraph.get_text(strip=True) for paragraph in paragraphs])
        if description:
            text_content = description

            print(f"{num} : {text_content}")
        else:
            print(f"{num} : NULL")

    except Exception as e:
        print(f"Error parsing HTML: {e}")

    # What I want to grab from each subreddit [Subreddit Descriptions]:
