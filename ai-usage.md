# AI Usage Log

This file documents every meaningful use of AI assistance in building the AI Displacement Index. The goal is transparency: what was asked, what was produced, and where human judgment overrode or corrected the output.

**Tool used:** Claude (Anthropic) — claude.ai chat interface
**Model:** Claude Sonnet 4.6

---

## Log

| # | Date | Stage | What I asked AI to do | What it produced | Human correction / judgment applied |
|---|---|---|---|---|---|
| 001 | 2026-03-31 | Project scoping | Scan Reddit/X for capstone project inspiration combining AI job displacement, developer AI sentiment, and finance | Proposed "AI Displacement Index" concept with data sources, architecture, dbt model layers, and Sigma dashboard tabs | Accepted overall direction. Narrowed scope to 4 dashboard tabs. Validated data sources independently. |
| 002 | 2026-03-31 | Environment setup | Guide step-by-step local environment setup on Windows with Conda, Git, dbt, Dagster, Docker | Step-by-step instructions — pyenv-win attempted first, then pivoted to Conda | pyenv-win abandoned after 3 failed attempts. Conda adopted. Windows Credential Manager bug (0x80070057) resolved via `git config credential.helper store`. |
| 003 | 2026-03-31 | Documentation | Draft README.md and ARCHITECTURE.md | README with narrative framing, stack table, status tracker. ARCHITECTURE with medallion pattern, schema design, dbt layers | Structure accepted. Causality caveat in AI halo analysis added. |
| 004 | 2026-03-31 | Infrastructure | Azure Blob Storage setup | Step-by-step Azure portal walkthrough | Azure rejected Revolut and prepaid cards (3 attempts). Switched to Cloudflare R2 — accepted. |
| 005 | 2026-03-31 | Infrastructure | Cloudflare R2 setup and connection test | Bucket setup walkthrough, boto3 test script | Worked first attempt. |
| 006 | 2026-03-31 | Infrastructure | Snowflake RBAC setup | `setup.sql` with roles, users, warehouses, schemas, privileges | Dedicated LOADER role requested by me — AI's initial draft had only TRANSFORMER and REPORTER. |
| 007 | 2026-03-31 | Infrastructure | Snowflake Python connection test | `test_snowflake_connection.py` | First run returned wrong user/role — `.env` variables not being read. Fixed manually. |
| 008 | 2026-03-31 | Ingestion | Layoffs.fyi ingestion script | Initial version hardcoded row/column counts | Caught hardcoded counts — replaced with dynamic `len(df)`. |
| 009 | 2026-03-31 | Ingestion | Stack Overflow survey download | Direct CDN URL for 2024 survey zip | URL returned 404. Switched to Kaggle. |
| 010 | 2026-03-31 | Ingestion | Stock price ingestion script | `ingest_stock_prices.py` pulling 70 tickers, flattened to long format | SQ (Block) failed — removed. 69 tickers retained. |
| 011 | 2026-04-01 | Ingestion | BLS API series IDs for tech occupations | Three separate attempts with different series ID formats | All three approaches failed: wrong series ID format (OEUS vs OEUN), then HTTP 403 on both BLS download domains. Failure documented in `ingest_bls.py`. Pivoted to AIOE dataset. |
| 012 | 2026-04-01 | Ingestion | AIOE exposure scores | `ingest_ai_exposure.py` downloading Felten et al. 2021 dataset from GitHub | Worked first attempt. `openpyxl` missing — installed. Produced 774 occupation scores. |
| 013 | 2026-04-01 | Analysis | BLS Data Analyst / Data Engineer classification gap | Research into why those roles had no standalone BLS series IDs | AI confirmed BLS 2018 SOC has no standalone codes for either role — both fall under 15-2051 Data Scientists. Flagged as analytical observation for dashboard, not a data quality complaint. Captured in NOTES.md. |

---

## Notes on methodology

AI was used as an accelerator, not an author. Every code block, config file, and architectural decision was reviewed before being applied. Where the AI was wrong — pyenv-win, Credential Manager, stale CDN URL, hardcoded row counts, incorrect BLS series IDs — the failure is logged above.

The project itself is about AI's effect on the labor market. Using AI to build it is intentional. The irony is not lost.

---

*This log is updated after each working session.*
