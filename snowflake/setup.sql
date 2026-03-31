-- =============================================================================
-- AI Displacement Index — Snowflake Setup
-- ⚠️ IMPORTANT: Replace user passwords before running the script
-- Run this script as ACCOUNTADMIN after creating a new Snowflake account.
-- Re-run after every 30-day free trial reset.
-- =============================================================================


-- =============================================================================
-- 1. ROLES
-- =============================================================================

USE ROLE ACCOUNTADMIN;

-- Functional roles
CREATE ROLE IF NOT EXISTS LOADER     COMMENT = 'Ingestion scripts — writes raw data only';
CREATE ROLE IF NOT EXISTS TRANSFORMER COMMENT = 'dbt — reads raw, writes staging and marts';
CREATE ROLE IF NOT EXISTS REPORTER   COMMENT = 'Sigma — reads marts only';

-- Grant role hierarchy up to SYSADMIN so SYSADMIN can manage all objects
GRANT ROLE LOADER      TO ROLE SYSADMIN;
GRANT ROLE TRANSFORMER TO ROLE SYSADMIN;
GRANT ROLE REPORTER    TO ROLE SYSADMIN;


-- =============================================================================
-- 2. USERS
-- =============================================================================

-- dbt user (TRANSFORMER)
CREATE USER IF NOT EXISTS DBT_USER
    PASSWORD             = 'ChangeMe123!'   -- replace before use
    DEFAULT_ROLE         = TRANSFORMER
    DEFAULT_WAREHOUSE    = TRANSFORMER_WH
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT              = 'Service user for dbt Core';

GRANT ROLE TRANSFORMER TO USER DBT_USER;

-- Loader user (ingestion scripts)
CREATE USER IF NOT EXISTS LOADER_USER
    PASSWORD             = 'ChangeMe123!'   -- replace before use
    DEFAULT_ROLE         = LOADER
    DEFAULT_WAREHOUSE    = LOADER_WH
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT              = 'Service user for Python ingestion scripts';

GRANT ROLE LOADER TO USER LOADER_USER;

-- Reporter user (Sigma)
CREATE USER IF NOT EXISTS REPORTER_USER
    PASSWORD             = 'ChangeMe123!'   -- replace before use
    DEFAULT_ROLE         = REPORTER
    DEFAULT_WAREHOUSE    = REPORTER_WH
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT              = 'Service user for Sigma dashboard';

GRANT ROLE REPORTER TO USER REPORTER_USER;


-- =============================================================================
-- 3. WAREHOUSES
-- One per role — all X-Small with aggressive auto-suspend to stay in free tier
-- =============================================================================

USE ROLE SYSADMIN;

CREATE WAREHOUSE IF NOT EXISTS LOADER_WH
    WAREHOUSE_SIZE        = 'X-SMALL'
    AUTO_SUSPEND          = 60
    AUTO_RESUME           = TRUE
    INITIALLY_SUSPENDED   = TRUE
    COMMENT               = 'Used by ingestion scripts';

CREATE WAREHOUSE IF NOT EXISTS TRANSFORMER_WH
    WAREHOUSE_SIZE        = 'X-SMALL'
    AUTO_SUSPEND          = 60
    AUTO_RESUME           = TRUE
    INITIALLY_SUSPENDED   = TRUE
    COMMENT               = 'Used by dbt';

CREATE WAREHOUSE IF NOT EXISTS REPORTER_WH
    WAREHOUSE_SIZE        = 'X-SMALL'
    AUTO_SUSPEND          = 60
    AUTO_RESUME           = TRUE
    INITIALLY_SUSPENDED   = TRUE
    COMMENT               = 'Used by Sigma';

-- Grant warehouse usage to the appropriate roles
GRANT USAGE ON WAREHOUSE LOADER_WH      TO ROLE LOADER;
GRANT USAGE ON WAREHOUSE TRANSFORMER_WH TO ROLE TRANSFORMER;
GRANT USAGE ON WAREHOUSE REPORTER_WH    TO ROLE REPORTER;


-- =============================================================================
-- 4. DATABASE AND SCHEMAS
-- =============================================================================

CREATE DATABASE IF NOT EXISTS AI_DISPLACEMENT
    COMMENT = 'AI Displacement Index — all schemas';

CREATE SCHEMA IF NOT EXISTS AI_DISPLACEMENT.RAW
    COMMENT = 'Direct copies of source files — no transformation';

