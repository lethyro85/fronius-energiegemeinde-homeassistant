"""Constants for the Fronius Energiegemeinschaft integration."""

DOMAIN = "fronius_energiegemeinschaft"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

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
