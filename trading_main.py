import yfinance as yf


def main():
    df = yf.download("AAPL", start="2024-01-01", auto_adjust=True)
    print(df.tail())
    df.to_csv("AAPL.csv")


if __name__ == "__main__":
    main()
