"""Test the Bus Line Tracker coordinator."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.bus_line_tracker import (
    BusLineDataCoordinator,
    async_setup_entry,
)
from custom_components.bus_line_tracker.const import (
    CONF_UPDATE_INTERVAL,
    DOMAIN,
)

from .test_config_flow import MockConfigEntry


async def test_coordinator_update_success(hass: HomeAssistant):
    """Test successful data update."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
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
    }

    with patch.object(coordinator, "_async_update_data", return_value=mock_data):
        await coordinator.async_refresh()
        assert coordinator.data == mock_data


async def test_coordinator_update_failure(hass: HomeAssistant):
    """Test failed data update."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
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
        data={},
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
        data={},
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
        data={},
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
