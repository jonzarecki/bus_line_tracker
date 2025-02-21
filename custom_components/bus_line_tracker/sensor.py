"""Support for Bus Line Tracker sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    ATTR_LOCATION,
    ATTR_SPEED,
    ATTR_BEARING,
    ATTR_DISTANCE_FROM_START,
    ATTR_DISTANCE_FROM_STATION,
    ATTR_VEHICLE_REF,
    ATTR_LAST_UPDATE,
    SPEED_UNITS,
    DISTANCE_UNITS,
    BEARING_UNITS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Bus Line Tracker sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        BusLocationSensor(coordinator, config_entry),
        BusSpeedSensor(coordinator, config_entry),
        BusBearingSensor(coordinator, config_entry),
        BusDistanceFromStartSensor(coordinator, config_entry),
        BusDistanceFromStationSensor(coordinator, config_entry),
    ]

    async_add_entities(sensors, True)


class BusLineSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for bus line sensors."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self.entity_description = SensorEntityDescription(
            key=self._attr_name.lower().replace(" ", "_"),
            name=self._attr_name,
            native_unit_of_measurement=self._attr_native_unit_of_measurement,
            device_class=self._attr_device_class,
            state_class=self._attr_state_class,
        )
        self._attr_unique_id = f"{config_entry.entry_id}_{self.entity_description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"Bus Line {config_entry.data.get('route_mkt', '')}",
            "manufacturer": "Israeli Ministry of Transport",
            "model": "SIRI API Bus Tracker",
            "sw_version": "1.0.0",
        }


class BusLocationSensor(BusLineSensorBase):
    """Sensor for bus location."""

    _attr_name = "Bus Location"
    _attr_native_unit_of_measurement = None
    _attr_device_class = None
    _attr_state_class = None

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(ATTR_LOCATION)
        return None


class BusSpeedSensor(BusLineSensorBase):
    """Sensor for bus speed."""

    _attr_name = "Bus Speed"
    _attr_native_unit_of_measurement = SPEED_UNITS
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(ATTR_SPEED)
        return None


class BusBearingSensor(BusLineSensorBase):
    """Sensor for bus bearing."""

    _attr_name = "Bus Bearing"
    _attr_native_unit_of_measurement = BEARING_UNITS
    _attr_device_class = None
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(ATTR_BEARING)
        return None


class BusDistanceFromStartSensor(BusLineSensorBase):
    """Sensor for distance from journey start."""

    _attr_name = "Distance from Start"
    _attr_native_unit_of_measurement = DISTANCE_UNITS
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(ATTR_DISTANCE_FROM_START)
        return None


class BusDistanceFromStationSensor(BusLineSensorBase):
    """Sensor for distance from configured station."""

    _attr_name = "Distance from Station"
    _attr_native_unit_of_measurement = DISTANCE_UNITS
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(ATTR_DISTANCE_FROM_STATION)
        return None 