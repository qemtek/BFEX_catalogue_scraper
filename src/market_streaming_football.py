import logging
import os

from configuration import project_dir
from data_retrieval_classes import MarketCatalogueLogger

# Add relevant paths to the file system

# Setup logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("botocore").setLevel(logging.WARNING)
# logging.basicConfig(level=logging.DEBUG)

# Define where the data will be stored
data_dir = os.path.join(project_dir, "data", "football", "market_streaming")

# Define market options (what markets and what data we want to download)
market_types = [
    "CORRECT_SCORE",
    "CORRECT_SCORE2",
    "PENALTY_TAKEN",
    "SENDING_OFF",
    "MATCH_ODDS",
    "OVER_UNDER_05",
    "OVER_UNDER_15",
    "OVER_UNDER_25",
    "FIRST_GOAL_SCORER",
    "CORNER_ODDS",
    "OVER_UNDER_105_CORNR",
    "OVER_UNDER_135_CORNR",
]

event_type_ids = ["1"]
country_codes = ["GB", "FR", "DE", "ES", "IT"]
data_fields = [
    "EX_BEST_OFFERS_DISP",
    "EX_BEST_OFFERS",
    "EX_ALL_OFFERS",
    "EX_TRADED",
    "EX_TRADED_VOL",
    "EX_MARKET_DEF",
]
market_projection = [
    "MARKET_START_TIME",
    "RUNNER_DESCRIPTION",
    "COMPETITION",
    "EVENT",
    "MARKET_DESCRIPTION",
]
market_projection2 = ["RUNNER_METADATA"]
#
# """DOWNLOAD ODDS STREAM (odds data from each market)"""
# # Create the streamer object
# streamer = FlumineStreamer()
#
# # Override data directory
# streamer.modify_save_location(data_dir)
#
# # Define market filter (what betting markets we want)
# market_filter = {
#     "bettingTypes": ["ODDS"],
#     "eventTypeIds": event_type_ids,
#     "countryCodes": country_codes,
#     "bspMarket": False,
#     "marketTypes": market_types,
# }
#
# # Define market data filter (what types of data we want from those markets)
# market_data_filter = {"fields": data_fields, "ladder_levels": 3}
#
# # Set up the stream using the filters we have defined
# streamer.create_streamer(
#     market_filter=market_filter, market_data_filter=market_data_filter
# )
#
# # Start the stream
# streamer.start()

"""DOWNLOAD MARKET CATALOGUES (information about each market)"""
logger = MarketCatalogueLogger()
# Create filters for the market catalogue
logger.create_logger(
    event_type_ids=event_type_ids,
    country=country_codes,
    market_types=market_types,
    market_projection=market_projection,
)
# Start listening for markets
logger.start_logger()

"""META-DATA LOGGER"""
logger2 = MarketCatalogueLogger()
# Create filters for the market catalogue
logger2.create_logger(
    event_type_ids=event_type_ids,
    country=country_codes,
    market_types=market_types,
    market_projection=market_projection2,
)
logger2.s3_folder = "metadata"
# Start listening for markets
logger2.start_logger()
