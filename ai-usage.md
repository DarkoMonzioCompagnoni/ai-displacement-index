# AI Usage Log

This file documents every meaningful use of AI assistance in building the AI Displacement Index. The goal is transparency: what was asked, what was produced, and where human judgment shaped or corrected the output.

**Tool used:** Claude (Anthropic) — claude.ai chat interface
**Model:** Claude Sonnet 4.6

---

## How AI was used in this project

AI generated code, configuration, SQL, and documentation throughout this build. Outputs were validated through terminal results, dbt previews, row counts, and error messages — not line-by-line code review. Architectural decisions, analytical framing, and judgment calls at key decision points remained with the author.

This is a deliberate working pattern, not a shortcut. A senior engineer using AI as an accelerator reviews design and validates outputs — the same way they would with a junior developer. The log below captures where that judgment was applied, where AI was wrong, and what corrections were made.

Where AI produced incorrect output — series IDs constructed from memory, wrong Snowflake syntax, stale URLs, hardcoded values — it is logged explicitly. These failures are part of the story, not embarrassments to hide.

---

## Log

| # | Date | Stage | What I asked AI to do | What it produced | Human correction / judgment applied |
|---|---|---|---|---|---|
| 001 | 2026-03-31 | Project scoping | Scan for capstone project inspiration combining AI job displacement, developer sentiment, and finance | Proposed "AI Displacement Index" with data sources, architecture, dbt layers, and Sigma dashboard tabs | Accepted direction. Narrowed to 4 dashboard tabs. Validated data sources independently. |
| 002 | 2026-03-31 | Environment setup | Guide local environment setup on Windows | pyenv-win attempted first, then Conda | pyenv-win abandoned after 3 failed attempts. Conda adopted. Windows Credential Manager bug (0x80070057) required manual fix via `git config credential.helper store`. |
| 003 | 2026-03-31 | Documentation | Draft README.md and ARCHITECTURE.md | Two-file structure: accessible README + technical ARCHITECTURE | Two-layer docs approach was my idea. Causality caveat in AI halo analysis added based on our design discussion. |
| 004 | 2026-03-31 | Infrastructure | Azure Blob Storage setup | Portal walkthrough | Azure rejected Revolut cards 3 times. I decided to switch to Cloudflare R2. AI suggested it as an alternative — I accepted. |
| 005 | 2026-03-31 | Infrastructure | Cloudflare R2 setup | Bucket walkthrough, boto3 test script | Worked first attempt. |
| 006 | 2026-03-31 | Infrastructure | Snowflake RBAC design | `setup.sql` with roles, users, warehouses, schemas, privileges | I asked for a dedicated LOADER role — not in AI's initial draft. Warehouses split per role at my request. |
| 007 | 2026-03-31 | Infrastructure | Snowflake Python connection test | `test_snowflake_connection.py` | First run returned wrong user/role — `.env` variables not read correctly. Fixed manually by me. |
| 008 | 2026-03-31 | Ingestion | Layoffs.fyi ingestion script | Script with hardcoded row/column counts | I caught the hardcoded values and asked for dynamic `len(df)`. AI had not flagged this proactively. |
| 009 | 2026-03-31 | Ingestion | Stack Overflow survey download | Direct CDN URL for 2024 zip | URL returned 404 — link had rotated. Switched to Kaggle. AI failure. |
| 010 | 2026-03-31 | Ingestion | Stock price ingestion | `ingest_stock_prices.py` + `company_tickers.csv` | SQ (Block) failed yfinance lookup — removed. I noticed the company_tickers.csv should be committed as config, not gitignored as data. |
| 011 | 2026-03-31 | Ingestion | BLS occupational employment data | Three approaches: BLS API, special.requests download, flat file server | All three failed. AI acknowledged series IDs were built from memory without verification. I asked why Data Analysts and Data Engineers were absent — AI researched and confirmed BLS has no standalone SOC codes for either role. I recognised this as a dashboard narrative opportunity, not just a data gap. |
| 012 | 2026-04-01 | Ingestion | AI Occupational Exposure dataset | `ingest_ai_exposure.py` downloading Felten et al. from GitHub | Missing `openpyxl` dependency. I noticed the AIOE top results (Genetic Counselors, Financial Examiners) were counterintuitive and worth surfacing explicitly in the dashboard. |
| 013 | 2026-04-01 | Loading | Snowflake external stage for R2 | `load_raw.sql` with S3-compatible stage | Two syntax errors fixed iteratively. Final blocker: Snowflake requires endpoint whitelisting — free trial account blocked. I decided to proceed with a Python loader workaround rather than wait for support. |
| 014 | 2026-04-01 | Loading | Python direct loader | `load_raw_python.py` using boto3 + write_pandas | Missing `snowflake-connector-python[pandas]` dependency. Worked after install. |
| 015 | 2026-04-01 | dbt | dbt project setup and profiles | `dbt init`, `profiles.yml`, `dbt_project.yml` | Password accidentally cleared during profiles.yml edit — connection failed until I restored it. `CREATE SCHEMA` privilege missing — I ran the grant after AI identified the root cause from debug output. Schema doubling (`STAGING_STAGING`) fixed by removing `+schema` overrides from `dbt_project.yml`. |
| 016 | 2026-04-01 | dbt | Staging models | Four staging models for all raw sources | `stg_layoffs_fyi`: `TRY_CAST` failed on numeric columns (FLOAT→INTEGER not supported). `USSTATE` column was not `US_STATE` — `write_pandas` uppercased it differently than expected. I validated each model with `dbt show` before accepting. |

---

## Honest assessment

The AI was most useful for: boilerplate code generation, debugging error messages, identifying root causes of permission and syntax errors, and drafting documentation quickly.

The AI was least reliable for: verifying external API formats from memory (BLS series IDs), predicting how specific tools handle edge cases (pyenv-win on Windows, Snowflake stage whitelisting), and maintaining awareness of what had already been committed vs. what was still pending.

The human judgment that mattered most: the analytical narrative (BLS classification gap, AIOE counterintuitive results, AI halo causality framing), architectural decisions (LOADER role, separate warehouses), and catching outputs that looked plausible but were wrong (hardcoded counts, wrong column names).

---

*This log is updated after each working session.*
