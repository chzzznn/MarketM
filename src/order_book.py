# /src/order_book.py
from collections import deque

class Order:
    def __init__(self, player_id, asset_name, price, quantity, is_buy):
        self.player_id = player_id
        self.asset_name = asset_name
        self.price = price
        self.quantity = quantity
        self.is_buy = is_buy

class OrderBook:
    def __init__(self):
        self.bids = deque()  # Highest price first
        self.asks = deque()  # Lowest price first

    def place_order(self, order: Order):
        if order.is_buy:
            self.bids.append(order)
            self.bids = deque(sorted(self.bids, key=lambda x: -x.price))
        else:
            self.asks.append(order)
            self.asks = deque(sorted(self.asks, key=lambda x: x.price))

    def match_orders(self):
        trades = []
        while self.bids and self.asks and self.bids[0].price >= self.asks[0].price:
            buy = self.bids.popleft()
            sell = self.asks.popleft()

            trade_quantity = min(buy.quantity, sell.quantity)
            trade_price = (buy.price + sell.price) / 2

            trades.append({
                "buyer": buy.player_id,
                "seller": sell.player_id,
                "price": trade_price,
                "quantity": trade_quantity,
                "asset": buy.asset_name
            })
            # Handle remaining quantity logic (optional)
        return trades
