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
        print("--- Starting Scrape ---")
        print(f"Fetching content from {URL}...")
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        # We don't need to save the HTML for this test
        # with open("page_content.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        soup = BeautifulSoup(response.content, "lxml")
        posts = soup.select(POST_SELECTOR)
        
        # --- NEW LOGGING ---
        print(f"Found {len(posts)} posts using selector '{POST_SELECTOR}'. Processing up to {MAX_ITEMS}.")
        if not posts:
            print("-> WARNING: No posts found. The POST_SELECTOR may be broken.")
            return # Exit if no posts are found

        fg = FeedGenerator()
        fg.title('NBC Sports Fantasy Football News')
        fg.link(href=URL, rel='alternate')
        fg.description('Latest player news and analysis for fantasy football from NBC Sports.')
        fg.language('en')

        for i, post in enumerate(reversed(posts[:MAX_ITEMS])):
            print(f"\n--- Processing Post {i+1} ---")
            title_element = post.select_one(TITLE_SELECTOR)
            body_element = post.select_one(BODY_SELECTOR)
            link_element = post.select_one(LINK_SELECTOR)

            post_title = title_element.get_text(strip=True) if title_element else None
            post_body = body_element.get_text(strip=True) if body_element else None
            post_url = link_element['data-share-url'] if link_element else None

            # --- NEW LOGGING ---
            print(f"  Title: {post_title}")
            print(f"  Body: {post_body}")
            print(f"  URL: {post_url}")
            
            if post_title and post_body and post_url:
                fe = fg.add_entry()
                fe.title(post_title)
                fe.link(href=post_url)
                fe.guid(post_url, permalink=True)
                fe.description(post_body)
            else:
                # --- NEW LOGGING ---
                print("  -> WARNING: Missing data for this post, skipping.")

        fg.rss_file('feed.xml', pretty=True)
        print("\n--- RSS feed 'feed.xml' generated successfully. ---")

    except Exception as e:
        print(f"An error occurred: {e}")
if __name__ == "__main__":
    scrape_and_generate_feed()
