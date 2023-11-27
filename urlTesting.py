import requests
from bs4 import BeautifulSoup


def get_subreddit_info(subreddit_url):
    try:
        # Send a GET request to the subreddit URL
        response = requests.get(subreddit_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the title tag in the HTML
            title_tag = soup.find('title')

            # Get the text content of the title tag
            if title_tag:
                title = title_tag.text.strip()
                print(f"Subreddit Title: {title}")
            else:
                print("Title not found on the page.")

        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")


def check_word_in_html(html_content, target_word):
    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract text from HTML
    text_content = soup.get_text()

    # Check if the target word is present
    if target_word.lower() in text_content.lower():
        return True
    else:
        return False


# Example usage:
subreddit_url = 'https://www.reddit.com/r/Home/'
get_subreddit_info(subreddit_url)
check_word_in_html()
