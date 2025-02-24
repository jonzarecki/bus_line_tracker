"""The Bus Line Tracker integration."""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from israel_bus_locator.bus_utils import (
    get_routes_for_route_mkt,
    get_vehicle_locations,
    split_by_ride_id,
)

from .const import (
    CONF_DIRECTION,
    CONF_FILTER_NAME,
    CONF_LAT,
    CONF_LON,
    CONF_ROUTE_MKT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bus Line Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    update_interval = entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL)

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
        self._route_mkt = config_entry.data[CONF_ROUTE_MKT]
        self._filter_name = config_entry.data.get(CONF_FILTER_NAME)
        self._direction = config_entry.data.get(CONF_DIRECTION)
        self._ref_point = None

        # Set up reference point if lat/lon are provided
        lat = config_entry.data.get(CONF_LAT)
        lon = config_entry.data.get(CONF_LON)
        if lat is not None and lon is not None:
            self._ref_point = (lat, lon)

    async def _async_update_data(self):
        """Update data via library."""
        # Get current date in Israel timezone
        now = datetime.now(ZoneInfo("Israel"))
        _LOGGER.debug(f"ref point: {self._ref_point}")

        # Get routes information
        try:
            date_str = now.strftime("%Y-%m-%d")
            routes_df = await self.hass.async_add_executor_job(
                get_routes_for_route_mkt,
                self._route_mkt,
                date_str,
                date_str,
                self._filter_name,
                self._direction,
            )
        except KeyError as e:
            _LOGGER.warning(
                "Failed to get routes with parameters: route_mkt=%s, date=%s, filter_name=%s, direction=%s",
                self._route_mkt,
                date_str,
                self._filter_name,
                self._direction,
            )
            _LOGGER.error(f"KeyError: {e}", exc_info=True)
            routes_df = pd.DataFrame()

        if routes_df.empty:
            _LOGGER.warning("No routes found for the given criteria")
            return {}

        _LOGGER.debug(f"routes_df:\n{routes_df}")

        # Check if we have line_ref column
        if "line_ref" not in routes_df.columns:
            _LOGGER.error("Required column 'line_ref' not found in routes data")
            return {}

        # Get vehicle locations for the last hour
        end_time = now.replace(second=0, microsecond=0)
        start_time = end_time - timedelta(minutes=30)

        vehicle_locations = pd.DataFrame()

        # Iterate through all line_refs
        for line_ref in routes_df["line_ref"]:
            try:
                line_locations = await self.hass.async_add_executor_job(
                    get_vehicle_locations,
                    line_ref,
                    start_time,
                    end_time,
                )
                # Append locations for this line to main dataframe
                vehicle_locations = pd.concat([vehicle_locations, line_locations])

            except KeyError as e:
                _LOGGER.debug(
                    "Failed to get vehicle locations with parameters: line_ref=%s, start_time=%s, end_time=%s",
                    line_ref,
                    start_time,
                    end_time,
                )
                _LOGGER.debug(f"KeyError: {e}", exc_info=True)
                continue

        if vehicle_locations.empty:
            _LOGGER.debug("No vehicle locations found")
            return {}

        # Log unique rides found
        unique_rides = vehicle_locations["siri_ride__id"].unique()
        _LOGGER.debug(f"Unique rides: {unique_rides}, shape: {vehicle_locations.shape}")
        # _LOGGER.debug(f"Vehicle locations:\n{vehicle_locations}")

        # Get the latest point for the ride closest to the journey start
        split_rides = split_by_ride_id(vehicle_locations)
        closest_ride = min(split_rides, key=lambda ride: ride["distance_from_journey_start"].iloc[0])
        
        latest_location = await self.hass.async_add_executor_job(lambda: closest_ride.iloc[0])
        _LOGGER.debug(f"Latest location: {latest_location}")

        return {
            "location": f"{latest_location['lat']:.4f},{latest_location['lon']:.4f}",
            "speed": latest_location.get("velocity", 0),
            "bearing": latest_location.get("bearing", 0),
            "distance_from_start": latest_location.get("distance_from_journey_start", 0),
            "distance_from_station": None
            if self._ref_point is None
            else (
                (latest_location["lat"] - self._ref_point[0]) ** 2 + (latest_location["lon"] - self._ref_point[1]) ** 2
            )
            ** 0.5,
            "vehicle_ref": latest_location["siri_ride__vehicle_ref"],
            "last_update": latest_location["recorded_at_time"],
        }
