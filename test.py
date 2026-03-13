# test.py
import numpy as np
import pandas as pd
from data import get_data


def compute_log_returns(prices):
    return np.log(prices / prices.shift(1)).dropna()


def portfolio_returns(returns, weights):
    return returns @ weights


def sharpe_ratio(portfolio_ret, risk_free_rate=0.0):
    daily_rf = risk_free_rate / 252
    excess_ret = portfolio_ret - daily_rf

    mean = excess_ret.mean()
    std = excess_ret.std(ddof=1)

    if std == 0:
        return 0.0

    return (mean / std) * np.sqrt(252)


if __name__ == "__main__":

    symbols = ["TSLA", "NVDA", "JPM", "INTC", "META", "SCHG", "TSM"]
    price_list = []

    for s in symbols:
        df = get_data(s)
        price_list.append(df["close"].rename(s))

    prices = pd.concat(price_list, axis=1).dropna()
    returns = compute_log_returns(prices)
    weights = np.ones(len(symbols)) / len(symbols)
    port_ret = portfolio_returns(returns, weights)
    sharpe = sharpe_ratio(port_ret)

    print("Annualized Sharpe Ratio:", round(sharpe, 4))