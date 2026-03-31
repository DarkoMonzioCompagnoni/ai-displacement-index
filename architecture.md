# Architecture

Technical reference for the AI Displacement Index pipeline. This document covers design decisions, schema structure, dbt model layers, and orchestration logic.

---

## Pipeline Overview

The pipeline follows a standard medallion pattern: raw files land in Cloudflare R2, get loaded into Snowflake staging tables, pass through intermediate transformations, and surface as analytics-ready mart tables consumed by Sigma.

```
[Ingest]         [Raw]              [Staging]          [Intermediate]     [Marts]
Python scripts   Cloudflare R2      Snowflake           Joined, typed,     Aggregated,
pull from APIs   (S3-compatible     raw schema          enriched models    dashboard-ready
and flat files    landing zone)     (1:1 with source)
```

Nothing is transformed before it hits Snowflake. Raw files are stored as-is in R2, giving a replayable source of truth that doesn't depend on the upstream API remaining available.

---

## Cloudflare R2 Storage

R2 is S3-compatible, meaning the Python SDK (`boto3`) works against it with only minor config changes — endpoint URL and credentials differ, but the API calls are identical to AWS S3.

**Bucket:** `ai-displacement-raw`

**Object structure:**

```
ai-displacement-raw/
├── layoffs_fyi/
│   └── layoffs_YYYYMMDD.csv
├── warn_notices/
│   └── warn_YYYYMMDD.csv
├── stackoverflow_survey/
│   └── survey_YYYY.csv
├── bls_projections/
│   └── bls_YYYYMMDD.json
└── stock_prices/
    └── prices_YYYYMMDD.csv
```

Each ingestion script writes a date-stamped file. Every run is preserved — reruns don't overwrite history.

**Why R2 over Azure Blob or AWS S3:**
- Genuinely free tier: 10GB storage, 1M Class A operations/month, 10M Class B operations/month
- No egress fees (unlike S3)
- S3-compatible API means the ingestion code is portable — switching to S3 later requires changing only credentials and endpoint

---

## Snowflake Structure

```sql
DATABASE: AI_DISPLACEMENT
  SCHEMA: RAW        -- direct copies of source files
  SCHEMA: STAGING    -- typed, renamed, lightly cleaned
  SCHEMA: MARTS      -- aggregated, analytics-ready
```

**Warehouse:** `COMPUTE_WH` (X-Small, auto-suspend after 60 seconds to stay within free tier limits)

The full setup script is in `snowflake/setup.sql`.

---

## dbt Model Layers

### Staging (`models/staging/`)

One model per source. No joins. Only:
- Column renaming to snake_case
- Type casting
- Null handling
- Source freshness tests

```
stg_layoffs_fyi.sql
stg_warn_notices.sql
stg_bls_projections.sql
stg_stackoverflow_survey.sql
stg_stock_prices.sql
```

### Intermediate (`models/intermediate/`)

Cross-source enrichment. This is where company names get standardised across sources, stock tickers get joined to layoff events, and BLS occupation codes get mapped to survey roles.

```
int_companies_enriched.sql        -- layoffs joined to stock tickers
int_ai_exposure_by_occupation.sql -- BLS projections + O*NET AI scores
int_survey_trends.sql             -- SO survey pivoted by year and role
```

### Marts (`models/marts/`)

One mart per dashboard tab. Aggregated to the grain the visualisation needs.

```
mart_layoff_trends.sql       -- layoffs by industry, quarter, company size
mart_developer_sentiment.sql -- AI trust/usage trends by year and experience
mart_ai_halo_effect.sql      -- layoff announcement → stock price (30-day window)
mart_occupation_risk.sql     -- AI exposure score vs. projected employment change
```

---

## dbt Tests

Every staging model has:
- `not_null` tests on primary keys
- `unique` tests on primary keys
- `accepted_values` on categorical columns (e.g. layoff type)
- Source freshness checks on date columns

Intermediate and mart models have relationship tests between joined keys.

---

## Dagster Orchestration

Two job types:

**Scheduled jobs** (run automatically):
- `bls_ingestion_job` — weekly, pulls latest BLS employment projections
- `stock_price_job` — weekly, pulls Yahoo Finance prices for tracked tickers

**Manual jobs** (triggered on demand):
- `layoffs_fyi_job` — run when a new CSV is downloaded
- `warn_notices_job` — run after monthly WARN data is published
- `stackoverflow_job` — run once per year when new survey drops

Each job: pulls data → writes to Cloudflare R2 → triggers Snowflake `COPY INTO` → runs dbt models downstream.

---

## The AI Halo Analysis

The `mart_ai_halo_effect` model computes a 30-day stock return window around two event types per company:

1. A major AI investment announcement (from the curated seed table)
2. A layoff event above a threshold (from Layoffs.fyi / WARN data)

This is **descriptive, not causal.** Confounders include earnings cycles, macro conditions, and sector rotation. The dashboard frames this explicitly. The goal is to surface the pattern and let the viewer interrogate it — not to make a causal claim.

---

## Environment Variables

All secrets are stored in `.env` (never committed). See `.env.example` for required keys:

```
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=AI_DISPLACEMENT
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_SCHEMA=RAW
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=ai-displacement-raw
BLS_API_KEY=
```

---

## Snowflake 120-Day Reset

The free student account expires every 120 days. To rebuild:

1. Create a new Snowflake account
2. Update `.env` with new credentials
3. Run `snowflake/setup.sql` to recreate warehouse and schemas
4. Re-run all ingestion scripts to reload raw data
5. Run `dbt build` to repopulate staging and marts

No data is lost — everything is preserved in Cloudflare R2 and the public source files.
