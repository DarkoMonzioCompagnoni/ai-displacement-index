with survey as (
    select * from {{ ref('int_survey_trends') }}
),

aggregated as (
    select
        survey_year,
        primary_dev_type,
        country,
        employment,
        org_size,

        count(*)                                        as respondent_count,

        -- AI adoption
        round(sum(uses_ai_tools) * 100.0 / count(*), 1)    as pct_uses_ai,

        -- AI threat perception
        round(sum(perceives_ai_threat) * 100.0 / count(*), 1) as pct_perceives_threat,

        -- AI accuracy trust
        round(sum(trusts_ai_accuracy) * 100.0 / count(*), 1)  as pct_trusts_accuracy,

        -- Raw counts for drill-down
        sum(uses_ai_tools)                              as uses_ai_count,
        sum(perceives_ai_threat)                        as perceives_threat_count,
        sum(trusts_ai_accuracy)                         as trusts_accuracy_count,

        -- Sentiment distribution (most common value)
        mode(ai_sentiment)                              as modal_ai_sentiment,
        mode(ai_job_threat)                             as modal_job_threat_response,

        -- Compensation
        median(comp_yearly_usd)                         as median_comp_usd

    from survey
    where primary_dev_type is not null
      and primary_dev_type != ''
    group by 1, 2, 3, 4, 5
)

select * from aggregated
