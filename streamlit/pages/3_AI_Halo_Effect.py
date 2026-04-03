import streamlit as st
import sys
sys.path.insert(0, '.')
from snowflake_connection import run_query

st.set_page_config(page_title="AI Halo Effect", layout="wide")
st.title("AI Halo Effect")
st.caption("Stock price trajectory around layoff announcements. Day 0 = announcement date. Returns indexed to closing price on that day.")

@st.cache_data(ttl=3600)
def load_companies():
    return run_query("""
        SELECT DISTINCT
            company,
            ticker,
            layoff_year,
            date_layoffs,
            laid_off
        FROM MARTS.MART_LAYOFF_PRICE_WINDOWS
        WHERE base_price IS NOT NULL
        ORDER BY company, date_layoffs
    """)

@st.cache_data(ttl=3600)
def load_window(company, date_layoffs):
    return run_query(f"""
        SELECT
            days_from_event,
            indexed_return,
            close_price,
            base_price
        FROM MARTS.MART_LAYOFF_PRICE_WINDOWS
        WHERE company = '{company}'
          AND date_layoffs = '{date_layoffs}'
        ORDER BY days_from_event
    """)

companies = load_companies()
companies["label"] = companies["company"] + " (" + companies["ticker"] + " - " + companies["layoff_year"].astype(str) + " - " + companies["date_layoffs"].astype(str) + ")"

# Filters
col1, col2 = st.columns(2)
with col1:
    years = sorted(companies["layoff_year"].dropna().unique().tolist())
    selected_year = st.selectbox("Year", ["All"] + years)
with col2:
    filtered_companies = companies if selected_year == "All" else companies[companies["layoff_year"] == selected_year]
    selected_label = st.selectbox("Company / Event", filtered_companies["label"].tolist())

selected_row = companies[companies["label"] == selected_label].iloc[0]
df = load_window(selected_row["company"], selected_row["date_layoffs"])

if not df.empty:
    laid_off = selected_row["laid_off"]
    st.metric("Employees laid off", f"{int(laid_off):,}" if laid_off and str(laid_off) != 'nan' else "N/A")

    st.subheader(f"{selected_row['company']} — {selected_row['date_layoffs']}")
    st.line_chart(df.set_index("days_from_event")["indexed_return"])
    st.caption("Pre-announcement movement shows whether the stock was already under pressure before the layoff was announced.")
else:
    st.warning("No price data available for this event.")

st.divider()
st.caption("This analysis is descriptive, not causal. Stock returns around layoff events reflect earnings cycles, macro conditions, and sector rotation. The AI halo pattern is a hypothesis, not a conclusion.")
