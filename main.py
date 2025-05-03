import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from atproto import Client, models
import logging
import io
from openai import OpenAI

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
BLUESKY_USERNAME = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

url = 'https://www.cgesp.org/v3//index.jsp'
news_url = 'https://www.cgesp.org/v3//noticias.jsp'

def scrape_image_url(url: str) -> str | None:
    """Scrapes the provided URL to find the background image URL within a style tag.

    Args:
        url: The URL of the page to scrape.

    Returns:
        The absolute URL of the background image as a string, or None if not found 
        or an error occurs.
    """
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
        

def scrape_news_url(news_url: str) -> str | None:
    """Scrapes the news page URL to extract the latest news text.

    Args:
        news_url: The URL of the news page.

    Returns:
        The extracted news text (up to 2200 characters) as a string, or None
        if not found or an error occurs.
    """
    try:
        html = requests.get(news_url)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, "html.parser")
        news_tag = soup.find("div", class_="noticia")
        if not news_tag:
            logging.error("No news block found")
            return None
        news_text = news_tag.get_text(strip=True, separator=' ')
        news = news_text[:2200]
        return news
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news url: {news_url}: {e}")
        return None

def summarize_text(news_text: str) -> str | None:
    """Summarizes the provided text using the OpenAI API.

    Args:
        news_text: The text to summarize.

    Returns:
        The summarized text as a string, or None if an error occurs or the summary 
        is empty.
    """
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Summarize the text the user will provide, keeping the "
                                "main and weather data and any alert or high"
                                "importance data, if there is any. "
                                "The result should be a short "
                                "text that can fit a microblog post matching the "
                                "original language (Brazilian-Portuguese). Aim for "
                                "the maximum of 300 characers. Mantenha qualquer "
                                "alerta ou informação de alta importância presente. "
                                "Use abreviações se necessário. "
                                "Foque nas médias quando providas."
                            )
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": news_text
                        }
                    ]
                }
            ],
            response_format={
                "type": "text"
            },
            temperature=0.45,
            max_completion_tokens=460,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            store=False
        )
        if response.choices and response.choices[0].message:
            summary = response.choices[0].message.content.strip()
            logging.info("Text summarized successfully.")
            return summary
        else:
            logging.error("No summary content found in OpenAI response.")
            return None
    except Exception as e:
        logging.error(f"Error summarizing text with OpenAI: {e}")
        return None

def download_image_bytes(final_url: str) -> bytes | None:
    """Downloads an image from the given URL.

    Args:
        final_url: The direct URL of the image file to download.

    Returns:
        The image content as bytes, or None if the download fails
        or the content is not an image.
    """
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

def post(image_data: bytes, news_summary: str, target_width: int = 16, 
         target_height: int = 9) -> str | None:
    """Posts an image and text summary to Bluesky using the atproto library.

    Uses credentials from environment variables BLUESKY_USERNAME and BLUESKY_PASSWORD.

    Args:
        image_data: The image content as bytes.
        news_summary: The text summary to include in the post.
        target_width: The target aspect ratio width for the image embed (default: 16).
        target_height: The target aspect ratio height for the image embed (default: 9).

    Returns:
        The URI of the created post as a string, or None 
        if the post fails or credentials are missing.
    """
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
        post_text = news_summary if news_summary else " "
        #bytes_data = io.BytesIO(image_data)
        #bytes_data.name = 'upload.png' #check if it needs a bin stream or can raw like:
        response_obj = client.send_image(
            text=post_text, image=image_data, langs=['pt-BR'], 
            image_alt="foto do céu de são paulo mostrando a situação atual", 
            image_aspect_ratio=aspect_ratio_object)
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
    """Orchestrates the process of scraping news, summarizing it, scraping an image URL,
    downloading the image, and posting both to Bluesky.

    Args:
        url: The URL of the main page to scrape the image from.

    Returns:
        The URI of the created Bluesky post as a string, or None if any step fails.
    """
    logging.info("Starting bot logic...")
    image_data = None
    post_uri = None
    scraped_text = scrape_news_url(news_url)
    scraped = scrape_image_url(url)
    news_summary = summarize_text(scraped_text)
    if scraped: #if scraped ran successfully, then proceed passing the url ahead
        image_data = download_image_bytes(scraped)
        if not image_data: #calls the download function, stores the bytes
            logging.error("Image download failed, aborting...")
            return None
        post_uri = post(image_data, news_summary)
        return post_uri #returns the post uri or None if failed
    else:
        logging.error("Scraping failed, aborting...")
        return None

def cloud_entry_point(request):
    """Google Cloud Function entry point triggered via HTTP (e.g., Cloud Scheduler).

    Orchestrates the bot logic and returns an appropriate HTTP response.

    Args:
        request: The HTTP request object (required by GCP, but not used by the function)

    Returns:
        A tuple containing a success or error message and the corresponding HTTP status 
        code (200 for success, 500 for failure).
    """
    logging.info("Cloud function triggered...")
    post_uri = run_bot_logic(url)
    if post_uri:
        logging.info(f"Post successful: {post_uri}")
        return f"Post successful: {post_uri}", 200
    else:
        logging.error("Post failed")
        return "Post failed", 500
#Main function for local testing
if __name__ == "__main__":
    logging.info("Starting script...")
    post_uri = run_bot_logic(url)
    if post_uri:
        logging.info(f"Post successful: {post_uri}")
    else:
        logging.error("Post failed")