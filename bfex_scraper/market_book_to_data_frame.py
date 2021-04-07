def market_book_to_data_frame(market_book: Union[MarketBook, dict]) -> pd.DataFrame:
    if type(market_book) is MarketBook:
        market_book = market_book._data
    return pd.DataFrame(
        {
            'market_id': market_book['marketId'],
            'inplay': market_book['inplay'],
            'selection_id': runner['selectionId'],
            'side': side,
            'depth': depth,
            'price': price_size['price'],
            'size': price_size['size'],
            **({'publish_time': market_book['publishTime']} if 'publishTime' in market_book else {})
        }
        for runner in market_book['runners']
        for side in ['Back', 'Lay']
        for depth, price_size in enumerate(runner.get('ex', {}).get(f'availableTo{side}', []))
    )