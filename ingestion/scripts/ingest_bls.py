import boto3
import os
import json
import requests
import pandas as pd
from datetime import date
from dotenv import load_dotenv

load_dotenv()

BLS_API_KEY = os.getenv("BLS_API_KEY")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")

# BLS OEWS series IDs for tech occupations
# Format: OEUS + 000000 (national) + SOC code + measurement code (01=employment)
SERIES = {
    "Software Developers":                "OEUS000000015113201",
    "Data Scientists":                    "OEUS000000015219401",
    "Information Security Analysts":      "OEUS000000015112201",
    "Computer & Info Systems Managers":   "OEUS000000011302101",
    "Database Administrators":            "OEUS000000015114201",
    "Web Developers":                     "OEUS000000015113401",
    "Computer Programmers":               "OEUS000000015113101",
    "IT Project Managers":                "OEUS000000015119901",
}

# BLS API allows max 50 series per request, 20 years of data
payload = {
    "seriesid": list(SERIES.values()),
    "startyear": "2015",
    "endyear": "2024",
    "registrationkey": BLS_API_KEY,
    "catalog": False,
    "calculations": False,
    "annualaverage": True,
}

print("Requesting BLS data...")
response = requests.post(
    "https://api.bls.gov/publicAPI/v2/timeseries/data/",
    json=payload
)
response.raise_for_status()
data = response.json()

if data["status"] != "REQUEST_SUCCEEDED":
    raise ValueError(f"BLS API error: {data['message']}")

# Parse into flat DataFrame
series_lookup = {v: k for k, v in SERIES.items()}
rows = []

for series in data["Results"]["series"]:
    series_id = series["seriesID"]
    occupation = series_lookup.get(series_id, series_id)
    for obs in series["data"]:
        # Annual average rows have period "M13"
        if obs["period"] == "M13":
            rows.append({
                "year": int(obs["year"]),
                "occupation": occupation,
                "series_id": series_id,
                "employment": float(obs["value"].replace(",", "")) if obs["value"] != "-" else None,
                "footnotes": obs.get("footnotes", [{}])[0].get("text", ""),
            })

df = pd.DataFrame(rows).sort_values(["occupation", "year"])

print(f"Records retrieved: {len(df)}")
print(df[["year", "occupation", "employment"]].head(10).to_string(index=False))

# Save and upload to R2
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
