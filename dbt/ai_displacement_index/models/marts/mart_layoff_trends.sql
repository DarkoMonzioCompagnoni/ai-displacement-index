with layoffs as (
    select * from {{ ref('int_companies_enriched') }}
),

aggregated as (
    select
        layoff_year,
        date_trunc('quarter', date_layoffs)     as layoff_quarter,
        country,
        industry,
        stage,

        count(*)                                as layoff_events,
        sum(laid_off)                           as total_laid_off,
        avg(pct_laid_off)                       as avg_pct_laid_off,
        avg(company_size_before)                as avg_company_size,
        avg(money_raised_mil)                   as avg_funding_mil,

        -- Companies with a ticker (publicly traded)
        count(case when ticker is not null then 1 end) as public_company_events,

        -- Percentage of events from public companies
        round(
            count(case when ticker is not null then 1 end) * 100.0 / count(*),
            1
        )                                       as pct_public_company_events

    from layoffs
    where date_layoffs is not null
    group by 1, 2, 3, 4, 5
)

select * from aggregated
