
# I don't know why I created this. I now have a database with much more cat data than I intended. I think now I'll
# create a website that posts photos of cats on specific pages

import ssl
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
        print("---Client---")
        print(client)
        # database connection is localhost client.[databaseName]
        db = client.CatPages
        print("---DB---")
        print(db)
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


# Appending seeds to the frontier to add to DB
def addLinksToFrontier(frontierList, url_string):
    if url_string in frontierList:
        print('Already Visited This Cat Page Link')
    else:

        # Check if the URL starts with the specified patterns
        if url_string.startswith("https://www.reddit.com/r/cat") or url_string.startswith(
                "https://www.reddit.com/t/cat"):
            frontierList.append(url_string)
    return frontierList


# returning the page found title
def find_target_page_title(url_string):
    html_page = urlopen(url_string)
    soupy = bs(html_page.read(), "html.parser")
    # find the "About the [CatName]" h1 tag
    h1 = soupy.find("title")

    if h1:
        targetPageTitle = h1.get_text()
    else:
        targetPageTitle = ''

    return targetPageTitle


# adding the documents to the database connection object
def save_html_content_db(url_string, page_title):
    print(f"Adding in {url_string}")

    db = connectDataBase()
    collection = db.CatDocuments
    createDate = datetime.datetime.now()
    htmlObj = urlopen(url_string)
    soupy = bs(htmlObj.read(), "html.parser")
    htmlText = soupy.find("h1", class_="text-24 xs:text-32 text-tone-1 font-bold px-xs mt-lg mb-xs")

    doc = {
        "Url": url_string,
        "PageTitle": page_title,
        "html": str(htmlText),
        "created_at": createDate
    }
    result = collection.insert_one(doc)
    print(result.inserted_id)


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def takeOutUnwantedLinks(list):
    for url in list:
        urlHref = url.get("href")
        if urlHref.startswith("https://www.reddit.com/r/cat") or urlHref.startswith("https://www.reddit.com/t/cat"):
            continue
        else:
            list.remove(url)


# ---------------------------- VV main method essentially VV----------------------------------#


# initial frontier setting of CFA.org (Cat Fanciers Association)
initialFrontier = ["https://reddit.com/r/cat", "https://reddit.com/t/cat"]

# Adding hopefully the cat links to the frontier after ../cat/
try:
    htmlPage = urlopen(initialFrontier[0])
except HTTPError as e:
    print(e)
else:
    soup = bs(htmlPage.read(), "html.parser")
    # creating a list of all links on each HTML page
    allLinks = soup.findAll('a', {})
    takeOutUnwantedLinks(allLinks)
    totalLinksVisited = 0

    # frontier priority queue
    for link in allLinks:
        hrefLink = link.get("href")
        print(f"Link visited: {hrefLink}")
        if hrefLink and is_valid_url(hrefLink):  # Check if the URL is valid
            initialFrontier = addLinksToFrontier(initialFrontier, hrefLink)
            print(initialFrontier)

            AboutTheCATNAME = find_target_page_title(hrefLink)

            save_html_content_db(hrefLink, AboutTheCATNAME)

            if totalLinksVisited >= 150:
                print(f"STOP Here because target page was found at page titled: {AboutTheCATNAME}")
                initialFrontier.clear()
                break
            totalLinksVisited += 1
            print(f"Link count is {totalLinksVisited}")
