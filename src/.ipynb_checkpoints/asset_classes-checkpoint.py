from enum import Enum

#class CardType(Enum):
    #STOCK = "stock"
    #BOND = "bond"
    #COMMODITY = "commodity"
    #CRYPTO = "crypto"

#class Card:
    #def __init__(self, name, card_type: CardType, base_price, volatility):
        #self.name = name
        #self.card_type = card_type
        #self.base_price = base_price
        #self.current_price = base_price
        #self.volatility = volatility

    #def __repr__(self):
        #return f"{self.name} (${self.current_price:.2f})"

# /src/asset_classes.py

class MarketAsset:
    def __init__(self, name, base_price, volatility):
        self.name = name
        self.base_price = base_price
        self.current_price = base_price
        self.volatility = volatility

    def update_price(self, die, sentiment, event_multiplier=1.0):
        from sentiment import sentiment_multiplier
        from dice import roll_direction, roll_dice_pool

        sentiment_mult = sentiment_multiplier(sentiment)
        change_percent = (die / 6) * self.volatility * sentiment_mult * event_multiplier
        direction = roll_direction()
        delta = self.base_price * change_percent * direction
        self.current_price = max(1, self.current_price + delta)
        print(f"{self.name} [{sentiment}] rolls {die}, changes by {delta:.2f}")

class StockCard(MarketAsset):
    def __init__(self, name, base_price, volatility, sector, dividend_yield=0.0):
        super().__init__(name, base_price, volatility)
        self.sector = sector
        self.dividend_yield = dividend_yield

class BondCard(MarketAsset):
    def __init__(self, name, base_price, volatility, duration, yield_percent):
        super().__init__(name, base_price, volatility)
        self.duration = duration
        self.yield_percent = yield_percent

class CommodityCard(MarketAsset):
    def __init__(self, name, base_price, volatility, reacts_to=None):
        super().__init__(name, base_price, volatility)
        self.reacts_to = reacts_to

class CryptoCard(MarketAsset):
    def __init__(self, name, base_price, volatility):
        super().__init__(name, base_price, volatility)

