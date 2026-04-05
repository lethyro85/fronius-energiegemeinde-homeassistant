# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.8] - 2026-04-05

### Fixed
- Statistics: regular updates now refresh **current + previous month** (not just current month).
  The Fronius portal has a ~2 day data delay, so the previous month's total can still change
  for the first 2 days of a new month. Without this fix the previous month's statistic
  would remain incomplete if the backfill ran before the data was fully settled.

## [0.2.7] - 2026-04-05

### Fixed
- Statistics import: `StatisticData`/`StatisticMetaData` moved from `recorder.models` to
  `recorder.statistics` in HA 2024+. Import now tries the new location first, falls back
  to the old location. Without this fix no statistics were written (silent ImportError).

## [0.2.6] - 2026-04-05

### Added

**Long-term statistics for monthly electricity costs**
- The integration now writes historical statistics directly into the HA recorder
  using `async_add_external_statistics`
- Statistic ID: `fronius_energiegemeinschaft:counter_point_{id}_monthly_cost`
- On first startup: backfills the last 13 months automatically with one API call per month
- On each subsequent update: refreshes only the current month (keeps running total current)
- Statistics include `state` (monthly net cost €) and `sum` (cumulative total)
- Visible in HA → Developer Tools → Statistics and usable in ApexCharts / Energy dashboard
- Added `"dependencies": ["recorder"]` to manifest.json

## [0.2.5] - 2026-03-02

### Fixed (API behaviour changes since v0.2.0)

Between v0.2.0 and v0.2.5 the Fronius portal API changed in several ways
that broke the integration at the start of March 2026:

**1. Community `data` section — intermittent list format (v0.2.1)**
- Old (v0.2.0): `energy_data["data"][rc_number]` was always a date-keyed dict
  `{"2026-02-01T00:00:00+01:00": {"crec": {"value": "1.23"}, ...}}`
- New (observed March 1): same key sometimes returned a **list** `[...]`
- Fix: added `_iter_daily_data()` helper that transparently handles both dict and list
- Fix: added `AttributeError` to all `except` clauses so sensors don't crash on startup

**2. Counter point `data` section — empty list when no current-month data (v0.2.5)**
- Old (v0.2.0): when no data, API returned `{}` (empty dict)
- New: when the current month has no data yet, API returns `[]` (empty **list**)
  while previous month still returns a proper dict `{"CC101056": {date: {...}}}`
- This caused all `daily_data_*` sensor attributes to be empty `{}`
- Fix: `_normalize_data()` treats `[]` as "no data available"
- Fix: `_merge_energy_data()` falls back to previous month's dict when current is empty

**3. Month boundary — no current-month data (v0.2.2)**
- Integration previously only fetched the current month
- At the start of a new month + 2-day smart meter delay → all values 0
- Fix: always fetch both current and previous month, merge the daily data

**Verified with live API test script** (`test_api.py`):
- Counter Point 913 (Consumer): 16 daily entries, Feb 28 ctotal=22.84 kWh
- Counter Point 914 (Producer): 16 daily entries, Feb 28 ftotal=0.17 kWh

## [0.2.4] - 2026-03-02

### Fixed
- Counter point daily_data attributes always empty
- Counter point API returns `data` as a **list** (not a dict with rc_key wrapper)
- `_merge_energy_data` now handles list format for counter points
- `FroniusCounterPointSensor` and `DailyCostSensor` now read list data directly

## [0.2.3] - 2026-03-02

### Changed
- Added comprehensive debug logging for counter point energy data structure
- Added robust handling for counter_points API response (list or dict wrapper)

## [0.2.2] - 2026-03-02

### Fixed
- All sensor values showing 0 at the start of a new month
- Now always fetches both current and previous month data and merges them
- Ensures ~60 days of daily data are always available regardless of month boundary
- Sensor state (total) reflects the most current month; daily_data attributes span both months

## [0.2.1] - 2026-03-02

### Fixed
- `AttributeError: 'list' object has no attribute 'items'` crash on startup
  - Fronius API changed daily data format from dict to list
  - All sensors now handle both dict and list formats transparently
  - Added `AttributeError` to exception handlers so sensors register even on unexpected formats
