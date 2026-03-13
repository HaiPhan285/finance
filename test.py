import backtrader as bt
import pandas as pd
from data import get_data

# --------------------------
# 1) Strategy Definition
# --------------------------
class SmaCross(bt.Strategy):
    params = dict(fast=20, slow=50)

    def __init__(self):
        self.sma_fast = bt.ind.SMA(self.data.close, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.data.close, period=self.p.slow)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.sell()



def run_backtest(symbol):
    df = get_data(symbol)

    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(SmaCross)

    cerebro.broker.setcash(10000)
    cerebro.broker.setcommission(commission=0.001)

    print("Starting Value:", cerebro.broker.getvalue())
    results = cerebro.run()
    print("Final Value:", cerebro.broker.getvalue())

    cerebro.plot()


if __name__ == "__main__":
    run_backtest("AAPL")