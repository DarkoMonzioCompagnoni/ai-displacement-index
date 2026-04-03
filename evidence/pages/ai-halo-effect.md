---
title: AI Halo Effect
---

# 📈 AI Halo Effect

Stock returns in the 30 days after a layoff announcement — for publicly traded tech companies.
```sql halo_by_company
select
    company,
    ticker,
    industry,
    layoff_year,
    laid_off,
    round(return_30d_pct, 2) as return_30d_pct,
    round(return_pre_30d_pct, 2) as return_pre_30d_pct
from snowflake.ai_halo_effect
where return_30d_pct is not null
order by laid_off desc nulls last
limit 50
```

<ScatterPlot
    data={halo_by_company}
    x=laid_off
    y=return_30d_pct
    series=industry
    title="Employees Laid Off vs. 30-Day Stock Return"
    xAxisTitle="Employees Laid Off"
    yAxisTitle="30-Day Return After Layoff (%)"
/>

<DataTable data={halo_by_company} rows=20>
    <Column id=company title="Company"/>
    <Column id=ticker title="Ticker"/>
    <Column id=layoff_year title="Year"/>
    <Column id=laid_off title="Laid Off"/>
    <Column id=return_30d_pct title="30d Return %" contentType=colorscale colorScale=diverging/>
    <Column id=return_pre_30d_pct title="Pre-Event 30d Return %"/>
</DataTable>

> **Important:** This analysis is descriptive, not causal. Stock returns around layoff events are influenced by earnings cycles, macro conditions, and sector rotation — not layoffs alone. The "AI halo" pattern is a hypothesis to investigate, not a conclusion.
