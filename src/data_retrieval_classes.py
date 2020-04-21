import datetime
import datetime as dt
import pandas as pd
from tenacity import retry, wait_exponential
import os
import pickle
import threading

import betfairlightweight
from settings import PROJECT_DIR
from src.utils.s3_tools import s3_dir_exists
from src.utils.s3_tools import upload_to_s3
from src.utils.utils import safe_open
from src.utils.logging import get_logger
from src.utils.betfair_tools import betfair_login

logger = get_logger()


class MarketCatalogueLogger(threading.Thread):
    """Main class for downloading market catalogue data from the Betfair Exchange API
    """
    def __init__(self):
        logger.info("Creating instance of MarketCatalogueLogger")
        self.max_results = 500
        self.__run_logger = False
        threading.Thread.__init__(self, target=self._logger)
        # Create API Client object (to interact with Betfair Exchange API)
        self.trading = betfair_login()
        self.project_dir = PROJECT_DIR
        # Log in
        self.trading.login()
        self.trading.race_card.login()
        self.last_keep_alive = dt.datetime.now()
        self.last_catalogue_update = dt.datetime.now() - dt.timedelta(minutes=60)
        self.s3_folder = "catalogue"

    def create_logger(self, event_type_ids, country, market_types, market_projection):
        """Define market filters, save them as class variables
        """
        logger.info("Executing create_logger()")
        self.event_filter = betfairlightweight.filters.market_filter(
            event_type_ids=event_type_ids,
            market_countries=country,
            market_type_codes=market_types,
        )
        self.market_projection = market_projection
        self.event_type_id = str(event_type_ids[0])
        # Log the creation time of the streamer
        self.creation_time = datetime.datetime.now()
        logger.info("Market catalogue streamer created at {}".format(self.creation_time))

    def start_logger(self):
        """Start logger thread
        """
        logger.info("Starting market catalogue streamer")
        self.__run_logger = True
        self.thread = threading.Thread(target=self._logger)
        self.thread.start()

    def stop_logger(self):
        """Stop logger thread
        """
        logger.info("Stopping market_catalogue streamer")
        self.__run_logger = False
        self.thread.join()

    def get_market_cat_dir(self):
        if self.event_type_id == "7":
            event_type = "horse_racing"
        elif self.event_type_id == "1":
            event_type = "football"
        else:
            event_type = "other"
        market_cat_dir = f"{self.project_dir}/data/{event_type}/" \
                         f"{'market_catalogues' if self.s3_folder == 'catalogue' else 'catalogue_meta'}"
        return market_cat_dir

    def get_race_card_dir(self):
        if self.event_type_id == "7":
            event_type = "horse_racing"
        elif self.event_type_id == "1":
            event_type = "football"
        else:
            event_type = "other"
        market_cat_dir = f"{self.project_dir}/data/{event_type}/race_cards"
        return market_cat_dir

    def get_race_result_dir(self):
        if self.event_type_id == "7":
            event_type = "horse_racing"
        elif self.event_type_id == "1":
            event_type = "football"
        else:
            event_type = "other"
        market_cat_dir = f"{self.project_dir}/data/{event_type}/race_results"
        return market_cat_dir

    @staticmethod
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10))
    def _save_to_s3(file, file_dir, s3_dir):
        # Check if the file exists in S3 already, or one is present locally
        # because of a failed upload attempt
        s3_file_exists = s3_dir_exists(s3_dir)
        logger.info("{} exists: {}".format(s3_dir, str(s3_file_exists)))
        # If the file dosent exist in S3, or exists locally
        if not s3_file_exists or os.path.exists(file_dir):
            # Save market catalogue
            logger.info(f"Saving file {file_dir} to {s3_dir}")
            with safe_open(file_dir, "wb") as outfile:
                outfile.write(pickle.dumps(file))
            upload_to_s3(file_dir, s3_dir)
            # Search for the file in S3 then write the result to the logger
            if s3_dir_exists(s3_dir):
                logger.info("File found in S3, upload success.")
                # Delete the file from the folder (if it exists)
                if os.path.exists(file_dir):
                    os.remove(file_dir)
            else:
                logger.info("File not found in S3, something went wrong :(")

    @retry(wait=wait_exponential(multiplier=1, min=2, max=50))
    def _get_event_data(self):
        # Get market catalogue with event info
        market_catalogues = self.trading.betting.list_market_catalogue(
            filter=self.event_filter,
            market_projection=self.market_projection,
            lightweight=True,
            max_results=self.max_results,
        )
        logger.info("Found {} catalogues".format(str(len(market_catalogues))))
        market_ids = []
        # Upload market catalogues
        for market_catalogue in market_catalogues:
            # Only log races that are 10min away from occuring, because some data is not updated
            # until closer to the race (like going)
            time_now = pd.Series(pd.to_datetime(dt.datetime.now())).dt.tz_localize('UTC').loc[0]
            mst = pd.to_datetime(market_catalogue.get('marketStartTime'))
            if (mst - time_now).total_seconds() < 600:
                # Only save these once per market. Find out if the market
                # already exists in the filesystem, if it does then skip
                market_cat_dir = self.get_market_cat_dir()
                market_id = str(market_catalogue.get('marketId'))
                market_ids.append(market_id)
                file_dir = f"{market_cat_dir}/{market_id}.joblib"
                s3_dir = f"lw_marketdata/{self.s3_folder}/{str(self.event_type_id)}/{str(market_id)}.joblib"
                self._save_to_s3(file=market_catalogue, file_dir=file_dir, s3_dir=s3_dir)
        # Upload race cards
        race_cards = self.trading.race_card.get_race_card(market_ids=market_ids, lightweight=True)
        for race_card in race_cards:
            race_card_dir = self.get_race_card_dir()
            race_id = race_card.get('race').get('raceIdExchange')
            file_dir = f"{race_card_dir}/{race_id}.joblib"
            s3_dir = f"race_cards/{self.s3_folder}/{str(self.event_type_id)}/{str(race_id)}.joblib"
            self._save_to_s3(file=race_card, file_dir=file_dir, s3_dir=s3_dir)
        # Upload race result
        race_results = self.trading.race_card.get_race_result(market_ids=market_ids, lightweight=True)
        for race_result in race_results:
                race_result_dir = self.get_race_result_dir()
                race_id = race_result.get('raceIdExchange')
                file_dir = f"{race_result_dir}/{race_id}.joblib"
                s3_dir = f"race_results/{self.s3_folder}/{str(self.event_type_id)}/{str(race_id)}.joblib"
                self._save_to_s3(file=race_result, file_dir=file_dir, s3_dir=s3_dir)
        # Log update time
        self.last_catalogue_update = dt.datetime.now()

    def _logger(self):
        """Main logger operation (user does not interact with this)
        """
        while self.__run_logger:
            # Keep connection alive every 10 minutes
            current_time = dt.datetime.now()
            # Check if the connection needs to be kept alive
            if (current_time - self.last_keep_alive).total_seconds() > 600:
                try:
                    self.trading.keep_alive()
                except betfairlightweight.exceptions.StatusCodeError as e:
                    logger.info(f'Error using keep_alive(): {e}')
            # Check if the catalogue data needs to be updated
            if (current_time - self.last_catalogue_update).total_seconds() > 3600:
                logger.info(f'Time since data was last scraped:'
                            f' {(current_time - self.last_catalogue_update).total_seconds()}. Running again')
                self._get_event_data()
