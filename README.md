# 🚌 Bus Line Tracker for Home Assistant

A focused Home Assistant integration that helps you catch your bus on time by tracking specific bus lines at your chosen stations using the Israeli Ministry of Transport's SIRI API.

## Features

### Real-time Bus Tracking
- 📍 Live bus positions with latitude and longitude
- 🚗 Vehicle speed and bearing information
- 📏 Distance tracking from journey start
- 🔄 Regular updates (every 30 seconds)
- 🗺️ **NEW**: Map view showing real-time bus positions

### Smart Notifications
- ⏰ "Time to leave" notifications based on:
  - Real-time bus location and bearing
  - Distance from journey start
  - Current vehicle speed
- 🚨 Alerts for:
  - Service disruptions
  - Significant delays
  - Last bus of the day

### Available Sensors
For each bus line at your configured stop:
- `bus_[line]_location`: Current bus location (lat, lon)
- `bus_[line]_speed`: Current vehicle speed in km/h
- `bus_[line]_bearing`: Vehicle direction in degrees
- `bus_[line]_distance_from_start`: Distance from journey start in meters
- `bus_[line]_distance_from_station`: Distance from configured reference point
- `bus_[line]_vehicle_ref`: Vehicle reference ID
- `bus_[line]_last_update`: Timestamp of last update

### Map Integration
- `device_tracker.bus_[line]_position`: Bus position tracker for map view

## Prerequisites
- Home Assistant installation
- Access to Israeli Ministry of Transport's SIRI API
- Internet connection
- HACS (Home Assistant Community Store) installed
- Required Python packages (automatically installed):
  - pandas
  - folium
  - stride
  - matplotlib
  - dateutil

## Installation

### HACS Installation (Recommended)
1. Open HACS in your Home Assistant instance
2. Click on the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL with category "Integration"
5. Click "Install" on the Bus Line Tracker card
6. Restart Home Assistant

### Manual Installation
1. Copy the `bus_line_tracker` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add configuration through UI or YAML
4. Set up your automations for notifications

## Configuration

Configure through Home Assistant UI or YAML:

```yaml
bus_line_tracker:
  # General settings
  update_interval: 30  # seconds

  # Route configurations
  routes:
    - route_mkt: "23056"  # Route market ID (e.g., for line 56)
      filter_name: "רדינג"  # Optional: Filter by route name
      direction: "1"  # Optional: Filter by direction
      reference_point:  # Optional: Reference point for distance calculations
        lat: 32.090260
        lon: 34.782621
      walking_time: 7  # minutes to reach station

  # Time windows for tracking
  time_windows:
    - name: "morning"
      start_time: "07:00:00"
      end_time: "10:00:00"
      weekdays:
        - mon
        - tue
        - wed
        - thu
        - fri
    - name: "evening"
      start_time: "16:00:00"
      end_time: "19:00:00"
      weekdays:
        - mon
        - tue
        - wed
        - thu
```

## Usage Examples

### Basic Automation Example
```yaml
automation:
  - alias: "Bus Departure Notification"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bus_56_distance_from_station
        below: 2000  # meters
    condition:
      - condition: time
        after: '07:00:00'
        before: '09:00:00'
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: notify.mobile_app
        data:
          message: >
            Bus 56 is {{ states('sensor.bus_56_distance_from_station') }} meters away,
            moving at {{ states('sensor.bus_56_speed') }} km/h
            in direction {{ states('sensor.bus_56_bearing') }}°.
```

### Map View Setup
You can add the bus tracker to your map view in the Home Assistant UI:

1. Go to **Settings** > **Dashboards** > **Edit Dashboard**
2. Add a new **Map** card
3. In the entities section, add your bus tracker: `device_tracker.bus_[line]_position`
4. Save the card

Or use YAML to create a map card:

```yaml
type: map
entities:
  - entity: device_tracker.bus_56_position
title: Bus 56 Live Tracking
hours_to_show: 0.5
```

## Version History

[![Current Release](https://img.shields.io/github/release/USERNAME/bus_line_tracker.svg)](https://github.com/USERNAME/bus_line_tracker/releases/latest)
[![HACS Default](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/integration)

Check the [changelog](CHANGELOG.md) for release notes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Israeli Ministry of Transport for providing the SIRI API
- Stride API for data access
- Home Assistant community for support and inspiration
- Folium for map visualizations

## Support

For issues and feature requests, please use the GitHub issues page. 