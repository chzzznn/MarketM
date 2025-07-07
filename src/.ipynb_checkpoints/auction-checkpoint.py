class Bid:
    def __init__(self, player_id, price):
        self.player_id = player_id
        self.price = price

def sealed_bid_auction(bids):
    sorted_bids = sorted(bids, key=lambda x: -x.price)
    winner = sorted_bids[0]
    price_paid = sorted_bids[1].price if len(sorted_bids) > 1 else winner.price
    return winner.player_id, price_paid
