# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/lethyro85/fronius-energiegemeinde-homeassistant/releases/tag/v0.1.0
