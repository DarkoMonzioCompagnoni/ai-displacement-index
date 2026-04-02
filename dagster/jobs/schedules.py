from dagster import ScheduleDefinition, define_asset_job

stock_price_job = define_asset_job(
    name="stock_price_job",
    selection=["stock_prices_asset"],
)

weekly_stock_price_schedule = ScheduleDefinition(
    job=stock_price_job,
    cron_schedule="0 6 * * 1",  # Every Monday at 6am
    name="weekly_stock_prices",
)
