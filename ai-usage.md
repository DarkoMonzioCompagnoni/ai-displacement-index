# AI Usage Log

This file documents every meaningful use of AI assistance in building the AI Displacement Index. The goal is transparency: what was asked, what was produced, and where human judgment overrode or corrected the output.

**Tool used:** Claude (Anthropic) — claude.ai chat interface
**Model:** Claude Sonnet 4.6

---

## Log

| # | Date | Stage | What I asked AI to do | What it produced | Human correction / judgment applied |
|---|---|---|---|---|---|
| 001 | 2026-03-31 | Project scoping | Scan Reddit/X for capstone project inspiration combining AI job displacement, developer AI sentiment, and finance | Proposed "AI Displacement Index" concept with data sources, architecture, dbt model layers, and Sigma dashboard tabs | Accepted overall direction. Narrowed scope to 4 dashboard tabs. Validated data sources independently. |
| 002 | 2026-03-31 | Environment setup | Guide step-by-step local environment setup on Windows with Conda, Git, dbt, Dagster, Docker | Step-by-step instructions — pyenv-win attempted first, then pivoted to Conda | pyenv-win abandoned after 3 failed attempts. Windows Credential Manager bug (0x80070057) blocked PAT storage — resolved via `git config credential.helper store`. |
| 003 | 2026-03-31 | Documentation | Draft README.md and ARCHITECTURE.md | README with narrative framing, stack table, status tracker. ARCHITECTURE with medallion pattern, schema design, dbt layers | Causality caveat in AI halo analysis added. Two-layer docs approach proposed by me. |
| 004 | 2026-03-31 | Infrastructure | Azure Blob Storage setup | Step-by-step Azure portal walkthrough | Azure rejected Revolut cards (3 attempts). AI suggested Cloudflare R2 — accepted. |
| 005 | 2026-03-31 | Infrastructure | Cloudflare R2 setup and connection test | Bucket walkthrough, boto3 test script | Worked first attempt. |
| 006 | 2026-03-31 | Infrastructure | Snowflake RBAC setup | `setup.sql` with roles, users, warehouses, schemas, privileges | Dedicated LOADER role requested by me. Warehouses split per role. |
| 007 | 2026-03-31 | Infrastructure | Snowflake Python connection test | `test_snowflake_connection.py` | First run returned wrong user/role — `.env` variables not read correctly. Fixed manually. |
| 008 | 2026-03-31 | Ingestion | Layoffs.fyi ingestion script | Initial version with hardcoded row/column counts | Caught hardcoded counts — replaced with dynamic `len(df)`. |
| 009 | 2026-03-31 | Ingestion | Stack Overflow survey download | Direct CDN URL for 2024 zip | URL returned 404 — CDN link rotated. Switched to Kaggle. |
| 010 | 2026-03-31 | Ingestion | Stock price ingestion for 69+ tickers | `ingest_stock_prices.py` + company_tickers.csv seed file | SQ (Block) failed yfinance — removed. 69 tickers retained. |
| 011 | 2026-03-31 | Ingestion | BLS occupational employment data | Three approaches attempted — all blocked by BLS | AI acknowledged series IDs were constructed from memory without verification. Replaced with AIOE dataset. |
| 012 | 2026-04-01 | Ingestion | AI Occupational Exposure (AIOE) dataset | `ingest_ai_exposure.py` | Worked after installing missing `openpyxl`. |
| 013 | 2026-04-01 | Loading | Snowflake external stage for Cloudflare R2 | `load_raw.sql` with S3-compatible stage using `s3compat://` URL and `ENDPOINT` parameter | Two syntax errors corrected iteratively. Final blocker: Snowflake requires endpoint whitelisting for S3-compatible stages. Free trial account returned "Endpoint cannot be used with storage type S3" despite R2 being a documented supported vendor. Snowflake support ticket submitted. Python direct loader adopted as workaround — downloads from R2 via boto3, writes to Snowflake via snowflake-connector-python. Both approaches documented in ARCHITECTURE.md. |

---

## Notes on methodology

AI was used as an accelerator, not an author. Every code block, config file, and architectural decision was reviewed before being applied. Where the AI was wrong — pyenv-win, Credential Manager, stale CDN URL, hardcoded row counts, BLS series IDs, Snowflake stage syntax — the failure is logged above.

The project itself is about AI's effect on the labor market. Using AI to build it is intentional. The irony is not lost.

---

*This log is updated after each working session.*
