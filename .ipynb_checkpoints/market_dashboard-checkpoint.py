import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import random

from asset_classes import StockCard, BondCard, CommodityCard, CryptoCard
from order_book import OrderBook
from market_simulation import run_simulation_round
from bots import RiskAverseBot, AggressiveBot, ContrarianBot
from risk_metrics import calculate_sharpe_ratio

# --- Session Initialization ---
if "assets" not in st.session_state:
    st.session_state.assets = [
        StockCard("TechCorp", 100, 5, "Technology"),
        StockCard("EcoPower", 90, 4, "Energy"),
        BondCard("GovBond 10Y", 95, 2, 10, 1.5),
        CommodityCard("Gold Futures", 85, 3, "Recession"),
        CryptoCard("BitNova", 110, 6)
    ]
    st.session_state.price_history = {a.name: [a.current_price] for a in st.session_state.assets}
    st.session_state.round = 0
    st.session_state.orderbook = OrderBook()
    st.session_state.bots = {
        "Risky": AggressiveBot("Risky"),
        "Safe": RiskAverseBot("Safe"),
        "Reverse": ContrarianBot("Reverse")
    }
    st.session_state.portfolio_values = {name: [] for name in st.session_state.bots}
    st.session_state.logs = []

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Simulation Control")
rounds_to_run = st.sidebar.slider("Simulate Rounds", 1, 20, 1)
inspect_round = st.sidebar.slider("Review Round", 0, st.session_state.round, st.session_state.round)
selected_player = st.sidebar.selectbox("Inspect Bot", list(st.session_state.bots.keys()))
selected_asset = st.sidebar.selectbox("Inspect Asset", list(st.session_state.price_history.keys()))
show_only_player = st.sidebar.checkbox("Show Only Selected Player")

# --- Title ---
st.set_page_config(layout="wide")
st.title("📊 Market Makers & Mavericks Dashboard")

# --- Simulation ---
if st.button("▶️ Run Simulation"):
    for _ in range(rounds_to_run):
        st.session_state.round += 1
        run_simulation_round(st.session_state.assets, st.session_state.orderbook)

        for a in st.session_state.assets:
            st.session_state.price_history[a.name].append(a.current_price)

        for name, bot in st.session_state.bots.items():
            value = bot.calculate_portfolio_value(st.session_state.assets)
            st.session_state.portfolio_values[name].append(value)
            bot.last_action = bot.latest_decision_summary()

# --- Asset Price Chart ---
st.subheader("📈 Asset Prices")
price_df = pd.DataFrame(st.session_state.price_history)
price_df["Round"] = list(range(len(price_df)))
price_df = price_df.set_index("Round")
if show_only_player:
    price_df = price_df[[selected_asset]]
st.plotly_chart(px.line(price_df, title="Asset Prices"))

# --- Portfolio Value Chart ---
st.subheader("💼 Bot Portfolio Values")
port_df = pd.DataFrame(st.session_state.portfolio_values)
port_df["Round"] = list(range(len(port_df)))
port_df = port_df.set_index("Round")
if show_only_player:
    port_df = port_df[[selected_player]]
st.line_chart(port_df)

# --- Rolling Sharpe Ratio ---
st.subheader("📈 Rolling Sharpe Ratios (5-Round)")
sharpe_data = {}
for pid, values in st.session_state.portfolio_values.items():
    if len(values) >= 2:
        returns = pd.Series(values).pct_change().dropna()
        rolling = returns.rolling(window=5)
        sharpe_data[pid] = rolling.apply(lambda x: calculate_sharpe_ratio(x), raw=False)
sharpe_df = pd.DataFrame(sharpe_data)
if not sharpe_df.empty:
    sharpe_df["Round"] = sharpe_df.index
    sharpe_df = sharpe_df.set_index("Round")
    if show_only_player:
        sharpe_df = sharpe_df[[selected_player]]
    st.line_chart(sharpe_df)

# --- Round Snapshot View ---
st.subheader(f"Round Snapshot: Round {inspect_round}")
snapshot_df = pd.DataFrame({
    "Asset": list(st.session_state.price_history.keys()),
    "Price": [round(st.session_state.price_history[a][inspect_round], 2)
              for a in st.session_state.price_history]
}).set_index("Asset")
st.dataframe(snapshot_df)

bot_snapshot_df = pd.DataFrame({
    "Bot": list(st.session_state.portfolio_values.keys()),
    "Value": [round(st.session_state.portfolio_values[b][inspect_round], 2)
              if len(st.session_state.portfolio_values[b]) > inspect_round else None
              for b in st.session_state.portfolio_values]
}).set_index("Bot")
st.dataframe(bot_snapshot_df)

# --- Bot Decisions ---
st.subheader("Latest Bot Decisions")
with st.expander("Bot Trading Decisions This Round"):
    for name, bot in st.session_state.bots.items():
        st.markdown(f"**{name}**: {bot.last_action}")

# --- Current Prices ---
st.subheader("Current Prices")
for asset in st.session_state.assets:
    st.markdown(f"**{asset.name}**: ${asset.current_price:.2f}")

# --- Logs ---
st.subheader("Event & Sentiment Log")
if st.session_state.logs:
    st.dataframe(pd.DataFrame(st.session_state.logs))

# --- CSV Export ---
st.subheader("Export Data")
st.download_button("📥 Download Price History", price_df.to_csv().encode(), "price_history.csv", "text/csv")
st.download_button("📥 Download Portfolio Values", port_df.to_csv().encode(), "portfolio_values.csv", "text/csv")
