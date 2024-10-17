# app.py

from flask import Flask, render_template, request, Response
from scraper import scrape, visited_urls, scraped_data, save_data_to_json
from config import config
from logging_config import setup_logging
from urllib.parse import urlparse
from models import PageData, session
from functools import wraps
import os
import json


# Initialize logging
setup_logging()

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Authentication Functions

def check_auth(username, password):
    """Check if a username/password combination is valid."""
    valid_username = os.getenv('BASIC_AUTH_USERNAME', 'admin')
    valid_password = os.getenv('BASIC_AUTH_PASSWORD', 'your_secure_password')
    return username == valid_username and password == valid_password

def authenticate():
    """Send a 401 response to prompt for credentials."""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You need to login with proper credentials.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """Decorator to prompt for authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

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

@app.route('/data')
@requires_auth
def view_data():
    # Retrieve all scraped pages from the database
    pages = session.query(PageData).all()
    return render_template('data.html', pages=pages)

def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])
