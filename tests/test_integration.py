"""Integration tests for Bus Line Tracker."""
from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bus_line_tracker import (
    BusLineDataCoordinator,
    DOMAIN,
)
from custom_components.bus_line_tracker.const import (
    CONF_DIRECTION,
    CONF_FILTER_NAME,
    CONF_LAT,
    CONF_LON,
    CONF_ROUTE_MKT,
    CONF_UPDATE_INTERVAL,
)

pytestmark = pytest.mark.integration

# Mock data for tests
MOCK_BUS_DATA = {
    "location": "32.0865,34.7876",
    "speed": 35.5,
    "bearing": 180,
    "distance_from_start": 1500,
    "distance_from_station": 500,
    "vehicle_ref": "12345",
    "last_update": datetime.now(ZoneInfo("Israel")),
}

MOCK_EMPTY_DATA = {}


@freeze_time("2024-03-20 10:00:00", tz_offset=2)  # 10 AM Israel time, when buses are running
async def test_real_bus_data_with_reference_point(hass: HomeAssistant):
    """Test fetching real bus data with a reference point."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_ROUTE_MKT: "23056",  # Line 56 in Tel Aviv
            CONF_FILTER_NAME: "רדינג",  # Reading terminal
            CONF_DIRECTION: "1",  # To Reading
            CONF_LAT: 32.090260,  # Reading station coordinates
            CONF_LON: 34.782621,
        },
        options={CONF_UPDATE_INTERVAL: 30},
    )

    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=timedelta(seconds=30),
    )

    with patch.object(coordinator, "_async_update_data", return_value=MOCK_BUS_DATA):
        await coordinator.async_refresh()

        # Verify we got data
        assert coordinator.data is not None
        assert isinstance(coordinator.data, dict)
        assert "location" in coordinator.data
        assert "speed" in coordinator.data
        assert "bearing" in coordinator.data
        assert "distance_from_start" in coordinator.data
        assert "distance_from_station" in coordinator.data
        assert "last_update" in coordinator.data


@freeze_time("2024-03-20 10:00:00", tz_offset=2)  # 10 AM Israel time, when buses are running
async def test_real_bus_data_without_reference_point(hass: HomeAssistant):
    """Test fetching real bus data without a reference point."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_ROUTE_MKT: "23056",  # Line 56 in Tel Aviv
            CONF_FILTER_NAME: "רדינג",  # Reading terminal
            CONF_DIRECTION: "1",  # To Reading
        },
        options={CONF_UPDATE_INTERVAL: 30},
    )

    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=timedelta(seconds=30),
    )

    with patch.object(coordinator, "_async_update_data", return_value=MOCK_BUS_DATA):
        await coordinator.async_refresh()

        # Verify we got data
        assert coordinator.data is not None
        assert isinstance(coordinator.data, dict)
        assert "location" in coordinator.data
        assert "speed" in coordinator.data
        assert "bearing" in coordinator.data
        assert "distance_from_start" in coordinator.data
        assert "last_update" in coordinator.data


@freeze_time("2024-03-20 03:00:00", tz_offset=2)  # 3 AM Israel time, when buses don't run
async def test_real_bus_data_no_buses_running(hass: HomeAssistant):
    """Test behavior when no buses are running on the route."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_ROUTE_MKT: "23056",
            CONF_FILTER_NAME: "רדינג",
            CONF_DIRECTION: "1",
            CONF_LAT: 32.090260,
            CONF_LON: 34.782621,
        },
        options={CONF_UPDATE_INTERVAL: 30},
    )

    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=timedelta(seconds=30),
    )

    with patch.object(coordinator, "_async_update_data", return_value=MOCK_EMPTY_DATA):
        await coordinator.async_refresh()

        # Should return empty data but not fail
        assert coordinator.data == {} 