import boto3
import os
import pandas as pd
from datetime import date
from dotenv import load_dotenv

load_dotenv()

LOCAL_PATH = "ingestion/scripts/data/layoffs_fyi_raw.csv"
R2_KEY = f"layoffs_fyi/layoffs_{date.today().strftime('%Y%m%d')}.csv"

# Schema reference (Kaggle dataset: ulrikeherold/tech-layoffs-2020-2024)
# Nr, Company, Location_HQ, Region, USState, Country, Continent,
# Laid_Off, Date_layoffs, Percentage, Company_Size_before_Layoffs,
# Company_Size_after_layoffs, Industry, Stage, Money_Raised_in__mil,
# Year, latitude, longitude

df = pd.read_csv(LOCAL_PATH)

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

print(f"Uploaded: {R2_KEY}")
print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
