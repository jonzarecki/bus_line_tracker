"""Test the Bus Line Tracker coordinator."""

from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.bus_line_tracker import (
    BusLineDataCoordinator,
    async_setup_entry,
    haversine_distance,
)
from custom_components.bus_line_tracker.const import (
    CONF_ROUTE_MKT,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
)

from .test_config_flow import MockConfigEntry


def test_haversine_distance():
    """Test the haversine distance calculation function."""
    # Test case 1: Same point should return 0
    assert haversine_distance(32.0, 34.0, 32.0, 34.0) == pytest.approx(0, abs=0.1)
    
    # Test case 2: Known distance between two points
    # Tel Aviv (32.0853, 34.7818) to Jerusalem (31.7683, 35.2137) is about 54.4 km
    distance = haversine_distance(32.0853, 34.7818, 31.7683, 35.2137)
    assert distance == pytest.approx(54400, rel=0.05)  # Within 5% of expected value
    
    # Test case 3: Short distance
    # Two points 1km apart
    lat1, lon1 = 32.0853, 34.7818
    lat2, lon2 = 32.0943, 34.7818  # Approximately 1km north
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    assert distance == pytest.approx(1000, rel=0.1)  # Within 10% of expected value


async def test_coordinator_update_success(hass: HomeAssistant):
    """Test successful data update."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ROUTE_MKT: "23056"},
        options={CONF_UPDATE_INTERVAL: 30},
    )

    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=timedelta(seconds=30),
    )

    # Mock successful data update
    mock_data = {
        "location": "32.0865,34.7876",
        "speed": 35.5,
        "bearing": 180,
        "distance_from_start": 1500,
        "distance_from_station": 500,
        "vehicle_ref": "12345",
        "last_update": datetime.now(ZoneInfo("Israel")),
    }

    with patch.object(coordinator, "_async_update_data", return_value=mock_data):
        await coordinator.async_refresh()
        assert coordinator.data == mock_data


async def test_coordinator_update_failure(hass: HomeAssistant):
    """Test failed data update."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ROUTE_MKT: "23056"},
        options={CONF_UPDATE_INTERVAL: 30},
    )

    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=timedelta(seconds=30),
    )

    # Mock failed data update
    error = UpdateFailed("API Error")
    with patch.object(coordinator, "_async_update_data", side_effect=error):
        await coordinator.async_refresh()
        assert coordinator.last_update_success is False
        assert coordinator.data is None
        assert coordinator.last_exception == error


async def test_coordinator_setup(hass: HomeAssistant):
    """Test coordinator setup."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ROUTE_MKT: "23056"},
        options={CONF_UPDATE_INTERVAL: 30},
    )
    config_entry.add_to_hass(hass)

    # Test successful setup
    with patch(
        "custom_components.bus_line_tracker.BusLineDataCoordinator._async_update_data",
        return_value={},
    ):
        assert await async_setup_entry(hass, config_entry)
        assert config_entry.entry_id in hass.data[DOMAIN]

    # Test failed setup
    config_entry2 = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test2",
        data={CONF_ROUTE_MKT: "23056"},
        options={CONF_UPDATE_INTERVAL: 30},
    )
    config_entry2.add_to_hass(hass)

    with patch(
        "custom_components.bus_line_tracker.BusLineDataCoordinator._async_update_data",
        side_effect=Exception("API Error"),
    ):
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, config_entry2)


async def test_update_interval_change(hass: HomeAssistant):
    """Test update interval changes."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ROUTE_MKT: "23056"},
        options={CONF_UPDATE_INTERVAL: 30},
    )

    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=timedelta(seconds=30),
    )

    assert coordinator.update_interval == timedelta(seconds=30)

    # Change update interval
    config_entry.options = {CONF_UPDATE_INTERVAL: 60}
    coordinator = BusLineDataCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=timedelta(seconds=60),
    )

    assert coordinator.update_interval == timedelta(seconds=60)
