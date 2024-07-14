import os
import pandas as pd
from pathlib import Path
import requests
from zipfile import ZipFile
from src.config import DATA_URLS_FILE, INFO_URLS_FILE, RAW_DIR,\
RAW_INTEGRATED_PM25_DIR, RAW_CONTINUOUS_PM25_DIR, STATIONS_RAW_CSV
from src.data.file_operation import ensure_directory_exists
from src.utils.logger_config import setup_logger

logger = setup_logger('data.download_data', 'download_data.log')

def download_file(url, directory, fname=''):
    """
    Download a file from a given URL and save it to a directory.
    - inputs:
        - url: URL to request (string)
        - directory: a directory path (string) to save a downloaded file
        - fname: Optional. Specify a file name (string) to save it when it is 
            different from that contained in url.
    """
    # extract file name from URL
    file_name = url.split('%2F')[-1] if fname == '' else fname
    file_path = os.path.join(directory, file_name)

    # mimic a browser to avoid the status code 403
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # send a GET request to the URL
    response = requests.get(url, headers=headers)
    
    # check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # open a file in binary write mode and save the content to the file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"Downloaded {url} to {file_path}")
    else:
        logger.error(
            f"Failed to download {url} to {file_path}. Status code: {response.status_code}")


def download_continuous_dataset():
    """
    Download and save continuous PM2.5 speciation data listed in DATA_URLS_FILE
    into a directory RAW_CONTINUOUS_PM25_DIR
    """ 
    url_df = pd.read_csv(DATA_URLS_FILE)
    continuous_df = url_df[url_df['type'] == 'continuous'].copy()
    ensure_directory_exists(RAW_CONTINUOUS_PM25_DIR)
    
    for index, row in continuous_df.iterrows():
       download_file(row['url'], RAW_CONTINUOUS_PM25_DIR)


def download_integrated_dataset():
    """
    Download and save continuous PM2.5 integrated data listed in DATA_URLS_FILE
    into a directory RAW_INTEGRATED_PM25_DIR
    """
    url_df = pd.read_csv(DATA_URLS_FILE)
    
    integrated_df = url_df[url_df['type'].str.startswith('integrated')].copy()
    ensure_directory_exists(RAW_INTEGRATED_PM25_DIR)
    
    for index, row in integrated_df.iterrows():
        # create a directory path for the year
        year = row['year']
        year_directory = os.path.join(RAW_INTEGRATED_PM25_DIR, str(year))
        
        # ensure the year directory exists
        if not os.path.exists(year_directory):
            os.makedirs(year_directory)
        
        download_file(row['url'], year_directory)


def download_station_data():
    """
    Download the NAPS-provided station data listed in INFO_URLS_FILE as a name of 
    STATIONS_RAW_CSV into the directory RAW_DIR,
    - inputs:
        - info_file_path: a file path (string) to the file of the programming info files
        - raw_data_dir: a directory path (string) to the downloaded data
        - stations_raw_csv: a file name (string) to save the raw stations data.
    """
    url_df = pd.read_csv(INFO_URLS_FILE)
    station_file_url = url_df.loc[url_df['type'] == 'stations', ['url']].squeeze()
    
    download_file(station_file_url, RAW_DIR, str(STATIONS_RAW_CSV).split('%2F')[-1])


def unzip_integrated_dataset():
    """
    Unzip downloaded data files listed in DATA_URLS_FILE and store them into 
    RAW_INTEGRATED_PM25_DIR
    """
    url_df = pd.read_csv(DATA_URLS_FILE)
    years = url_df.sort_values('year')['year'].unique()
    
    for year in years :
        logger.info(f'Unzip data files of year {year}: ')
        
        target_dir = Path(str(RAW_INTEGRATED_PM25_DIR) + '/' + str(year) + '/')
        
        # extract file names to unzip
        urls = url_df[url_df['year'] == year]['url']
        filenames = [url.split('%2F')[-1] for url in urls]
        
        for item in target_dir.iterdir():
            # unzip files listed in the CSV, skipping any other zip files
            if (item.name.endswith('.zip')) & (item.name in filenames):
                with ZipFile(item, 'r') as f:
                    f.extractall(target_dir)
                
                # for logging
                item_str = str(item)
                unzipped_file = item_str[item_str.rindex('/') + 1:]
                logger.info(f'\t{unzipped_file}')
