# AI Displacement Index

**A public data pipeline tracking tech layoffs, developer sentiment on AI, and market reaction — built with Snowflake, dbt, Cloudflare R2, and Dagster.**

---

## What This Project Tracks

Since ChatGPT's release in late 2022, companies have announced record AI investments while simultaneously cutting thousands of workers. The story told in press releases doesn't always match the data.

This project builds an end-to-end analytics pipeline to examine three connected questions:

- **Labor:** Which industries and roles shed workers fastest since 2022, and how does that map to AI adoption timelines?
- **Sentiment:** Are developers trusting AI more or less over time? Does that split by experience level?
- **Finance:** Do companies that announce major AI initiatives see stock gains even while laying off workers — the "AI halo" effect?

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
| [Layoffs.fyi](https://layoffs.fyi) | Tech layoff events since 2022 | Manual / monthly |
| WARN Act (ICPSR / Federal Reserve) | Formal US layoff notices by state | Monthly |
| Stack Overflow Developer Survey 2022–2025 | Developer AI sentiment over time | Annual |
| BLS Employment Projections API | Occupation-level AI exposure scores | Annual |
| Yahoo Finance (`yfinance`) | Stock prices for major tech firms | Daily |
| AI investment announcements | Curated seed table (MSFT, Google, Meta, Amazon) | Manual |

---

## Architecture

For a detailed breakdown of the pipeline design, schema structure, and dbt model layers, see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

```
[Sources]                [Storage]            [Warehouse]     [Transform]    [Serve]

BLS API      ───┐
Yahoo Finance───┤──► Cloudflare R2 ────────► Snowflake ──────► dbt ─────────► Sigma
Layoffs CSV  ───┤    (raw zone,               (staging +        (marts)         Dashboard
WARN CSV     ───┘     S3-compatible)           warehouse)
SO Survey CSV
```

Dagster orchestrates the scheduled pulls (BLS + Yahoo Finance run on a weekly cadence). Annual sources are loaded manually. A `docker-compose.yml` runs the full stack locally.

---

## Project Status

| Step | Status |
|---|---|
| Local environment setup | ✅ Complete |
| Cloudflare R2 storage | ✅ Complete |
| Snowflake setup | ✅ Complete |
| Ingestion scripts | 🔄 In progress |
| dbt models | ⏳ Pending |
| Dagster orchestration | ⏳ Pending |
| Sigma dashboard | ⏳ Pending |

---

## Repository Structure

```
ai-displacement-index/
├── README.md                            # This file
├── ARCHITECTURE.md                      # Technical deep-dive
├── ai-usage.md                          # Transparent log of AI assistance
├── requirements.txt                     # Pinned Python dependencies
├── .env.example                         # Required environment variables (no secrets)
├── .gitignore
├── ingestion/
│   └── scripts/
│       ├── test_r2_connection.py        # Validates Cloudflare R2 connectivity
│       └── test_snowflake_connection.py # Validates Snowflake connectivity
├── dagster/
│   └── jobs/                            # Dagster job definitions
├── dbt/                                 # Populated by dbt init
├── snowflake/
│   └── setup.sql                        # Full RBAC + warehouse + schema setup
├── sigma/                               # Dashboard export / embed link
└── docker-compose.yml                   # Local orchestration
```

---

## Snowflake Free Trial Note

This project runs on Snowflake's free trial (30 days, $400 credits). The `snowflake/setup.sql` script re-creates all roles, warehouses, and schemas from scratch. Credentials are managed via `.env` — see `.env.example` for the required variables.

---

## AI Usage

This project was built with AI as an accelerator. Claude was used for scaffolding, debugging, and drafting. Every prompt, decision, and correction is logged in [`ai-usage.md`](./ai-usage.md) — including the cases where the AI was wrong and I had to fix it.

---

## Author

**Darko Monzio Compagnoni**
[GitHub](https://github.com/DarkoMonzioCompagnoni) · [LinkedIn](https://www.linkedin.com/in/darko-monzio-compagnoni)
