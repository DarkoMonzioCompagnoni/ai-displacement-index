import streamlit as st
import sys
sys.path.insert(0, '.')
from snowflake_connection import run_query

st.set_page_config(page_title="Developer Pulse", layout="wide")
st.title("Developer Pulse")
st.caption("How developers feel about AI tools. Stack Overflow Developer Survey 2024, 65,437 respondents.")

@st.cache_data(ttl=3600)
def load_data():
    return run_query("""
        SELECT
            primary_dev_type,
            SUM(respondent_count) as respondents,
            ROUND(AVG(pct_uses_ai), 1) as pct_uses_ai,
            ROUND(AVG(pct_perceives_threat), 1) as pct_sees_threat,
            ROUND(AVG(pct_trusts_accuracy), 1) as pct_trusts_accuracy
        FROM MARTS.MART_DEVELOPER_SENTIMENT
        WHERE primary_dev_type IS NOT NULL
          AND primary_dev_type NOT IN ('', 'Other (please specify):')
          AND respondent_count > 10
        GROUP BY 1
        ORDER BY 3 DESC
        LIMIT 15
    """)

df = load_data()

# Filter
min_respondents = st.slider("Minimum respondents per role", 10, 500, 50, step=10)
filtered = df[df["respondents"] >= min_respondents]

st.subheader("AI adoption by developer role")
st.dataframe(
    filtered[["primary_dev_type", "respondents", "pct_uses_ai", "pct_sees_threat", "pct_trusts_accuracy"]]
    .rename(columns={
        "primary_dev_type": "Role",
        "respondents": "Respondents",
        "pct_uses_ai": "% Uses AI",
        "pct_sees_threat": "% Sees AI as Threat",
        "pct_trusts_accuracy": "% Trusts Accuracy"
    }),
    use_container_width=True,
    hide_index=True
)

st.subheader("Usage vs. perceived threat by role")
st.scatter_chart(
    filtered,
    x="pct_uses_ai",
    y="pct_sees_threat",
    color="primary_dev_type",
    x_label="% Using AI Tools",
    y_label="% Seeing AI as Job Threat"
)

st.caption("Usage and trust are diverging. More developers use AI tools than ever, but fewer trust them. Source: Stack Overflow Developer Survey 2024.")
