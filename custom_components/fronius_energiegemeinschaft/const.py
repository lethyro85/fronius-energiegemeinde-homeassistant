"""Constants for the Fronius Energiegemeinschaft integration."""

DOMAIN = "fronius_energiegemeinschaft"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Pricing configuration keys
CONF_PRICE_GRID_CONSUMPTION = "price_grid_consumption"
CONF_PRICE_COMMUNITY_CONSUMPTION = "price_community_consumption"
CONF_PRICE_GRID_FEED_IN = "price_grid_feed_in"
CONF_PRICE_COMMUNITY_FEED_IN = "price_community_feed_in"

# Default prices (€/kWh)
DEFAULT_PRICE_GRID_CONSUMPTION = 0.35
DEFAULT_PRICE_COMMUNITY_CONSUMPTION = 0.25
DEFAULT_PRICE_GRID_FEED_IN = 0.12
DEFAULT_PRICE_COMMUNITY_FEED_IN = 0.18

# API endpoints
BASE_URL = "https://energiegemeinschaften.fronius.at"
API_LOGIN = "/backend/login"
API_CSRF = "/backend/api/csrf-token"
API_COMMUNITY = "/vis/community"
API_COMMUNITY_ENERGY = "/vis/community/{community_id}/energy_data"
API_COUNTER_POINT = "/vis/counter_point"
API_COUNTER_POINT_ENERGY = "/vis/counter_point/{counter_point_id}/energy_data"

# Update interval
UPDATE_INTERVAL = 300  # 5 minutes

# Data keys
DATA_COORDINATOR = "coordinator"
DATA_CLIENT = "client"
DATA_PRICING = "pricing"
