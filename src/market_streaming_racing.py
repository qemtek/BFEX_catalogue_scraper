import logging
import os

from configuration import project_dir
from data_retrieval_classes import FlumineStreamer
from data_retrieval_classes import MarketCatalogueLogger
from utils import get_venue_groups

# Add relevant paths to the file system

# Setup logging
# logging.basicConfig(level=logging.INFO)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)

# Define where the data will be stored
data_dir = os.path.join(project_dir, "data", "horse_racing", "market_streaming")

# Define market options (what markets and what data we want to download)
market_types = ["WIN"]
event_type_ids = ["7"]
country_codes = ["GB", "IE"]
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
    "EVENT_TYPE",
    "MARKET_START_TIME",
    "MARKET_DESCRIPTION",
]
market_projection2 = ["RUNNER_METADATA"]

"""DOWNLOAD ODDS STREAM (odds data from each market)"""
# Create the streamer objects
stream_groups = ["A", "B", "C", "D"]
venues = get_venue_groups()
streamers = {}
for stream in stream_groups:
    streamers[stream] = FlumineStreamer()

# Override the default save directory in each streamer
for streamer in streamers.values():
    streamer.modify_save_location(data_dir)

# Define market data filter (what types of data we want from those markets)
market_data_filter = {"fields": data_fields, "ladder_levels": 3}

# Define market filters (what betting markets we want)
market_filters = {}
for stream in stream_groups:
    market_filters[stream] = {
        "eventTypeIds": event_type_ids,
        "countryCodes": country_codes,
        "marketTypes": market_types,
        "venues": venues[stream],
    }

# Set up the stream using the filters we have defined and start the stream
market_filter_iter = market_filters.values().__iter__()
for streamer in streamers.values():
    streamer.create_streamer(
        market_filter=market_filter_iter.__next__(),
        market_data_filter=market_data_filter,
    )
    streamer.start()


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
