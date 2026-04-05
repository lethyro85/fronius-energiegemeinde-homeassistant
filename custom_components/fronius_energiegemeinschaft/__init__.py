"""The Fronius Energiegemeinschaft integration."""
from __future__ import annotations

import logging
import zoneinfo
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    UPDATE_INTERVAL,
    DATA_COORDINATOR,
    DATA_CLIENT,
    DATA_PRICING,
    CONF_PRICE_GRID_CONSUMPTION,
    CONF_PRICE_COMMUNITY_CONSUMPTION,
    CONF_PRICE_GRID_FEED_IN,
    CONF_PRICE_COMMUNITY_FEED_IN,
    DEFAULT_PRICE_GRID_CONSUMPTION,
    DEFAULT_PRICE_COMMUNITY_CONSUMPTION,
    DEFAULT_PRICE_GRID_FEED_IN,
    DEFAULT_PRICE_COMMUNITY_FEED_IN,
)
from .api_client import FroniusEnergyClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


def _get_last_n_months(n: int, reference: datetime | None = None) -> list[str]:
    """Return list of YYYY-MM strings for the last n months, oldest first."""
    if reference is None:
        reference = datetime.now()
    months = []
    dt = reference.replace(day=1)
    for _ in range(n):
        months.append(dt.strftime("%Y-%m"))
        dt = (dt - timedelta(days=1)).replace(day=1)
    return list(reversed(months))


def _extract_float(val) -> float:
    """Extract float from API value (dict with 'value' key, or direct string/number)."""
    if isinstance(val, dict):
        return float(val.get("value", 0) or 0)
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return 0.0


