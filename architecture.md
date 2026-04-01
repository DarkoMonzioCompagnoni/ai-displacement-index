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

R2 is S3-compatible. The Python SDK (`boto3`) works against it with only credential and endpoint changes from AWS S3.

**Bucket:** `ai-displacement-raw`

**Object structure:**

```
ai-displacement-raw/
├── layoffs_fyi/
│   └── layoffs_YYYYMMDD.csv
├── stackoverflow_survey/
│   └── survey_YYYY.csv
├── stock_prices/
│   └── prices_YYYYMMDD.csv
├── ai_exposure/
│   └── aioe_scores_YYYYMMDD.csv
└── test/
    └── connection_check.txt
```

Each ingestion script writes a date-stamped file. Every run is preserved — reruns don't overwrite history.

---

## Data Sources

### Layoffs.fyi (via Kaggle)
- **Dataset:** ulrikeherold/tech-layoffs-2020-2024
- **Rows:** 2,412 | **Columns:** 18
- **Key fields:** Company, Industry, Country, Laid_Off, Date_layoffs, Percentage, Stage
- **Script:** `ingestion/scripts/ingest_layoffs_fyi.py`

### Stack Overflow Developer Survey 2024
- **Rows:** 65,437 | **Columns:** 114
- **Key AI fields:** AISelect, AISent, AIBen, AIAcc, AIComplex, AIThreat, AIEthics
- **Segmentation:** DevType, YearsCodePro, OrgSize, Country
- **Script:** `ingestion/scripts/ingest_so_survey.py`

### Yahoo Finance Stock Prices
- **Tickers:** 69 publicly traded tech companies (`ingestion/scripts/data/company_tickers.csv`)
- **Date range:** 2020-01-01 to present
- **Fields:** date, ticker, open, close, volume
- **Rows:** ~103,000
- **Script:** `ingestion/scripts/ingest_stock_prices.py`

### AIOE — AI Occupational Exposure Scores
- **Source:** Felten, Raj & Seamans (2021), Strategic Management Journal
- **GitHub:** https://github.com/AIOE-Data/AIOE
- **Rows:** 774 occupations indexed by 6-digit SOC code
- **Key field:** AIOE score — standardised measure of exposure to AI capabilities
- **Score range:** -2.67 (least exposed) to +1.53 (most exposed)
- **Script:** `ingestion/scripts/ingest_ai_exposure.py`

### BLS OEWS — DOCUMENTED FAILURE
- **Intent:** National occupational employment counts 2015–2024
- **Status:** All programmatic access blocked (HTTP 403) across three endpoints:
  - BLS Public Data API
  - `www.bls.gov/oes/special.requests/` direct download
  - `download.bls.gov/pub/time.series/oe/` flat file server
- **Script:** `ingestion/scripts/ingest_bls.py` — preserved as documented failure
- **Workaround:** Manual download available at [bls.gov/oes/tables.htm](https://www.bls.gov/oes/tables.htm)

---

## BLS Classification Gap

The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer". Both roles are classified under `15-2051 Data Scientists`. This is a classification system that predates the industry's role specialisation and is surfaced explicitly in the dashboard. See `NOTES.md` for framing guidance.

---

## Snowflake Structure

### RBAC Design

```
ACCOUNTADMIN          ← used only for initial setup
│
├── SYSADMIN          ← owns all objects
│
├── LOADER            ← ingestion scripts write raw data only
├── TRANSFORMER       ← dbt reads raw, writes staging + intermediate + marts
└── REPORTER          ← Sigma reads marts only
```

| Role | User | Warehouse |
|---|---|---|
| LOADER | LOADER_USER | LOADER_WH |
| TRANSFORMER | DBT_USER | TRANSFORMER_WH |
| REPORTER | REPORTER_USER | REPORTER_WH |

All warehouses are X-Small with 60-second auto-suspend.

### Privilege Matrix

| Schema | LOADER | TRANSFORMER | REPORTER |
|---|---|---|---|
| RAW | INSERT, UPDATE | SELECT | — |
| STAGING | — | ALL | — |
| INTERMEDIATE | — | ALL | — |
| MARTS | — | ALL | SELECT |

FUTURE grants applied on all schemas.

### Database and Schemas

```sql
DATABASE: AI_DISPLACEMENT
  SCHEMA: RAW           -- direct copies of source files
  SCHEMA: STAGING       -- typed, renamed, lightly cleaned
  SCHEMA: INTERMEDIATE  -- cross-source joins and enrichment
  SCHEMA: MARTS         -- aggregated, dashboard-ready
```

---

## dbt Model Layers

### Staging (`models/staging/`)

One model per source. No joins. Only typing, renaming, and null handling.

```
stg_layoffs_fyi.sql
stg_stackoverflow_survey.sql
stg_stock_prices.sql
stg_ai_exposure.sql
```

### Intermediate (`models/intermediate/`)

```
int_companies_enriched.sql        -- layoffs joined to stock tickers
int_ai_exposure_by_occupation.sql -- AIOE scores with occupation metadata
int_survey_trends.sql             -- SO survey pivoted by year and role
```

### Marts (`models/marts/`)

| Mart | Dashboard Tab | What it answers |
|---|---|---|
| `mart_layoff_trends.sql` | Tab 1 | Layoffs by industry, quarter, company size |
| `mart_developer_sentiment.sql` | Tab 2 | AI trust/usage trends by year and experience level |
| `mart_ai_halo_effect.sql` | Tab 3 | Layoff announcement → 30-day stock return window |
| `mart_occupation_risk.sql` | Tab 4 | AIOE exposure score vs. layoff prevalence by occupation |

### How AIOE feeds mart_occupation_risk

- AIOE provides a standardised exposure score per SOC code
- Layoffs.fyi provides company-level layoff events with industry tags
- The intermediate model joins them via O*NET occupation-to-industry mapping
- The mart aggregates: `occupation | aioe_score | layoff_count | avg_pct_workforce_cut`
- Visualised as a scatter in Sigma: x = AIOE score, y = layoff intensity

---

## dbt Tests

Every staging model has `not_null` and `unique` tests on primary keys, `accepted_values` on categorical columns, and source freshness checks. Intermediate and mart models have relationship tests between joined keys.

---

## Dagster Orchestration

**Scheduled:** `stock_price_job` — weekly

**Manual:** `layoffs_fyi_job`, `so_survey_job`, `ai_exposure_job` — on demand

---

## The AI Halo Analysis

The `mart_ai_halo_effect` model computes a 30-day stock return window around AI investment announcements and layoff events. This is **descriptive, not causal.** See `NOTES.md` for dashboard framing.

---

## Snowflake Free Trial Reset

1. Create a new Snowflake account
2. Update `.env` with new credentials
3. Run `snowflake/setup.sql` as `ACCOUNTADMIN`
4. Re-run all ingestion scripts
5. Run `dbt build`

No source data is lost — everything is preserved in Cloudflare R2.
