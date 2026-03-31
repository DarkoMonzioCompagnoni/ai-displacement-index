# AI Usage Log

This file documents every meaningful use of AI assistance in building the AI Displacement Index. The goal is transparency: what was asked, what was produced, and where human judgment overrode or corrected the output.

**Tool used:** Claude (Anthropic) — claude.ai chat interface
**Model:** Claude Sonnet 4.6

---

## Format

| # | Date | Stage | What I asked AI to do | What it produced | Human correction / judgment applied |
|---|---|---|---|---|---|
| 001 | 2025-03-31 | Project scoping | Scan Reddit/X for capstone project inspiration combining AI job displacement, developer AI sentiment, and finance | Proposed "AI Displacement Index" concept with data sources, architecture, dbt model layers, and Sigma dashboard tabs | Accepted overall direction. Narrowed scope to 4 dashboard tabs. Validated data sources independently. |
| 002 | 2025-03-31 | Environment setup | Guide step-by-step local environment setup on Windows with Conda, Git, dbt, Dagster, Docker | Step-by-step instructions for pyenv-win (failed), then pivoted to Conda | pyenv-win approach abandoned after 3 failed attempts. Conda route adopted. Credential Manager bug (0x80070057) required manual debugging beyond AI's initial suggestion. |
| 003 | 2025-03-31 | Documentation | Draft README.md and ARCHITECTURE.md for the project | README with narrative framing, stack table, status tracker, and architecture diagram. ARCHITECTURE with medallion pattern, schema design, dbt layers, Dagster jobs, and 120-day reset instructions | Tone and structure accepted. "Why I built this" section to be reviewed for personal voice. Causality caveat in AI halo analysis added based on prior project design discussion. |

---

## Notes on methodology

AI was used as an accelerator, not an author. Every code block, config file, and architectural decision was reviewed before being applied. Where the AI was wrong — pyenv-win version lookup, Windows Credential Manager PAT storage — the failure is logged above and the fix is documented in the commit history.

The project itself is about AI's effect on the labor market. Using AI to build it is intentional. The irony is not lost.

---

*This log is updated after each working session.*
