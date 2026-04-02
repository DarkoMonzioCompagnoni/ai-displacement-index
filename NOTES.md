# AI Usage Log

This file documents every meaningful use of AI assistance in building the AI Displacement Index. The goal is transparency: what was asked, what was produced, and where human judgment shaped or corrected the output.

**Tool used:** Claude (Anthropic) — claude.ai chat interface
**Model:** Claude Sonnet 4.6

---

## How AI was used in this project

AI generated code, configuration, SQL, and documentation throughout this build. Outputs were validated through terminal results, dbt previews, row counts, and error messages — not line-by-line code review. Architectural decisions, analytical framing, and judgment calls at key decision points remained with the author.

This is a deliberate working pattern, not a shortcut. A senior engineer using AI as an accelerator reviews design and validates outputs — the same way they would with a junior developer. The log below captures where that judgment was applied, where AI was wrong, and what corrections were made.

---

## Log

| # | Date | Stage | What I asked AI to do | What it produced | Human correction / judgment applied |
|---|---|---|---|---|---|
| 001 | 2026-03-31 | Project scoping | Scan for capstone project inspiration combining AI job displacement, developer sentiment, and finance | Proposed "AI Displacement Index" with data sources, architecture, dbt layers, and Sigma dashboard tabs | Accepted direction. Narrowed to 4 dashboard tabs. Validated data sources independently. |
| 002 | 2026-03-31 | Environment setup | Guide local environment setup on Windows | pyenv-win attempted first, then Conda | pyenv-win abandoned after 3 failed attempts. Conda adopted. Windows Credential Manager bug (0x80070057) required manual fix. |
| 003 | 2026-03-31 | Documentation | Draft README.md and ARCHITECTURE.md | Two-file structure: accessible README + technical ARCHITECTURE | Two-layer docs approach was my idea. Causality caveat in AI halo analysis added based on our design discussion. |
| 004 | 2026-03-31 | Infrastructure | Azure Blob Storage setup | Portal walkthrough | Azure rejected Revolut cards 3 times. I decided to switch to Cloudflare R2. |
| 005 | 2026-03-31 | Infrastructure | Cloudflare R2 setup | Bucket walkthrough, boto3 test script | Worked first attempt. |
| 006 | 2026-03-31 | Infrastructure | Snowflake RBAC design | `setup.sql` with roles, users, warehouses, schemas, privileges | I asked for a dedicated LOADER role — not in AI's initial draft. Warehouses split per role at my request. |
| 007 | 2026-03-31 | Infrastructure | Snowflake Python connection test | `test_snowflake_connection.py` | First run returned wrong user/role — `.env` variables not read correctly. Fixed manually. |
| 008 | 2026-03-31 | Ingestion | Layoffs.fyi ingestion script | Script with hardcoded row/column counts | I caught the hardcoded values. AI had not flagged this proactively. |
| 009 | 2026-03-31 | Ingestion | Stack Overflow survey download | Direct CDN URL for 2024 zip | URL returned 404 — link had rotated. Switched to Kaggle. AI failure. |
| 010 | 2026-03-31 | Ingestion | Stock price ingestion | `ingest_stock_prices.py` + `company_tickers.csv` | SQ (Block) failed yfinance. I noticed company_tickers.csv should be committed as config, not gitignored. |
| 011 | 2026-03-31 | Ingestion | BLS occupational employment data | Three approaches — all blocked | AI series IDs built from memory without verification. I asked why Data Analysts and Data Engineers were absent — confirmed BLS has no standalone SOC codes. I recognised this as a dashboard narrative opportunity. |
| 012 | 2026-04-01 | Ingestion | AI Occupational Exposure dataset | `ingest_ai_exposure.py` | Missing `openpyxl` dependency. I noticed AIOE top results were counterintuitive and worth surfacing in dashboard. |
| 013 | 2026-04-01 | Loading | Snowflake external stage for R2 | `load_raw.sql` with S3-compatible stage | Two syntax errors fixed iteratively. Final blocker: endpoint whitelisting required. I decided to proceed with Python loader rather than wait for support. |
| 014 | 2026-04-01 | Loading | Python direct loader | `load_raw_python.py` | Missing `snowflake-connector-python[pandas]` dependency. |
| 015 | 2026-04-01 | dbt | dbt project setup | `dbt init`, `profiles.yml`, `dbt_project.yml` | Password cleared during edit — fixed. `CREATE SCHEMA` privilege missing — identified and granted. Schema doubling (`STAGING_STAGING`) fixed by removing `+schema` overrides. |
| 016 | 2026-04-01 | dbt | Staging models | Four staging models | `TRY_CAST` failed on FLOAT columns — fixed with `::` cast syntax. `USSTATE` column name differed from expected `US_STATE`. Validated each model with `dbt show`. |
| 017 | 2026-04-01 | dbt | Intermediate models | Three intermediate models | `int_companies_enriched` failed — `stg_stock_prices` has no `COMPANY` column. Fixed by using `company_tickers.csv` as a dbt seed instead. |
| 018 | 2026-04-01 | dbt | Mart models | Four mart models — one per dashboard tab | All passed on first run. Validated with `dbt show`. Full `dbt build` successful. |

---

## Honest assessment

**AI was most useful for:** boilerplate code generation, debugging error messages, identifying root causes of permission and syntax errors, drafting documentation quickly, and surfacing data sources I hadn't considered.

**AI was least reliable for:** verifying external API formats from memory (BLS series IDs), predicting tool edge cases (pyenv-win, Snowflake stage whitelisting), and maintaining awareness of what was committed vs. pending.

**Human judgment mattered most for:** the analytical narrative (BLS gap, AIOE counterintuitive results, AI halo causality framing), architectural decisions (LOADER role, separate warehouses), catching outputs that looked plausible but were wrong (hardcoded counts, wrong column names), and deciding when to pivot vs. persist on a blocker.

---

*This log is updated after each working session.*
