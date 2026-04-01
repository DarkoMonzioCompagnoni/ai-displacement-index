import boto3
import os
import io
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# load_raw_python.py
#
# Workaround for Snowflake external stage endpoint whitelisting requirement.
# Downloads files from Cloudflare R2 via boto3 and loads directly into
# Snowflake RAW schema using snowflake-connector-python write_pandas.
#
# Replace with COPY INTO from external stage once Snowflake support
# whitelists the R2 endpoint. See snowflake/load_raw.sql.
# =============================================================================

# --- R2 client ---
s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    region_name="auto",
)
bucket = os.getenv("R2_BUCKET_NAME")

# --- Snowflake connection (LOADER role) ---
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_LOADER_USER"),
    password=os.getenv("SNOWFLAKE_LOADER_PASSWORD"),
    role=os.getenv("SNOWFLAKE_LOADER_ROLE"),
    warehouse=os.getenv("SNOWFLAKE_LOADER_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema="RAW",
)

def get_latest_file(prefix):
    """Get the most recent file from an R2 prefix."""
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])
    if not objects:
        raise FileNotFoundError(f"No files found at R2 prefix: {prefix}")
    latest = sorted(objects, key=lambda x: x["LastModified"], reverse=True)[0]
    return latest["Key"]

def load_table(prefix, table_name, dtype=None):
    """Download latest CSV from R2 and load into Snowflake table."""
    key = get_latest_file(prefix)
    print(f"Loading {key} → {table_name}...")

    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(obj["Body"].read()), dtype=dtype, low_memory=False)

    # Normalise column names to uppercase for Snowflake
    df.columns = [c.upper().replace(" ", "_").replace("-", "_") for c in df.columns]

    cur = conn.cursor()
    cur.execute(f"TRUNCATE TABLE IF EXISTS {table_name}")

    from snowflake.connector.pandas_tools import write_pandas
    success, nchunks, nrows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        schema="RAW",
        database=os.getenv("SNOWFLAKE_DATABASE"),
        auto_create_table=True,
        overwrite=True,
    )
    print(f"  ✓ {nrows} rows loaded into {table_name}")
    cur.close()

# --- Load each source ---
load_table("layoffs_fyi/",        "LAYOFFS_FYI")
load_table("stackoverflow_survey/", "STACKOVERFLOW_SURVEY")
load_table("stock_prices/",       "STOCK_PRICES")
load_table("ai_exposure/",        "AI_EXPOSURE")

conn.close()
print("\nAll tables loaded successfully.")
