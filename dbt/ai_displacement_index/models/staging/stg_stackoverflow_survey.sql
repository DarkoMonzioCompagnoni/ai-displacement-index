with source as (
    select * from {{ source('raw', 'stackoverflow_survey') }}
),

renamed as (
    select
        responseid,
        mainbranch,
        employment,
        remotework,
        edlevel                 as education_level,
        yearscode               as years_coding_total,
        yearscodepro             as years_coding_pro,
        devtype,
        orgsize                 as org_size,
        country,
        aiselect                as ai_select,
        aisent                  as ai_sentiment,
        aiben                   as ai_benefit,
        aiacc                   as ai_accuracy_trust,
        aicomplex               as ai_complex_tasks,
        aithreat                as ai_job_threat,
        aiethics                as ai_ethics_concern,
        aichallenges            as ai_challenges,
        try_cast(convertedcompyearly as float) as comp_yearly_usd
    from source
)

select * from renamed
