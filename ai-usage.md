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
| 015 | 2026-04-01 | dbt | dbt project setup | `dbt init`, `profiles.yml`, `dbt_project.yml` | Password cleared during edit — fixed. `CREATE SCHEMA` privilege missing. Schema doubling (`STAGING_STAGING`) fixed by removing `+schema` overrides. |
| 016 | 2026-04-01 | dbt | Staging models | Four staging models | `TRY_CAST` failed on FLOAT columns — fixed with `::` cast. `USSTATE` column name differed from expected. Validated each model with `dbt show`. |
| 017 | 2026-04-01 | dbt | Intermediate models | Three intermediate models | `int_companies_enriched` failed — `stg_stock_prices` has no `COMPANY` column. Fixed by using `company_tickers.csv` as a dbt seed. |
| 018 | 2026-04-01 | dbt | Mart models | Four mart models | All passed on first run. Full `dbt build` successful. |
| 019 | 2026-04-01 | Dagster | Orchestration setup | Assets, schedules, definitions, workspace.yaml | Module naming collision — local `dagster/` folder shadowed the installed `dagster` package. Resolved with `-d` working directory flag. Dagster temp files created in project root — moved to `dagster/.dagster_home` via `DAGSTER_HOME` env var. GitHub auth failed (work account stored in Credential Manager) — resolved by embedding PAT in remote URL temporarily. |
| 020 | 2026-04-01 | Visualization | Tool selection | Evaluated Sigma, Lightdash, Evidence.dev, Streamlit, Superset, Metabase | Sigma: company partner account, no admin rights, company email required for personal trial. Lightdash: same email restriction. I chose Evidence.dev — code-first, deploys to GitHub Pages, no account restrictions, strong signal for a data engineering portfolio. |
| 021 | 2026-04-02 | Evidence.dev | Dashboard setup | Four pages created | PowerShell UTF-8 encoding corrupted SQL fences in .md files — emoji and dashes mangled. Fix: rewrite pages via Python with explicit UTF-8 encoding. |
| 022 | 2026-04-03 | Evidence.dev | Developer Pulse page | ScatterPlot component | Vite error: `threat_by_experience` not defined. Root cause: missing blank line between `</DataTable>` and next ```sql fence. Fixed with Python string replace. PowerShell backtick interpretation blocked inline fix — used `Out-File` script approach instead. |
| 023 | 2026-04-03 | dbt | Developer Sentiment mart | `uses_ai_tools` metric | Claude generated CASE WHEN matching a non-existent string value. Real survey values are 'Yes'/'No'. Produced pct_uses_ai = 0 silently across all rows. Caught by Darko noticing 0% in dashboard. Fixed manually. Lesson: AI cannot know categorical values it has never seen — always verify against `SELECT DISTINCT` before trusting generated CASE WHEN logic. |
| 024 | 2026-04-03 | Evidence.dev | Cache invalidation | Dashboard not updating after dbt run | Evidence caches query results locally. After dbt rebuilds marts, must run `npm run sources` or delete `.evidence/template/.evidence-queries` then restart dev server. |
| 025 | 2026-04-03 | dbt | New mart | `mart_layoff_price_windows` | Built to support daily stock price trajectory visualization ±30 days around each layoff event. Indexed to day 0 (announcement date). Edge case: weekend/holiday announcements produce NULL base_price and are excluded. |
| 026 | 2026-04-03 | Visualization | Tool switch | Replaced Evidence.dev with Streamlit | Evidence.dev discarded: markdown authoring friction, cache invalidation after every dbt run, PowerShell encoding issues. Streamlit chosen: pure Python, queries Snowflake directly, deploys from GitHub to Streamlit Community Cloud. All four pages built and running locally. |

---

## Honest assessment

**AI was most useful for:** boilerplate code generation, debugging error messages, identifying root causes of permission and syntax errors, drafting documentation quickly, and surfacing data sources and tool alternatives.

**AI was least reliable for:** verifying external API formats from memory (BLS series IDs), predicting tool edge cases (pyenv-win, Snowflake stage whitelisting, Sigma email restrictions), and maintaining awareness of what was committed vs. pending.

**Human judgment mattered most for:** the analytical narrative (BLS gap, AIOE counterintuitive results, AI halo causality framing), architectural decisions (LOADER role, separate warehouses, Evidence.dev over Sigma), catching outputs that looked plausible but were wrong, and deciding when to pivot vs. persist on a blocker.

---

*This log is updated after each working session.*
