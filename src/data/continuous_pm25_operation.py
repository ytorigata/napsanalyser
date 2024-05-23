import numpy as np
import pandas as pd
from src.config import OUTPUT_IMG_DIR, CONTINUOUS_PM25_DIR
from src.data.parameter_check import *

def error_to_none(df, measurement):
    # NaN, negative values are counted as an error.
    # Note: In visualization for the later analysis, they will be treated as NaN.
    df[measurement] = np.where(df[measurement] < 0, np.NaN, df[measurement])
    return df


def get_continuous_pm25_data(site_id, target_years):
    """
    Load continuous PM2.5 data for a specified site and years
    """
    # construct a file name based on the site_id
    fname = str(CONTINUOUS_PM25_DIR) + '/' + str(site_id) + '.csv'
    site_df = pd.read_csv(fname, parse_dates=['sampling_date'], index_col='sampling_date')

    years = list(range(2003, 2020)) if are_all_sites_included(target_years) else target_years
    
    site_df = site_df.loc[str(years[0]):str(years[-1])]
    site_df = error_to_none(site_df, 'PM2.5')
    return site_df

