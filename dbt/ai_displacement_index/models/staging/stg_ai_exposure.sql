with source as (
    select * from {{ source('raw', 'ai_exposure') }}
),

renamed as (
    select
        soc_code,
        occupation_title,
        aioe_score::float       as aioe_score,
        source                  as data_source,
        year_published::integer as year_published
    from source
)

select * from renamed
