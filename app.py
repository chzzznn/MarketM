
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.asset_classes import StockCard, BondCard, CommodityCard, CryptoCard
from src.order_book import OrderBook
from src.market_simulation import run_simulation_round
from src.bots import RiskAverseBot, AggressiveBot, ContrarianBot

st.set_page_config(page_title="Market Makers & Mavericks", layout="wide")

# --- Initialization ---
if "assets" not in st.session_state:
    st.session_state.assets = [
        StockCard("TechCorp", base_price=100, volatility=5, sector="Technology"),
        StockCard("EcoPower", base_price=90, volatility=4, sector="Energy"),
        BondCard("GovBond 10Y", base_price=95, volatility=2, duration=10, yield_percent=1.5),
        CommodityCard("Gold Futures", base_price=85, volatility=3, reacts_to="Recession"),
        CryptoCard("BitNova", base_price=110, volatility=6)
    ]
    st.session_state.orderbook = OrderBook()
    st.session_state.round = 0
    st.session_state.portfolios = {"Player1": [], "Player2": []}
    st.session_state.price_history = {a.name: [a.current_price] for a in st.session_state.assets}

st.title("📈 Market Makers & Mavericks Simulator")

if st.button("▶️ Simulate Round"):
    st.session_state.round += 1
    run_simulation_round(
        st.session_state.assets,
        st.session_state.orderbook,
        st.session_state.portfolios
    )
    for a in st.session_state.assets:
        st.session_state.price_history[a.name].append(a.current_price)

# --- Plotting ---
st.subheader("📊 Asset Prices Over Time")
for name, history in st.session_state.price_history.items():
    plt.plot(history, label=name)
plt.xlabel("Round")
plt.ylabel("Price")
plt.legend()
st.pyplot(plt)
