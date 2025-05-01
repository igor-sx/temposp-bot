import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from atproto import Client, models
import logging
#from PIL import Image
import io

#from typing import Optional # will be using | operator instead 
#from urllib.request import urlretrieve
#this script scrapes the image file from the weather page and post to bluesky through
#its API using atproto library
#hosting on google cloud platform with cloud scheduler

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
BLUESKY_USERNAME = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')

url = 'https://www.cgesp.org/v3//estacoes-meteorologicas.jsp'

def scrape_image_url(url: str) -> str | None:
    """Start scraping, parses the html, performs
    regex and return the image url as str or None if not found"""
    try:
        html = requests.get(url)
        html.raise_for_status()
        bs = BeautifulSoup(html.text, 'html.parser')
        style_tag = bs.find('style')
        if not style_tag:
            logging.error("style tag not found")
        backgroundImage = style_tag.text
        
        image_url = None
        match = re.search(r"\.condTempo\s*\{.*?background.*?:.*?url\((.*?)\)", 
        backgroundImage,
        re.IGNORECASE | re.DOTALL)
        if match:
            image_url = match.group(1).strip().strip("'\"")
            final_url = urljoin(url, image_url)
            logging.info(f"found image url: {final_url}")
            return final_url
        else:
            logging.error("regex failed")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching url: {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error scraping image url: {e}")
        return None
        

def download_image_bytes(final_url: str) -> bytes | None:
    """Download image file from url and return the bytes of the image
    Args:       final_url: direct url to image file to be downloaded
    Returns:    bytes of the image file or None if failed."""
    try:
        response = requests.get(final_url)  
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            logging.error(f"Content not an image: {final_url}, {content_type}")
            return None
        logging.info(f"Image downloaded successfully from: {final_url}")
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching image: {final_url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error fetching image: {e}")
        return None

def post(image_data: bytes, target_width: int = 16, target_height: int = 9) -> str | None:
    """Post the image file using atproto lib with os env var credentials, language,
    and text.
    Args:       image_data: bytes of the image file to be posted
    Returns:    str of the post URI or None if failed."""
    post_uri = None
    if not BLUESKY_PASSWORD or not BLUESKY_USERNAME:
        logging.error("Bluesky credentials not set")
        return None
    try:
        client = Client()
        client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
        aspect_ratio_object = models.AppBskyEmbedDefs.AspectRatio(
            width=target_width,
            height=target_height
        )
        #bytes_data = io.BytesIO(image_data)
        #bytes_data.name = 'upload.png' #check if it needs a bin stream or can raw like:
        response_obj = client.send_image(text="test", image=image_data, langs=['pt-BR'], image_alt="imagem do tempo", image_aspect_ratio=aspect_ratio_object)
        if hasattr(response_obj, 'uri'):
            post_uri = response_obj.uri
            logging.info(f"Image posted successfully: {post_uri}")
        else:
            logging.warning(f"Post OK but could not retrieve URI from response")
            post_uri = None
    except Exception as e:
        logging.error(f"Error submitting post: {e}")
    return post_uri

def run_bot_logic(url: str) -> str | None:
    """Orchestrates scraping image URL and downloading image file
    as bytes, and posting to Bluesky.
    If successful, call post_to_bluesky (passing the bytes)
    Args:       url: url to scrape image from
    Returns:    str of the post URI or None if failed.
    """
    logging.info("Starting bot logic...")
    image_data = None #must initizalize this var?
    post_uri = None
    scraped = scrape_image_url(url)
    if scraped: #if scraped ran successfully, then proceed passing the url ahead
        image_data = download_image_bytes(scraped)
        if not image_data: #calls the download function, stores the bytes
            logging.error("Image download failed, aborting...")
            return None
        post_uri = post(image_data) #must inialize this var (?) to call post with the bytes data
        return post_uri #returns the post uri or None if failed
    else:
        logging.error("Scraping failed, aborting...")
        return None

def cloud_entry_point(request):
    """Google Cloud Function entry point via Cloud Scheduler
    Args:       request: required by GCP via http but not used here
    Returns:    str of the post URI or None if failed.
    """
    logging.info("Cloud function triggered...")
    post_uri = run_bot_logic(url)
    if post_uri:
        logging.info(f"Post successful: {post_uri}")
        return f"Post successful: {post_uri}", 200
    else:
        logging.error("Post failed")
        return "Post failed", 500
# --- Main function for local testing ---
if __name__ == "__main__":
    logging.info("Starting script...")
    post_uri = run_bot_logic(url)
    if post_uri:
        logging.info(f"Post successful: {post_uri}")
    else:
        logging.error("Post failed")