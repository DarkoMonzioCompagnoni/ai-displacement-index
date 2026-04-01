with exposure as (
    select * from {{ ref('int_ai_exposure_by_occupation') }}
),

layoffs as (
    select
        industry,
        count(*)        as layoff_events,
        sum(laid_off)   as total_laid_off
    from {{ ref('int_companies_enriched') }}
    group by 1
),

final as (
    select
        e.soc_code,
        e.occupation_title,
        e.occupation_group,
        e.soc_major_group,
        e.aioe_score,
        e.exposure_tier,
        e.is_tech_adjacent,
        e.data_source,
        e.year_published,

        -- Note: direct join between occupation and layoff industry
        -- is approximate — SOC codes don't map cleanly to Layoffs.fyi industries.
        -- This is a known limitation documented in ARCHITECTURE.md.
        -- Use for directional analysis only.
        l.layoff_events,
        l.total_laid_off

    from exposure e
    left join layoffs l
        on lower(e.occupation_group) = lower(l.industry)
)

select * from final