- Added debug logging to capture actual API response structure for future format diagnostics

## [0.2.0] - 2026-02-21

### Added
- **Pricing Configuration**: Configure electricity prices during setup
  - Grid consumption price (€/kWh)
  - Community consumption price (€/kWh)
  - Grid feed-in price (€/kWh)
  - Community feed-in price (€/kWh)
- **Options Flow**: Change pricing configuration after installation via integration options
- **Cost Sensors**: Three new sensor types per counter point
  - **Daily Cost Sensor**: Shows daily net costs with detailed breakdown
    - Attributes: `daily_costs`, `daily_costs_breakdown`, `last_30_days_costs`
  - **Monthly Cost Sensor**: Aggregates costs per month
    - Attributes: `monthly_costs`, `monthly_costs_breakdown`
  - **Yearly Cost Sensor**: Aggregates costs per year
    - Attributes: `yearly_costs`, `yearly_cost_breakdown`
- **Cost Calculations**: Automatic calculation of net costs (consumption - feed-in revenue)
- **Dashboard Examples**: New cost visualization dashboards
  - `dashboard_costs_monthly.yaml`: Monthly cost overview with grid/community breakdown
  - `dashboard_costs_daily_detail.yaml`: Daily cost details for last 30 days
  - `dashboard_costs_monthly_selector.yaml`: Monthly statistics with comparison
- **HACS Logo**: Added logo.png to fix "image not found" in HACS

### Changed
- Config flow now includes pricing step during initial setup
- Pricing is stored in entry.options (with fallback to entry.data for backwards compatibility)
- Integration reloads automatically when pricing is changed via options

### Technical Details
- Cost sensors use `SensorDeviceClass.MONETARY` with Euro currency
- Pricing defaults: Grid €0.35, Community €0.25 (consumption); Grid €0.12, Community €0.18 (feed-in)
- All cost values are rounded to 2 decimal places
- Monthly/yearly costs use `SensorStateClass.TOTAL`, daily costs use `None`
- Update listener registered to reload integration when options change

### Migration Notes
- Existing users upgrading from v0.1.0 will use default pricing values
- Users should configure their actual prices via integration options after upgrade
- All existing sensors continue to work without changes
- Cost sensors appear automatically after pricing is configured

## [0.1.0] - 2026-02-20

### Added
- Initial release of Fronius Energiegemeinschaft integration
- Login and authentication with Fronius portal using Laravel CSRF tokens
- Community sensors tracking total energy consumption and production
- Counter point sensors for personal metering points (consumer/producer)
- Daily data attributes for all sensors (last 30 days)
  - `daily_data_crec`: Community consumption per day
  - `daily_data_cgrid`: Grid consumption per day
  - `daily_data_ctotal`: Total consumption per day
  - `daily_data_frec`: Community feed-in per day
  - `daily_data_fgrid`: Grid feed-in per day
  - `daily_data_ftotal`: Total feed-in per day
- `last_30_days_*` list attributes for easy access to recent data
- Config flow for easy UI-based setup
- Automatic session management with re-authentication on expiry
- Installation script (`install.sh`) for easy deployment
- Dashboard examples:
  - Basic cards with absolute values
  - Advanced cards with percentage visualization
- German translations

### Fixed
- CSRF token handling (use cookie value, not separate API call)
- Login endpoint (use `/backend/login` not `/backend/api/auth/login`)
- Counter point data extraction (handle nested rc_number structure)
- Session cleanup to prevent "Unclosed client session" warnings

### Technical Details
- Update interval: 5 minutes
- Data delay: ~2 days (due to smart meter transmission)
- Supports multiple communities and counter points
- Compatible with Home Assistant 2023.1.0+

[0.2.0]: https://github.com/lethyro85/fronius-energiegemeinde-homeassistant/releases/tag/v0.2.0
[0.1.0]: https://github.com/lethyro85/fronius-energiegemeinde-homeassistant/releases/tag/v0.1.0
