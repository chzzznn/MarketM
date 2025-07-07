import random
import streamlit as st  # Required if logging to st.session_state
from src.dice import roll_dice_pool
from src.sentiment import roll_sentiment
from src.event_system import maybe_trigger_event
from src.order_book import Order
from src.risk_metrics import calculate_sharpe_ratio, calculate_volatility, calculate_exposure

def run_simulation_round(assets, orderbook, portfolios=None, event=None):
    print("\n🔄 Simulating Market Round...")

    event_impact = event["impact"] if event else {}
    event_name = event["name"] if event else "None"

    print(f"\n🌐 Market Event: {event_name}")

    sentiment_map = {}
    for asset in assets:
        die = roll_dice_pool(size=2, strategy='max')
        sentiment = roll_sentiment()
        sentiment_map[asset.name] = sentiment

        multiplier = 1.0
        if event_impact:
            impact = event_impact.get(asset.name) or event_impact.get("all")
            if impact:
                multiplier += impact

        asset.update_price(die, sentiment, multiplier)

        # Market maker adds liquidity
        for mm_order in generate_market_maker_orders(asset):
            orderbook.place_order(mm_order)

    if portfolios:
        trades = orderbook.match_orders()
        for trade in trades:
            buyer = trade["buyer"]
            seller = trade["seller"]
            asset_name = trade["asset"]
            qty = trade["quantity"]
            price = trade["price"]

            if buyer in portfolios:
                portfolios[buyer].update_position(asset_name, qty, price, is_buy=True)
            if seller in portfolios:
                portfolios[seller].update_position(asset_name, qty, price, is_buy=False)

        print("\n🎁 Diversification Bonuses:")
        for pid, pf in portfolios.items():
            if check_diversification_bonus(pf, assets):
                pf.cash += 10
                print(f"✅ {pid} earns +10 MAVUSD for diversification!")

    print("\n📊 Prices After Round:")
    for asset in assets:
        print(f"{asset.name}: ${asset.current_price:.2f}")

    if hasattr(st.session_state, "logs"):
        st.session_state.logs.append({
            "round": st.session_state.round,
            "event": event_name,
            "sentiments": sentiment_map
        })

    return event_name

def generate_market_maker_orders(asset, spread=2, quantity=1):
    bid_price = asset.current_price - spread
    ask_price = asset.current_price + spread

    bid = Order("MarketMaker", asset.name, bid_price, quantity, True)
    ask = Order("MarketMaker", asset.name, ask_price, quantity, False)
    return [bid, ask]

def check_diversification_bonus(portfolio, asset_objects):
    held_types = set()
    for asset in asset_objects:
        if portfolio.holdings.get(asset.name, 0) > 0:
            held_types.add(asset.__class__.__name__)
    return len(held_types) >= 3