CREATE SCHEMA IF NOT EXISTS AI_DISPLACEMENT.STAGING
    COMMENT = 'Typed, renamed, lightly cleaned — one model per source';

CREATE SCHEMA IF NOT EXISTS AI_DISPLACEMENT.INTERMEDIATE
    COMMENT = 'Cross-source enrichment — joins and mappings';

CREATE SCHEMA IF NOT EXISTS AI_DISPLACEMENT.MARTS
    COMMENT = 'Aggregated, dashboard-ready — one mart per Sigma tab';


-- =============================================================================
-- 5. PRIVILEGES
-- Following least-privilege: each role gets only what it needs.
-- =============================================================================

-- LOADER: write access to RAW only
GRANT USAGE ON DATABASE AI_DISPLACEMENT          TO ROLE LOADER;
GRANT USAGE ON SCHEMA AI_DISPLACEMENT.RAW        TO ROLE LOADER;
GRANT CREATE TABLE ON SCHEMA AI_DISPLACEMENT.RAW TO ROLE LOADER;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA AI_DISPLACEMENT.RAW TO ROLE LOADER;
GRANT INSERT, UPDATE ON FUTURE TABLES IN SCHEMA AI_DISPLACEMENT.RAW TO ROLE LOADER;

-- TRANSFORMER: read RAW, write STAGING + INTERMEDIATE + MARTS
GRANT USAGE ON DATABASE AI_DISPLACEMENT               TO ROLE TRANSFORMER;
GRANT USAGE ON SCHEMA AI_DISPLACEMENT.RAW             TO ROLE TRANSFORMER;
GRANT SELECT ON ALL TABLES IN SCHEMA AI_DISPLACEMENT.RAW TO ROLE TRANSFORMER;
GRANT SELECT ON FUTURE TABLES IN SCHEMA AI_DISPLACEMENT.RAW TO ROLE TRANSFORMER;

GRANT USAGE ON SCHEMA AI_DISPLACEMENT.STAGING         TO ROLE TRANSFORMER;
GRANT CREATE TABLE ON SCHEMA AI_DISPLACEMENT.STAGING  TO ROLE TRANSFORMER;
GRANT ALL ON ALL TABLES IN SCHEMA AI_DISPLACEMENT.STAGING TO ROLE TRANSFORMER;
GRANT ALL ON FUTURE TABLES IN SCHEMA AI_DISPLACEMENT.STAGING TO ROLE TRANSFORMER;

GRANT USAGE ON SCHEMA AI_DISPLACEMENT.INTERMEDIATE        TO ROLE TRANSFORMER;
GRANT CREATE TABLE ON SCHEMA AI_DISPLACEMENT.INTERMEDIATE TO ROLE TRANSFORMER;
GRANT ALL ON ALL TABLES IN SCHEMA AI_DISPLACEMENT.INTERMEDIATE TO ROLE TRANSFORMER;
GRANT ALL ON FUTURE TABLES IN SCHEMA AI_DISPLACEMENT.INTERMEDIATE TO ROLE TRANSFORMER;

GRANT USAGE ON SCHEMA AI_DISPLACEMENT.MARTS           TO ROLE TRANSFORMER;
GRANT CREATE TABLE ON SCHEMA AI_DISPLACEMENT.MARTS    TO ROLE TRANSFORMER;
GRANT ALL ON ALL TABLES IN SCHEMA AI_DISPLACEMENT.MARTS TO ROLE TRANSFORMER;
GRANT ALL ON FUTURE TABLES IN SCHEMA AI_DISPLACEMENT.MARTS TO ROLE TRANSFORMER;

-- REPORTER: read MARTS only
GRANT USAGE ON DATABASE AI_DISPLACEMENT            TO ROLE REPORTER;
GRANT USAGE ON SCHEMA AI_DISPLACEMENT.MARTS        TO ROLE REPORTER;
GRANT SELECT ON ALL TABLES IN SCHEMA AI_DISPLACEMENT.MARTS TO ROLE REPORTER;
GRANT SELECT ON FUTURE TABLES IN SCHEMA AI_DISPLACEMENT.MARTS TO ROLE REPORTER;


-- =============================================================================
-- END OF SETUP
-- Verify with:
--   SHOW ROLES;
--   SHOW WAREHOUSES;
--   SHOW SCHEMAS IN DATABASE AI_DISPLACEMENT;
-- =============================================================================
