"""Config flow for Bus Line Tracker integration."""
import re
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_UPDATE_INTERVAL,
    CONF_ROUTES,
    CONF_ROUTE_MKT,
    CONF_FILTER_NAME,
    CONF_DIRECTION,
    CONF_REFERENCE_POINT,
    CONF_WALKING_TIME,
    CONF_LAT,
    CONF_LON,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_WALKING_TIME,
)

# Validation constants
MIN_UPDATE_INTERVAL = 10  # seconds
MAX_UPDATE_INTERVAL = 3600  # seconds
MIN_WALKING_TIME = 1  # minutes
MAX_WALKING_TIME = 60  # minutes
MIN_LAT = 29.0  # Southernmost point of Israel
MAX_LAT = 34.0  # Northernmost point of Israel
MIN_LON = 34.0  # Westernmost point of Israel
MAX_LON = 36.0  # Easternmost point of Israel


class BusLineTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bus Line Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate route_mkt format (should be numeric)
            if not user_input[CONF_ROUTE_MKT].isdigit():
                errors[CONF_ROUTE_MKT] = "invalid_route_mkt"

            # Validate lat/lon if provided
            if CONF_LAT in user_input and user_input[CONF_LAT] is not None:
                if not MIN_LAT <= user_input[CONF_LAT] <= MAX_LAT:
                    errors[CONF_LAT] = "invalid_lat"

            if CONF_LON in user_input and user_input[CONF_LON] is not None:
                if not MIN_LON <= user_input[CONF_LON] <= MAX_LON:
                    errors[CONF_LON] = "invalid_lon"

            # Validate walking time
            walking_time = user_input.get(CONF_WALKING_TIME, DEFAULT_WALKING_TIME)
            if not MIN_WALKING_TIME <= walking_time <= MAX_WALKING_TIME:
                errors[CONF_WALKING_TIME] = "invalid_walking_time"

            # Validate update interval
            update_interval = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            if not MIN_UPDATE_INTERVAL <= update_interval <= MAX_UPDATE_INTERVAL:
                errors[CONF_UPDATE_INTERVAL] = "invalid_update_interval"

            # If direction is provided, validate it's either "1" or "2"
            if CONF_DIRECTION in user_input and user_input[CONF_DIRECTION]:
                if user_input[CONF_DIRECTION] not in ["1", "2"]:
                    errors[CONF_DIRECTION] = "invalid_direction"

            if not errors:
                return self.async_create_entry(
                    title=f"Bus Line {user_input[CONF_ROUTE_MKT]}",
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ROUTE_MKT): str,
                    vol.Optional(CONF_FILTER_NAME): str,
                    vol.Optional(CONF_DIRECTION): vol.In(["1", "2"]),
                    vol.Optional(CONF_LAT): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=MIN_LAT, max=MAX_LAT)
                    ),
                    vol.Optional(CONF_LON): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=MIN_LON, max=MAX_LON)
                    ),
                    vol.Optional(
                        CONF_WALKING_TIME,
                        default=DEFAULT_WALKING_TIME
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_WALKING_TIME, max=MAX_WALKING_TIME)
                    ),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=DEFAULT_UPDATE_INTERVAL
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Bus Line Tracker."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Validate walking time
            walking_time = user_input.get(CONF_WALKING_TIME, DEFAULT_WALKING_TIME)
            if not MIN_WALKING_TIME <= walking_time <= MAX_WALKING_TIME:
                errors[CONF_WALKING_TIME] = "invalid_walking_time"

            # Validate update interval
            update_interval = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            if not MIN_UPDATE_INTERVAL <= update_interval <= MAX_UPDATE_INTERVAL:
                errors[CONF_UPDATE_INTERVAL] = "invalid_update_interval"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                CONF_UPDATE_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                ),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
            ),
            vol.Optional(
                CONF_WALKING_TIME,
                default=self.config_entry.options.get(
                    CONF_WALKING_TIME, DEFAULT_WALKING_TIME
                ),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_WALKING_TIME, max=MAX_WALKING_TIME),
            ),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options),
            errors=errors,
        ) 