import os
import pickle
import time
import betfairlightweight
import threading
import flumine
from flumine.resources import MarketRecorder
from flumine.storage import storageengine
import datetime
import zipfile

from src.utils import safe_open, mkdir_p
from src.s3_tools import upload_to_s3
from configuration import project_dir, betfair_credentials
from configuration import s3_credentials

# Get API credentials from configuration file
username = betfair_credentials['betfairlightweight'].get('username')
password = betfair_credentials['betfairlightweight'].get('password')
app_key = betfair_credentials['betfairlightweight'].get('app_key')
certs = betfair_credentials['betfairlightweight'].get('certs')


class FlumineStreamer:
    """Main class for streaming odds data from the Betfair Exchange API"""

    def __init__(self):
        self.credentials = betfair_credentials

    def create_streamer(self, market_filter, market_data_filter):
        """Create a streaming object with the Flumine package"""
        self.market_filter = market_filter
        self.market_data_filter = market_data_filter
        # Define storage engine (to upload to S3)
        self.storage_engine = storageengine.S3(
            directory=s3_credentials['directory'],
            access_key=s3_credentials['access_key'],
            secret_key=s3_credentials['secret_key']
        )

        # Define Flumine streaming object
        self.flumine = flumine.Flumine(
            recorder=MarketRecorder(
                storage_engine=self.storage_engine,
                market_filter=market_filter,
                market_data_filter=market_data_filter
            ),
            settings=self.credentials,
        )
        # Log the creation time of the streamer
        self.creation_time = datetime.datetime.now()
        print('Odds streamer created at {}'.format(self.creation_time))

    def start(self):
        """Start the streamer"""
        self.flumine.start()
        print('Odds streamer started')

    def stop(self):
        """Stop the streamer"""
        self.flumine.stop()
        print('Odds streamer paused')

    @staticmethod
    def modify_save_location(data_dir):
        """Change the location that streaming data is stored in by monkey
        patching the FLUMINE_DATA variable inside the flumine package"""
        # Create the directory if it dosent exist
        mkdir_p(data_dir)
        # Override FLUMINE_DATA
        flumine.flumine.FLUMINE_DATA = data_dir
        flumine.resources.recorder.FLUMINE_DATA = data_dir
        flumine.storage.storageengine.FLUMINE_DATA = data_dir


class MarketCatalogueLogger(threading.Thread):
    """Main class for downloading market catalogue data from the Betfair
    Exchange API"""
    def __init__(self):
        self.delay_seconds = 60
        self.max_results = 500
        self.__run_logger = False
        threading.Thread.__init__(self, target=self._logger)
        # Create API Client object (to interact with betfair exchange)
        self.trading = betfairlightweight.APIClient(
            username=username, password=password,
            app_key=app_key, certs=certs)
        self.project_dir = project_dir
        # Log in
        self.trading.login()

    def create_logger(self, event_type_ids, country, market_types,
                      market_projection):
        """Define market filters, save them as class variables"""
        self.event_filter = betfairlightweight.filters.market_filter(
            event_type_ids=event_type_ids,
            market_countries=country,
            market_type_codes=market_types
        )
        self.market_projection = market_projection
        self.event_type_id = str(event_type_ids[0])
        # Log the creation time of the streamer
        self.creation_time = datetime.datetime.now()
        print('Market catalogue streamer created at {}'.format(
            self.creation_time))

    def start_logger(self):
        """Start logger thread"""
        print('Starting market catalogue streamer')
        self.__run_logger = True
        self.thread = threading.Thread(target=self._logger)
        self.thread.start()

    def stop_logger(self):
        """Stop logger thread"""
        print('Stopping market_catalogue streamer')
        self.__run_logger = False
        self.thread.join()

    def _logger(self):
        """Main logger operation (user does not interact with this)"""
        try:
            # Keep connection alive
            self.trading.keep_alive()
            while self.__run_logger:
                # Get market catalogue with event info
                market_catalogues = self.trading.betting.list_market_catalogue(
                    filter=self.event_filter,
                    market_projection=self.market_projection,
                    max_results=self.max_results)
                print('Time: {}'.format(str(datetime.datetime.now())))
                print('Found {} catalogues'.format(str(len(market_catalogues))))

                for market_catalogue in market_catalogues:
                    # Only save these once per market. Find out if the market
                    # already exists in the filesystem, if it does then skip
                    if self.event_type_id == '7':
                        event_type = 'horse_racing'
                    elif self.event_type_id == '1':
                        event_type = 'football'
                    else:
                        event_type = 'unknown'
                    market_cat_dir = os.path.join(
                        self.project_dir, 'data', event_type,
                        'market_catalogues')
                    # If the market directory does not exist, then create it
                    try:
                        market_dirs = os.listdir(market_cat_dir)
                    except FileNotFoundError:
                        mkdir_p(market_cat_dir)
                        market_dirs = []
                    market_id = market_catalogue.market_id
                    if market_id+'.joblib' not in market_dirs:
                        file_dir = os.path.join(
                            market_cat_dir, str(market_id))
                        # Save market catalogue
                        with safe_open(file_dir+'.joblib', 'wb') as outfile:
                             outfile.write(pickle.dumps(market_catalogue))
                        upload_to_s3(file_dir+'.joblib',
                                     os.path.join('data', event_type,
                                                  'market_catalogues',
                                                  str(market_id)+'.joblib'))
        except ConnectionError:
            print('Lost connection to server, retrying...')
        # Wait before checking again
        time.sleep(self.delay_seconds)

    # ToDo: When the market closes, add a method to upload the file to S3
