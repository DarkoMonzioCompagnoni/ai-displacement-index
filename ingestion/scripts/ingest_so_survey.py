import boto3
import os
import pandas as pd
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# Source and destination
LOCAL_PATH = "ingestion/scripts/data/so_survey_2024.csv"
SURVEY_YEAR = 2024
R2_KEY = f"stackoverflow_survey/survey_{SURVEY_YEAR}.csv"

# Schema reference (Stack Overflow Developer Survey 2024, 65,437 respondents)
# Key AI columns: AISelect, AISent, AIBen, AIAcc, AIComplex, AIThreat, AIEthics
# Segmentation: DevType, YearsCodePro, OrgSize, Country, Employment

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
