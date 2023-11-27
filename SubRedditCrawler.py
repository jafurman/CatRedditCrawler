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
        print(f"... +1 Database addition with ID:")
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


# Appending seeds to the frontier to add to DB
def addLinksToFrontier(frontierList, url_string):
    if url_string in frontierList:
        print('Already Visited This Subreddit Link')
    else:
        # Store all tags because that's just more opportunity to find more content (it'll skip)
        frontierList.append(url_string)
    return frontierList


# returning the page found title
def find_target_page_title(url_string):
    try:
        html_page = urlopen(url_string)
        soupy = bs(html_page.read(), "html.parser")

        # Find the <title> tag
        title_tag = soupy.find("h1", {"class": "font-bold text-18 xs:text-32"})

        if title_tag:
            target_page_title = title_tag.get_text().strip()
        else:
            # If <title> tag is not found or has a default value, look for other relevant tags
            h1_tag = soupy.find('h1', {'class': 'title'})
            if h1_tag:
                target_page_title = h1_tag.get_text().strip()
            else:
                target_page_title = "No Relevant Title"  # Set a default value

    except Exception as e:
        print(f"Error fetching page title for {url_string}: {e}")
        target_page_title = "Error Fetching Title"

    return target_page_title


# adding the documents to the database connection object
def save_html_content_db(url_string, page_title):
    print(f"Adding in {url_string}")

    db = connectDataBase()
    collection = db.CatSr
    createDate = datetime.datetime.now()
    htmlObj = urlopen(url_string)
    soupy = bs(htmlObj.read(), "html.parser")
    htmlText = str(soupy)

    doc = {
        "PageTitle": page_title,
        "Url": url_string,
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


def takeOutUnwantedLinks(link_list):
    valid_links = []

    for url in link_list:
        url_href = url.get("href")
        if url_href and (
                url_href.startswith("https://www.reddit.com/r/") or url_href.startswith("https://www.reddit.com/t/")):
            continue
        else:
            valid_links.append(url)

    return valid_links


# ---------------------------- VV main method essentially VV----------------------------------#


# initial frontier setting of CFA.org (Cat Fanciers Association)
initialFrontier = ["https://reddit.com/r", "https://reddit.com/t"]

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
            print(f"FRONTIER QUEUE: {initialFrontier}")

            AboutTheCATNAME = find_target_page_title(hrefLink)

            save_html_content_db(hrefLink, AboutTheCATNAME)

            if totalLinksVisited >= 300:
                print(f"STOP Here because target page was found at page titled: {AboutTheCATNAME}")
                initialFrontier.clear()
                break
            totalLinksVisited += 1
            print(f"Link count is {totalLinksVisited}")
