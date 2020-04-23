import os
import logging

from bfex_scraper.src.utils.configuration import get_attribute

# Project credentials
PROJECT_DIR = get_attribute('PROJECT_DIR')
os.environ['PYTHONPATH'] = PROJECT_DIR
print(f"Project dir: {PROJECT_DIR}")
db_dir = os.path.join(PROJECT_DIR, 'data', 'hr_db.sqlite')
model_dir = os.path.join(PROJECT_DIR, 'models')
plots_dir = os.path.join(PROJECT_DIR, 'plots')

# Logging settings
FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s —"
    "%(funcName)s:%(lineno)d — %(message)s")
# Create log directory
LOG_DIR = f"{PROJECT_DIR}/logs"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
LOG_FILE = f"{LOG_DIR}/streamer.log"

# Betfair Exchange API credentials
BFEX_USERNAME = get_attribute('BFEX_USERNAME')
BFEX_PASSWORD = get_attribute('BFEX_PASSWORD')
BFEX_APP_KEY = get_attribute('BFEX_APP_KEY')
BFEX_CERTS_DIR = get_attribute('BFEX_CERTS_DIR')

# S3 credentials
S3_DIR = get_attribute('S3_DIR')
AWS_ACCESS_KEY_ID = get_attribute('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_attribute('AWS_SECRET_ACCESS_KEY')

SCRAPE_FOOTBALL = get_attribute('SCRAPE_FOOTBALL')
SCRAPE_RACING = get_attribute('SCRAPE_RACING')

DATA_FIELDS = get_attribute('DATA_FIELDS', is_json=True)
MARKET_PROJECTION = get_attribute('MARKET_PROJECTION', is_json=True)
MARKET_TYPES = get_attribute('MARKET_TYPES', is_json=True)
COUNTRY_CODES = get_attribute('COUNTRY_CODES', is_json=True)
EVENT_TYPE_IDS = get_attribute('EVENT_TYPE_IDS', is_json=True)
