import pandas as pd
from src.config import STATIONS_CSV

def format_float(val, n=2):
    """
    Return a given value with n decimal places.
    - inputs:
        - val: The value to be formatted.
        - n: Number of decimal places (int; default is 2).
    - output:
        - val: Formatted float as a string with n decimal places if val is a float.
            Or the original value if val is not a float.
    """
    if isinstance(val, float):
        # Create format string dynamically
        format_str = "{:." + str(n) + "f}"
        return format_str.format(val)
    else:
        return val


def get_naps_station_name(site_id):
    """
    Return a NAPS site name from its site ID. The name should be titled.
    e.g., BURNABY SOUTH should be converted to Burnabe South.
    - input: site_id: NAPS site ID (int)
    - output: titled_station_name: NAPS station name (string) in titled format
    """
    stations = pd.read_csv(STATIONS_CSV)
    station_name = stations.loc[stations['site_id'] == site_id, 'station_name'].iloc[0]
    titled_station_name = station_name.title()
    return titled_station_name


def split_df(func, df):
    """
    Halve the length of a given DataFrame and call a given function 
    to display (and/or save) a long table.
    - inputs:
        - df: a DataFrame
        - func: any function for display of a DataFrame
    - outputs: (none; display two DataFrames)
    """
    split_idx = len(df) // 2
    upper_df = df.iloc[:split_idx]
    lower_df = df.iloc[split_idx:]

    upper_result = func(upper_df)
    lower_result = func(lower_df)
    
    return upper_result, lower_result

