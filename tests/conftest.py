"""Test fixtures."""

from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import (
    MockModule,
    MockPlatform,
    mock_integration,
    mock_platform,
)

from custom_components.bus_line_tracker.config_flow import BusLineTrackerConfigFlow
from custom_components.bus_line_tracker.const import DOMAIN


async def async_mock_coro(*args, **kwargs):
    """Create a mock coroutine function."""
    return True


@pytest.fixture(autouse=True)
async def auto_enable_custom_integrations(hass):
    """Enable custom integrations for testing."""
    with patch("homeassistant.loader.async_get_custom_components", return_value={DOMAIN: None}):
        mock_platform(hass, f"{DOMAIN}.config_flow", MockPlatform())
        mock_module = MockModule(DOMAIN)
        mock_module.CONFIG_FLOW = BusLineTrackerConfigFlow
        mock_module.async_setup = MagicMock(side_effect=async_mock_coro)
        mock_module.async_setup_entry = MagicMock(side_effect=async_mock_coro)
        mock_module.async_unload_entry = MagicMock(side_effect=async_mock_coro)
        mock_module.async_remove_entry = MagicMock(side_effect=async_mock_coro)
        mock_module.async_migrate_entry = MagicMock(side_effect=async_mock_coro)
        mock_integration(hass, mock_module)
        await hass.async_block_till_done()
        yield


@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    return MagicMock(side_effect=async_mock_coro)


@pytest.fixture
def mock_get_config_entry():
    """Get a mock config entry."""
    return MagicMock()


@pytest.fixture
def mock_bus_data():
    """Get mock bus data."""
    return {
        "ATTR_LOCATION": (32.0853, 34.7818),
        "ATTR_SPEED": 35.0,
        "ATTR_BEARING": 180.0,
        "ATTR_DISTANCE_FROM_START": 5.0,
        "ATTR_DISTANCE_FROM_STATION": 0.5,
    }