import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = 'https://www.cgesp.org/v3//estacoes-meteorologicas.jsp'
def get_css(url):
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

if __name__ == '__main__':
    test = get_css(url)
    print(f"fullurl: {test}")