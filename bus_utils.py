import pandas as pd
import datetime
from dateutil import tz
import folium
import stride
from typing import Optional, List, Union


def localize_dates(data: pd.DataFrame, dt_columns: Optional[List[str]] = None) -> pd.DataFrame:
    if dt_columns is None:
        dt_columns = []
    
    data = data.copy()
    
    for c in dt_columns:
        data[c] = pd.to_datetime(data[c]).dt.tz_convert('Israel')
    
    return data


def get_routes_for_route_mkt(
    route_mkt: str, 
    date_from: str, 
    date_to: str, 
    filter_name: Optional[str] = None, 
    direction: Optional[str] = None
) -> pd.DataFrame:
    """Get routes dataframe filtered by route_mkt and optionally by name and direction.
    
    Args:
        route_mkt (str): Route market ID
        date_from (str): Start date in YYYY-MM-DD format
        date_to (str): End date in YYYY-MM-DD format
        filter_name (str, optional): String to filter route names. Defaults to None.
        direction (str, optional): Direction to filter by. Defaults to None.
    
    Returns:
        pd.DataFrame: Filtered routes dataframe
    """
    routes_df = pd.DataFrame(stride.get('/gtfs_routes/list', {
        'route_mkt': route_mkt,
        'date_from': date_from,
        'date_to': date_to
    }))
    
    if filter_name:
        routes_df = routes_df[routes_df['route_long_name'].apply(lambda s: filter_name in s)]
    
    if direction:
        routes_df = routes_df[routes_df['route_direction'] == direction]
    
    return routes_df


def get_vehicle_locations(
    line_ref: str, 
    start_time: datetime.datetime, 
    end_time: datetime.datetime, 
    limit: int = 100_000
) -> pd.DataFrame:
    """Get vehicle locations for a specific line reference and time range.
    
    Args:
        line_ref (str): Line reference ID
        start_time (datetime): Start time with timezone
        end_time (datetime): End time with timezone
        limit (int, optional): Maximum number of records to retrieve. Defaults to 100_000.
    
    Returns:
        pd.DataFrame: Vehicle locations dataframe with localized dates
    """
    locations_df = pd.DataFrame(stride.iterate('/siri_vehicle_locations/list', {
        'siri_routes__line_ref': line_ref,
        'siri_rides__schedualed_start_time_from': start_time,
        'siri_rides__schedualed_start_time_to': end_time,
        'order_by': 'recorded_at_time desc',
        'limit': -1,
    }, limit=limit,))  #  pre_requests_callback='print'
    
    dt_columns = ['recorded_at_time', 'siri_ride__scheduled_start_time']
    return localize_dates(locations_df, dt_columns)


if __name__ == '__main__':
    # Example usage with current values
    date_from = '2025-02-19'
    date_to = '2025-02-19'
    
    # Get routes for Reading direction 1
    routes_df = get_routes_for_route_mkt('23056', date_from, date_to, 
                                    filter_name="רדינג", direction='1')
    
    line_ref = routes_df['line_ref'].iloc[0]
    
    # Get vehicle locations for the specified time range
    start_time = datetime.datetime(2025, 2, 19, 9, tzinfo=tz.gettz('Israel'))
    end_time = datetime.datetime(2025, 2, 19, 12, tzinfo=tz.gettz('Israel'))
    
    siri_vehicle_locations_480 = get_vehicle_locations(line_ref, start_time, end_time)

    
    # Filter for the newest siri_ride__id
    newest_ride_id = siri_vehicle_locations_480['siri_ride__id'].iloc[0] # sorted by desc
    siri_vehicle_locations_480 = siri_vehicle_locations_480[siri_vehicle_locations_480['siri_ride__id'] == newest_ride_id]


    print(siri_vehicle_locations_480.shape)