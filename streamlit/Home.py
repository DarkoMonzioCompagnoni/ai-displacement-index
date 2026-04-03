import streamlit as st

st.set_page_config(
    page_title="AI Displacement Index",
    page_icon="📊",
    layout="wide"
)

st.title("AI Displacement Index")
st.markdown("""
A data pipeline tracking tech layoffs, developer sentiment on AI, and market reaction to AI announcements.

**Four datasets. One question:** is AI displacing tech workers, or is that story more complicated than the headlines suggest?

---

| Page | Question |
|---|---|
| Layoff Tracker | Which industries and years saw the most cuts? |
| Developer Pulse | Are developers trusting AI more or less over time? |
| AI Halo Effect | Do stocks rise when companies announce layoffs framed as AI restructuring? |
| Occupation Risk | Which roles face the highest AI exposure? |

---

**Stack:** Python · Snowflake · dbt · Cloudflare R2 · Dagster · Streamlit

**Data sources:** Layoffs.fyi · Stack Overflow Survey 2024 · Yahoo Finance · Felten et al. AIOE (2021)

**Author:** [Darko Monzio Compagnoni](https://www.linkedin.com/in/darko-monzio-compagnoni)
""")
