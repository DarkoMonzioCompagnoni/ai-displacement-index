from dagster import Definitions
from assets import (
    layoffs_fyi_asset,
    so_survey_asset,
    stock_prices_asset,
    ai_exposure_asset,
)
from schedules import weekly_stock_price_schedule

defs = Definitions(
    assets=[
        layoffs_fyi_asset,
        so_survey_asset,
        stock_prices_asset,
        ai_exposure_asset,
    ],
    schedules=[weekly_stock_price_schedule],
)
