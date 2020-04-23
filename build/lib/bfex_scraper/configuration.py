import pathlib
import json

PROJECT_DIR = str(pathlib.Path(__file__).resolve().parent)
print(f"Package root: {PROJECT_DIR}")

BFEX_USERNAME = 'qembet'
BFEX_PASSWORD = 'Double16!'
BFEX_APP_KEY = 'dNfmqo4rsDF6ygJl'
BFEX_CERTS_DIR = '/Users/chriscollins/Documents/certs'

S3_DIR = 'betfair-exchange-qemtek'
AWS_ACCESS_KEY_ID = 'AKIATUMWGOXOAT6GEHYO'
AWS_SECRET_ACCESS_KEY = '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'

SCRAPE_FOOTBALL = True
SCRAPE_RACING = True

DATA_FIELDS = json.loads('["EX_ALL_OFFERS","EX_TRADED","EX_TRADED_VOL","EX_MARKET_DEF"]')
MARKET_PROJECTION = json.loads('["MARKET_START_TIME","RUNNER_DESCRIPTION","COMPETITION","EVENT","MARKET_DESCRIPTION"]')
MARKET_TYPES = json.loads('["WIN"]')
EVENT_TYPE_IDS = json.loads('["7"]')
COUNTRY_CODES = json.loads('["GB","IE","US","AU"]')
