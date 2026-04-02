import boto3
import os
import io
import pandas as pd
import requests
import yfinance as yf
from datetime import date
from dotenv import load_dotenv
from dagster import asset, Output, MetadataValue

load_dotenv()

# --- Shared R2 client ---
def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )

BUCKET = os.getenv("R2_BUCKET_NAME")


@asset(group_name="ingestion", description="Upload latest Layoffs.fyi CSV to R2")
def layoffs_fyi_asset():
    local_path = "ingestion/scripts/data/layoffs_fyi_raw.csv"
    r2_key = f"layoffs_fyi/layoffs_{date.today().strftime('%Y%m%d')}.csv"

    df = pd.read_csv(local_path)
    s3 = get_r2_client()

    with open(local_path, "rb") as f:
        s3.put_object(Bucket=BUCKET, Key=r2_key, Body=f)

    return Output(
        value=r2_key,
        metadata={
            "rows": MetadataValue.int(len(df)),
            "r2_key": MetadataValue.text(r2_key),
        }
    )


@asset(group_name="ingestion", description="Upload Stack Overflow survey CSV to R2")
def so_survey_asset():
    local_path = "ingestion/scripts/data/so_survey_2024.csv"
    r2_key = f"stackoverflow_survey/survey_2024.csv"

    df = pd.read_csv(local_path)
    s3 = get_r2_client()

    with open(local_path, "rb") as f:
        s3.put_object(Bucket=BUCKET, Key=r2_key, Body=f)

    return Output(
        value=r2_key,
        metadata={
            "rows": MetadataValue.int(len(df)),
            "r2_key": MetadataValue.text(r2_key),
        }
    )


@asset(group_name="ingestion", description="Pull stock prices from Yahoo Finance and upload to R2")
def stock_prices_asset():
    tickers_path = "ingestion/scripts/data/company_tickers.csv"
    tickers_df = pd.read_csv(tickers_path)
    tickers = tickers_df["ticker"].tolist()

    start_date = "2020-01-01"
    end_date = date.today().strftime("%Y-%m-%d")

    raw = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )

    close = raw["Close"].reset_index().melt(id_vars="Date", var_name="ticker", value_name="close")
    volume = raw["Volume"].reset_index().melt(id_vars="Date", var_name="ticker", value_name="volume")
    open_ = raw["Open"].reset_index().melt(id_vars="Date", var_name="ticker", value_name="open")

    df = close.merge(volume, on=["Date", "ticker"]).merge(open_, on=["Date", "ticker"])
    df = df.rename(columns={"Date": "date"})
    df = df.dropna(subset=["close"])
    df = df[["date", "ticker", "open", "close", "volume"]].sort_values(["ticker", "date"])

    local_path = "ingestion/scripts/data/stock_prices_temp.csv"
    r2_key = f"stock_prices/prices_{date.today().strftime('%Y%m%d')}.csv"
    df.to_csv(local_path, index=False)

    s3 = get_r2_client()
    with open(local_path, "rb") as f:
        s3.put_object(Bucket=BUCKET, Key=r2_key, Body=f)

    os.remove(local_path)

    return Output(
        value=r2_key,
        metadata={
            "rows": MetadataValue.int(len(df)),
            "tickers": MetadataValue.int(df["ticker"].nunique()),
            "r2_key": MetadataValue.text(r2_key),
        }
    )


@asset(group_name="ingestion", description="Download AIOE scores from GitHub and upload to R2")
def ai_exposure_asset():
    url = "https://github.com/AIOE-Data/AIOE/raw/main/AIOE_DataAppendix.xlsx"
    r2_key = f"ai_exposure/aioe_scores_{date.today().strftime('%Y%m%d')}.csv"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    df = pd.read_excel(io.BytesIO(response.content), sheet_name="Appendix A")
    df.columns = ["soc_code", "occupation_title", "aioe_score"]
    df["soc_code"] = df["soc_code"].str.strip()
    df["source"] = "Felten, Raj & Seamans (2021) - Strategic Management Journal"
    df["year_published"] = 2021

    local_path = "ingestion/scripts/data/aioe_temp.csv"
    df.to_csv(local_path, index=False)

    s3 = get_r2_client()
    with open(local_path, "rb") as f:
        s3.put_object(Bucket=BUCKET, Key=r2_key, Body=f)

    os.remove(local_path)

    return Output(
        value=r2_key,
        metadata={
            "rows": MetadataValue.int(len(df)),
            "r2_key": MetadataValue.text(r2_key),
        }
    )
