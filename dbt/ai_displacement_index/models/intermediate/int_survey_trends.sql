with survey as (
    select * from {{ ref('stg_stackoverflow_survey') }}
),

cleaned as (
    select
        responseid,
        country,
        employment,
        education_level,
        years_coding_pro,
        org_size,

        -- Split multi-value devtype into primary role (first value before semicolon)
        split_part(devtype, ';', 1)     as primary_dev_type,

        -- AI sentiment columns — all varchar from survey
        ai_select,
        ai_sentiment,
        ai_benefit,
        ai_accuracy_trust,
        ai_complex_tasks,
        ai_job_threat,
        ai_ethics_concern,

        -- Derived binary flags for aggregation
        case when ai_select = 'Yes'
            then 1 else 0
        end                             as uses_ai_tools,

        case when ai_job_threat in ('Yes', 'Somewhat')
            then 1 else 0
        end                             as perceives_ai_threat,

        case when ai_accuracy_trust in ('Highly trust', 'Somewhat trust')
            then 1 else 0
        end                             as trusts_ai_accuracy,

        -- Survey year (static — one year of data)
        2024                            as survey_year,

        comp_yearly_usd

    from survey
    where mainbranch = 'I am a developer by profession'  -- professional devs only
)

select * from cleaned
