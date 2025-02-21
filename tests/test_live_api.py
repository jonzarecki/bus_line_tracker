"""Test the Bus Line Tracker integration with live API."""
import asyncio
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from israel_bus_locator.bus_utils import (
    get_routes_for_route_mkt,
    get_vehicle_locations,
    get_current_distances_to_ref,
)


@pytest.mark.skipif(
    "pytest" in sys.modules,
    reason="This test should be run directly with Python, not with pytest"
)
@pytest.mark.enable_socket
@pytest.mark.allow_hosts(['5.100.248.220', '194.36.90.155', 'open-bus-stride-api.hasadna.org.il'])
async def test_live_api_flow():
    """Test the complete flow with live API."""
    # Test parameters
    route_mkt = "23056"  # Replace with a known route number
    filter_name = None
    direction = None
    ref_point = (32.0731, 34.7913)  # Tel Aviv coordinates
    
    # Get current date in Israel timezone
    now = datetime.now(ZoneInfo("Israel"))
    date_str = now.strftime("%Y-%m-%d")
    
    # Test getting routes
    routes_df = get_routes_for_route_mkt(
        route_mkt,
        '2025-02-19',
        '2025-02-20',
        filter_name,
        direction,
    )
    
    assert not routes_df.empty, "No routes found"
    print(f"\nRoutes DataFrame:\n{routes_df.head()}")
    print(f"\nRoutes DataFrame columns:\n{routes_df.columns.tolist()}")
    
    # Get line_ref from first route
    line_ref = routes_df["line_ref"].iloc[0]
    
    # Test getting vehicle locations
    end_time = datetime(2025, 2, 19, 12, 0, 0, tzinfo=ZoneInfo("Israel")).replace(microsecond=0)
    start_time = end_time - timedelta(hours=1)
    
    vehicle_locations = get_vehicle_locations(
        line_ref,
        start_time,
        end_time,
    )
    
    assert not vehicle_locations.empty, "No vehicle locations found"
    print(f"\nVehicle Locations DataFrame columns:\n{vehicle_locations.columns.tolist()}")
    print(f"\nVehicle Locations sample:\n{vehicle_locations.head()}")
    
    # Test getting distances to reference point
    if not vehicle_locations.empty:
        current_distances = get_current_distances_to_ref(
            vehicle_locations,
            ref_point,
        )
        
        assert current_distances, "No distances calculated"
        print(f"\nCurrent distances:\n{current_distances}")


def main():
    """Run the test directly."""
    print("Running live API test directly...")
    asyncio.run(test_live_api_flow())
    print("\nLive API test completed successfully!")


if __name__ == "__main__":
    main() 