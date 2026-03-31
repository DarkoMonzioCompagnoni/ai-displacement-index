# AI Usage Log

This file documents every meaningful use of AI assistance in building the AI Displacement Index. The goal is transparency: what was asked, what was produced, and where human judgment overrode or corrected the output.

**Tool used:** Claude (Anthropic) — claude.ai chat interface
**Model:** Claude Sonnet 4.6

---

## Log

| # | Date | Stage | What I asked AI to do | What it produced | Human correction / judgment applied |
|---|---|---|---|---|---|
| 001 | 2025-03-31 | Project scoping | Scan Reddit/X for capstone project inspiration combining AI job displacement, developer AI sentiment, and finance | Proposed "AI Displacement Index" concept with data sources, architecture, dbt model layers, and Sigma dashboard tabs | Accepted overall direction. Narrowed scope to 4 dashboard tabs. Validated data sources independently. |
| 002 | 2025-03-31 | Environment setup | Guide step-by-step local environment setup on Windows with Conda, Git, dbt, Dagster, Docker | Step-by-step instructions — pyenv-win attempted first, then pivoted to Conda | pyenv-win abandoned after 3 failed attempts (stale version registry on Windows). Conda adopted instead. Windows Credential Manager bug (0x80070057) blocked PAT storage — resolved via `git config credential.helper store`. |
| 003 | 2025-03-31 | Documentation | Draft README.md and ARCHITECTURE.md | README with narrative framing, stack table, status tracker, architecture diagram. ARCHITECTURE with medallion pattern, schema design, dbt layers, Dagster jobs, reset instructions | Structure accepted. Causality caveat in AI halo analysis added based on project design discussion. "Why I built this" section reviewed for personal voice. |
| 004 | 2025-03-31 | Infrastructure | Azure Blob Storage setup | Step-by-step Azure portal walkthrough | Azure rejected Revolut and prepaid cards (3 attempts). AI suggested Cloudflare R2 as alternative — accepted. R2 chosen for S3-compatible API, no egress fees, and genuinely free tier. All docs updated to reflect switch. |
| 005 | 2025-03-31 | Infrastructure | Cloudflare R2 bucket creation and Python connection test | Bucket setup walkthrough, boto3 test script using S3-compatible endpoint | Worked first attempt. No corrections needed. |
| 006 | 2025-03-31 | Infrastructure | Snowflake RBAC setup | `setup.sql` with 4 roles (LOADER, TRANSFORMER, REPORTER, SYSADMIN), 3 service users, 3 warehouses, 4 schemas, full privilege matrix with FUTURE grants | RBAC model accepted. Dedicated LOADER role requested by me — AI's initial draft had only TRANSFORMER and REPORTER. Added LOADER role and split warehouses per role. |
| 007 | 2025-03-31 | Infrastructure | Snowflake Python connection test | `test_snowflake_connection.py` verifying user, role, warehouse, and database | First run returned `DARKO / ACCOUNTADMIN / COMPUTE_WH / None` — `.env` variables were not being read correctly. Fixed manually. Second run returned correct values. |

---

## Notes on methodology

AI was used as an accelerator, not an author. Every code block, config file, and architectural decision was reviewed before being applied. Where the AI was wrong — pyenv-win version lookup, Windows Credential Manager PAT storage, initial Snowflake connection config — the failure is logged above and the fix is documented in the commit history.

The project itself is about AI's effect on the labor market. Using AI to build it is intentional. The irony is not lost.

---

*This log is updated after each working session.*
