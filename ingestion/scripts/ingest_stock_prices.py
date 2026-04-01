import boto3
import os
import pandas as pd
import yfinance as yf
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

# Load ticker list from seed file
TICKERS_PATH = "ingestion/scripts/data/company_tickers.csv"
tickers_df = pd.read_csv(TICKERS_PATH)
tickers = tickers_df["ticker"].tolist()

# Pull stock prices from 2020-01-01 to today
# 2020 start gives pre-COVID baseline for context
START_DATE = "2020-01-01"
END_DATE = date.today().strftime("%Y-%m-%d")

print(f"Pulling prices for {len(tickers)} tickers from {START_DATE} to {END_DATE}...")

# Download all tickers in one batch call — faster than looping
raw = yf.download(
    tickers=tickers,
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True,
    progress=False,
)

# yfinance returns a MultiIndex DataFrame — flatten to long format
# Each row: date, ticker, open, high, low, close, volume
close = raw["Close"].reset_index().melt(
    id_vars="Date",
    var_name="ticker",
    value_name="close"
)
volume = raw["Volume"].reset_index().melt(
    id_vars="Date",
    var_name="ticker",
    value_name="volume"
)
open_ = raw["Open"].reset_index().melt(
    id_vars="Date",
    var_name="ticker",
    value_name="open"
)

df = close.merge(volume, on=["Date", "ticker"]).merge(open_, on=["Date", "ticker"])
df = df.rename(columns={"Date": "date"})
df = df.dropna(subset=["close"])
df = df[["date", "ticker", "open", "close", "volume"]]
df = df.sort_values(["ticker", "date"])

# Save locally then upload to R2
LOCAL_PATH = "ingestion/scripts/data/stock_prices_temp.csv"
R2_KEY = f"stock_prices/prices_{date.today().strftime('%Y%m%d')}.csv"

df.to_csv(LOCAL_PATH, index=False)

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    region_name="auto",
)

bucket = os.getenv("R2_BUCKET_NAME")

with open(LOCAL_PATH, "rb") as f:
    s3.put_object(Bucket=bucket, Key=R2_KEY, Body=f)

os.remove(LOCAL_PATH)

print(f"Uploaded: {R2_KEY}")
print(f"Rows: {len(df)} | Tickers with data: {df['ticker'].nunique()}")
