import betfairlightweight

from settings import BFEX_USERNAME, BFEX_PASSWORD, BFEX_APP_KEY, BFEX_CERTS_DIR
from src.utils.logging import get_logger

# setup logging
logger = get_logger()


def betfair_login():
    """Log into the Betfair Exchange API using credentials stored in configuration.py"""
    trading = betfairlightweight.APIClient(
        username=BFEX_USERNAME, password=BFEX_PASSWORD, app_key=BFEX_APP_KEY, certs=BFEX_CERTS_DIR)
    return trading
