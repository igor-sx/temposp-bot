import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
#from urllib.request import urlretrieve

url = 'https://www.cgesp.org/v3//estacoes-meteorologicas.jsp'

def scrape_image_url(url): #todo: better error handling
    html = requests.get(url)
    bs = BeautifulSoup(html.text, 'html.parser')
    backgroundImage = bs.find('style').text #finds the style tag and extracts the full text
    
    image_url = None #variable to store the image full url
    
    match = re.search(r"\.condTempo\s*\{.*?background.*?:.*?url\((.*?)\)", backgroundImage, re.IGNORECASE | re.DOTALL) #regex to tind the specific file url
    if match:
        image_url = match.group(1) #assigns the regex result to image_url var
        final_url = urljoin(url, image_url) #joins the base url with the image url, providing the full path to the file
    else:
        final_url = None
    return final_url

def download_image(final_url, save_path):
    try:
        response = requests.get(final_url)
        response.raise_for_status() #raise an exception if unsuccessful
        #if response.status_code == 200:  #not needed as the exception is raised above, if unsuccessful
        with open (save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False
    
def scrape_and_save(url, image_path):
    try:
        fileurl = scrape_image_url(url)
        if fileurl: #check for a valid url
            sucess = download_image(fileurl, image_path)
            return sucess
        return False
    except Exception as e:
        print(f"Error scraping image URL: {e}")
        return False