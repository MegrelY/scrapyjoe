# app.py

from flask import Flask, render_template, request
from scraper import scrape, visited_urls, scraped_data, save_data_to_json
from config import config
from logging_config import setup_logging
from urllib.parse import urlparse

# Initialize logging
setup_logging()

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        url = request.form['url']
        max_depth = request.form['max_depth']
        max_pages = request.form['max_pages']

        # Validate input
        if not url or not is_valid_url(url):
            error = "Invalid URL provided."
            return render_template('index.html', error=error)

        if not max_depth.isdigit() or not max_pages.isdigit():
            error = "Max depth and pages must be numbers."
            return render_template('index.html', error=error)

        max_depth = int(max_depth)
        max_pages = int(max_pages)

        # Reset data
        visited_urls.clear()
        scraped_data.clear()

        scrape(url, max_depth, max_pages)
        save_data_to_json()

        stats = {
            'pages_scraped': len(visited_urls),
            'max_depth_reached': max_depth
        }

        return render_template('results.html', stats=stats)
    return render_template('index.html', error=error)

def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])
