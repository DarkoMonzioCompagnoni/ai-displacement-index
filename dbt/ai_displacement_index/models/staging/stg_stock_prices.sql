with source as (
    select * from {{ source('raw', 'stock_prices') }}
),

renamed as (
    select
        try_cast(date as date)  as price_date,
        ticker,
        open::float             as open_price,
        close::float            as close_price,
        volume::bigint          as volume
    from source
)

select * from renamed
