# AI Usage Log

This file documents every meaningful use of AI assistance in building the AI Displacement Index. The goal is transparency: what was asked, what was produced, and where human judgment overrode or corrected the output.

**Tool used:** Claude (Anthropic) — claude.ai chat interface
**Model:** Claude Sonnet 4.6

---

## Log

| # | Date | Stage | What I asked AI to do | What it produced | Human correction / judgment applied |
|---|---|---|---|---|---|
| 001 | 2026-03-31 | Project scoping | Scan Reddit/X for capstone project inspiration combining AI job displacement, developer AI sentiment, and finance | Proposed "AI Displacement Index" concept with data sources, architecture, dbt model layers, and Sigma dashboard tabs | Accepted overall direction. Narrowed scope to 4 dashboard tabs. Validated data sources independently. |
| 002 | 2026-03-31 | Environment setup | Guide step-by-step local environment setup on Windows with Conda, Git, dbt, Dagster, Docker | Step-by-step instructions — pyenv-win attempted first, then pivoted to Conda | pyenv-win abandoned after 3 failed attempts (stale version registry). Conda adopted instead. Windows Credential Manager bug (0x80070057) blocked PAT storage — resolved via `git config credential.helper store`. |
| 003 | 2026-03-31 | Documentation | Draft README.md and ARCHITECTURE.md | README with narrative framing, stack table, status tracker, architecture diagram. ARCHITECTURE with medallion pattern, schema design, dbt layers, Dagster jobs | Structure accepted. Causality caveat in AI halo analysis added based on project design discussion. |
| 004 | 2026-03-31 | Infrastructure | Azure Blob Storage setup | Step-by-step Azure portal walkthrough | Azure rejected Revolut and prepaid cards (3 attempts). AI suggested Cloudflare R2 — accepted. R2 chosen for S3-compatible API, no egress fees, and genuinely free tier. |
| 005 | 2026-03-31 | Infrastructure | Cloudflare R2 bucket creation and Python connection test | Bucket setup walkthrough, boto3 test script | Worked first attempt. No corrections needed. |
| 006 | 2026-03-31 | Infrastructure | Snowflake RBAC setup | `setup.sql` with roles, users, warehouses, schemas, privileges | Dedicated LOADER role requested by me — AI's initial draft had only TRANSFORMER and REPORTER. LOADER added, warehouses split per role. |
| 007 | 2026-03-31 | Infrastructure | Snowflake Python connection test | `test_snowflake_connection.py` | First run returned wrong user/role — `.env` variables not being read. Fixed manually. |
| 008 | 2026-03-31 | Ingestion | Layoffs.fyi ingestion script | Initial version hardcoded row/column counts | Caught hardcoded counts — replaced with dynamic `len(df)` after I flagged the issue. |
| 009 | 2026-03-31 | Ingestion | Stack Overflow survey download | Provided direct CDN URL for 2024 survey zip | URL returned 404 — CDN link had rotated. Switched to Kaggle download instead. |
| 010 | 2026-03-31 | Ingestion | Stock price ingestion script | `ingest_stock_prices.py` pulling 70 tickers via yfinance, flattened to long format | SQ (Block) failed with "possibly delisted" warning — removed from ticker list. 69 tickers retained. |
| 011 | 2026-03-31 | Ingestion | BLS API series IDs for tech occupations | Initial list of 8 occupations. Expanded to 22 when I asked for more roles | I asked why Data Analysts and Data Engineers were missing. AI researched and confirmed BLS has no standalone SOC codes for either role as of 2018 SOC — both fall under 15-2051 Data Scientists. Flagged as analytical observation worth surfacing in dashboard, not a data quality complaint. |

---

## Notes on methodology

AI was used as an accelerator, not an author. Every code block, config file, and architectural decision was reviewed before being applied. Where the AI was wrong — pyenv-win, Credential Manager, stale CDN URL, hardcoded row counts — the failure is logged above.

The project itself is about AI's effect on the labor market. Using AI to build it is intentional. The irony is not lost.

---

*This log is updated after each working session.*
