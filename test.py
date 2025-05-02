import requests
from bs4 import BeautifulSoup

url = "https://www.cgesp.org/v3//noticias.jsp"  # Replace with the real URL
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the first news block
noticia = soup.find("div", class_="noticia")

if noticia:
    # Extract the headline and date
    headline = noticia.find("h2").get_text(strip=True)

    # Extract all paragraph text
    paragraphs = noticia.find_all("p")
    body_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

    print("Headline:", headline)
    print("Content:\n", body_text)
else:
    print("No news block found.")
