from settings import MARKET_PROJECTION, MARKET_TYPES, EVENT_TYPE_IDS, COUNTRY_CODES
from src.data_retrieval_classes import MarketCatalogueLogger

scraper = MarketCatalogueLogger()
# Create filters for the market catalogue
scraper.create_logger(
    event_type_ids=EVENT_TYPE_IDS,
    country=COUNTRY_CODES,
    market_types=MARKET_TYPES,
    market_projection=MARKET_PROJECTION,
)
# Start listening for markets
scraper.start_logger()
