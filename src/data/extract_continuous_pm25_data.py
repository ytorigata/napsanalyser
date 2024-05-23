import numpy as np
import pandas as pd
from datetime import datetime
from src.config import CONTINUOUS_PM25_DIR, RAW_CONTINUOUS_PM25_DIR
from src.data.file_operation import *
from src.data.parameter_check import *
from src.utils.logger_config import setup_logger

logger = setup_logger('data.extract_continuous_pm25_data', 'extract_data.log')

def transform_combined_df(df):
    # Assuming you have a function to determine the file's date format
    def detect_date_format(date_cell):
        date_str = str(date_cell)
        if '-' in date_str:
            return '%Y-%m-%d'
        else:
            return '%Y%m%d'
    
    # detect the date format, which vary across years
    date_format = detect_date_format(df['sampling_date'].iloc[0])

    df_melted = df.melt(id_vars=['site_id', 'sampling_date'], var_name='Hour', value_name='PM2.5')
    
    # parse the date and combine with hour
    df_melted['datetime_with_hour'] = pd.to_datetime(
        df_melted['sampling_date'], format=date_format) + pd.to_timedelta(df_melted['Hour'].astype(int), unit='h')

    # set 'tmp_datetime_index' as the new index
    df_melted.set_index('datetime_with_hour', inplace=True)
    
    # drop the now redundant columns
    df_melted.drop(columns=['sampling_date', 'Hour'], inplace=True)
    
    # name the index again
    df_melted.index.name = 'sampling_date'
    df_melted.sort_index(ascending=True, inplace=True)
    return df_melted
    

def extract_continuous_pm25_data(year):
    """
    Extract hourly PM2.5 data from the continuous data file.
    The data before or after 2006 is treated differently due to the formats.
    - input:
        - year: a year (int) of the data to extract
    - outputs:
        - pm25_df: a DataFrame containing extracted hourly PM2.5 data
    """
    file_name = f'PM25_{year}.csv'
    file_path = str(RAW_CONTINUOUS_PM25_DIR) + '/' + file_name
    
    pm25_df = pd.DataFrame()
    columns = []
    
    if year < 2005:
        pm25_df = pd.read_csv(file_path, encoding='ISO-8859-1', skiprows=5, low_memory=False)

        columns = ['NAPSID', 'Date'] + [col for col in pm25_df.columns if col.startswith('H')]
        pm25_df = pm25_df.rename(columns={
            'NAPSID': 'site_id',
            'Date': 'sampling_date'
        })
        hours_old = [f'H{str(i).zfill(2)}' for i in range(1, 25)]
        old_columns = ['NAPSID', 'Date'] + hours_old

    else:
        pm25_df = pd.read_csv(file_path, skiprows=7, low_memory=False)

        columns = ['NAPS ID//Identifiant SNPA', 'Date//Date'] + [col for col in pm25_df.columns if col.startswith('H')]
        pm25_df = pm25_df.rename(columns={
            'NAPS ID//Identifiant SNPA': 'site_id',
            'Date//Date': 'sampling_date'
        })
        hours_old = [f'H{str(i).zfill(2)}//H{str(i).zfill(2)}' for i in range(1, 25)]
        old_columns = ['NAPSID', 'Date'] + hours_old
        
    new_columns = ['site_id', 'sampling_date'] + list(np.arange(0, 24))
    rename_dict = dict(zip(old_columns, new_columns))
    pm25_df = pm25_df.rename(columns=rename_dict)
    pm25_df = pm25_df.loc[:, new_columns]
        
    pm25_df = transform_combined_df(pm25_df)
    
    return pm25_df


def save_continuous_pm25_data(concatenated_df, target_sites):
    """
    Save a site specific continuous PM2.5 data
    """
    
    ensure_directory_exists(CONTINUOUS_PM25_DIR)
    
    # split the concatenated DataFrame by 'site_id' and write to new CSVs
    for site_id, site_df in concatenated_df.groupby('site_id'):
        
        if (not are_all_sites_included(target_sites)):
            if (site_id not in target_sites) :
                continue
        
        # if 'all' OR (not 'all' AND site_ids are given)
        
        site_df.sort_index(ascending=True, inplace=True)
        
        # construct a file name based on the site_id
        fname_to_save = str(CONTINUOUS_PM25_DIR) + '/' + str(site_id) + '.csv'
        
        # write the site-specific DataFrame to a CSV file
        site_df.to_csv(fname_to_save, encoding='utf-8')
        
        logger.debug(f'Data for site {site_id} written to {fname_to_save}')


def extract_continuous_pm25(target_sites):
        
    target_years = np.arange(2004, 2020)
    
    # read each CSV into a DataFrame and store them in a list
    dataframes = [extract_continuous_pm25_data(year) for year in target_years]
    
    # concatenate all DataFrames into one
    concatenated_df = pd.concat(dataframes)
    
    # save site-specific continuous data sets
    save_continuous_pm25_data(concatenated_df, target_sites)


def plot_continuous_pm25(site_id, df):
    fig, ax = plt.subplots(figsize = (12, 3))
    
    # replace values <= 0 with NaN
    df['PM2.5'] = df['PM2.5'].apply(lambda x: np.nan if x <= 0 else x)
    
    ax.plot(df.index, df['PM2.5'], label='PM$_{2.5}$', color='grey', linestyle='None', marker=',')
    
    ax.set_xlabel('Time')
    plt.gcf().autofmt_xdate()
    ax.set_ylabel('PM$_{2.5}$ (µg/m$^3$)')
    ax.legend()
    plt.show()

