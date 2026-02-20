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
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DATA_COORDINATOR, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

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

            entities.append(
                FroniusCounterPointSensor(
                    coordinator,
                    cp_id,
                    cp_number,
                    energy_direction,
                    cp_data.get("energy", {}),
                )
            )

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

            # Counter points have data directly under "data", not under "data.total"
            raw_data = energy_data.get("data", {})
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
                            daily_dict[date_only] = float(values[key])
                        except (ValueError, TypeError):
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
