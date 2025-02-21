"""Test the Bus Line Tracker config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from custom_components.bus_line_tracker.const import (
    DOMAIN,
    CONF_ROUTE_MKT,
    CONF_FILTER_NAME,
    CONF_DIRECTION,
    CONF_LAT,
    CONF_LON,
    CONF_WALKING_TIME,
    CONF_UPDATE_INTERVAL,
)

from custom_components.bus_line_tracker.config_flow import (
    MIN_UPDATE_INTERVAL,
    MAX_UPDATE_INTERVAL,
    MIN_WALKING_TIME,
    MAX_WALKING_TIME,
    MIN_LAT,
    MAX_LAT,
    MIN_LON,
    MAX_LON,
)


class MockConfigEntry:
    """Mock config entry."""

    def __init__(self, *, domain=None, data=None, options=None, entry_id=None, title=None, source=None, unique_id=None):
        """Initialize mock config entry."""
        self.domain = domain or "bus_line_tracker"
        self.data = data or {}
        self._options = options or {}
        self.entry_id = entry_id or "test_entry_id"
        self.title = title or "Test Title"
        self.source = source or "user"
        self._unique_id = unique_id or "test_unique_id"
        self.state = "not_loaded"
        self.disabled_by = None
        self._version = 1

    @property
    def unique_id(self):
        """Return unique ID."""
        return self._unique_id

    @property
    def options(self):
        """Return options."""
        return self._options

    @options.setter
    def options(self, value):
        """Set options."""
        self._options = value

    @property
    def version(self):
        """Return version."""
        return self._version

    async def add_to_hass(self, hass):
        """Add entry to hass."""
        pass

    async def async_update_entry(self, **kwargs):
        """Update entry."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self


async def test_successful_config_flow(hass):
    """Test a successful config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Test submission with valid data
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ROUTE_MKT: "123",
            CONF_FILTER_NAME: "Test Route",
            CONF_DIRECTION: "1",
            CONF_LAT: 32.0,
            CONF_LON: 35.0,
            CONF_WALKING_TIME: 5,
            CONF_UPDATE_INTERVAL: 30,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Bus Line 123"
    assert result["data"][CONF_ROUTE_MKT] == "123"
    assert result["data"][CONF_FILTER_NAME] == "Test Route"


@pytest.mark.parametrize(
    "field,value,error",
    [
        (CONF_ROUTE_MKT, "abc", "invalid_route_mkt"),
        (CONF_LAT, 28.0, "invalid_lat"),
        (CONF_LAT, 35.0, "invalid_lat"),
        (CONF_LON, 33.0, "invalid_lon"),
        (CONF_LON, 37.0, "invalid_lon"),
        (CONF_WALKING_TIME, 0, "invalid_walking_time"),
        (CONF_WALKING_TIME, 61, "invalid_walking_time"),
        (CONF_UPDATE_INTERVAL, 5, "invalid_update_interval"),
        (CONF_UPDATE_INTERVAL, 3601, "invalid_update_interval"),
        (CONF_DIRECTION, "3", "invalid_direction"),
    ],
)
async def test_invalid_inputs(hass, field, value, error):
    """Test invalid config flow inputs."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Create valid data and override with test value
    user_input = {
        CONF_ROUTE_MKT: "123",
        CONF_FILTER_NAME: "Test Route",
        CONF_DIRECTION: "1",
        CONF_LAT: 32.0,
        CONF_LON: 35.0,
        CONF_WALKING_TIME: 5,
        CONF_UPDATE_INTERVAL: 30,
    }
    user_input[field] = value

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input,
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"][field] == error


async def test_options_flow(hass):
    """Test config flow options."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={
            CONF_UPDATE_INTERVAL: 30,
            CONF_WALKING_TIME: 5,
        },
    )
    config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_UPDATE_INTERVAL: 60,
            CONF_WALKING_TIME: 10,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert config_entry.options[CONF_UPDATE_INTERVAL] == 60
    assert config_entry.options[CONF_WALKING_TIME] == 10 