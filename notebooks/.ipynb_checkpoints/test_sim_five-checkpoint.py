# testsim_dashboard.py

import csv
import random
import streamlit as st
import pandas as pd
import sys

sys.path.append('../src')

from asset_classes import StockCard, BondCard, CommodityCard, CryptoCard
from order_book import OrderBook
from bots import RiskAverseBot, AggressiveBot, ContrarianBot
from market_simulation import run_simulation_round
from sentiment import roll_sentiment
from portfolio import Portfolio
from event_system import maybe_trigger_event
from market_maker import sentiment_adaptive_strategy

# --- Game Setup ---
def initialize_game():
    assets = [
        StockCard("TechCorp", 100, 5, sector="Technology"),
        StockCard("EcoPower", 90, 4, sector="Energy"),
        BondCard("GovBond 10Y", 95, 2, duration=10, yield_percent=1.5),
        CommodityCard("Gold Futures", 85, 3, reacts_to="Recession"),
        CryptoCard("BitNova", 110, 6)
    ]
    orderbook = OrderBook()
    players = [f"Player{i}" for i in range(1, 5)]
    portfolios = {pid: Portfolio(pid, initial_cash=500) for pid in players}
    portfolios["MarketMaker"] = Portfolio("MarketMaker", initial_cash=9999)

    bots = {
        "Player1": RiskAverseBot("Player1"),
        "Player2": AggressiveBot("Player2"),
        "Player3": ContrarianBot("Player3"),
        "Player4": RiskAverseBot("Player4")
    }

    price_history = {a.name: [a.current_price] for a in assets}
    portfolio_value_history = {pid: [pf.get_total_value({a.name: a.current_price for a in assets})] for pid, pf in portfolios.items()}
    logs = []

    return assets, orderbook, players, portfolios, bots, price_history, portfolio_value_history, logs

# --- Session State ---
if "round" not in st.session_state:
    (st.session_state.assets,
     st.session_state.orderbook,
     st.session_state.players,
     st.session_state.portfolios,
     st.session_state.bots,
     st.session_state.price_history,
     st.session_state.portfolio_value_history,
     st.session_state.logs) = initialize_game()
    st.session_state.round = 0
    st.session_state.current_sentiment = None

# --- Simulate Rounds ---
def simulate_round():
    st.session_state.round += 1
    sentiment = roll_sentiment()
    st.session_state.current_sentiment = sentiment

    # Trigger event (FULL event object passed now)
    event = maybe_trigger_event()

    # Market Maker provides liquidity
    for asset in st.session_state.assets:
        mm_orders = sentiment_adaptive_strategy(asset)
        for order in mm_orders:
            st.session_state.orderbook.place_order(order)

    # Bots decide and submit orders
    for pid in st.session_state.players:
        bot = st.session_state.bots[pid]
        orders = bot.decide_trades(st.session_state.portfolios[pid], st.session_state.assets, sentiment)
        for order in orders:
            st.session_state.orderbook.place_order(order)

    # ⬅️ Now pass full event object!

        event_name = run_simulation_round(
        st.session_state.assets,
        st.session_state.orderbook,
        st.session_state.portfolios,
        event
    )

    # Update price and portfolio history
    for asset in st.session_state.assets:
        st.session_state.price_history[asset.name].append(asset.current_price)

    for pid in st.session_state.portfolios:
        pf = st.session_state.portfolios[pid]
        value = pf.get_total_value({a.name: a.current_price for a in st.session_state.assets})
        st.session_state.portfolio_value_history[pid].append(value)

        if pid in st.session_state.bots:
            bot = st.session_state.bots[pid]
            if bot.update_performance(value):
                if isinstance(bot, (RiskAverseBot, ContrarianBot)):
                    st.session_state.bots[pid] = AggressiveBot(pid)
                elif isinstance(bot, AggressiveBot):
                    st.session_state.bots[pid] = ContrarianBot(pid)

    st.session_state.logs.append({
        "round": st.session_state.round,
        "sentiment": sentiment,
        "event": event_name
    })

# --- Streamlit UI ---
st.title("📈 Market Makers & Mavericks")
st.write(f"### Round {st.session_state.round}")

if st.session_state.current_sentiment:
    st.markdown(f"**🧠 Sentiment:** `{st.session_state.current_sentiment}`")

if st.button("▶️ Simulate Next Round"):
    simulate_round()

if st.button("🔄 Reset Game"):
    st.session_state.clear()
    st.experimental_rerun()

# --- Charts ---
st.subheader("📊 Asset Price History")
st.line_chart(pd.DataFrame(st.session_state.price_history))

st.subheader("💼 Portfolio Value History")
st.line_chart(pd.DataFrame(st.session_state.portfolio_value_history))

st.subheader("🗒️ Sentiment & Event Log")
st.dataframe(pd.DataFrame(st.session_state.logs))

# --- Declare Winner ---
if st.session_state.round >= 20:
    final_prices = {a.name: a.current_price for a in st.session_state.assets}
    values = {pid: pf.get_total_value(final_prices) for pid, pf in st.session_state.portfolios.items()}
    winner = max(values, key=values.get)
    st.success(f"🏆 Winner: **{winner}** with portfolio value: ${values[winner]:.2f}")
