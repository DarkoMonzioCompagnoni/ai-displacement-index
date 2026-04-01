# AI Displacement Index

**A public data pipeline tracking tech layoffs, developer sentiment on AI, and market reaction — built with Snowflake, dbt, Cloudflare R2, and Dagster.**

---

## What This Project Tracks

Since ChatGPT's release in late 2022, companies have announced record AI investments while simultaneously cutting thousands of workers. The story told in press releases doesn't always match the data.

This project builds an end-to-end analytics pipeline to examine three connected questions:

- **Labor:** Which industries and roles shed workers fastest since 2022, and how does that map to AI adoption timelines?
- **Sentiment:** Are developers trusting AI more or less over time? Does that split by experience level?
- **Finance:** Do companies that announce major AI investments see stock gains even while laying off workers — the "AI halo" effect?

The goal is not to prove a thesis. It is to put clean, structured data in front of those questions and let the numbers speak.

---

## Why I Built This

I work as a data analytics engineer. AI is reshaping the tools I use, the roles around me, and the industry I work in. I wanted a project that reflected that reality — not a toy dataset, but something with genuine analytical weight that exercises the full stack I work with professionally.

I also wanted to be transparent about how I used AI in building it. You'll find that in [`ai-usage.md`](./ai-usage.md).

---

## Stack

| Layer | Tool |
|---|---|
| Cloud Warehouse | Snowflake (free trial) |
| Cloud Storage | Cloudflare R2 (raw landing zone) |
| Transformation | dbt Core + Snowflake adapter |
| Orchestration | Dagster |
| Visualization | Sigma (public dashboard) |
| Containerization | Docker |
| Language | Python 3.11 |

---

## Data Sources

| Source | What it provides | Refresh |
|---|---|---|
| [Layoffs.fyi via Kaggle](https://www.kaggle.com/datasets/ulrikeherold/tech-layoffs-2020-2024) | Tech layoff events 2020–2025, 2,412 records | Manual / monthly |
| Stack Overflow Developer Survey 2024 | Developer AI sentiment, 65,437 respondents | Annual |
| Yahoo Finance (`yfinance`) | Daily stock prices for 69 publicly traded tech companies | Daily |
| Felten, Raj & Seamans (2021) AIOE | AI exposure scores for 774 occupations by SOC code | Static |
| AI investment announcements | Curated seed table (MSFT, Google, Meta, Amazon) | Manual |

**A note on BLS data:** Programmatic access to BLS OEWS data was blocked at all endpoints — API, direct download, and flat file server. The script is preserved in `ingestion/scripts/ingest_bls.py` with full documentation of the failure. Employment denominator data can be manually downloaded from [bls.gov/oes/tables.htm](https://www.bls.gov/oes/tables.htm) when needed.

**A note on BLS classification:** The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer" — both fall under `15-2051 Data Scientists`. This limitation is surfaced explicitly in the dashboard.

---

## Architecture

For a detailed breakdown of the pipeline design, schema structure, and dbt model layers, see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

```
[Sources]                [Storage]            [Warehouse]     [Transform]    [Serve]

Yahoo Finance───┐
Layoffs CSV  ───┤──► Cloudflare R2 ────────► Snowflake ──────► dbt ─────────► Sigma
SO Survey    ───┤    (raw zone,               (staging +        (marts)         Dashboard
AIOE CSV     ───┘     S3-compatible)           warehouse)
```

Dagster orchestrates the scheduled pulls (Yahoo Finance runs on a weekly cadence). Annual and static sources are loaded manually.

---

## Project Status

| Step | Status |
|---|---|
| Local environment setup | ✅ Complete |
| Cloudflare R2 storage | ✅ Complete |
| Snowflake setup | ✅ Complete |
| Ingestion scripts | ✅ Complete |
| dbt models | 🔄 In progress |
| Dagster orchestration | ⏳ Pending |
| Sigma dashboard | ⏳ Pending |

---

## Repository Structure

```
ai-displacement-index/
├── README.md
├── ARCHITECTURE.md
├── NOTES.md                              # Analytical observations for the dashboard
├── ai-usage.md
├── requirements.txt
├── .env.example
├── .gitignore
├── ingestion/
│   └── scripts/
│       ├── data/
│       │   └── company_tickers.csv       # 69 publicly traded tech companies
│       ├── ingest_layoffs_fyi.py         # Layoffs.fyi → R2
│       ├── ingest_so_survey.py           # Stack Overflow survey → R2
│       ├── ingest_stock_prices.py        # Yahoo Finance → R2
│       ├── ingest_ai_exposure.py         # AIOE scores → R2
│       ├── ingest_bls.py                 # DOCUMENTED FAILURE — BLS blocked
│       ├── test_r2_connection.py
│       └── test_snowflake_connection.py
├── dagster/
│   └── jobs/
├── dbt/                                  # Populated by dbt init
├── snowflake/
│   └── setup.sql
├── sigma/
└── docker-compose.yml
```

---

## Snowflake Free Trial Note

The `snowflake/setup.sql` script re-creates all roles, warehouses, and schemas from scratch. Credentials are managed via `.env` — see `.env.example` for required variables.

---

## AI Usage

This project was built with AI as an accelerator. Every prompt, decision, and correction is logged in [`ai-usage.md`](./ai-usage.md) — including the cases where the AI was wrong and I had to fix it.

---

## Author

**Darko Monzio Compagnoni**
[GitHub](https://github.com/DarkoMonzioCompagnoni) · [LinkedIn](https://www.linkedin.com/in/darko-monzio-compagnoni)
