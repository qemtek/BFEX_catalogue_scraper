import time
import logging
import betfairlightweight
from pythonjsonlogger import jsonlogger

from flumine import Flumine, clients
from flumine.streams.datastream import DataStream
from market_recorder2 import MarketRecorder, S3MarketRecorder

from settings import S3_DIR, BFEX_USERNAME, BFEX_PASSWORD, BFEX_APP_KEY, BFEX_CERTS_DIR, tmp_dir

logger = logging.getLogger()

custom_format = "%(asctime) %(levelname) %(message)"
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(custom_format)
formatter.converter = time.gmtime
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

trading = betfairlightweight.APIClient(
    username=BFEX_USERNAME,
    password=BFEX_PASSWORD,
    app_key=BFEX_APP_KEY,
    certs=BFEX_CERTS_DIR
)
client = clients.BetfairClient(trading)

framework = Flumine(client=client)

strategy = S3MarketRecorder(
    name="WIN",
    market_filter=betfairlightweight.filters.streaming_market_filter(
        event_type_ids=["7"],
        country_codes=["GB", "IE", "AU", "US"],
        market_types=["WIN"],
    ),
    stream_class=DataStream,
    context={
        "local_dir": tmp_dir,
        "eventTypeId": "7",
        "marketType": ["WIN", "PLACE"],
        "bucket": S3_DIR,
        "force_update": False,
        "remove_file": True,
    },
)

framework.add_strategy(strategy)

framework.run()
