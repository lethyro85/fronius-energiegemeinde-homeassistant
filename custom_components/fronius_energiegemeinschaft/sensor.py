"""Sensor platform for Fronius Energiegemeinschaft."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy

# Try to import CURRENCY_EURO, fallback to string for older HA versions
try:
    from homeassistant.const import CURRENCY_EURO
except ImportError:
    CURRENCY_EURO = "€"
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DATA_COORDINATOR, DATA_PRICING, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    pricing = hass.data[DOMAIN][config_entry.entry_id][DATA_PRICING]

    entities: list[SensorEntity] = []

    # Create sensors for each community
    if coordinator.data and "communities" in coordinator.data:
        for community_id, community_data in coordinator.data["communities"].items():
            community_info = community_data["info"]
            community_name = community_info["name"]
            rc_number = community_info.get("rc_number", "")

            # Total values from energy data
            energy_data = community_data.get("energy", {})
            total_data = energy_data.get("total", {}).get(rc_number, {})

            # Create sensors for community totals
            entities.extend([
                FroniusCommunitySensor(
                    coordinator,
                    community_id,
                    community_name,
                    rc_number,
                    "crec",
                    "Community Received",
                    total_data.get("crec", {}).get("value", "0"),
                ),
                FroniusCommunitySensor(
                    coordinator,
                    community_id,
                    community_name,
                    rc_number,
                    "cgrid",
                    "Grid Consumption",
                    total_data.get("cgrid", {}).get("value", "0"),
                ),
                FroniusCommunitySensor(
                    coordinator,
                    community_id,
                    community_name,
                    rc_number,
                    "ctotal",
                    "Total Consumption",
                    total_data.get("ctotal", {}).get("value", "0"),
                ),
                FroniusCommunitySensor(
                    coordinator,
                    community_id,
                    community_name,
                    rc_number,
                    "frec",
                    "Community Feed-in",
                    total_data.get("frec", {}).get("value", "0"),
                ),
                FroniusCommunitySensor(
                    coordinator,
                    community_id,
                    community_name,
                    rc_number,
                    "fgrid",
                    "Grid Feed-in",
                    total_data.get("fgrid", {}).get("value", "0"),
                ),
                FroniusCommunitySensor(
                    coordinator,
                    community_id,
                    community_name,
                    rc_number,
                    "ftotal",
                    "Total Feed-in",
                    total_data.get("ftotal", {}).get("value", "0"),
                ),
            ])

    # Create sensors for each counter point
    if coordinator.data and "counter_points" in coordinator.data:
        for cp_id, cp_data in coordinator.data["counter_points"].items():
            cp_info = cp_data["info"]
            cp_number = cp_info.get("counter_number", str(cp_id))
            energy_direction = "Producer" if cp_info.get("energy_direction") == "1" else "Consumer"

            # Energy sensor
            entities.append(
                FroniusCounterPointSensor(
                    coordinator,
                    cp_id,
                    cp_number,
                    energy_direction,
                    cp_data.get("energy", {}),
                )
            )

            # Cost sensors
            entities.extend([
                DailyCostSensor(coordinator, cp_id, cp_number, energy_direction, pricing),
                MonthlyCostSensor(coordinator, cp_id, cp_number, energy_direction, pricing),
                YearlyCostSensor(coordinator, cp_id, cp_number, energy_direction, pricing),
            ])

    async_add_entities(entities)


class FroniusCommunitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Fronius Community Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        community_id: int,
        community_name: str,
        rc_number: str,
        data_key: str,
        sensor_name: str,
        initial_value: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._community_id = community_id
        self._community_name = community_name
        self._rc_number = rc_number
        self._data_key = data_key
        self._sensor_name = sensor_name
        self._attr_name = f"{community_name} {sensor_name}"
        self._attr_unique_id = f"fronius_community_{community_id}_{data_key}"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        try:
            community_data = self.coordinator.data["communities"].get(self._community_id, {})
            total_data = community_data.get("energy", {}).get("total", {}).get(self._rc_number, {})
            value_str = total_data.get(self._data_key, {}).get("value", "0")
            return float(value_str)
        except (KeyError, ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        try:
            community_data = self.coordinator.data["communities"].get(self._community_id, {})
            energy_data = community_data.get("energy", {})
            total_data = energy_data.get("total", {}).get(self._rc_number, {})

            data_point = total_data.get(self._data_key, {})

            # Get daily data from the energy_data
            daily_data = {}
            raw_data = energy_data.get("data", {}).get(self._rc_number, {})
            for date_str, values in raw_data.items():
                if self._data_key in values:
                    # Extract just the date part (YYYY-MM-DD)
                    date_only = date_str.split("T")[0]
                    value = values[self._data_key].get("value", "0")
                    try:
                        daily_data[date_only] = float(value)
                    except (ValueError, TypeError):
                        pass

            return {
                "community_id": self._community_id,
                "community_name": self._community_name,
                "rc_number": self._rc_number,
                "value_type": data_point.get("value_type"),
                "null_values": data_point.get("null_values"),
                "unit": energy_data.get("meta", {}).get("unit", "kWh"),
                "daily_data": daily_data,
                "last_30_days": list(daily_data.values())[-30:] if daily_data else [],
            }
        except (KeyError, TypeError):
            return {}


class FroniusCounterPointSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Fronius Counter Point Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        cp_id: int,
        cp_number: str,
        energy_direction: str,
        energy_data: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._cp_id = cp_id
        self._cp_number = cp_number
        self._energy_direction = energy_direction
        self._attr_name = f"Counter Point {cp_number} ({energy_direction})"
        self._attr_unique_id = f"fronius_counter_point_{cp_id}"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        try:
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            energy_data = cp_data.get("energy", {})
            total_data = energy_data.get("total", {}).get("total", {})

            # For producers, use ftotal, for consumers use ctotal
            if self._energy_direction == "Producer":
                value_str = total_data.get("ftotal", "0")
            else:
                value_str = total_data.get("ctotal", "0")

            return float(value_str)
        except (KeyError, ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        try:
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            cp_info = cp_data.get("info", {})
            energy_data = cp_data.get("energy", {})
            total_data = energy_data.get("total", {}).get("total", {})

            # Get daily data from the energy_data
            daily_data_crec = {}
            daily_data_cgrid = {}
            daily_data_ctotal = {}
            daily_data_frec = {}
            daily_data_fgrid = {}
            daily_data_ftotal = {}

            # Counter points have data under rc_number key(s), similar to communities
            # Get the first (usually only) rc_number key
            data_dict = energy_data.get("data", {})
            if data_dict:
                # Take the first rc_number key (usually there's only one)
                rc_key = list(data_dict.keys())[0]
                raw_data = data_dict.get(rc_key, {})

                for date_str, values in raw_data.items():
                    # Extract just the date part (YYYY-MM-DD)
                    date_only = date_str.split("T")[0]

                    # Extract all data keys
                    for key, daily_dict in [
                        ("crec", daily_data_crec),
                        ("cgrid", daily_data_cgrid),
                        ("ctotal", daily_data_ctotal),
                        ("frec", daily_data_frec),
                        ("fgrid", daily_data_fgrid),
                        ("ftotal", daily_data_ftotal),
                    ]:
                        if key in values:
                            try:
                                daily_dict[date_only] = float(values[key].get("value", "0"))
                            except (ValueError, TypeError, AttributeError):
                                pass

            return {
                "counter_point_id": self._cp_id,
                "counter_number": self._cp_number,
                "counter_point_number": cp_info.get("counter_point_number"),
                "energy_direction": self._energy_direction,
                "crec": total_data.get("crec"),
                "cgrid": total_data.get("cgrid"),
                "ctotal": total_data.get("ctotal"),
                "frec": total_data.get("frec"),
                "fgrid": total_data.get("fgrid"),
                "ftotal": total_data.get("ftotal"),
                "unit": energy_data.get("meta", {}).get("unit", "kWh"),
                "daily_data_crec": daily_data_crec,
                "daily_data_cgrid": daily_data_cgrid,
                "daily_data_ctotal": daily_data_ctotal,
                "daily_data_frec": daily_data_frec,
                "daily_data_fgrid": daily_data_fgrid,
                "daily_data_ftotal": daily_data_ftotal,
                "last_30_days_crec": list(daily_data_crec.values())[-30:] if daily_data_crec else [],
                "last_30_days_cgrid": list(daily_data_cgrid.values())[-30:] if daily_data_cgrid else [],
                "last_30_days_ctotal": list(daily_data_ctotal.values())[-30:] if daily_data_ctotal else [],
                "last_30_days_frec": list(daily_data_frec.values())[-30:] if daily_data_frec else [],
                "last_30_days_fgrid": list(daily_data_fgrid.values())[-30:] if daily_data_fgrid else [],
                "last_30_days_ftotal": list(daily_data_ftotal.values())[-30:] if daily_data_ftotal else [],
            }
        except (KeyError, TypeError):
            return {}


class DailyCostSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Daily Cost Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        cp_id: int,
        cp_number: str,
        energy_direction: str,
        pricing: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._cp_id = cp_id
        self._cp_number = cp_number
        self._energy_direction = energy_direction
        self._pricing = pricing
        self._attr_name = f"Counter Point {cp_number} Daily Cost"
        self._attr_unique_id = f"fronius_counter_point_{cp_id}_daily_cost"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self._attr_state_class = None  # Daily cost is not cumulative

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor (most recent daily cost)."""
        try:
            daily_costs = self._calculate_daily_costs()
            if daily_costs:
                # Return the most recent day's cost
                return round(list(daily_costs.values())[-1], 2)
            return None
        except (KeyError, ValueError, TypeError):
            return None

    def _calculate_daily_costs(self) -> dict[str, float]:
        """Calculate daily costs from energy data."""
        try:
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            energy_data = cp_data.get("energy", {})
            data_dict = energy_data.get("data", {})

            if not data_dict:
                return {}

            # Get the first (usually only) rc_number key
            rc_key = list(data_dict.keys())[0]
            raw_data = data_dict.get(rc_key, {})

            daily_costs = {}
            for date_str, values in raw_data.items():
                date_only = date_str.split("T")[0]

                # Consumption costs
                cgrid = float(values.get("cgrid", {}).get("value", "0"))
                crec = float(values.get("crec", {}).get("value", "0"))
                consumption_cost = (
                    cgrid * self._pricing["grid_consumption"]
                    + crec * self._pricing["community_consumption"]
                )

                # Feed-in revenue (negative cost)
                fgrid = float(values.get("fgrid", {}).get("value", "0"))
                frec = float(values.get("frec", {}).get("value", "0"))
                feed_in_revenue = (
                    fgrid * self._pricing["grid_feed_in"]
                    + frec * self._pricing["community_feed_in"]
                )

                # Net cost
                net_cost = consumption_cost - feed_in_revenue
                daily_costs[date_only] = net_cost

            return daily_costs
        except (KeyError, ValueError, TypeError):
            return {}

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        try:
            daily_costs = self._calculate_daily_costs()
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            energy_data = cp_data.get("energy", {})
            data_dict = energy_data.get("data", {})

            if not data_dict:
                return {}

            rc_key = list(data_dict.keys())[0]
            raw_data = data_dict.get(rc_key, {})

            # Calculate breakdown
            daily_breakdown = {}
            for date_str, values in raw_data.items():
                date_only = date_str.split("T")[0]

                cgrid = float(values.get("cgrid", {}).get("value", "0"))
                crec = float(values.get("crec", {}).get("value", "0"))
                fgrid = float(values.get("fgrid", {}).get("value", "0"))
                frec = float(values.get("frec", {}).get("value", "0"))

                daily_breakdown[date_only] = {
                    "grid_consumption_cost": round(
                        cgrid * self._pricing["grid_consumption"], 2
                    ),
                    "community_consumption_cost": round(
                        crec * self._pricing["community_consumption"], 2
                    ),
                    "grid_feed_in_revenue": round(
                        fgrid * self._pricing["grid_feed_in"], 2
                    ),
                    "community_feed_in_revenue": round(
                        frec * self._pricing["community_feed_in"], 2
                    ),
                }

            return {
                "counter_point_id": self._cp_id,
                "counter_number": self._cp_number,
                "energy_direction": self._energy_direction,
                "pricing": self._pricing,
                "daily_costs": {k: round(v, 2) for k, v in daily_costs.items()},
                "daily_costs_breakdown": daily_breakdown,
                "last_30_days_costs": [
                    round(v, 2) for v in list(daily_costs.values())[-30:]
                ]
                if daily_costs
                else [],
            }
        except (KeyError, TypeError):
            return {}


class MonthlyCostSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Monthly Cost Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        cp_id: int,
        cp_number: str,
        energy_direction: str,
        pricing: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._cp_id = cp_id
        self._cp_number = cp_number
        self._energy_direction = energy_direction
        self._pricing = pricing
        self._attr_name = f"Counter Point {cp_number} Monthly Cost"
        self._attr_unique_id = f"fronius_counter_point_{cp_id}_monthly_cost"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor (current month cost)."""
        try:
            monthly_costs = self._calculate_monthly_costs()
            if monthly_costs:
                # Return the most recent month's cost
                return round(list(monthly_costs.values())[-1], 2)
            return None
        except (KeyError, ValueError, TypeError):
            return None

    def _calculate_monthly_costs(self) -> dict[str, float]:
        """Calculate monthly costs from energy data."""
        try:
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            energy_data = cp_data.get("energy", {})
            data_dict = energy_data.get("data", {})

            if not data_dict:
                return {}

            rc_key = list(data_dict.keys())[0]
            raw_data = data_dict.get(rc_key, {})

            monthly_totals = {}
            for date_str, values in raw_data.items():
                date_only = date_str.split("T")[0]
                month_key = date_only[:7]  # YYYY-MM

                # Consumption costs
                cgrid = float(values.get("cgrid", {}).get("value", "0"))
                crec = float(values.get("crec", {}).get("value", "0"))
                consumption_cost = (
                    cgrid * self._pricing["grid_consumption"]
                    + crec * self._pricing["community_consumption"]
                )

                # Feed-in revenue
                fgrid = float(values.get("fgrid", {}).get("value", "0"))
                frec = float(values.get("frec", {}).get("value", "0"))
                feed_in_revenue = (
                    fgrid * self._pricing["grid_feed_in"]
                    + frec * self._pricing["community_feed_in"]
                )

                net_cost = consumption_cost - feed_in_revenue

                if month_key not in monthly_totals:
                    monthly_totals[month_key] = 0
                monthly_totals[month_key] += net_cost

            return monthly_totals
        except (KeyError, ValueError, TypeError):
            return {}

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        try:
            monthly_costs = self._calculate_monthly_costs()
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            energy_data = cp_data.get("energy", {})
            data_dict = energy_data.get("data", {})

            if not data_dict:
                return {}

            rc_key = list(data_dict.keys())[0]
            raw_data = data_dict.get(rc_key, {})

            # Calculate monthly breakdown
            monthly_breakdown = {}
            for date_str, values in raw_data.items():
                date_only = date_str.split("T")[0]
                month_key = date_only[:7]

                cgrid = float(values.get("cgrid", {}).get("value", "0"))
                crec = float(values.get("crec", {}).get("value", "0"))
                fgrid = float(values.get("fgrid", {}).get("value", "0"))
                frec = float(values.get("frec", {}).get("value", "0"))

                if month_key not in monthly_breakdown:
                    monthly_breakdown[month_key] = {
                        "grid_consumption_cost": 0,
                        "community_consumption_cost": 0,
                        "grid_feed_in_revenue": 0,
                        "community_feed_in_revenue": 0,
                        "days_count": 0,
                    }

                monthly_breakdown[month_key]["grid_consumption_cost"] += (
                    cgrid * self._pricing["grid_consumption"]
                )
                monthly_breakdown[month_key]["community_consumption_cost"] += (
                    crec * self._pricing["community_consumption"]
                )
                monthly_breakdown[month_key]["grid_feed_in_revenue"] += (
                    fgrid * self._pricing["grid_feed_in"]
                )
                monthly_breakdown[month_key]["community_feed_in_revenue"] += (
                    frec * self._pricing["community_feed_in"]
                )
                monthly_breakdown[month_key]["days_count"] += 1

            # Round all values
            for month in monthly_breakdown:
                for key in monthly_breakdown[month]:
                    if key != "days_count":
                        monthly_breakdown[month][key] = round(
                            monthly_breakdown[month][key], 2
                        )

            return {
                "counter_point_id": self._cp_id,
                "counter_number": self._cp_number,
                "energy_direction": self._energy_direction,
                "pricing": self._pricing,
                "monthly_costs": {k: round(v, 2) for k, v in monthly_costs.items()},
                "monthly_costs_breakdown": monthly_breakdown,
            }
        except (KeyError, TypeError):
            return {}


class YearlyCostSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Yearly Cost Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        cp_id: int,
        cp_number: str,
        energy_direction: str,
        pricing: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._cp_id = cp_id
        self._cp_number = cp_number
        self._energy_direction = energy_direction
        self._pricing = pricing
        self._attr_name = f"Counter Point {cp_number} Yearly Cost"
        self._attr_unique_id = f"fronius_counter_point_{cp_id}_yearly_cost"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor (current year cost)."""
        try:
            yearly_costs = self._calculate_yearly_costs()
            if yearly_costs:
                # Return the most recent year's cost
                return round(list(yearly_costs.values())[-1], 2)
            return None
        except (KeyError, ValueError, TypeError):
            return None

    def _calculate_yearly_costs(self) -> dict[str, float]:
        """Calculate yearly costs from energy data."""
        try:
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            energy_data = cp_data.get("energy", {})
            data_dict = energy_data.get("data", {})

            if not data_dict:
                return {}

            rc_key = list(data_dict.keys())[0]
            raw_data = data_dict.get(rc_key, {})

            yearly_totals = {}
            for date_str, values in raw_data.items():
                date_only = date_str.split("T")[0]
                year_key = date_only[:4]  # YYYY

                # Consumption costs
                cgrid = float(values.get("cgrid", {}).get("value", "0"))
                crec = float(values.get("crec", {}).get("value", "0"))
                consumption_cost = (
                    cgrid * self._pricing["grid_consumption"]
                    + crec * self._pricing["community_consumption"]
                )

                # Feed-in revenue
                fgrid = float(values.get("fgrid", {}).get("value", "0"))
                frec = float(values.get("frec", {}).get("value", "0"))
                feed_in_revenue = (
                    fgrid * self._pricing["grid_feed_in"]
                    + frec * self._pricing["community_feed_in"]
                )

                net_cost = consumption_cost - feed_in_revenue

                if year_key not in yearly_totals:
                    yearly_totals[year_key] = 0
                yearly_totals[year_key] += net_cost

            return yearly_totals
        except (KeyError, ValueError, TypeError):
            return {}

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        try:
            yearly_costs = self._calculate_yearly_costs()
            cp_data = self.coordinator.data["counter_points"].get(self._cp_id, {})
            energy_data = cp_data.get("energy", {})
            data_dict = energy_data.get("data", {})

            if not data_dict:
                return {}

            rc_key = list(data_dict.keys())[0]
            raw_data = data_dict.get(rc_key, {})

            # Calculate yearly breakdown
            yearly_breakdown = {}
            for date_str, values in raw_data.items():
                date_only = date_str.split("T")[0]
                year_key = date_only[:4]

                cgrid = float(values.get("cgrid", {}).get("value", "0"))
                crec = float(values.get("crec", {}).get("value", "0"))
                fgrid = float(values.get("fgrid", {}).get("value", "0"))
                frec = float(values.get("frec", {}).get("value", "0"))

                if year_key not in yearly_breakdown:
                    yearly_breakdown[year_key] = {
                        "grid_consumption_cost": 0,
                        "community_consumption_cost": 0,
                        "grid_feed_in_revenue": 0,
                        "community_feed_in_revenue": 0,
                    }

                yearly_breakdown[year_key]["grid_consumption_cost"] += (
                    cgrid * self._pricing["grid_consumption"]
                )
                yearly_breakdown[year_key]["community_consumption_cost"] += (
                    crec * self._pricing["community_consumption"]
                )
                yearly_breakdown[year_key]["grid_feed_in_revenue"] += (
                    fgrid * self._pricing["grid_feed_in"]
                )
                yearly_breakdown[year_key]["community_feed_in_revenue"] += (
                    frec * self._pricing["community_feed_in"]
                )

            # Round all values
            for year in yearly_breakdown:
                for key in yearly_breakdown[year]:
                    yearly_breakdown[year][key] = round(yearly_breakdown[year][key], 2)

            return {
                "counter_point_id": self._cp_id,
                "counter_number": self._cp_number,
                "energy_direction": self._energy_direction,
                "pricing": self._pricing,
                "yearly_costs": {k: round(v, 2) for k, v in yearly_costs.items()},
                "yearly_cost_breakdown": yearly_breakdown,
            }
        except (KeyError, TypeError):
            return {}
