"""Test the Bus Line Tracker config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from pytest_homeassistant_custom_component.common import MockConfigEntry

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
    assert result["errors"] == {field: error}


async def test_options_flow(hass: HomeAssistant) -> None:
    """Test config flow options."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_1",
        data={},
        options={
            CONF_UPDATE_INTERVAL: 30,
            CONF_WALKING_TIME: 5,
        },
    )

    with patch(
        "custom_components.bus_line_tracker.BusLineDataCoordinator._async_update_data",
        return_value={},
    ):
        config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

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
        assert config_entry.options == {
            CONF_UPDATE_INTERVAL: 60,
            CONF_WALKING_TIME: 10,
        } 