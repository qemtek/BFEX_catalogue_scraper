from src.data_retrieval_classes import MarketCatalogueLogger
from settings import MARKET_PROJECTION, MARKET_TYPES, EVENT_TYPE_IDS, COUNTRY_CODES

def test_s3_credentials():
    try:
        import boto3
        bucket_name = 'betfair-exchange-qemtek'
        client = boto3.client("s3")
        response = client.list_objects(Bucket=bucket_name)
        output = []
        for content in response.get("Contents", []):
            output.append(content.get("Key"))
        assert len(output) > 0, 'No files found in S3 directory'
    except:
        assert False, 'Cannot connect to S3'

def test_bfex_credentials():
    try:
        from src.utils.betfair_tools import betfair_login
        trading = betfair_login()
        trading.login()
    except:
        assert False, 'Cannot log into the Betfair Exchange API'

def test_list_market_catalogue():
    try:
        from src.utils.betfair_tools import betfair_login
        import betfairlightweight
        trading = betfair_login()
        trading.login()
        # Create filter criteria
        event_filter = betfairlightweight.filters.market_filter(
            event_type_ids=EVENT_TYPE_IDS,
            market_countries=COUNTRY_CODES,
            market_type_codes=MARKET_TYPES,
        )
        # Get market catalogue with event info
        market_catalogues = trading.betting.list_market_catalogue(
            filter=event_filter,
            market_projection=MARKET_PROJECTION,
            lightweight=True,
            max_results=1,
        )
        assert len(market_catalogues) > 0, 'No market catalogues could be found'
    except:
        assert False, 'Cannot list market catalogues'


def test_save_to_s3():
    import pandas as pd
    from settings import PROJECT_DIR
    from src.utils.s3_tools import s3_dir_exists
    mcl = MarketCatalogueLogger()
    test_file_dir = f"{PROJECT_DIR}/tests/test_file.csv"
    test_file = pd.DataFrame([1,2])
    s3_dir = 'test_file.csv'
    mcl._save_to_s3(file=test_file, file_dir=test_file_dir, s3_dir=s3_dir)
    assert s3_dir_exists(s3_dir), 'Saved file cannot be found in S3'
