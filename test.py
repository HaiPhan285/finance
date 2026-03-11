import datetime as dt
import backtrader as bt
import yfinance as yf


class SmaCrossWithTradeLog(bt.Strategy):
    params = dict(fast=20, slow=50, stake=10)

    def __init__(self):
        fast = bt.ind.SMA(self.data.close, period=self.p.fast)
        slow = bt.ind.SMA(self.data.close, period=self.p.slow)
        self.x = bt.ind.CrossOver(fast, slow)

        self.order = None
        self.trades = []

        self._entry_date = None
        self._entry_price = None
        self._entry_size = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        exec_dt = bt.num2date(order.executed.dt) if order.executed.dt else None

        if order.status == order.Completed:
            side = "BUY" if order.isbuy() else "SELL"
            print(
                f"{exec_dt} {side} "
                f"price={order.executed.price:.4f} "
                f"size={order.executed.size} "
                f"value={order.executed.value:.2f} "
                f"comm={order.executed.comm:.2f}"
            )

            if order.isbuy():
                self._entry_date = exec_dt
                self._entry_price = order.executed.price
                self._entry_size = order.executed.size

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"{self.data.datetime.datetime(0)} ORDER FAILED: {order.Status[order.status]}")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        close_dt = self.data.datetime.datetime(0)

        entry_value = (self._entry_price or 0.0) * abs(self._entry_size or trade.size)
        pnl_net = trade.pnlcomm
        pnl_pct = (pnl_net / entry_value * 100.0) if entry_value else 0.0

        self.trades.append(
            dict(
                entry_dt=self._entry_date,
                close_dt=close_dt,
                entry_price=float(self._entry_price) if self._entry_price is not None else None,
                exit_price=float(self.data.close[0]),
                size=int(trade.size),
                pnl_net=float(pnl_net),
                pnl_pct=float(pnl_pct),
                bars_held=int(trade.barlen),
            )
        )

        print(
            f"{close_dt} TRADE CLOSED "
            f"pnl_net={pnl_net:.2f} "
            f"pnl_pct={pnl_pct:.2f}% "
            f"bars_held={trade.barlen}"
        )

        self._entry_date = None
        self._entry_price = None
        self._entry_size = 0

    def next(self):
        if self.order:
            return

        if not self.position and self.x > 0:
            self.order = self.buy(size=self.p.stake)
        elif self.position and self.x < 0:
            self.order = self.close()


def main():
    symbol = "SPY"

    # Yahoo 1-minute data has limited lookback; use period (e.g., 7d, 30d, 60d)
    period = "1d"
    interval = "1m"

    df = yf.download(
        tickers=symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        group_by="column",
        progress=False,
        prepost= True,     # set True if you want pre/after-hours (if available)
    )

    # Flatten MultiIndex columns if they exist
    if hasattr(df.columns, "levels"):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    df = df.dropna()

    print("Data start:", df.index.min())
    print("Data end:  ", df.index.max())
    print("Rows:", len(df))

    data = bt.feeds.PandasData(
        dataname=df,
        open="Open",
        high="High",
        low="Low",
        close="Close",
        volume="Volume",
        openinterest=None,
        timeframe=bt.TimeFrame.Minutes,
        compression=1,
    )

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.adddata(data)
    cerebro.addstrategy(SmaCrossWithTradeLog, fast=20, slow=50, stake=10)

    start_cash = 100_000
    cerebro.broker.setcash(start_cash)
    cerebro.broker.setcommission(commission=0.001)

    # Buy/Sell markers on the graph
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Trades)

    results = cerebro.run()
    strat = results[0]

    end_value = cerebro.broker.getvalue()
    net_profit = end_value - start_cash
    total_return_pct = (end_value / start_cash - 1.0) * 100.0

    closed = strat.trades
    wins = [t for t in closed if t["pnl_net"] > 0]
    losses = [t for t in closed if t["pnl_net"] < 0]
    win_rate_pct = (len(wins) / len(closed) * 100.0) if closed else 0.0
    avg_win_pct = (sum(t["pnl_pct"] for t in wins) / len(wins)) if wins else 0.0
    avg_loss_pct = (sum(t["pnl_pct"] for t in losses) / len(losses)) if losses else 0.0

    print("\n===== SUMMARY ($) =====")
    print(f"Symbol: {symbol}")
    print(f"Start Cash: {start_cash:.2f}")
    print(f"End Value:  {end_value:.2f}")
    print(f"Net P/L:    {net_profit:.2f}")

    print("\n===== SUMMARY (%) =====")
    print(f"Total Return: {total_return_pct:.2f}%")
    print(f"Win Rate:     {win_rate_pct:.2f}%")
    print(f"Avg Win %:    {avg_win_pct:.2f}%")
    print(f"Avg Loss %:   {avg_loss_pct:.2f}%")

    if closed:
        print("\nPer-trade:")
        for t in closed:
            print(
                f"{t['entry_dt']} -> {t['close_dt']}  "
                f"entry={t['entry_price']:.4f} exit={t['exit_price']:.4f}  "
                f"pnl={t['pnl_net']:.2f}  pct={t['pnl_pct']:.2f}%  "
                f"bars={t['bars_held']}"
            )

    cerebro.plot(style="candlestick")


if __name__ == "__main__":
    main()