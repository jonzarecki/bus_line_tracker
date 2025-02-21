"""Fixtures for Bus Line Tracker tests."""
import pytest
from unittest.mock import MagicMock, patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockModule, mock_integration, MockConfigEntry

from custom_components.bus_line_tracker.const import (
    DOMAIN,
    ATTR_LOCATION,
    ATTR_SPEED,
    ATTR_BEARING,
    ATTR_DISTANCE_FROM_START,
    ATTR_DISTANCE_FROM_STATION,
)


@pytest.fixture(autouse=True)
async def auto_enable_custom_integrations(hass: HomeAssistant) -> None:
    """Enable custom integrations in Home Assistant."""
    with patch("homeassistant.loader.async_get_custom_components", return_value={DOMAIN: None}):
        mock_integration(
            hass,
            MockModule(DOMAIN),
        )


@pytest.fixture
def mock_setup_entry() -> None:
    """Mock setting up a config entry."""
    return MagicMock(return_value=True)


@pytest.fixture
def mock_get_config_entry():
    """Return a mocked config entry."""
    return MagicMock()


@pytest.fixture
def mock_bus_data():
    """Return mock bus data."""
    return {
        ATTR_LOCATION: (32.0853, 34.7818),
        ATTR_SPEED: 35.0,
        ATTR_BEARING: 180.0,
        ATTR_DISTANCE_FROM_START: 5.0,
        ATTR_DISTANCE_FROM_STATION: 0.5,
    } 