import sys
import logging
import json
from src.data_retrieval_classes import MarketCatalogueLogger


def setup_logging():
    logger = logging.getLogger("marketCatalogueScraper")
    logger.setLevel(logging.INFO)
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(message)s | %(filename)s | %(module)s",
        level=logging.INFO,
    )


def main():
    setup_logging()
    event_type_ids = json.loads(sys.argv[1])
    country_codes = json.loads(sys.argv[2])
    market_types = json.loads(sys.argv[3])
    market_projection = json.loads(sys.argv[4])

    streamer = MarketCatalogueLogger()
    # Create filters for the market catalogue
    streamer.create_logger(
        event_type_ids=event_type_ids,
        country=country_codes,
        market_types=market_types,
        market_projection=market_projection,
    )
    # Start listening for markets
    streamer.start_logger()

    while True:
        a = 1  # Do nothing


if __name__ == '__main__':
    main()
