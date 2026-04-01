import boto3
import os
import pandas as pd
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")

# Felten, Raj & Seamans (2021) — AI Occupational Exposure (AIOE) scores
# Source: https://github.com/AIOE-Data/AIOE
# 774 occupations indexed by 6-digit SOC code
# AIOE score = standardized measure of occupation's exposure to AI capabilities
# Higher score = greater exposure to AI displacement or augmentation
# Based on O*NET occupational abilities linked to AI application benchmarks

LOCAL_PATH = "ingestion/scripts/data/aioe_scores.xlsx"
R2_KEY = f"ai_exposure/aioe_scores_{date.today().strftime('%Y%m%d')}.csv"

df = pd.read_excel(LOCAL_PATH, sheet_name="Appendix A")
df.columns = ["soc_code", "occupation_title", "aioe_score"]
df["soc_code"] = df["soc_code"].str.strip()
df["source"] = "Felten, Raj & Seamans (2021) - Strategic Management Journal"
df["year_published"] = 2021

print(f"Occupations loaded: {len(df)}")
print(f"AIOE score range: {df['aioe_score'].min():.3f} to {df['aioe_score'].max():.3f}")
print(f"\nTop 10 most AI-exposed occupations:")
print(df.nlargest(10, "aioe_score")[["soc_code", "occupation_title", "aioe_score"]].to_string(index=False))
print(f"\nBottom 10 least AI-exposed occupations:")
print(df.nsmallest(10, "aioe_score")[["soc_code", "occupation_title", "aioe_score"]].to_string(index=False))

# Save to CSV and upload to R2
csv_path = "ingestion/scripts/data/aioe_temp.csv"
df.to_csv(csv_path, index=False)

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)

with open(csv_path, "rb") as f:
    s3.put_object(Bucket=R2_BUCKET_NAME, Key=R2_KEY, Body=f)

os.remove(csv_path)
print(f"\nUploaded: {R2_KEY}")
