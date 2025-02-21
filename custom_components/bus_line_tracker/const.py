"""Constants for the Bus Line Tracker integration."""

DOMAIN = "bus_line_tracker"

# Configuration
CONF_UPDATE_INTERVAL = "update_interval"
CONF_ROUTES = "routes"
CONF_ROUTE_MKT = "route_mkt"
CONF_FILTER_NAME = "filter_name"
CONF_DIRECTION = "direction"
CONF_REFERENCE_POINT = "reference_point"
CONF_WALKING_TIME = "walking_time"
CONF_TIME_WINDOWS = "time_windows"
CONF_LAT = "lat"
CONF_LON = "lon"

# Defaults
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_WALKING_TIME = 7

# Sensor attributes
ATTR_LOCATION = "location"
ATTR_SPEED = "speed"
ATTR_BEARING = "bearing"
ATTR_DISTANCE_FROM_START = "distance_from_start"
ATTR_DISTANCE_FROM_STATION = "distance_from_station"
ATTR_VEHICLE_REF = "vehicle_ref"
ATTR_LAST_UPDATE = "last_update"

# Units
SPEED_UNITS = "km/h"
DISTANCE_UNITS = "m"
BEARING_UNITS = "°"
