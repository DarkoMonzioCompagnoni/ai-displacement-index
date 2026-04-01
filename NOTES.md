# Dashboard Notes

Analytical observations, framing decisions, and narrative flags to incorporate into the Sigma dashboard. Updated as the project develops.

---

## Confirmed observations to surface

### 1. The BLS classification gap
**Where:** Tab 4 (Occupation Risk)
**What:** The BLS 2018 SOC system has no standalone codes for "Data Analyst" or "Data Engineer". Both roles fall under `15-2051 Data Scientists`.
**Why it matters:** The government agency responsible for tracking AI's labor market impact does not yet classify two of the roles most discussed in that context. This is not a data quality complaint — it's a genuine reflection of how fast the industry has specialised relative to official classification systems.
**Framing:** State it plainly as a methodology note on the dashboard tab. Let the audience draw their own conclusions.

### 2. The AI halo effect is descriptive, not causal
**Where:** Tab 3 (AI Halo Effect)
**What:** Companies that announce AI investments while laying off workers often see short-term stock gains. The 30-day return window shows a pattern — but correlation is not causation.
**Confounders to name:** Earnings cycles, macro conditions, sector rotation, investor sentiment independent of AI news.
**Framing:** A disclaimer on the chart. "This chart shows stock returns around layoff and AI announcement events. It is descriptive — not a causal claim."

### 3. The post-pandemic correction vs. AI restructuring shift
**Where:** Tab 1 (Layoff Tracker)
**What:** 2022–2023 layoffs were driven by post-pandemic over-hiring corrections. By 2024–2025, companies began explicitly framing cuts as AI-driven restructuring (SAP, Workday, Microsoft). The total volume may have declined from the 2023 peak, but the stated intent became more structural.
**Framing:** Annotate the timeline chart with two phases: "Correction phase (2022–2023)" and "Restructuring phase (2024–2025)".

### 4. Developer trust in AI is falling even as usage rises
**Where:** Tab 2 (Developer Pulse)
**What:** Stack Overflow survey data shows AI tool usage increased from 62% (2024) to 84% (2025) of developers — but favorable sentiment dropped from 70%+ to 60% in the same period. Usage and trust are diverging.
**Framing:** Two lines on the same chart. The gap between them is the story.

---

## Observations to investigate

- Do companies that announce AI investments *before* layoffs outperform those that announce *after*? (Timing analysis in mart_ai_halo_effect)
- Is developer sentiment toward AI lower in occupations with higher BLS employment decline? (Cross-source join between SO survey DevType and BLS occupation)
- Which industries in the Layoffs.fyi data have the highest layoff rates relative to their BLS employment base?

---

*Add new observations here as they emerge during the dbt and dashboard build.*
