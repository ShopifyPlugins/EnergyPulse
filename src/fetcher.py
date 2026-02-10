import logging
from datetime import timedelta

import pandas as pd
from entsoe import EntsoePandasClient

from src.config import ENTSOE_API_KEY, DEFAULT_BIDDING_ZONE

logger = logging.getLogger(__name__)

# ENTSO-E area codes for supported bidding zones
ZONE_MAP = {
    "DE_LU": "10Y1001A1001A82H",  # Germany/Luxembourg
    "FR": "10YFR-RTE------C",      # France
    "NL": "10YNL----------L",      # Netherlands
    "AT": "10YAT-APG------L",      # Austria
    "BE": "10YBE----------2",      # Belgium
}


def _get_client() -> EntsoePandasClient:
    return EntsoePandasClient(api_key=ENTSOE_API_KEY)


def _resolve_zone(zone: str) -> str:
    code = ZONE_MAP.get(zone)
    if code is None:
        raise ValueError(f"Unknown zone: {zone}. Supported: {list(ZONE_MAP.keys())}")
    return code


def fetch_day_ahead_prices(
    zone: str = DEFAULT_BIDDING_ZONE, days: int = 7
) -> pd.Series:
    """Fetch day-ahead electricity prices (EUR/MWh) from ENTSO-E."""
    area_code = _resolve_zone(zone)
    end = pd.Timestamp.now(tz="Europe/Berlin").normalize() + timedelta(days=1)
    start = end - timedelta(days=days)

    client = _get_client()
    prices = client.query_day_ahead_prices(area_code, start=start, end=end)
    # Convert EUR/MWh → EUR/kWh
    prices = prices / 1000.0
    logger.info("Fetched %d price points for zone %s", len(prices), zone)
    return prices


def fetch_latest_prices(zone: str = DEFAULT_BIDDING_ZONE) -> pd.Series:
    """Fetch today's and tomorrow's prices (if available after 13:00 CET)."""
    area_code = _resolve_zone(zone)
    today = pd.Timestamp.now(tz="Europe/Berlin").normalize()
    end = today + timedelta(days=2)

    client = _get_client()
    prices = client.query_day_ahead_prices(area_code, start=today, end=end)
    prices = prices / 1000.0
    return prices
