import streamlit as st
import pandas as pd
import sys
sys.path.insert(0, '.')
from snowflake_connection import run_query

st.set_page_config(page_title="Layoff Tracker", layout="wide")
st.title("Layoff Tracker")
st.caption("Tech layoffs 2020-2025. Two phases: post-pandemic correction (2022-2023) and AI-driven restructuring (2024-2025).")

@st.cache_data(ttl=3600)
def load_data():
    return run_query("""
        SELECT * FROM MARTS.MART_LAYOFF_TRENDS
        WHERE LAYOFF_YEAR IS NOT NULL
    """)

df = load_data()

# Filters
col1, col2 = st.columns(2)
with col1:
    years = sorted(df["layoff_year"].dropna().unique().tolist())
    selected_years = st.multiselect("Year", years, default=years)
with col2:
    industries = sorted(df["industry"].dropna().unique().tolist())
    selected_industries = st.multiselect("Industry", industries, default=industries)

filtered = df[
    df["layoff_year"].isin(selected_years) &
    df["industry"].isin(selected_industries)
]

# By year
st.subheader("Employees laid off by year")
by_year = (
    filtered.groupby("layoff_year")
    .agg(employees_laid_off=("total_laid_off", "sum"), layoff_events=("layoff_events", "sum"))
    .reset_index()
    .sort_values("layoff_year")
)
st.bar_chart(by_year.set_index("layoff_year")["employees_laid_off"])

# By industry
st.subheader("Top industries by employees laid off")
by_industry = (
    filtered.groupby("industry")
    .agg(employees_laid_off=("total_laid_off", "sum"))
    .reset_index()
    .sort_values("employees_laid_off", ascending=False)
    .head(15)
)
st.bar_chart(by_industry.set_index("industry")["employees_laid_off"])

# By stage
st.subheader("Layoffs by company stage")
by_stage = (
    filtered[filtered["stage"].notna() & (filtered["stage"] != "Unknown")]
    .groupby("stage")
    .agg(employees_laid_off=("total_laid_off", "sum"))
    .reset_index()
    .sort_values("employees_laid_off", ascending=False)
)
st.bar_chart(by_stage.set_index("stage")["employees_laid_off"])

st.caption("Source: Layoffs.fyi via Kaggle. 2022-2023 layoffs were post-pandemic corrections. By 2024-2025, companies began explicitly framing cuts as AI-driven restructuring.")
