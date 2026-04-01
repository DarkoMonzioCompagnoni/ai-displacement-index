# Dashboard Notes

Analytical observations, framing decisions, and narrative flags to incorporate into the Sigma dashboard. Updated as the project develops.

---

## Confirmed observations to surface

### 1. The BLS classification gap
**Where:** Tab 4 (Occupation Risk)
**What:** The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer". Both roles fall under `15-2051 Data Scientists`.
**Why it matters:** The government agency responsible for tracking AI's labor market impact does not yet classify two of the roles most discussed in that context. This is not a data quality complaint — it's a genuine reflection of how fast the industry has specialised relative to official classification systems.
**Framing:** State it plainly as a methodology note on the dashboard tab.

### 2. The AI halo effect is descriptive, not causal
**Where:** Tab 3 (AI Halo Effect)
**What:** Companies that announce AI investments while laying off workers often see short-term stock gains. The 30-day return window shows a pattern — but correlation is not causation.
**Confounders to name:** Earnings cycles, macro conditions, sector rotation, investor sentiment independent of AI news.
**Framing:** Dashboard disclaimer — "This chart shows stock returns around layoff and AI announcement events. It is descriptive, not a causal claim."

### 3. The post-pandemic correction vs. AI restructuring shift
**Where:** Tab 1 (Layoff Tracker)
**What:** 2022–2023 layoffs were driven by post-pandemic over-hiring corrections. By 2024–2025, companies began explicitly framing cuts as AI-driven restructuring (SAP, Workday, Microsoft).
**Framing:** Annotate the timeline chart with two phases: "Correction phase (2022–2023)" and "Restructuring phase (2024–2025)".

### 4. Developer trust in AI is falling even as usage rises
**Where:** Tab 2 (Developer Pulse)
**What:** Stack Overflow 2025 survey shows AI tool usage increased to 84% of developers — but favorable sentiment dropped from 70%+ to 60%. Usage and trust are diverging.
**Framing:** Two lines on the same chart. The gap between them is the story.

### 5. AIOE results: finance and legal, not tech, top the exposure list
**Where:** Tab 4 (Occupation Risk)
**What:** The top 10 most AI-exposed occupations per Felten et al. are dominated by finance, legal, and analytical roles — Genetic Counselors, Financial Examiners, Actuaries, Budget Analysts, Accountants. Tech roles sit in the mid-range.
**Why it matters:** Challenges the common narrative that AI primarily threatens software developers. The data suggests white-collar analytical roles outside tech are more structurally exposed.
**Framing:** Surface this directly on Tab 4. Let the audience interrogate whether the layoff data confirms or contradicts the AIOE scores.

---

## Observations to investigate

- Do companies that announce AI investments *before* layoffs outperform those that announce *after*?
- Is developer sentiment toward AI lower in occupations with higher AIOE scores?
- Which industries in the Layoffs.fyi data have the highest layoff rates relative to their size?
- Do AIOE scores correlate with actual layoff counts in the dataset?

---

*Add new observations here as they emerge during the dbt and dashboard build.*
