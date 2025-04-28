import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from atproto import Client
import logging
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
        

def download_image(final_url: str, save_path: str) -> bool:
    """Save image file to specified path, returns a either True or False if
    successful or not.
    
    Args: 
        final_url: direct url to image file to be downloaded
        save_path: path to save the image file
    Returns: either true or false for success or failure"""
    try:
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        response = requests.get(final_url)
        response.raise_for_status()
        with open (save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return False
    
def scrape_and_save(url: str, image_path: str) -> bool:
    """Orchestrates scraping image URL and downloading the image file
    to specified path
    
    todo: change download_image to download_image_bytes which will return bytes | None 
    instead of bool and will not save the file.
    
    Rename scrape_and_save to something like run_bot_logic
    new orchestrator function call scrape_image_url
    If successful, call download_image_bytes; call post_to_bluesky (passing the bytes)
    
    might not need to return bool
    """
    try:
        fileurl = scrape_image_url(url)
        if fileurl:
            success = download_image(fileurl, image_path)
            return success
        return False
    except Exception as e:
        logging.error(f"Error scraping image URL: {e}")
        return False

def post(image_path: str) -> str | None:
    """Post the image file using atproto lib with os env var credentials, language,
    and text"""
    post_uri = None
    if not BLUESKY_PASSWORD or not BLUESKY_USERNAME:
        logging.error("Bluesky credentials not set")
        return None
    try:
        client = Client()
        client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
        with open(image_path, 'rb') as f:
            img_data = f.read()
            response_obj = client.send_image(text="TEST", image=img_data, lang='pt-BR')
            if hasattr(response_obj, 'uri'):
                post_uri = response_obj.uri
                logging.info(f"Image posted successfully: {post_uri}")
            else:
                logging.warning(f"Post OK but could not retrieve URI from response")
                post_uri = None
    except FileNotFoundError:
        logging.error(f"File not found at {image_path}")
    except Exception as e:
        logging.error(f"Error posting image: {e}")
    return post_uri

if __name__ == "__main__":
    target_url = 'https://www.cgesp.org/v3//estacoes-meteorologicas.jsp'
    save_location = os.path.join("tmp", "estacao.png")
    if scrape_and_save(target_url, save_location):
        logging.info("Image downloaded successfully. Starting post...")
        post_result_uri = post(save_location)
        if post_result_uri:
            logging.info(f"Image posted successfully: {post_result_uri}")
        else:
            logging.error("Failed to post image")
    else:
        logging.error("Image download was not successful. Aborting...")
#todo: test google cloud entry point;