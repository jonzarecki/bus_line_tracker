"""Test the Bus Line Tracker sensors."""
from unittest.mock import patch, MagicMock
from datetime import timedelta

import pytest
from homeassistant.const import UnitOfLength, UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.bus_line_tracker.const import (
    DOMAIN,
    CONF_ROUTE_MKT,
    ATTR_LOCATION,
    ATTR_SPEED,
    ATTR_BEARING,
    ATTR_DISTANCE_FROM_START,
    ATTR_DISTANCE_FROM_STATION,
    SPEED_UNITS,
    DISTANCE_UNITS,
    BEARING_UNITS,
)
from custom_components.bus_line_tracker.sensor import (
    BusLocationSensor,
    BusSpeedSensor,
    BusBearingSensor,
    BusDistanceFromStartSensor,
    BusDistanceFromStationSensor,
)

from .test_config_flow import MockConfigEntry


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        ATTR_LOCATION: "32.0865,34.7876",
        ATTR_SPEED: 35.5,
        ATTR_BEARING: 180,
        ATTR_DISTANCE_FROM_START: 1500,
        ATTR_DISTANCE_FROM_STATION: 500,
    }
    return coordinator


async def test_sensor_creation(hass: HomeAssistant):
    """Test sensor creation."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ROUTE_MKT: "123"},
    )
    config_entry.add_to_hass(hass)

    with patch(
        "custom_components.bus_line_tracker.BusLineDataCoordinator"
    ) as mock_coordinator_class:
        mock_coordinator = mock_coordinator_class.return_value
        mock_coordinator.data = {}

        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        # Verify all sensors are created
        state = hass.states.get("sensor.bus_line_123_location")
        assert state is not None

        state = hass.states.get("sensor.bus_line_123_speed")
        assert state is not None
        assert state.attributes["unit_of_measurement"] == SPEED_UNITS

        state = hass.states.get("sensor.bus_line_123_bearing")
        assert state is not None
        assert state.attributes["unit_of_measurement"] == BEARING_UNITS

        state = hass.states.get("sensor.bus_line_123_distance_from_start")
        assert state is not None
        assert state.attributes["unit_of_measurement"] == DISTANCE_UNITS

        state = hass.states.get("sensor.bus_line_123_distance_from_station")
        assert state is not None
        assert state.attributes["unit_of_measurement"] == DISTANCE_UNITS


def test_sensor_state_updates(mock_coordinator):
    """Test sensor state updates."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ROUTE_MKT: "123"},
    )

    # Test location sensor
    location_sensor = BusLocationSensor(mock_coordinator, config_entry)
    assert location_sensor.state == "32.0865,34.7876"

    # Test speed sensor
    speed_sensor = BusSpeedSensor(mock_coordinator, config_entry)
    assert speed_sensor.state == 35.5
    assert speed_sensor.native_unit_of_measurement == SPEED_UNITS

    # Test bearing sensor
    bearing_sensor = BusBearingSensor(mock_coordinator, config_entry)
    assert bearing_sensor.state == 180
    assert bearing_sensor.native_unit_of_measurement == BEARING_UNITS

    # Test distance from start sensor
    distance_start_sensor = BusDistanceFromStartSensor(mock_coordinator, config_entry)
    assert distance_start_sensor.state == 1500
    assert distance_start_sensor.native_unit_of_measurement == DISTANCE_UNITS

    # Test distance from station sensor
    distance_station_sensor = BusDistanceFromStationSensor(mock_coordinator, config_entry)
    assert distance_station_sensor.state == 500
    assert distance_station_sensor.native_unit_of_measurement == DISTANCE_UNITS


def test_sensor_unavailable_state(mock_coordinator):
    """Test sensor behavior when data is unavailable."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ROUTE_MKT: "123"},
    )

    # Set coordinator data to None
    mock_coordinator.data = None

    # Test all sensors return None when data is unavailable
    location_sensor = BusLocationSensor(mock_coordinator, config_entry)
    assert location_sensor.state is None

    speed_sensor = BusSpeedSensor(mock_coordinator, config_entry)
    assert speed_sensor.state is None

    bearing_sensor = BusBearingSensor(mock_coordinator, config_entry)
    assert bearing_sensor.state is None

    distance_start_sensor = BusDistanceFromStartSensor(mock_coordinator, config_entry)
    assert distance_start_sensor.state is None

    distance_station_sensor = BusDistanceFromStationSensor(mock_coordinator, config_entry)
    assert distance_station_sensor.state is None 