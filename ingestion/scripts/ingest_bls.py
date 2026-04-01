# =============================================================================
# ingest_bls.py — DOCUMENTED FAILURE
# =============================================================================
#
# INTENT: Pull national occupational employment data from the BLS OEWS API
# and flat files, filter to tech-relevant occupations, and upload to R2.
#
# WHY IT FAILED:
# The BLS blocks all programmatic access to its data files:
#
#   1. BLS Public Data API (api.bls.gov/publicAPI/v2/timeseries/data/)
#      — Series IDs for OEWS are undocumented and could not be verified.
#        Two separate attempts with different series ID formats both returned
#        "Series does not exist" for all occupations.
#
#   2. BLS special requests download (www.bls.gov/oes/special.requests/)
#      — Returns HTTP 403 Forbidden for non-browser clients.
#
#   3. BLS flat file server (download.bls.gov/pub/time.series/oe/)
#      — Also returns HTTP 403 Forbidden for non-browser clients,
#        despite being a public file server with no login required.
#
# WORKAROUND ADOPTED:
# Replaced with two alternative sources that serve the same analytical purpose:
#
#   - ingestion/scripts/ingest_ai_exposure.py
#     Downloads the Felten, Raj & Seamans (2021) AIOE scores from GitHub.
#     774 occupations with AI exposure scores indexed by SOC code.
#     Used in: mart_occupation_risk (Tab 4)
#
#   - For employment denominators (total workers per occupation):
#     The BLS OEWS Excel files are available at bls.gov/oes/tables.htm
#     and must be downloaded manually. Place the national file at:
#     ingestion/scripts/data/bls_oews_raw.xlsx
#     A future ingestion script can process this file on demand.
#
# LOGGED IN: ai-usage.md entry #011
# =============================================================================
