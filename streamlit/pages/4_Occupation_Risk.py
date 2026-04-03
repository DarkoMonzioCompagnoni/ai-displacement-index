import streamlit as st
import sys
sys.path.insert(0, '.')
from snowflake_connection import run_query

st.set_page_config(page_title="Occupation Risk", layout="wide")
st.title("Occupation Risk")
st.caption("AI Occupational Exposure (AIOE) scores for 774 occupations. Source: Felten, Raj & Seamans (2021).")

@st.cache_data(ttl=3600)
def load_data():
    return run_query("SELECT * FROM MARTS.MART_OCCUPATION_RISK")

df = load_data()

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    groups = sorted(df["occupation_group"].dropna().unique().tolist())
    selected_groups = st.multiselect("Occupation group", groups, default=groups)
with col2:
    tiers = sorted(df["exposure_tier"].dropna().unique().tolist())
    selected_tiers = st.multiselect("Exposure tier", tiers, default=tiers)
with col3:
    tech_only = st.checkbox("Tech-adjacent only", value=False)

filtered = df[
    df["occupation_group"].isin(selected_groups) &
    df["exposure_tier"].isin(selected_tiers)
]
if tech_only:
    filtered = filtered[filtered["is_tech_adjacent"] == True]

# Top 20 by AIOE score
st.subheader("Top 20 occupations by AIOE score")
top20 = filtered.sort_values("aioe_score", ascending=False).head(20)
st.bar_chart(top20.set_index("occupation_title")["aioe_score"])

# Average by group
st.subheader("Average AIOE score by occupation group")
by_group = (
    filtered.groupby("occupation_group")["aioe_score"]
    .mean()
    .round(3)
    .reset_index()
    .sort_values("aioe_score", ascending=False)
)
st.bar_chart(by_group.set_index("occupation_group")["aioe_score"])

# Full table
st.subheader("All occupations")
st.dataframe(
    filtered[["occupation_title", "occupation_group", "aioe_score", "exposure_tier", "is_tech_adjacent"]]
    .sort_values("aioe_score", ascending=False)
    .rename(columns={
        "occupation_title": "Occupation",
        "occupation_group": "Group",
        "aioe_score": "AIOE Score",
        "exposure_tier": "Tier",
        "is_tech_adjacent": "Tech Adjacent"
    }),
    use_container_width=True,
    hide_index=True
)

st.caption("Most AI-exposed occupations are not software developers. Genetic Counselors (1.53), Financial Examiners (1.53), and Actuaries (1.52) rank highest. The BLS has no standalone SOC codes for Data Analyst or Data Engineer — both fall under 15-2051 Data Scientists.")
