# data.py
from openbb import obb
import pandas as pd

def get_data(symbol, start="2023-01-01", end="2025-01-01"):
    df = obb.equity.price.historical(
        symbol,
        start_date=start,
        end_date=end
    ).to_dataframe()

    df.index = pd.to_datetime(df.index).tz_localize(None)

    df = df[["open", "high", "low", "close", "volume"]].dropna()

    return df