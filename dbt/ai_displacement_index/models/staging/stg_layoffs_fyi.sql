with source as (
    select * from {{ source('raw', 'layoffs_fyi') }}
),

renamed as (
    select
        nr                                          as row_nr,
        company,
        location_hq,
        region,
        usstate                                     as us_state,
        country,
        continent,
        laid_off::integer                           as laid_off,
        try_cast(date_layoffs as date)              as date_layoffs,
        percentage                                  as pct_laid_off,
        company_size_before_layoffs::integer        as company_size_before,
        company_size_after_layoffs::integer         as company_size_after,
        industry,
        stage,
        money_raised_in__mil                        as money_raised_mil,
        year::integer                               as layoff_year

        -- latitude and longitude dropped — not needed for analysis
    from source
)

select * from renamed
