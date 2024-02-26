# I don't know why I created this. I now have a database with much more cat data than I intended. I think now I'll
# create a website that posts photos of cats on specific pages
from collections import deque
from http.client import InvalidURL
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
import pymongo
import traceback
import datetime
from urllib.parse import urlparse
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


# Appending seeds to the frontier to add to DB
def addLinksToFrontier(frontierQueue, url_string):
    if url_string not in frontierQueue:
        # fix crawl logic on part where /r/{word}/ NOTHING PAST THIS '/'

        frontierQueue.append(url_string)
    return frontierQueue


def extract_subreddit(url_string):
    try:
        url_string = str(url_string)
        # regular expression pattern to handle URLs with query parameters
        pattern = r'https://www\.reddit\.com/r/([^/?]+)?'

        # Using re.match to get match
        match = re.match(pattern, url_string)

        if match:
            subreddit_name = match.group(1)
            return f'https://www.reddit.com/r/{subreddit_name}'
        else:
            raise ValueError()

    except ValueError as e:
        return url_string


def crawlSubreddits(frontierQueue, visited_urls):
    total_links_visited = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        while frontierQueue:
            current_url = frontierQueue.popleft()

            try:
                # Use executor.submit to run the fetching process in parallel
                future = executor.submit(urlopen, current_url, timeout=10)  # Add timeout parameter
                html_page = future.result()
            except HTTPError as e:
                print(f"Error opening {current_url}: {e}")
                continue
            except URLError as e:
                print(f"URLError opening {current_url}: {e}")
                continue
            except InvalidURL as e:
                print(f"Invalid URL {current_url}: {e}")
                continue
            except Exception as e:
                print(f"Error processing {current_url}: {e}")
                continue

            try:
                soupy = bs(html_page.read(), "html.parser")
            except Exception as e:
                print(f"Error parsing HTML for {current_url}: {e}")
                continue

            all_links = soupy.findAll('a', {})
            valid_links = all_links

            for link in valid_links:
                href_link = link.get("href")
                if href_link and is_valid_url(href_link):
                    frontierQueue = addLinksToFrontier(frontierQueue, href_link)
                    href_link = extract_subreddit(href_link)
                    if href_link not in visited_urls and href_link.startswith("https://www.reddit.com/r/"):
                        total_links_visited += 1
                        save_html_content_db(href_link, total_links_visited)
                        visited_urls.add(href_link)

                    if total_links_visited >= 100000:
                        frontierQueue.clear()
                        break


# ---------------------------- VV main method essentially VV----------------------------------#


visited_urls = set()
# initial frontier setting of reddit
initialFrontier = deque(["https://www.reddit.com/r"])

# Adding hopefully the cat links to the frontier after ../cat/
crawlSubreddits(initialFrontier, visited_urls)
