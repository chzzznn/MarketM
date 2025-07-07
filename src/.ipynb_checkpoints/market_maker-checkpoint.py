# /src/market_maker.py
from src.order_book import Order
from src.sentiment import sentiment_multiplier

def fixed_spread_strategy(asset, spread=2, quantity=1):
    bid = Order("MM", asset.name, asset.current_price - spread, quantity, True)
    ask = Order("MM", asset.name, asset.current_price + spread, quantity, False)
    return [bid, ask]

def vol_scaled_strategy(asset, quantity=1):
    spread = asset.volatility * 1.2
    bid = Order("MM", asset.name, asset.current_price - spread, quantity, True)
    ask = Order("MM", asset.name, asset.current_price + spread, quantity, False)
    return [bid, ask]

def sentiment_adaptive_strategy(asset, sentiment, quantity=1):
    bias = sentiment_multiplier(sentiment) - 1.0
    base_spread = 2
    mid_price = asset.current_price * (1 + bias * 0.5)

    bid = Order("MM", asset.name, mid_price - base_spread, quantity, True)
    ask = Order("MM", asset.name, mid_price + base_spread, quantity, False)
    return [bid, ask]


