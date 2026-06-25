# main.py
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# --- CONFIGURATION ---
URL = "https://www.nbcsports.com/fantasy/football/player-news"
MAX_ITEMS = 15

# Selectors for the different parts of each post on the page.
# NOTE: iterate over the full PlayerNewsPost container, not PlayerNewsPost-content,
# because the share button lives outside the -content div. Title/body selectors are
# tag-agnostic since the headline is now an <h3> (previously a <div>).
POST_SELECTOR = "div.PlayerNewsPost"          # The main container for each news item
TITLE_SELECTOR = ".PlayerNewsPost-headline"   # The element with the headline text
BODY_SELECTOR = ".PlayerNewsPost-analysis"    # The element with the analysis text
LINK_SELECTOR = "button[data-share-url]"      # The button with the permanent link
DATE_SELECTOR = ".PlayerNewsPost-date"        # The element carrying data-timestamp
# --- END CONFIGURATION ---


def scrape_and_generate_feed():
    """
    Scrapes a single page to get the title, body, link, and timestamp for
    each post, then generates an RSS feed.
    """
    try:
        print("--- Starting Scrape ---")
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")
        posts = soup.select(POST_SELECTOR)
        print(f"Found {len(posts)} posts. Processing up to {MAX_ITEMS}.")

        fg = FeedGenerator()
        fg.title('NBC Sports Fantasy Football News')
        fg.link(href=URL, rel='alternate')
        fg.description('Latest player news and analysis for fantasy football from NBC Sports.')
        fg.language('en')

        for post in posts[:MAX_ITEMS]:
            title_element = post.select_one(TITLE_SELECTOR)
            body_element = post.select_one(BODY_SELECTOR)
            link_element = post.select_one(LINK_SELECTOR)
            date_element = post.select_one(DATE_SELECTOR)
            
            post_datetime = None

            # --- NEW TIMESTAMP PARSING LOGIC ---
            # The page carries the ISO datetime in data-date (data-timestamp is empty),
            # e.g. "2026-06-25T02:43:52.378Z".
            if date_element and date_element.get('data-date'):
                timestamp_str = date_element.get('data-date')
                try:
                    # The 'Z' at the end stands for Zulu time (UTC).
                    # We replace it with a standard UTC offset that Python can read.
                    post_datetime = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    print(f"  -> WARNING: Could not parse timestamp string '{timestamp_str}', skipping date.")
            # -----------------------------------

            if title_element and body_element and link_element:
                post_title = title_element.get_text(strip=True)
                post_body = body_element.get_text(strip=True)
                post_url = link_element['data-share-url']

                # The page lists posts newest-first; append (rather than the
                # default prepend) so the feed stays newest-first too.
                fe = fg.add_entry(order='append')
                fe.title(post_title)
                fe.link(href=post_url)
                fe.guid(post_url, permalink=True)
                fe.description(post_body)

                if post_datetime:
                    fe.pubDate(post_datetime)
            else:
                print("  -> WARNING: Missing essential data (title, body, or link), skipping post.")

        fg.rss_file('feed.xml', pretty=True)
        print("\n--- RSS feed 'feed.xml' generated successfully. ---")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    scrape_and_generate_feed()
