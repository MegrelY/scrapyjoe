# config.py

import os
import yaml
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.SECRET_KEY = os.getenv('SECRET_KEY')

        # Load YAML configurations
        with open('config.yaml', 'r') as f:
            cfg = yaml.safe_load(f)
            self.SCRAPING = cfg.get('scraping', {})
            self.DATABASE_URI = cfg.get('database', {}).get('uri', 'sqlite:///scrapyjoe.db')

config = Config()
