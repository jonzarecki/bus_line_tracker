# 🚌 Bus Line Tracker for Home Assistant

A focused Home Assistant integration that helps you catch your bus on time by tracking specific bus lines at your chosen stations using the Israeli Ministry of Transport's SIRI API.

## Features

### Real-time Bus Tracking
- ⏰ Precise arrival times for your specific bus lines
- ⌚ Time until next arrival
- 🔄 Regular updates (every 30 seconds)

### Smart Notifications
- ⏰ "Time to leave" notifications based on:
  - Real-time bus location
  - Historical delay patterns
  - Current traffic conditions
- 🚨 Alerts for:
  - Service disruptions
  - Significant delays
  - Last bus of the day

### Available Sensors
For each bus line at your configured stop:
- Next arrival time
- Time until arrival
- Bus location (distance from station)
- Delay status
- Historical reliability score
- Crowding information (when available)

## Prerequisites
- Home Assistant installation
- API key from the Israeli Ministry of Transport
- Internet connection
- HACS (Home Assistant Community Store) installed

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
  api_key: !secret mot_api_key
  stations:
    - station_id: "12345"
      lines: 
        - "11"
        - "24A"
      walking_time: 7  # minutes to reach station
  update_interval: 30  # seconds
```

## Usage Examples

### Basic Automation Example
```yaml
automation:
  - alias: "Bus Departure Notification"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bus_11_next_arrival
        below: 10  # minutes
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
          message: "Bus 11 arriving in {{ states('sensor.bus_11_next_arrival') }} minutes. Time to leave!"
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
- Home Assistant community for support and inspiration

## Support

For issues and feature requests, please use the GitHub issues page. 