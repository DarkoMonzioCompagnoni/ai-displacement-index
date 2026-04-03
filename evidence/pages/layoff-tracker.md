---
title: Layoff Tracker
---

# 📉 Layoff Tracker

Tech layoffs since 2020 — broken into two phases: the post-pandemic correction (2022–2023) and the AI-driven restructuring (2024–2025).
```sql layoffs_by_year
select
    layoff_year as year,
    sum(total_laid_off) as employees_laid_off,
    sum(layoff_events) as layoff_events
from snowflake.layoff_trends
where layoff_year is not null
group by 1
order by 1
```

<BarChart
    data={layoffs_by_year}
    x=year
    y=employees_laid_off
    title="Employees Laid Off by Year"
    colorPalette={['#e63946']}
/>
```sql layoffs_by_industry
select
    industry,
    sum(total_laid_off) as employees_laid_off,
    sum(layoff_events) as layoff_events
from snowflake.layoff_trends
where industry is not null
group by 1
order by 2 desc
limit 15
```

<BarChart
    data={layoffs_by_industry}
    x=industry
    y=employees_laid_off
    swapXY=true
    title="Top 15 Industries by Employees Laid Off"
    colorPalette={['#457b9d']}
/>
```sql layoffs_by_stage
select
    stage,
    sum(total_laid_off) as employees_laid_off,
    sum(layoff_events) as layoff_events
from snowflake.layoff_trends
where stage is not null and stage != 'Unknown'
group by 1
order by 2 desc
```

<BarChart
    data={layoffs_by_stage}
    x=stage
    y=employees_laid_off
    swapXY=true
    title="Layoffs by Company Stage"
    colorPalette={['#2a9d8f']}
/>

> **Note:** 2022–2023 layoffs were driven by post-pandemic over-hiring corrections. By 2024–2025, companies began explicitly framing cuts as AI-driven restructuring.
