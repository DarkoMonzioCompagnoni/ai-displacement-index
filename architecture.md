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

Nothing is transformed before it hits Snowflake. Raw files are stored as-is in R2, giving a replayable source of truth.

---

## Cloudflare R2 Storage

R2 is S3-compatible — `boto3` works against it with a different endpoint URL but identical API calls to AWS S3.

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
└── warn_notices/                        # Pending
```

Each ingestion script writes a date-stamped file, preserving full history.

**Why R2:** Free tier (10GB, 1M ops/month), no egress fees, S3-compatible API.

---

## Ingestion Scripts

| Script | Source | Method | Status |
|---|---|---|---|
| `ingest_layoffs_fyi.py` | Kaggle CSV | Manual download → R2 | ✅ |
| `ingest_so_survey.py` | Kaggle CSV (Stack Overflow 2024) | Manual download → R2 | ✅ |
| `ingest_stock_prices.py` | Yahoo Finance API | API → R2, 69 tickers | ✅ |
| `ingest_ai_exposure.py` | Felten et al. AIOE (GitHub) | HTTP download → R2 | ✅ |
| `ingest_bls.py` | BLS OEWS | **FAILED** — BLS blocks programmatic access | ❌ |

### BLS Ingestion Failure

Three approaches attempted and blocked:

1. **BLS Public Data API** — OEWS series IDs are undocumented. Two attempts with different formats both returned "Series does not exist".
2. **BLS special requests download** (www.bls.gov) — HTTP 403 for non-browser clients.
3. **BLS flat file server** (download.bls.gov) — HTTP 403 for non-browser clients.

**Replacement:** Felten et al. AIOE dataset. See `ingestion/scripts/ingest_bls.py` for full documentation.

---

## Loading Raw Data into Snowflake

### Intended approach — Snowflake External Stage (S3-compatible)

The designed approach uses a Snowflake external stage pointing to Cloudflare R2, then `COPY INTO` to load tables in the RAW schema. The stage definition is in `snowflake/load_raw.sql`.

```sql
CREATE OR REPLACE STAGE r2_raw_stage
    URL = 's3compat://ai-displacement-raw/'
    ENDPOINT = '<account_id>.r2.cloudflarestorage.com'
    CREDENTIALS = (AWS_KEY_ID = '...' AWS_SECRET_KEY = '...');

