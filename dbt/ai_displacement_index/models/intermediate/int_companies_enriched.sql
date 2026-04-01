with layoffs as (
    select * from {{ ref('stg_layoffs_fyi') }}
),

tickers as (
    select
        company,
        ticker
    from {{ ref('company_tickers') }}
),

company_mapping as (
    select * from (values
        ('Google', 'GOOGL'),
        ('Meta', 'META'),
        ('Amazon', 'AMZN'),
        ('Microsoft', 'MSFT'),
        ('Alphabet', 'GOOGL'),
        ('Twitter', null),
        ('Salesforce', 'CRM'),
        ('Snap', 'SNAP'),
        ('Spotify', 'SPOT'),
        ('Lyft', 'LYFT'),
        ('Uber', 'UBER'),
        ('Airbnb', 'ABNB'),
        ('Coinbase', 'COIN'),
        ('Robinhood', 'HOOD'),
        ('Peloton', 'PTON'),
        ('Wayfair', 'W'),
        ('Zoom', 'ZM'),
        ('Shopify', 'SHOP'),
        ('Stripe', null),
        ('DoorDash', 'DASH'),
        ('Roblox', 'RBLX'),
        ('Unity', 'U'),
        ('Twilio', 'TWLO'),
        ('Dropbox', 'DBX'),
        ('DocuSign', 'DOCU'),
        ('Workday', 'WDAY'),
        ('Okta', 'OKTA'),
        ('Atlassian', 'TEAM'),
        ('HubSpot', 'HUBS'),
        ('Cisco', 'CSCO'),
        ('Intel', 'INTC'),
        ('IBM', 'IBM'),
        ('Oracle', 'ORCL'),
        ('SAP', 'SAP'),
        ('Dell', 'DELL'),
        ('HP', 'HPQ'),
        ('Qualcomm', 'QCOM'),
        ('PayPal', 'PYPL'),
        ('Block', 'SQ'),
        ('eBay', 'EBAY'),
        ('Netflix', 'NFLX'),
        ('Tesla', 'TSLA'),
        ('Apple', 'AAPL'),
        ('NVIDIA', 'NVDA'),
        ('AMD', 'AMD')
    ) as t(company_name, ticker_symbol)
),

enriched as (
    select
        l.company,
        l.location_hq,
        l.country,
        l.industry,
        l.stage,
        l.date_layoffs,
        l.layoff_year,
        l.laid_off,
        l.pct_laid_off,
        l.company_size_before,
        l.money_raised_mil,
        coalesce(
            m.ticker_symbol,
            t.ticker
        )                           as ticker
    from layoffs l
    left join company_mapping m
        on lower(l.company) = lower(m.company_name)
    left join tickers t
        on lower(l.company) = lower(t.company)
        and m.ticker_symbol is null
)

select * from enriched
