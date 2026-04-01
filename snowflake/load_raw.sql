-- =============================================================================
-- Load raw data from Cloudflare R2 into Snowflake RAW schema
-- Run as ACCOUNTADMIN (for stage creation) then LOADER for COPY INTO
-- Replace <R2_ACCOUNT_ID>, <R2_ACCESS_KEY_ID>, <R2_SECRET_ACCESS_KEY>
-- with your actual values before running
-- =============================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE AI_DISPLACEMENT;
USE SCHEMA RAW;

-- -----------------------------------------------------------------------------
-- 1. Storage integration (one-time setup)
-- Cloudflare R2 is S3-compatible — use S3 integration type
-- -----------------------------------------------------------------------------
CREATE STORAGE INTEGRATION IF NOT EXISTS r2_integration
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::000000000000:role/placeholder'
    STORAGE_ALLOWED_LOCATIONS = ('s3://ai-displacement-raw/');

-- NOTE: Cloudflare R2 doesn't support IAM role-based integration.
-- We use a direct credentials stage instead (see below).
-- The integration above is a placeholder — use CREDENTIALS in the stage.

-- -----------------------------------------------------------------------------
-- 2. External stage pointing to Cloudflare R2
-- -----------------------------------------------------------------------------
CREATE STAGE IF NOT EXISTS r2_raw_stage
    URL = 's3://ai-displacement-raw/'
    CREDENTIALS = (
        AWS_KEY_ID = '<R2_ACCESS_KEY_ID>'
        AWS_SECRET_KEY = '<R2_SECRET_ACCESS_KEY>'
    )
    ENDPOINT = '<R2_ACCOUNT_ID>.r2.cloudflarestorage.com'
    FILE_FORMAT = (
        TYPE = CSV
        SKIP_HEADER = 1
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF = ('', 'NULL', 'null', 'None')
        EMPTY_FIELD_AS_NULL = TRUE
    );

-- Verify stage is accessible
LIST @r2_raw_stage;

-- -----------------------------------------------------------------------------
-- 3. Create raw tables
-- -----------------------------------------------------------------------------
USE ROLE LOADER;

CREATE TABLE IF NOT EXISTS layoffs_fyi (
    nr                          INTEGER,
    company                     VARCHAR,
    location_hq                 VARCHAR,
    region                      VARCHAR,
    us_state                    VARCHAR,
    country                     VARCHAR,
    continent                   VARCHAR,
    laid_off                    INTEGER,
    date_layoffs                VARCHAR,
    percentage                  FLOAT,
    company_size_before_layoffs INTEGER,
    company_size_after_layoffs  INTEGER,
    industry                    VARCHAR,
    stage                       VARCHAR,
    money_raised_in_mil         FLOAT,
    year                        INTEGER,
    latitude                    FLOAT,
    longitude                   FLOAT
);

CREATE TABLE IF NOT EXISTS stackoverflow_survey (
    responseid      VARCHAR,
    mainbranch      VARCHAR,
    age             VARCHAR,
    employment      VARCHAR,
    remotework      VARCHAR,
    codingactivities VARCHAR,
    edlevel         VARCHAR,
    learncode       VARCHAR,
    yearscode       VARCHAR,
    yearscodepo     VARCHAR,
    devtype         VARCHAR,
    orgsize         VARCHAR,
    country         VARCHAR,
    aiselect        VARCHAR,
    aisent          VARCHAR,
    aiben           VARCHAR,
    aiacc           VARCHAR,
    aicomplex       VARCHAR,
    aitoolcurrently VARCHAR,
    aitoolinterested VARCHAR,
    ainextintegrated VARCHAR,
    aithreat        VARCHAR,
    aiethics        VARCHAR,
    aichallenges    VARCHAR,
    currency        VARCHAR,
    convertedcompyearly FLOAT,
    jobsat          VARCHAR
);

CREATE TABLE IF NOT EXISTS stock_prices (
    date    DATE,
    ticker  VARCHAR,
    open    FLOAT,
    close   FLOAT,
    volume  FLOAT
);

CREATE TABLE IF NOT EXISTS ai_exposure (
    soc_code         VARCHAR,
    occupation_title VARCHAR,
    aioe_score       FLOAT,
    source           VARCHAR,
    year_published   INTEGER
);

-- -----------------------------------------------------------------------------
-- 4. Load data with COPY INTO
-- -----------------------------------------------------------------------------

-- Layoffs
COPY INTO layoffs_fyi
    FROM @r2_raw_stage/layoffs_fyi/
    PATTERN = '.*\.csv'
    ON_ERROR = CONTINUE;

-- Stack Overflow survey
COPY INTO stackoverflow_survey
    FROM @r2_raw_stage/stackoverflow_survey/
    PATTERN = '.*\.csv'
    ON_ERROR = CONTINUE;

-- Stock prices
COPY INTO stock_prices
    FROM @r2_raw_stage/stock_prices/
    PATTERN = '.*\.csv'
    ON_ERROR = CONTINUE;

-- AI exposure scores
COPY INTO ai_exposure
    FROM @r2_raw_stage/ai_exposure/
    PATTERN = '.*\.csv'
    ON_ERROR = CONTINUE;

-- -----------------------------------------------------------------------------
-- 5. Verify row counts
-- -----------------------------------------------------------------------------
SELECT 'layoffs_fyi'       AS table_name, COUNT(*) AS rows FROM layoffs_fyi
UNION ALL
SELECT 'stackoverflow_survey', COUNT(*) FROM stackoverflow_survey
UNION ALL
SELECT 'stock_prices',         COUNT(*) FROM stock_prices
UNION ALL
SELECT 'ai_exposure',          COUNT(*) FROM ai_exposure;
