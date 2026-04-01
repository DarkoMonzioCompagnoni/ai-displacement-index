import boto3
import os
import io
import requests
import pandas as pd
from datetime import date
from dotenv import load_dotenv

load_dotenv()

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")

# BLS OEWS flat file — publicly accessible file server (no browser auth needed)
# oe.occupation maps 6-digit occupation codes to names
# oe.data.1.AllData contains all historical employment/wage observations
OE_OCCUPATION_URL = "https://download.bls.gov/pub/time.series/oe/oe.occupation"
OE_DATA_URL       = "https://download.bls.gov/pub/time.series/oe/oe.data.1.AllData"
OE_SERIES_URL     = "https://download.bls.gov/pub/time.series/oe/oe.series"

# 6-digit occupation codes (SOC without hyphen) we want
# Note: no standalone codes for Data Analyst or Data Engineer in 2018 SOC
TARGET_OCC_CODES = {
    "151252": "Software Developers",
    "151253": "Software QA Analysts",
    "151254": "Web Developers",
    "151211": "Computer Systems Analysts",
    "151212": "Information Security Analysts",
    "151241": "Computer Network Architects",
    "151244": "Network & Computer Systems Admins",
    "151242": "Database Administrators",
    "151243": "Database Architects",
    "152051": "Data Scientists (incl. Data Analysts)",
    "152041": "Statisticians",
    "152031": "Operations Research Analysts",
    "113021": "Computer & Info Systems Managers",
    "131199": "Project Management Specialists",
    "273042": "Technical Writers",
    "131161": "Market Research Analysts",
    "132051": "Financial Analysts",
    "434051": "Customer Service Representatives",
}

print("Step 1/3: Downloading series file to find matching series IDs...")
series_resp = requests.get(OE_SERIES_URL, timeout=60)
series_resp.raise_for_status()

series_df = pd.read_csv(
    io.StringIO(series_resp.text),
    sep="\t",
    dtype=str
)
series_df.columns = series_df.columns.str.strip()
series_df = series_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

print(f"  Total series: {len(series_df)}")
print(f"  Columns: {series_df.columns.tolist()}")

# Filter to national (area_code = 0000000), all industries (industry_code = 000000),
# employment datatype (datatype_code = 01), our target occupations
target_series = series_df[
    (series_df["occupation_code"].isin(TARGET_OCC_CODES.keys())) &
    (series_df["industry_code"] == "000000") &
    (series_df["datatype_code"] == "01")
]["series_id"].tolist()

print(f"  Matching series IDs found: {len(target_series)}")

if not target_series:
    print("  No series found. Showing sample rows:")
    print(series_df[series_df["occupation_code"].isin(TARGET_OCC_CODES.keys())].head(10))
    raise ValueError("No matching series found — check occupation codes and filter conditions")

print("\nStep 2/3: Downloading full OEWS data file (~300MB, takes ~60s)...")
data_resp = requests.get(OE_DATA_URL, timeout=300, stream=True)
data_resp.raise_for_status()

chunks = []
downloaded = 0
for chunk in data_resp.iter_content(chunk_size=10 * 1024 * 1024):
    chunks.append(chunk)
    downloaded += len(chunk)
    print(f"  Downloaded {downloaded / 1024 / 1024:.0f} MB...", end="\r")

print(f"\n  Download complete: {downloaded / 1024 / 1024:.0f} MB")

raw_data = pd.read_csv(
    io.StringIO(b"".join(chunks).decode("utf-8")),
    sep="\t",
    dtype=str
)
raw_data.columns = raw_data.columns.str.strip()
raw_data = raw_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

print(f"  Total rows: {len(raw_data)}")

# Filter to our series and annual average period (A01)
df = raw_data[
    (raw_data["series_id"].isin(target_series)) &
    (raw_data["period"] == "A01")
].copy()

# Join occupation names
df["occupation_code"] = df["series_id"].map(
    series_df.set_index("series_id")["occupation_code"]
)
df["occupation"] = df["occupation_code"].map(TARGET_OCC_CODES)
df["employment"] = pd.to_numeric(df["value"], errors="coerce")
df = df[["year", "occupation_code", "occupation", "employment"]].dropna()
df["year"] = df["year"].astype(int)
df = df.sort_values(["occupation", "year"])

print(f"\nStep 3/3: Results")
print(f"  Occupations found: {df['occupation'].nunique()}")
print(f"  Year range: {df['year'].min()} – {df['year'].max()}")
print(f"  Total rows: {len(df)}")
print(df.groupby("occupation")[["year", "employment"]].last().to_string())

# Upload to R2
LOCAL_PATH = "ingestion/scripts/data/bls_temp.csv"
R2_KEY = f"bls_projections/bls_{date.today().strftime('%Y%m%d')}.csv"

df.to_csv(LOCAL_PATH, index=False)

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)

with open(LOCAL_PATH, "rb") as f:
    s3.put_object(Bucket=R2_BUCKET_NAME, Key=R2_KEY, Body=f)

os.remove(LOCAL_PATH)
print(f"\nUploaded: {R2_KEY}")
