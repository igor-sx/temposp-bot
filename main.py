import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from atproto import Client
import logging
#from urllib.request import urlretrieve
#this script scrapes the image file from the weather page and post to bluesky through its API using atproto library
#hosting on google cloud platform with cloud scheduler
 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BLUESKY_USERNAME = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')

url = 'https://www.cgesp.org/v3//estacoes-meteorologicas.jsp'

def scrape_image_url(url):
    try:
        html = requests.get(url)
        html.raise_for_status()
        bs = BeautifulSoup(html.text, 'html.parser')
        style_tag = bs.find('style') #finds the style tag and extracts the full text
        if not style_tag:
            logging.error("style tag not found")
        backgroundImage = style_tag.text
        
        image_url = None #variable to store the image full url
        match = re.search(r"\.condTempo\s*\{.*?background.*?:.*?url\((.*?)\)", backgroundImage, re.IGNORECASE | re.DOTALL) #regex to tind the specific file url
        if match:
            image_url = match.group(1).strip().strip("'\"") #assigns the regex result to image_url var
            final_url = urljoin(url, image_url) #joins the base url with the image url, providing the full path to the file
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
        

def download_image(final_url, save_path):
    try:
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        response = requests.get(final_url)
        response.raise_for_status() #raise an exception if unsuccessful
        #if response.status_code == 200:  #not needed as the exception is raised above, if unsuccessful
        with open (save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return False
    
def scrape_and_save(url, image_path):
    try:
        fileurl = scrape_image_url(url)
        if fileurl: #check for a valid url
            sucess = download_image(fileurl, image_path)
            return sucess
        return False
    except Exception as e:
        logging.error(f"Error scraping image URL: {e}")
        return False

def post(image_path):
    try:
        client = Client()
        client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
        with open(image_path, 'rb') as f:
            img_data = f.read()
        response = client.send_image(text="TEST", image=img_data, lang='pt-BR')
    except Exception as e:
        logging.error(f"Error posting image: {e}")

if __name__ == "__main__":
    target_url = 'https://www.cgesp.org/v3//estacoes-meteorologicas.jsp'
    save_location = os.path.join("tmp", "estacao.png")
    if scrape_and_save(target_url, save_location):
        logging.info("Image downloaded successfully")
    else:
        logging.error("Failed to download image")
#todo: test google cloud entry point;