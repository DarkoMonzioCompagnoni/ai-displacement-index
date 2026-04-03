import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_REPORTER_USER"),
        password=os.getenv("SNOWFLAKE_REPORTER_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_REPORTER_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="MARTS",
        role=os.getenv("SNOWFLAKE_REPORTER_ROLE")
    )

def run_query(sql: str):
    import pandas as pd
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0].lower() for d in cur.description]
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()
