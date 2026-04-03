---
title: Developer Pulse
---

# 💬 Developer Pulse

How developers feel about AI tools — from the Stack Overflow Developer Survey 2024 (65,437 respondents).
```sql ai_adoption_by_role
select
    primary_dev_type as developer_role,
    sum(respondent_count) as respondents,
    round(avg(pct_uses_ai), 1) as pct_uses_ai,
    round(avg(pct_perceives_threat), 1) as pct_sees_ai_as_threat,
    round(avg(pct_trusts_accuracy), 1) as pct_trusts_accuracy
from snowflake.developer_sentiment
where primary_dev_type is not null
  and primary_dev_type not in ('', 'Other (please specify):')
  and respondent_count > 10
group by 1
order by 3 desc
limit 15
```

<DataTable data={ai_adoption_by_role} rows=15>
    <Column id=developer_role title="Developer Role"/>
    <Column id=pct_uses_ai title="% Uses AI" contentType=colorscale colorScale=positive/>
    <Column id=pct_sees_ai_as_threat title="% Sees AI as Threat" contentType=colorscale colorScale=negative/>
    <Column id=pct_trusts_accuracy title="% Trusts Accuracy" contentType=colorscale colorScale=positive/>
</DataTable>

```sql threat_by_experience
select
    primary_dev_type as developer_role,
    round(avg(pct_perceives_threat), 1) as pct_sees_threat,
    round(avg(pct_uses_ai), 1) as pct_uses_ai,
    sum(respondent_count) as respondents
from snowflake.developer_sentiment
where primary_dev_type is not null
  and respondent_count > 50
group by 1
order by 2 desc
limit 12
```

<ScatterPlot
    data={threat_by_experience}
    x=pct_uses_ai
    y=pct_sees_threat
    series=developer_role
    title="AI Usage vs. Perceived Threat by Developer Role"
    xAxisTitle="% Using AI Tools"
    yAxisTitle="% Seeing AI as Job Threat"
/>

> **Key finding:** Usage and trust are diverging. More developers use AI tools than ever — but fewer trust them. Source: Stack Overflow Developer Survey 2024.
