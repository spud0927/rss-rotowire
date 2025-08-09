# main.py
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# --- CONFIGURATION ---
# Based on your screenshot, these are the correct selectors found directly on the page.
URL = "https://www.nbcsports.com/fantasy/football/player-news"

# The selectors for the different parts of each post
POST_SELECTOR = "div.PlayerNewsPost-content"    # The main container for each news item
TITLE_SELECTOR = "div.PlayerNewsPost-headline"  # The element with the headline text
BODY_SELECTOR = "div.PlayerNewsPost-analysis"   # The element with the analysis text
LINK_SELECTOR = "button[data-share-url]"        # The button with the permanent link
# --- END CONFIGURATION ---


def scrape_and_generate_feed():
    """
    Scrapes a single page to get the title, body, and link for
    each post, then generates an RSS feed.
    """
    try:
        print(f"Fetching content from {URL}...")
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        print("Content fetched successfully.")

        soup = BeautifulSoup(response.content, "lxml")

        fg = FeedGenerator()
        fg.title('NBC Sports Fantasy Football News')
        fg.link(href=URL, rel='alternate')
        fg.description('Latest player news and analysis for fantasy football from NBC Sports.')
        fg.language('en')

        posts = soup.select(POST_SELECTOR)
        print(f"Found {len(posts)} posts. Processing up to {MAX_ITEMS}.")

        # Add the reversed() function to process the list from last to first
        for post in reversed(posts[:MAX_ITEMS]):
            title_element = post.select_one(TITLE_SELECTOR)
            body_element = post.select_one(BODY_SELECTOR)
            link_element = post.select_one(LINK_SELECTOR)

            if title_element and body_element and link_element:
                post_title = title_element.get_text(strip=True)
                post_body = body_element.get_text(strip=True)
                post_url = link_element['data-share-url']

                fe = fg.add_entry()
                fe.title(post_title)
                fe.link(href=post_url)
                fe.guid(post_url, permalink=True)
                fe.description(post_body)

        fg.rss_file('feed.xml', pretty=True)
        print("RSS feed 'feed.xml' generated successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_and_generate_feed()
