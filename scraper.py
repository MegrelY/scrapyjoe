# scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import urllib.robotparser
import json
from logging_config import logger
from config import config
from models import PageData, session  # Assuming you have models.py as per Step 5

visited_urls = set()
scraped_data = []

def is_allowed(url, user_agent): 
        return True  # Be cautious and default to disallow


def scrape(url, max_depth, max_pages, depth=0):
    # ...
    user_agent = config.SCRAPING.get('user_agent', 'Scrapy Joe Bot')

    # Log the user-agent
    logger.info("Using User-Agent", user_agent=user_agent)

    headers = {'User-Agent': user_agent}
    # ...

    if depth > max_depth or len(visited_urls) >= max_pages:
        return

    if url in visited_urls:
        return

    user_agent = config.SCRAPING.get('user_agent', 'Scrapy Joe Bot')

    if not is_allowed(url, user_agent):
        logger.warning("Disallowed by robots.txt", url=url)
        return

    try:
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.warning("Non-200 status code", url=url, status_code=response.status_code)
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        data = {
            'timestamp': datetime.utcnow().isoformat(),
            'url': url,
            'title': soup.title.string.strip() if soup.title and soup.title.string else '',
            'headings': {
                'h1': [h.get_text().strip() for h in soup.find_all('h1')],
                'h2': [h.get_text().strip() for h in soup.find_all('h2')],
                'h3': [h.get_text().strip() for h in soup.find_all('h3')],
            },
            'paragraphs': [p.get_text().strip() for p in soup.find_all('p')],
            'lists': {
                'unordered': [ul.get_text().strip() for ul in soup.find_all('ul')],
                'ordered': [ol.get_text().strip() for ol in soup.find_all('ol')],
            },
            'links': [a.get('href') for a in soup.find_all('a', href=True)],
        }

        scraped_data.append(data)
        visited_urls.add(url)
        logger.info("Page scraped", url=url, depth=depth)

        # Save data to the database
        save_data_to_db(data)

        time.sleep(1)  # Be polite; don't overload the server

        for link in data['links']:
            full_link = urljoin(url, link)
            parsed_link = urlparse(full_link)
            if parsed_link.netloc == urlparse(url).netloc and full_link not in visited_urls:
                scrape(full_link, max_depth, max_pages, depth + 1)

    except Exception as e:
        logger.error("Error scraping page", url=url, error=str(e))

def save_data_to_db(data):
    if session.query(PageData).filter_by(url=data['url']).first():
        logger.info("URL already in database", url=data['url'])
        return

    page = PageData(
        timestamp=data['timestamp'],
        url=data['url'],
        title=data['title'],
        content=json.dumps(data)
    )
    session.add(page)
    session.commit()
    logger.info("Data saved to database", url=data['url'])

def save_data_to_json(filename='scraped_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)
