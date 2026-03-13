# data.py
from openbb import obb
import pandas as pd
from datetime import datetime

end = datetime.today().strftime("%Y-%m-%d")
#year - month - day
def get_data(symbol: str, start: str = "2023-01-01", end: str | None = None) -> pd.DataFrame:
    df = obb.equity.price.historical(
        symbol,
        start_date=start,
        end_date=end
    ).to_dataframe()

    df.index = pd.to_datetime(df.index).tz_localize(None)

    df = df[[ "close"]].dropna()

    return df