COPY INTO layoffs_fyi FROM @r2_raw_stage/layoffs_fyi/ PATTERN = '.*\.csv';
```

**Why it is not currently active:** Snowflake requires endpoints to be whitelisted before S3-compatible stages can connect. Despite Cloudflare R2 being listed as a supported vendor and the docs stating `r2.cloudflarestorage.com` is "enabled by default," the free trial account returns `Endpoint cannot be used with storage type S3`. A Snowflake support ticket has been submitted to whitelist the endpoint. Once approved, `load_raw.sql` can be run in Snowsight to migrate from the Python loader to the stage-based approach.

### Current approach — Python direct loader

As a workaround, `snowflake/load_raw_python.py` downloads files from R2 via `boto3` and writes directly to Snowflake using `snowflake-connector-python`. No external stage required.

This approach:
- Is less elegant than COPY INTO (loads in memory, slower for large files)
- Works without Snowflake support intervention
- Is a valid real-world pattern for smaller datasets
- Is documented here as a deliberate engineering decision, not a shortcut

Once the stage is whitelisted, the Python loader will be retired in favour of `COPY INTO`.

---

## Snowflake Structure

### RBAC Design

```
ACCOUNTADMIN          ← initial setup only
│
├── SYSADMIN          ← owns all objects
├── LOADER            ← ingestion scripts: writes RAW only
├── TRANSFORMER       ← dbt: reads RAW, writes STAGING + INTERMEDIATE + MARTS
└── REPORTER          ← Sigma: reads MARTS only
```

| Role | User | Warehouse |
|---|---|---|
| LOADER | LOADER_USER | LOADER_WH |
| TRANSFORMER | DBT_USER | TRANSFORMER_WH |
| REPORTER | REPORTER_USER | REPORTER_WH |

All warehouses: X-Small, 60-second auto-suspend.

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

## Data Sources

### Layoffs.fyi (via Kaggle)
- **Rows:** 2,412 | **Columns:** 18
- **Key fields:** Company, Industry, Country, Laid_Off, Date_layoffs, Percentage, Stage
- **Dropped in staging:** latitude, longitude

### Stack Overflow Developer Survey 2024
- **Rows:** 65,437 | **Columns:** 114
- **Key AI fields:** AISelect, AISent, AIBen, AIAcc, AIComplex, AIThreat, AIEthics
- **Segmentation:** DevType, YearsCodePro, OrgSize, Country

### Yahoo Finance Stock Prices
- **Tickers:** 69 publicly traded tech companies
- **Date range:** 2020-01-01 to present
- **Fields:** date, ticker, open, close, volume
- **Rows:** ~103,000

### Felten, Raj & Seamans AIOE Scores
- **Occupations:** 774 indexed by 6-digit SOC code
- **Score range:** -2.67 (Dancers) to +1.53 (Genetic Counselors)
- **Citation:** Felten E, Raj M, Seamans R (2021), Strategic Management Journal 42(12):2195–2217

#### BLS Classification Gap

The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer". Both fall under `15-2051 Data Scientists`. Surfaced explicitly in the dashboard.

---

## dbt Model Layers

### Staging (`models/staging/`)

One model per source. No joins. Type casting, column renaming, null handling, source freshness tests.

```
stg_layoffs_fyi.sql
stg_stackoverflow_survey.sql
stg_stock_prices.sql
stg_ai_exposure.sql
```

### Intermediate (`models/intermediate/`)

```
int_companies_enriched.sql        -- layoffs joined to stock tickers
int_ai_exposure_by_occupation.sql -- AIOE scores mapped to occupation groups
int_survey_trends.sql             -- SO survey pivoted by year and role
```

### Marts (`models/marts/`)

| Mart | Dashboard Tab | What it answers |
|---|---|---|
| `mart_layoff_trends.sql` | Tab 1 | Layoffs by industry, quarter, company size |
| `mart_developer_sentiment.sql` | Tab 2 | AI trust/usage trends by year and experience level |
| `mart_ai_halo_effect.sql` | Tab 3 | Layoff announcement → 30-day stock return window |
| `mart_layoff_price_windows.sql` | Tab 3 (detail) | Daily stock prices ±30 days around each layoff event |
| `mart_occupation_risk.sql` | Tab 4 | AIOE exposure score vs. layoff prevalence by occupation |

### New mart: `mart_layoff_price_windows`

Built to support the AI Halo Effect page's stock trajectory visualization. Joins each layoff event to daily stock prices in a ±30 day window. `indexed_return` is calculated relative to the closing price on the announcement date (day 0 = 0%), making pre/post movement directly comparable across companies.

One edge case: if the announcement falls on a weekend or holiday, `base_price` is NULL and the event is excluded from the visualization.

---

## dbt Tests

Every staging model:
- `not_null` and `unique` on primary keys
- `accepted_values` on categorical columns
- Source freshness checks on date columns

Intermediate and mart models: relationship tests between joined keys.

---

## Dagster Orchestration

**Scheduled:** `stock_price_job` — weekly

**Manual:** `layoffs_fyi_job`, `so_survey_job`, `ai_exposure_job`

---

## The AI Halo Analysis

Descriptive, not causal. See `NOTES.md` for dashboard framing guidance.

---

## Environment Variables

See `.env.example`.

---

## Snowflake Free Trial Reset

1. Create new Snowflake account
2. Update `.env`
3. Run `snowflake/setup.sql` as `ACCOUNTADMIN`
4. Run `snowflake/load_raw_python.py` to reload raw tables
5. Run `dbt build`

Source data preserved in Cloudflare R2.
