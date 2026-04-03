with layoffs as (
    select
        company,
        ticker,
        industry,
        date_layoffs,
        layoff_year,
        laid_off
    from {{ ref('int_companies_enriched') }}
    where ticker is not null
      and date_layoffs is not null
),
prices as (
    select * from {{ ref('stg_stock_prices') }}
),
windowed as (
    select
        l.company,
        l.ticker,
        l.industry,
        l.date_layoffs,
        l.layoff_year,
        l.laid_off,
        p.price_date,
        p.close_price,
        datediff('day', l.date_layoffs, p.price_date) as days_from_event
    from layoffs l
    inner join prices p
        on p.ticker = l.ticker
        and p.price_date between dateadd('day', -30, l.date_layoffs)
                             and dateadd('day', 30, l.date_layoffs)
),
normalized as (
    select
        w.*,
        event_price.close_price as base_price,
        round(
            (w.close_price - event_price.close_price)
            / nullif(event_price.close_price, 0) * 100,
        2) as indexed_return
    from windowed w
    left join prices event_price
        on event_price.ticker = w.ticker
        and event_price.price_date = w.date_layoffs
)
select * from normalized
