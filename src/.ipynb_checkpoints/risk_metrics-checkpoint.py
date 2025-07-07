# /src/risk_metrics.py

import numpy as np

def calculate_sharpe_ratio(portfolio_returns, risk_free_rate=0.0):
    excess_returns = np.array(portfolio_returns) - risk_free_rate
    if len(excess_returns) < 2:
        return 0
    return np.mean(excess_returns) / np.std(excess_returns)

def calculate_volatility(portfolio_returns):
    return np.std(portfolio_returns)

def calculate_exposure(portfolio, asset_objects):
    exposure = {}
    for asset in asset_objects:
        qty = portfolio.holdings.get(asset.name, 0)
        exposure[asset.name] = qty * asset.current_price
    return exposure
