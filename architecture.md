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
│   └── bls_YYYYMMDD.csv
└── stock_prices/
    └── prices_YYYYMMDD.csv
```

Each ingestion script writes a date-stamped file. Every run is preserved — reruns don't overwrite history.

**Why R2 over Azure Blob or AWS S3:**
- Genuinely free tier: 10GB storage, 1M Class A operations/month, 10M Class B operations/month
- No egress fees (unlike S3)
- S3-compatible API means the ingestion code is portable

---

## Snowflake Structure

### RBAC Design

Four roles following least-privilege access:

```
ACCOUNTADMIN          ← used only for initial setup
│
├── SYSADMIN          ← owns all objects
│
├── LOADER            ← ingestion scripts write raw data only
├── TRANSFORMER       ← dbt reads raw, writes staging + intermediate + marts
└── REPORTER          ← Sigma reads marts only
```

Each role has a dedicated service user and warehouse:

| Role | User | Warehouse |
|---|---|---|
| LOADER | LOADER_USER | LOADER_WH |
| TRANSFORMER | DBT_USER | TRANSFORMER_WH |
| REPORTER | REPORTER_USER | REPORTER_WH |

All warehouses are X-Small with 60-second auto-suspend to stay within free tier limits.

### Privilege Matrix

| Schema | LOADER | TRANSFORMER | REPORTER |
|---|---|---|---|
| RAW | INSERT, UPDATE | SELECT | — |
| STAGING | — | ALL | — |
| INTERMEDIATE | — | ALL | — |
| MARTS | — | ALL | SELECT |

FUTURE grants are applied on all schemas so permissions extend automatically to newly created tables.

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
- **Dataset:** ulrikeherold/tech-layoffs-2020-2024
- **Rows:** 2,412 | **Columns:** 18
- **Key fields:** Company, Industry, Country, Laid_Off, Date_layoffs, Percentage, Stage
- **Dropped in staging:** latitude, longitude (not needed for analysis)

### Stack Overflow Developer Survey 2024
- **Rows:** 65,437 | **Columns:** 114
- **Key AI fields:** AISelect, AISent, AIBen, AIAcc, AIComplex, AIThreat, AIEthics
- **Segmentation fields:** DevType, YearsCodePro, OrgSize, Country

### Yahoo Finance Stock Prices
- **Tickers:** 69 publicly traded tech companies (see `ingestion/scripts/data/company_tickers.csv`)
- **Date range:** 2020-01-01 to present
- **Fields:** date, ticker, open, close, volume
- **Rows:** ~103,000

### BLS OEWS (Occupational Employment and Wage Statistics)
- **Series:** 22 occupations covering software, data, security, management, and AI-adjacent roles
- **Date range:** 2015–2024 (annual averages)
- **Key limitation:** See note below

#### BLS Classification Gap

The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer". Both roles are classified under `15-2051 Data Scientists`. This is not a data quality issue — it is a classification system that predates the industry's role specialisation.

This gap is surfaced explicitly in the dashboard. The government agency responsible for tracking AI's labor market impact does not yet have a category for two of the roles most discussed in that context. This is a genuine analytical observation worth highlighting to the project's target audience of data professionals and hiring managers.

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

```
int_companies_enriched.sql        -- layoffs joined to stock tickers
int_ai_exposure_by_occupation.sql -- BLS employment trends + AI exposure proxy
int_survey_trends.sql             -- SO survey pivoted by year and role
```

### Marts (`models/marts/`)

| Mart | Dashboard Tab | What it answers |
|---|---|---|
| `mart_layoff_trends.sql` | Tab 1 | Layoffs by industry, quarter, company size |
| `mart_developer_sentiment.sql` | Tab 2 | AI trust/usage trends by year and experience level |
| `mart_ai_halo_effect.sql` | Tab 3 | Layoff announcement → 30-day stock return window |
| `mart_occupation_risk.sql` | Tab 4 | BLS employment change vs. AI exposure score by occupation |

#### How BLS data feeds mart_occupation_risk

The mart answers: which occupations are shrinking, and does AI exposure correlate with that decline?

- BLS provides annual employment counts per occupation (2015–2024)
- Year-over-year change rates are computed in the intermediate layer
- AI exposure scores are joined from an O*NET-derived proxy or SO survey data
- The resulting grain: `occupation | year | employment | yoy_change_pct | ai_exposure_score`
- Visualised as a scatter in Sigma: x = AI exposure, y = employment change

#### How BLS data feeds mart_layoff_trends

BLS employment totals serve as a denominator. A company cutting 1,000 software developers is contextualised against 1.7 million nationally — expressing layoffs as a share of total occupation employment makes scale meaningful.

---

## dbt Tests

Every staging model has:
- `not_null` and `unique` tests on primary keys
- `accepted_values` on categorical columns
- Source freshness checks on date columns

Intermediate and mart models have relationship tests between joined keys.

---

## Dagster Orchestration

**Scheduled jobs:**
- `bls_ingestion_job` — weekly
- `stock_price_job` — weekly

**Manual jobs:**
- `layoffs_fyi_job` — on new CSV download
- `warn_notices_job` — monthly after WARN data publishes
- `stackoverflow_job` — annual

---

## The AI Halo Analysis

The `mart_ai_halo_effect` model computes a 30-day stock return window around two event types per company: a major AI investment announcement and a layoff event above a threshold.

This is **descriptive, not causal.** Confounders include earnings cycles, macro conditions, and sector rotation. The dashboard frames this explicitly.

---

## Environment Variables

See `.env.example` for all required keys.

---

## Snowflake Free Trial Reset

The free trial lasts 30 days. To rebuild:

1. Create a new Snowflake account
2. Update `.env` with new credentials
3. Run `snowflake/setup.sql` as `ACCOUNTADMIN`
4. Re-run all ingestion scripts
5. Run `dbt build`

No source data is lost — everything is preserved in Cloudflare R2.
