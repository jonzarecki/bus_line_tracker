"""Fixtures for Bus Line Tracker tests."""
import pytest
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.bus_line_tracker.const import (
    ATTR_LOCATION,
    ATTR_SPEED,
    ATTR_BEARING,
    ATTR_DISTANCE_FROM_START,
    ATTR_DISTANCE_FROM_STATION,
)


@pytest.fixture
def mock_setup_entry() -> None:
    """Mock setting up a config entry."""
    return


@pytest.fixture
def mock_get_config_entry():
    """Return a mocked config entry."""
    return MagicMock()


@pytest.fixture
def mock_bus_data():
    """Return mock bus data."""
    return {
        ATTR_LOCATION: "32.0865,34.7876",
        ATTR_SPEED: 35.5,
        ATTR_BEARING: 180,
        ATTR_DISTANCE_FROM_START: 1500,
        ATTR_DISTANCE_FROM_STATION: 500,
    } 