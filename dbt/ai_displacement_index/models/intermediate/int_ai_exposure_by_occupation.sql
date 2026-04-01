with exposure as (
    select * from {{ ref('stg_ai_exposure') }}
),

grouped as (
    select
        soc_code,
        occupation_title,
        aioe_score,
        data_source,
        year_published,

        -- Broad occupation group from first 2 digits of SOC code
        left(soc_code, 2)           as soc_major_group,

        case left(soc_code, 2)
            when '11' then 'Management'
            when '13' then 'Business & Financial'
            when '15' then 'Computer & Mathematical'
            when '17' then 'Architecture & Engineering'
            when '19' then 'Life, Physical & Social Science'
            when '21' then 'Community & Social Service'
            when '23' then 'Legal'
            when '25' then 'Education'
            when '27' then 'Arts, Design & Media'
            when '29' then 'Healthcare Practitioners'
            when '31' then 'Healthcare Support'
            when '33' then 'Protective Service'
            when '35' then 'Food Preparation'
            when '37' then 'Building & Grounds'
            when '39' then 'Personal Care'
            when '41' then 'Sales'
            when '43' then 'Office & Administrative'
            when '45' then 'Farming, Fishing & Forestry'
            when '47' then 'Construction'
            when '49' then 'Installation & Maintenance'
            when '51' then 'Production'
            when '53' then 'Transportation'
            else 'Other'
        end                         as occupation_group,

        -- Flag occupations most relevant to tech layoff narrative
        case
            when left(soc_code, 2) = '15' then true
            when left(soc_code, 2) = '11' then true
            when left(soc_code, 2) = '13' then true
            else false
        end                         as is_tech_adjacent,

        -- Exposure tier for dashboard filtering
        case
            when aioe_score >= 1.0  then 'High'
            when aioe_score >= 0.0  then 'Medium'
            when aioe_score >= -1.0 then 'Low'
            else 'Very Low'
        end                         as exposure_tier

    from exposure
)

select * from grouped
