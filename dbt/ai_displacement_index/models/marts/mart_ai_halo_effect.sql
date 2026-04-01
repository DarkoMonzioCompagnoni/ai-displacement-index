with layoffs as (
    select * from {{ ref('int_companies_enriched') }}
    where ticker is not null
      and date_layoffs is not null
),

prices as (
    select * from {{ ref('stg_stock_prices') }}
),

-- For each layoff event with a ticker, compute stock return
-- in the 30 days before and after the layoff date
layoff_windows as (
    select
        l.company,
        l.ticker,
        l.industry,
        l.date_layoffs,
        l.layoff_year,
        l.laid_off,
        l.pct_laid_off,
        l.stage,

        -- Price on layoff date (or nearest trading day)
        event_price.close_price          as price_on_event,

        -- Price 30 days before
        pre_price.close_price            as price_30d_before,

        -- Price 30 days after
        post_price.close_price           as price_30d_after

    from layoffs l

    -- Event day price
    left join prices event_price
        on event_price.ticker = l.ticker
        and event_price.price_date = l.date_layoffs

    -- Pre-event price (~30 days before)
    left join prices pre_price
        on pre_price.ticker = l.ticker
        and pre_price.price_date = dateadd('day', -30, l.date_layoffs)

    -- Post-event price (~30 days after)
    left join prices post_price
        on post_price.ticker = l.ticker
        and post_price.price_date = dateadd('day', 30, l.date_layoffs)
),

returns as (
    select
        company,
        ticker,
        industry,
        date_layoffs,
        layoff_year,
        laid_off,
        pct_laid_off,
        stage,
        price_on_event,
        price_30d_before,
        price_30d_after,

        -- 30-day return after layoff announcement
        case
            when price_on_event > 0 and price_30d_after is not null
            then round((price_30d_after - price_on_event) / price_on_event * 100, 2)
        end                             as return_30d_pct,

        -- 30-day return before (context: was stock already moving?)
        case
            when price_30d_before > 0 and price_on_event is not null
            then round((price_on_event - price_30d_before) / price_30d_before * 100, 2)
        end                             as return_pre_30d_pct

    from layoff_windows
)

select * from returns
where price_on_event is not null
