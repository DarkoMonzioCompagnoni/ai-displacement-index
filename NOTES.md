# Dashboard Notes & Content Ideas

Analytical observations, framing decisions, and narrative flags for the Sigma dashboard and LinkedIn content. Updated as the project develops.

---

## Dashboard observations (confirmed)

### 1. The BLS classification gap
**Where:** Tab 4 (Occupation Risk)
**What:** The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer". Both fall under `15-2051 Data Scientists`.
**Why it matters:** The government agency tracking AI's labor market impact doesn't classify two of the most-discussed roles in that context. Not a data quality complaint — a reflection of how fast the industry has specialised relative to official systems.
**Framing:** State plainly as a methodology note. Let the audience connect the dots.
**LinkedIn angle:** "I tried to pull BLS employment data for Data Analysts and Data Engineers. They don't exist as categories. Here's what that tells us about how slowly official labour statistics move compared to the industry."

### 2. The AI halo effect is descriptive, not causal
**Where:** Tab 3 (AI Halo Effect)
**What:** Companies announcing AI investments while laying off workers often see short-term stock gains. Pattern visible, causation unproven.
**Confounders:** Earnings cycles, macro conditions, sector rotation.
**Framing:** Dashboard disclaimer: "This chart shows stock returns around layoff and AI announcement events. It is descriptive — not a causal claim."

### 3. The two-phase layoff narrative
**Where:** Tab 1 (Layoff Tracker)
**What:** 2022–2023 = post-pandemic over-hiring correction. 2024–2025 = AI-driven restructuring (SAP, Workday, Microsoft explicitly framing cuts this way).
**Framing:** Annotate timeline with two labelled phases.
**LinkedIn angle:** "Tech layoffs didn't stop in 2023. The reason just changed."

### 4. Developer trust in AI is falling even as usage rises
**Where:** Tab 2 (Developer Pulse)
**What:** SO survey: usage up (62% → 84%, 2024→2025), favorable sentiment down (70%+ → 60%).
**Framing:** Two lines on the same chart. The divergence is the story.
**LinkedIn angle:** "More developers are using AI tools. Fewer trust them. Here's what the data says."

### 5. The AIOE top results are counterintuitive
**Where:** Tab 4 (Occupation Risk)
**What:** Most AI-exposed occupations: Genetic Counselors (1.53), Financial Examiners (1.53), Actuaries (1.52). Least exposed: Dancers (-2.67), Fitness Trainers (-2.11), construction helpers.
**Why it matters:** Challenges the narrative that AI primarily threatens tech workers. High information processing + pattern matching + document analysis = high exposure, regardless of sector.
**Framing:** Call out explicitly. "The occupations most exposed to AI are not who you'd expect."
**LinkedIn angle:** "According to the Felten et al. AIOE index, Genetic Counselors are more exposed to AI than Software Developers. Here's why that makes sense — and what it means for your career."

---

## Engineering observations worth writing about

### The BLS API failure
Three approaches, all blocked. API series IDs undocumented and constructed from memory (AI error). Special requests URL gated behind browser session. Flat file server blocks non-browser clients.
**LinkedIn angle:** "I spent a day trying to programmatically pull BLS occupational data. Here's every way it blocked me — and what I used instead."

### The Snowflake + Cloudflare R2 stage whitelisting issue
R2 is documented as a supported Snowflake S3-compatible vendor. Endpoint is listed as "enabled by default." Free trial account still blocked. Required support ticket.
**LinkedIn angle:** "The docs said it would work. It didn't. Here's the workaround and what I learned about testing documentation claims against real free-tier accounts."

### Two ways to load data into Snowflake from object storage
External stage (COPY INTO) vs. Python direct loader (write_pandas). Trade-offs documented. Both approaches in the repo.
**LinkedIn angle:** "There's more than one way to get data from cloud storage into Snowflake. Here are two — when to use each, and which one I ended up using on this project."

### The ai-usage.md transparency log
Keeping a structured log of every AI interaction, including failures and corrections.
**LinkedIn angle:** "I used AI to build this project. Here's the honest log of every time it was wrong — and what I had to fix."

---

## Observations to investigate during dashboard build

- Do companies that announce AI investments *before* layoffs outperform those that announce *after*?
- Is developer sentiment toward AI lower in DevTypes with higher AIOE scores?
- Which industries have the highest layoff rates relative to their AIOE exposure?
- Software Developers have a moderate AIOE score — does the data support displacement or augmentation?
- Does layoff intensity correlate with company funding stage? (Layoffs.fyi has `Stage` column)

---

## MVP vs. future development

**MVP (publish first):**
- All 4 Sigma dashboard tabs live
- README, ARCHITECTURE, ai-usage.md polished
- LinkedIn post: project overview + key findings

**Phase 2 (content series):**
- RLS implementation (simulate multi-role data access in Sigma)
- Data masking on Stack Overflow respondent data
- Dagster orchestration running on a schedule
- Snowflake Intelligence exploration

**Each phase 2 item = one LinkedIn post + repo update.**

---

*Add new observations here as they emerge during the dbt and dashboard build.*
