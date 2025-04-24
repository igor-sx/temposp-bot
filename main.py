import re
import requests
from bs4 import BeautifulSoup

url = 'https://www.cgesp.org/v3//estacoes-meteorologicas.jsp'
 
def get_css(url):
    html = requests.get(url)
    bs = BeautifulSoup(html.text, 'html.parser')
    backgroundImage = bs.find('style').text
    return backgroundImage

if __name__ == '__main__':
    print(f"css: {url}")
    css2 = get_css(url)
    print(css2)