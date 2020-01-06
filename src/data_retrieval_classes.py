import datetime
import datetime as dt
import logging
import os
import pickle
import threading
import time

import betfairlightweight

from src.s3_tools import s3_dir_exists
from src.s3_tools import upload_to_s3
from src.utils import safe_open

logger = logging.getLogger("marketCatalogueScraper")
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s | %(filename)s | %(module)s",
    level=logging.INFO,
)


class MarketCatalogueLogger(threading.Thread):
    """Main class for downloading market catalogue data from the Betfair
    Exchange API"""

    def __init__(self):
        logging.info("Creating instance of MarketCatalogueLogger")
        # Define how long to wait before scanning the markets again
        self.delay_seconds = 60
        # Define the max number of results to return
        self.max_results = 1000
        self.__run_logger = False
        threading.Thread.__init__(self, target=self._logger)
        # Create API Client object (to interact with betfair exchange)
        username = os.environ.get("username")
        password = os.environ.get("password")
        app_key = os.environ.get("app_key")
        certs = os.environ.get("certs")
        self.trading = betfairlightweight.APIClient(
            username=username, password=password, app_key=app_key, certs=certs
        )
        self.trading.login()
        self.last_keep_alive = dt.datetime.today()
        self.s3_folder = "catalogue"

    def create_logger(self, event_type_ids, country, market_types, market_projection):
        """Define market filters, save them as class variables"""
        logging.info("Executing create_logger()")
        self.event_filter = betfairlightweight.filters.market_filter(
            event_type_ids=event_type_ids,
            market_countries=country,
            market_type_codes=market_types,
        )
        self.market_projection = market_projection
        self.event_type_id = str(event_type_ids[0])
        # Log the creation time of the streamer
        self.creation_time = datetime.datetime.now()
        logger.info(
            "Market catalogue streamer created at {}".format(self.creation_time)
        )

    def start_logger(self):
        """Start logger thread"""
        logger.info("Starting market catalogue streamer")
        self.__run_logger = True
        self.thread = threading.Thread(target=self._logger)
        self.thread.start()

    def stop_logger(self):
        """Stop logger thread"""
        logger.info("Stopping market_catalogue streamer")
        self.__run_logger = False
        self.thread.join()

    def _logger(self):
        """Main logger operation (user does not interact with this)"""
        while self.__run_logger:
            try:
                # Keep connection alive every hour (3600 seconds)
                current_time = dt.datetime.today()
                if (current_time - self.last_keep_alive).total_seconds() > 600:
                    try:
                        self.trading.keep_alive()
                    except betfairlightweight.exceptions.StatusCodeError:
                        pass  # Do nothing

                # Get market catalogue with event info
                market_catalogues = self.trading.betting.list_market_catalogue(
                    filter=self.event_filter,
                    market_projection=self.market_projection,
                    max_results=self.max_results,
                )
                logger.info("Time: {}".format(str(datetime.datetime.now())))
                logger.info("Found {} catalogues".format(str(len(market_catalogues))))

                for market_catalogue in market_catalogues:
                    # Only save these once per market. Find out if the market
                    # already exists in the filesystem, if it does then skip
                    if self.event_type_id == "7":
                        event_type = "horse_racing"
                    elif self.event_type_id == "1":
                        event_type = "football"
                    else:
                        event_type = "other"
                    market_cat_dir = os.path.join(
                        "data",
                        event_type,
                        "market_catalogues"
                        if self.s3_folder == "catalogue"
                        else "catalogue_meta",
                    )
                    market_id = market_catalogue.market_id
                    file_dir = os.path.join(market_cat_dir, str(market_id)) + ".joblib"
                    s3_dir = os.path.join(
                        "marketdata",
                        self.s3_folder,
                        str(self.event_type_id),
                        str(market_id) + ".joblib",
                    )
                    # Check if the file exists in S3 already, or one is present
                    # locally because of a failed upload attempt
                    s3_file_exists = s3_dir_exists(
                        s3_dir, bucket=os.environ["directory"]
                    )
                    logger.info("{} exists: {}".format(s3_dir, str(s3_file_exists)))
                    if not s3_file_exists or os.path.exists(file_dir):
                        # Save market catalogue
                        logger.info(
                            "Saving market_id {} to {}".format(market_id, file_dir)
                        )
                        with safe_open(file_dir, "wb") as outfile:
                            outfile.write(pickle.dumps(market_catalogue))
                            if os.path.exists(file_dir):
                                logger.info("File saved")
                            else:
                                logger.info("File NOT SAVED")
                        logger.info("Attempting to upload saved file to S3")
                        upload_to_s3(file_dir, s3_dir, bucket=os.environ["directory"])
                        # Search for the file in S3 then write the result to the logger
                        if s3_dir_exists(s3_dir):
                            logger.info("File found in S3, upload success :)")
                            # Delete the file from the folder (if it exists)
                            if os.path.exists(file_dir):
                                os.remove(file_dir)
                        else:
                            logger.info("File not found in S3, something went wrong :(")
                # Wait before checking again
                time.sleep(self.delay_seconds)
            except ConnectionError:
                print("Lost connection to server, retrying...")
                # Wait before checking again
                time.sleep(self.delay_seconds)
