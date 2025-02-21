"""The Bus Line Tracker integration."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bus Line Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    update_interval = entry.options.get(
        "update_interval", DEFAULT_UPDATE_INTERVAL
    )

    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=entry,
        update_interval=timedelta(seconds=update_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class BusLineDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching bus data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.config_entry = config_entry

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # TODO: Implement actual data fetching from SIRI API
            return {}
        except Exception as error:
            _LOGGER.error("Error fetching bus_line_tracker data: %s", error)
            raise UpdateFailed(str(error)) 