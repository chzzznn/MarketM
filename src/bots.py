import random
from src.order_book import Order
from src.sentiment import roll_sentiment, sentiment_multiplier
from src.asset_classes import CryptoCard

class BaseBot:
    def __init__(self, player_id):
        self.player_id = player_id
        self.last_prices = {}
        self.performance_history = []
        self.last_action = ""

    def record_prices(self, assets):
        for asset in assets:
            self.last_prices[asset.name] = asset.current_price

    def update_performance(self, current_value):
        self.performance_history.append(current_value)
        if len(self.performance_history) >= 4:
            if all(self.performance_history[-i] < self.performance_history[-i-1] for i in range(1, 4)):
                print(f"{self.player_id} is underperforming — evolving strategy!")
                return True
        return False

    def calculate_portfolio_value(self, assets):
        value = 0
        for asset in assets:
            qty = getattr(self, "portfolio", {}).get(asset.name, 0)
            value += qty * asset.current_price
        return round(value, 2)

    def latest_decision_summary(self):
        return self.last_action or "No actions this round"


class RiskAverseBot(BaseBot):
    def decide_trades(self, portfolio, assets, sentiment):
        orders = []
        logs = []
        for asset in assets:
            if isinstance(asset, CryptoCard) or asset.volatility > 3:
                continue

            price = asset.current_price
            base = asset.base_price
            qty = 1

            if price < base * 0.95 and portfolio.cash >= price * qty:
                orders.append(Order(self.player_id, asset.name, price, qty, is_buy=True))
                logs.append(f"BUY {asset.name} @ ${price:.2f} x{qty}")
            elif price > base * 1.05 and portfolio.holdings.get(asset.name, 0) >= qty:
                orders.append(Order(self.player_id, asset.name, price, qty, is_buy=False))
                logs.append(f"SELL {asset.name} @ ${price:.2f} x{qty}")
        self.last_action = ", ".join(logs) or "No trades"
        self.record_prices(assets)
        return orders


class AggressiveBot(BaseBot):
    def decide_trades(self, portfolio, assets, sentiment):
        orders = []
        logs = []
        bullish = sentiment == "Bull"

        for asset in assets:
            if asset.volatility < 4:
                continue

            price = asset.current_price
            base = asset.base_price
            qty = random.randint(2, 4)
            prev = self.last_prices.get(asset.name, price)
            momentum = price > prev

            if bullish or momentum:
                if portfolio.cash >= price * qty:
                    orders.append(Order(self.player_id, asset.name, price, qty, is_buy=True))
                    logs.append(f"BUY {asset.name} @ ${price:.2f} x{qty}")
            else:
                if portfolio.holdings.get(asset.name, 0) >= qty:
                    orders.append(Order(self.player_id, asset.name, price, qty, is_buy=False))
                    logs.append(f"SELL {asset.name} @ ${price:.2f} x{qty}")
        self.last_action = ", ".join(logs) or "No trades"
        self.record_prices(assets)
        return orders


class ContrarianBot(BaseBot):
    def decide_trades(self, portfolio, assets, sentiment):
        orders = []
        logs = []
        for asset in assets:
            price = asset.current_price
            base = asset.base_price
            qty = 1
            prev = self.last_prices.get(asset.name, price)
            momentum = price > prev

            if sentiment == "Bull":
                if portfolio.holdings.get(asset.name, 0) >= qty:
                    orders.append(Order(self.player_id, asset.name, price, qty, is_buy=False))
                    logs.append(f"SELL {asset.name} @ ${price:.2f} x{qty}")
            elif sentiment == "Bear":
                if portfolio.cash >= price * qty:
                    orders.append(Order(self.player_id, asset.name, price, qty, is_buy=True))
                    logs.append(f"BUY {asset.name} @ ${price:.2f} x{qty}")
            else:
                if price < base * 0.9 and portfolio.cash >= price * qty:
                    orders.append(Order(self.player_id, asset.name, price, qty, is_buy=True))
                    logs.append(f"BUY {asset.name} @ ${price:.2f} x{qty}")
                elif price > base * 1.1 and portfolio.holdings.get(asset.name, 0) >= qty:
                    orders.append(Order(self.player_id, asset.name, price, qty, is_buy=False))
                    logs.append(f"SELL {asset.name} @ ${price:.2f} x{qty}")
        self.last_action = ", ".join(logs) or "No trades"
        self.record_prices(assets)
        return orders
