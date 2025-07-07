# /src/portfolio.py 

class Portfolio:
    def __init__(self, player_id, initial_cash=1000):
        self.player_id = player_id
        self.cash = initial_cash
        self.holdings = {}  # asset_name: quantity
        self.trade_log = []  # optional for later analytics

    def update_position(self, asset_name, quantity, price, is_buy):
        cost = quantity * price
        if is_buy:
            if self.cash >= cost:
                self.cash -= cost
                self.holdings[asset_name] = self.holdings.get(asset_name, 0) + quantity
            else:
                print(f"❌ {self.player_id} cannot afford {quantity} of {asset_name}")
        else:
            if self.holdings.get(asset_name, 0) >= quantity:
                self.cash += cost
                self.holdings[asset_name] -= quantity
            else:
                print(f"❌ {self.player_id} not enough {asset_name} to sell")
    def get_total_value(self, asset_prices):
        value = self.cash
        for asset_name, quantity in self.holdings.items():
            price = asset_prices.get(asset_name, 0)
            value += quantity * price
        return value

