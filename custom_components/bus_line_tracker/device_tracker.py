"""Support for Bus Line Tracker device trackers."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, 
    ATTR_LOCATION, 
    ATTR_VEHICLE_REF, 
    ATTR_SPEED, 
    ATTR_BEARING, 
    ATTR_DISTANCE_FROM_START, 
    ATTR_DISTANCE_FROM_STATION,
    ATTR_LAST_UPDATE,
    SPEED_UNITS,
    DISTANCE_UNITS,
    BEARING_UNITS
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bus Line Tracker device tracker from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    trackers = [
        BusPositionTracker(coordinator, config_entry),
    ]

    async_add_entities(trackers, True)


class BusPositionTracker(CoordinatorEntity, TrackerEntity):
    """Bus position tracker."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry):
        """Initialize the tracker."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        route_mkt = config_entry.data.get("route_mkt", "")
        self._attr_name = f"Bus {route_mkt} Position"
        self._attr_unique_id = f"{config_entry.entry_id}_bus_position"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"Bus Line {route_mkt}",
            "manufacturer": "Israeli Ministry of Transport",
            "model": "SIRI API Bus Tracker",
        }
        self._attr_icon = "mdi:bus"

    @property
    def source_type(self) -> SourceType:
        """Return the source type of the device."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        if not self.coordinator.data or ATTR_LOCATION not in self.coordinator.data:
            return None
        
        try:
            location = self.coordinator.data.get(ATTR_LOCATION, "")
            if location and "," in location:
                lat_str, _ = location.split(",", 1)
                return float(lat_str)
        except (ValueError, TypeError):
            return None
        
        return None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        if not self.coordinator.data or ATTR_LOCATION not in self.coordinator.data:
            return None
        
        try:
            location = self.coordinator.data.get(ATTR_LOCATION, "")
            if location and "," in location:
                _, lon_str = location.split(",", 1)
                return float(lon_str)
        except (ValueError, TypeError):
            return None
        
        return None
    
    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        if not self.coordinator.data:
            return {}
        
        # Format attributes for better display
        speed = self.coordinator.data.get(ATTR_SPEED)
        bearing = self.coordinator.data.get(ATTR_BEARING)
        dist_start = self.coordinator.data.get(ATTR_DISTANCE_FROM_START)
        dist_station = self.coordinator.data.get(ATTR_DISTANCE_FROM_STATION)
        vehicle_ref = self.coordinator.data.get(ATTR_VEHICLE_REF)
        last_update = self.coordinator.data.get(ATTR_LAST_UPDATE)
        
        return {
            "friendly_name": f"Bus {self._config_entry.data.get('route_mkt', '')}",
            "vehicle_ref": vehicle_ref,
            "speed": f"{speed} {SPEED_UNITS}" if speed is not None else None,
            "bearing": f"{bearing} {BEARING_UNITS}" if bearing is not None else None,
            "distance_from_start": f"{dist_start} {DISTANCE_UNITS}" if dist_start is not None else None,
            "distance_from_station": f"{dist_station} {DISTANCE_UNITS}" if dist_station is not None else None,
            "last_update": last_update,
        }

    @property
    def entity_picture(self) -> str | None:
        """Return the entity picture to use in the frontend."""
        return "local/bus_icon.png" if self.hass.config.path("www/bus_icon.png") else None 