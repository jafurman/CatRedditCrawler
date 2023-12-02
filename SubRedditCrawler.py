# I don't know why I created this. I now have a database with much more cat data than I intended. I think now I'll
# create a website that posts photos of cats on specific pages
import time
from collections import deque
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import traceback
import datetime
from urllib.parse import urlparse
import random
import re


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # database connection is localhost client.[databaseName]
        db = client.CatDB
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


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
def save_html_content_db(url_string, totalLinksNum):
    print(f"+ 1 Subreddit: {url_string} w/ link count: {totalLinksNum}")

    db = connectDataBase()
    collection = db.Subreddits
    createDate = datetime.datetime.now()
    try:
        htmlObj = urlopen(url_string)
        soupy = bs(htmlObj.read(), "html.parser")
        htmlText = str(soupy)

        doc = {
            "Url": url_string,
            "html": str(htmlText),
            "created_at": createDate
        }
        result = collection.insert_one(doc)
    except HTTPError as e:
        if e.code == 404:
            print(f"Error 404: HTML obj not found on {url_string}")


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# TEST FOR UNWANTED LINKS PAST 75 ENTRIES RNNNNnnnnnnnnnn!!!!!!
def takeOutUnwantedLinks(link_list):
    valid_links = []

    for url in link_list:
        url_href = url.get("href")
        if url_href and url_href.startswith("https://www.reddit.com/r/"):
            parsed_url = urlparse(url_href)
            # Extract the path from the URL
            path_segments = parsed_url.path.split('/')
            # Check if there are only two path segments (r/{name}) and no characters after that
            if len(path_segments) == 4 and parsed_url.query == '' and parsed_url.fragment == '' and path_segments[3] == '':
                valid_links.append(url)

    return valid_links


# Appending seeds to the frontier to add to DB
def addLinksToFrontier(frontierQueue, url_string):
    if url_string not in frontierQueue:
        # fix crawl logic on part where /r/{word}/ NOTHING PAST THIS '/'

        # second check of adding /r/{com}/ END to extract base reddit url
        url = str(url_string)
        url_string = extract_subreddit(url)

        frontierQueue.append(url_string)
    return frontierQueue


def extract_subreddit(url_string):
    try:
        # regular expression pattern to handle URLs with query parameters
        pattern = r'https://www\.reddit\.com/r/([^/?]+)?'

        # Using re.match to get match
        match = re.match(pattern, url_string)

        if match:
            subreddit_name = match.group(1)
            return f'https://www.reddit.com/r/{subreddit_name}'
        else:
            raise ValueError("Invalid URL format")

    except ValueError as e:
        print(f"Error: {e}")
        # Handle the error as needed (e.g., logging, returning a default value, etc.)
        # In this example, we'll return the original URL
        return url_string


def crawlSubreddits(frontierQueue):
    total_links_visited = 0

    while frontierQueue:
        current_url = frontierQueue.popleft()

        # see which links are being cralwed through (for logging if needed, can make permanent list here)
        # print(f"Visiting and passing : {current_url}")

        try:
            html_page = urlopen(current_url)
        except HTTPError as e:
            print(f"Error opening {current_url}: {e}")
            continue

        soupy = bs(html_page.read(), "html.parser")
        all_links = soupy.findAll('a', {})
        valid_links = takeOutUnwantedLinks(all_links)

        for link in valid_links:
            href_link = link.get("href")
            if href_link and is_valid_url(href_link):
                frontierQueue = addLinksToFrontier(frontierQueue, href_link)
                total_links_visited += 1
                save_html_content_db(href_link, total_links_visited)

                if total_links_visited >= 100000:
                    frontierQueue.clear()
                    break


# ---------------------------- VV main method essentially VV----------------------------------#


# initial frontier setting of reddit
initialFrontier = deque(["https://www.reddit.com/r/"])

# Adding hopefully the cat links to the frontier after ../cat/
crawlSubreddits(initialFrontier)
