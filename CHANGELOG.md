# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