async def _write_cp_monthly_cost_statistics(
    hass: HomeAssistant,
    client,
    cp_id: int,
    cp_number: str,
    months: list[str],
    pricing: dict,
) -> None:
    """Fetch monthly totals for each month and write cost statistics to HA recorder."""
    # HA 2024+ has all three in recorder.statistics; older versions split across models
    try:
        from homeassistant.components.recorder.statistics import (  # noqa: PLC0415
            StatisticData,
            StatisticMetaData,
            async_add_external_statistics,
        )
    except ImportError:
        try:
            from homeassistant.components.recorder.statistics import (  # noqa: PLC0415
                async_add_external_statistics,
            )
            from homeassistant.components.recorder.models import (  # noqa: PLC0415
                StatisticData,
                StatisticMetaData,
            )
        except ImportError:
            _LOGGER.warning("Recorder statistics API not available — skipping historical stats")
            return

    tz = zoneinfo.ZoneInfo(hass.config.time_zone)
    statistic_id = f"{DOMAIN}:counter_point_{cp_id}_monthly_cost"

    metadata = StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=f"Counter Point {cp_number} Monthly Cost",
        source=DOMAIN,
        statistic_id=statistic_id,
        unit_of_measurement="€",
    )

    statistics = []
    cumulative_sum = 0.0

    for month_str in months:
        try:
            energy_data = await client.get_counter_point_energy_data(
                cp_id, view="month", time=month_str
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not fetch %s for statistics: %s", month_str, err)
            continue

        total_data = energy_data.get("total", {}).get("total", {})
        if not total_data:
            _LOGGER.debug(
                "No total data for counter point %s month %s — skipping", cp_id, month_str
            )
            continue

        cgrid = _extract_float(total_data.get("cgrid"))
        crec = _extract_float(total_data.get("crec"))
        fgrid = _extract_float(total_data.get("fgrid"))
        frec = _extract_float(total_data.get("frec"))

        consumption_cost = (
            cgrid * pricing["grid_consumption"] + crec * pricing["community_consumption"]
        )
        feed_in_revenue = (
            fgrid * pricing["grid_feed_in"] + frec * pricing["community_feed_in"]
        )
        net_cost = consumption_cost - feed_in_revenue
        cumulative_sum += net_cost

        dt = datetime.strptime(month_str, "%Y-%m").replace(tzinfo=tz)
        statistics.append(
            StatisticData(start=dt, state=round(net_cost, 2), sum=round(cumulative_sum, 2))
        )

    if statistics:
        async_add_external_statistics(hass, metadata, statistics)
        _LOGGER.info(
            "Wrote %d monthly cost statistics for counter point %s (id=%s)",
            len(statistics),
            cp_number,
            cp_id,
        )


def _normalize_data(data) -> dict | list | None:
    """Normalize data: treat empty list as None (no data available)."""
    if isinstance(data, list) and len(data) == 0:
        return None
    return data


def _merge_energy_data(current: dict, previous: dict) -> dict:
    """Merge energy data from two months (current wins on overlap).

    Keeps 'total' and 'meta' from the current month.
    Merges 'data' so daily entries from both months are available.

    The API returns 'data' as:
    - dict {"RC12345": {"2026-02-01": {...}}} when data exists
    - [] (empty list) when no data for that month yet
    """
    merged = dict(current)
    current_data = _normalize_data(current.get("data"))
    prev_data = _normalize_data(previous.get("data"))

    if isinstance(current_data, dict) and isinstance(prev_data, dict):
        # Both months have dict data — merge by rc_key, current overwrites on overlap
        merged_data = {}
        for rc_key in set(list(current_data.keys()) + list(prev_data.keys())):
            curr_rc = current_data.get(rc_key, {})
            prev_rc = prev_data.get(rc_key, {})
            if isinstance(curr_rc, dict) and isinstance(prev_rc, dict):
                merged_data[rc_key] = {**prev_rc, **curr_rc}
            else:
                merged_data[rc_key] = curr_rc if curr_rc else prev_rc
        merged["data"] = merged_data
    elif isinstance(current_data, dict):
        # Only current has data
        merged["data"] = current_data
    elif isinstance(prev_data, dict):
        # Current month has no data yet (empty list) — use previous month
        merged["data"] = prev_data
    elif isinstance(current_data, list) and isinstance(prev_data, list):
        # Both are non-empty lists — concatenate (prev first)
        merged["data"] = prev_data + current_data

    return merged


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fronius Energiegemeinschaft from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    # Get pricing from options (preferred) or data (fallback for upgrades)
    pricing = {
        "grid_consumption": entry.options.get(
            CONF_PRICE_GRID_CONSUMPTION,
            entry.data.get(CONF_PRICE_GRID_CONSUMPTION, DEFAULT_PRICE_GRID_CONSUMPTION),
        ),
        "community_consumption": entry.options.get(
            CONF_PRICE_COMMUNITY_CONSUMPTION,
            entry.data.get(
                CONF_PRICE_COMMUNITY_CONSUMPTION, DEFAULT_PRICE_COMMUNITY_CONSUMPTION
            ),
        ),
        "grid_feed_in": entry.options.get(
            CONF_PRICE_GRID_FEED_IN,
            entry.data.get(CONF_PRICE_GRID_FEED_IN, DEFAULT_PRICE_GRID_FEED_IN),
        ),
        "community_feed_in": entry.options.get(
            CONF_PRICE_COMMUNITY_FEED_IN,
            entry.data.get(CONF_PRICE_COMMUNITY_FEED_IN, DEFAULT_PRICE_COMMUNITY_FEED_IN),
        ),
    }

    client = FroniusEnergyClient(username, password, hass)

    # Test login
    try:
        await client.login()
    except Exception as err:
        _LOGGER.error("Failed to login: %s", err)
        return False

    # Track whether historical statistics have been written (backfill once on startup)
    stats_backfilled = False

    async def async_update_data():
        """Fetch data from API."""
        nonlocal stats_backfilled
        try:
            now = datetime.now()
            current_month = now.strftime("%Y-%m")
            prev_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

            # Get communities
            communities = await client.get_communities()

            # Get community energy data for all communities (current + previous month)
            community_data = {}
            for community in communities:
                community_id = community["id"]
                energy_current = await client.get_community_energy_data(
                    community_id, view="month", time=current_month
                )
                energy_prev = await client.get_community_energy_data(
                    community_id, view="month", time=prev_month
                )
                energy_data = _merge_energy_data(energy_current, energy_prev)

                # Log data structure for debugging
                data_section = energy_data.get("data", {})
                for rc_key, rc_val in (data_section.items() if isinstance(data_section, dict) else []):
                    _LOGGER.debug(
                        "Community %s rc_key=%s data type=%s entries=%s",
                        community_id, rc_key, type(rc_val).__name__,
                        len(rc_val) if rc_val else 0,
                    )
                    break

                community_data[community_id] = {
                    "info": community,
                    "energy": energy_data,
                }

            # Get counter points
            counter_points_raw = await client.get_counter_points()
            _LOGGER.debug(
                "Counter points raw response type=%s value=%s",
                type(counter_points_raw).__name__,
                str(counter_points_raw)[:500],
            )
            # Handle both list and dict ({"data": [...]}) response formats
            if isinstance(counter_points_raw, dict):
                counter_points = counter_points_raw.get("data", [])
            elif isinstance(counter_points_raw, list):
                counter_points = counter_points_raw
            else:
                counter_points = []

            # Get counter point energy data (current + previous month)
            counter_point_data = {}
            for counter_point in counter_points:
                cp_id = counter_point["id"]
                energy_current = await client.get_counter_point_energy_data(
                    cp_id, view="month", time=current_month
                )
                energy_prev = await client.get_counter_point_energy_data(
                    cp_id, view="month", time=prev_month
                )
                energy_data = _merge_energy_data(energy_current, energy_prev)

                data_section = energy_data.get("data")
                _LOGGER.debug(
                    "CounterPoint %s data type=%s entries=%s",
                    cp_id,
                    type(data_section).__name__,
                    len(data_section) if data_section else 0,
                )

                counter_point_data[cp_id] = {
                    "info": counter_point,
                    "energy": energy_data,
                }

            # Write monthly cost statistics to recorder
            # First run: backfill last 13 months
            # Subsequent runs: update current + previous month (prev may still be settling
            # due to ~2 day data delay from Fronius portal)
            months_for_stats = (
                _get_last_n_months(13, now) if not stats_backfilled else [prev_month, current_month]
            )
            for counter_point in counter_points:
                cp_id = counter_point["id"]
                cp_number = counter_point_data[cp_id]["info"].get(
                    "counter_number", str(cp_id)
                )
                try:
                    await _write_cp_monthly_cost_statistics(
                        hass, client, cp_id, cp_number, months_for_stats, pricing
                    )
                except Exception as stats_err:  # noqa: BLE001
                    _LOGGER.error(
                        "Failed to write statistics for counter point %s: %s",
                        cp_id,
                        stats_err,
                    )
            stats_backfilled = True

            return {
                "communities": community_data,
                "counter_points": counter_point_data,
            }
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_CLIENT: client,
        DATA_PRICING: pricing,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Close the API client session
        client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
        await client.close()

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
