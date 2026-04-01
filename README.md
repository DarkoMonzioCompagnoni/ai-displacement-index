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
| [Layoffs.fyi via Kaggle](https://www.kaggle.com/datasets/ulrikeherold/tech-layoffs-2020-2024) | Tech layoff events 2020–2025, 2,412 rows | Manual / monthly |
| Stack Overflow Developer Survey 2024 | Developer AI sentiment and usage, 65,437 respondents | Annual |
| Yahoo Finance (`yfinance`) | Daily stock prices for 69 publicly traded tech companies | Daily |
| [Felten, Raj & Seamans AIOE](https://github.com/AIOE-Data/AIOE) | AI Occupational Exposure scores for 774 occupations | Static (2021) |

**A note on BLS data:** The BLS OEWS API and flat file server both block programmatic access. After two failed approaches, BLS employment data was replaced with the Felten et al. (2021) AIOE dataset. See [`ingestion/scripts/ingest_bls.py`](./ingestion/scripts/ingest_bls.py) for the documented failure and rationale.

**A note on BLS classification:** The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer" — both fall under `15-2051 Data Scientists`. This gap is surfaced explicitly in the dashboard.

---

## Architecture

For a detailed breakdown of the pipeline design, schema structure, and dbt model layers, see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

```
[Sources]                [Storage]            [Warehouse]     [Transform]    [Serve]

Yahoo Finance───┐
Layoffs CSV  ───┤──► Cloudflare R2 ────────► Snowflake ──────► dbt ─────────► Sigma
SO Survey CSV───┤    (raw zone,               (staging +        (marts)         Dashboard
AIOE scores  ───┘     S3-compatible)           warehouse)
```

---

## dbt Pipeline

```
RAW schema (Snowflake)
└── Staging (views)
    ├── stg_layoffs_fyi
    ├── stg_stock_prices
    ├── stg_stackoverflow_survey
    └── stg_ai_exposure
        └── Intermediate (views)
            ├── int_companies_enriched
            ├── int_ai_exposure_by_occupation
            └── int_survey_trends
                └── Marts (tables)
                    ├── mart_layoff_trends          → Tab 1: Layoff Tracker
                    ├── mart_developer_sentiment    → Tab 2: Developer Pulse
                    ├── mart_ai_halo_effect         → Tab 3: AI Halo Effect
                    └── mart_occupation_risk        → Tab 4: Occupation Risk
```

---

## Project Status

| Step | Status |
|---|---|
| Local environment setup | ✅ Complete |
| Cloudflare R2 storage | ✅ Complete |
| Snowflake setup | ✅ Complete |
| Ingestion scripts | ✅ Complete |
| dbt models | ✅ Complete |
| Dagster orchestration | 🔄 In progress |
| Sigma dashboard | ⏳ Pending |

---

## Repository Structure

```
ai-displacement-index/
├── README.md
├── ARCHITECTURE.md
├── NOTES.md
├── ai-usage.md
├── requirements.txt
├── .env.example
├── .gitignore
├── ingestion/
│   └── scripts/
│       ├── data/
│       │   └── company_tickers.csv
│       ├── ingest_layoffs_fyi.py
│       ├── ingest_so_survey.py
│       ├── ingest_stock_prices.py
│       ├── ingest_ai_exposure.py
│       ├── ingest_bls.py               # documented failure
│       ├── test_r2_connection.py
│       └── test_snowflake_connection.py
├── dagster/
│   └── jobs/
├── dbt/
│   └── ai_displacement_index/
│       ├── models/
│       │   ├── staging/
│       │   ├── intermediate/
│       │   └── marts/
│       ├── seeds/
│       │   └── company_tickers.csv
│       └── tests/
├── snowflake/
│   ├── setup.sql
│   ├── load_raw.sql                    # intended stage-based loader (blocked)
│   └── load_raw_python.py              # active Python loader workaround
├── sigma/
└── docker-compose.yml
```

---

## Snowflake Free Trial Note

This project runs on Snowflake's free trial (30 days, $400 credits). The `snowflake/setup.sql` script re-creates all roles, warehouses, and schemas from scratch. Run `snowflake/load_raw_python.py` to reload raw data, then `dbt build` to repopulate all models.

---

## AI Usage

This project was built with AI as an accelerator. Claude was used for scaffolding, debugging, and drafting. Every prompt, decision, and correction is logged in [`ai-usage.md`](./ai-usage.md) — including the cases where the AI was wrong and I had to fix it.

---

## Author

**Darko Monzio Compagnoni**
[GitHub](https://github.com/DarkoMonzioCompagnoni) · [LinkedIn](https://www.linkedin.com/in/darko-monzio-compagnoni)
