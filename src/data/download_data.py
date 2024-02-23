import os
import pandas as pd
from pathlib import Path
import requests
from zipfile import ZipFile
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
        logger.info(f"Downloaded {file_name} to {directory}")
    else:
        logger.error(
            f"Failed to download {file_name} to {directory}. Status code: {response.status_code}")

def download_NAPS_dataset(data_file_path, raw_data_dir):
    """
    Read URLs and years from a CSV file and download each file 
    to a directory named by year within the base directory.
    - inputs:
        - data_file_path: A local file path to a CSV file (string). The file must 
            contain columns named 'year' and 'url'.
        - base_directory: A local directory path (string) which will be a 
            parent directory of each year's directory to save downloaded files.
    """
    url_df = pd.read_csv(data_file_path)
    ensure_directory_exists(raw_data_dir)
    
    for index, row in url_df.iterrows():
        # create a directory path for the year
        year = row['year']
        year_directory = os.path.join(raw_data_dir, str(year))
        
        # ensure the year directory exists
        if not os.path.exists(year_directory):
            os.makedirs(year_directory)
        
        download_file(row['url'], year_directory)

def download_station_data(info_file_path, raw_data_dir):
    """
    Download the NAPS-provided station data.
    - inputs:
        - info_file_path: a file path (string) to the file of the programming info files
        - raw_data_dir: a directory path (string) to the downloaded data
    """
    url_df = pd.read_csv(info_file_path)
    station_file_url = url_df.loc[url_df['type'] == 'stations', ['url']].squeeze()
    
    download_file(station_file_url, raw_data_dir, station_file_url.split('%2F')[-1])

def ensure_directory_exists(directory: Path):
    """
    Ensure the directory exists, create it if it does not.
    """
    directory.mkdir(parents=True, exist_ok=True)

def unzip_NAPS_dataset(data_file_path, raw_data_dir):
    """
    Unzip downloaded data files and store them.
    - inputs:
        - data_file_path: a file path (strin) to the list of data files
        - raw_data_dir: a directory path (string) to the downloaded data
    """
    url_df = pd.read_csv(data_file_path)
    years = url_df.sort_values('year')['year'].squeeze().unique()
    
    for year in years :
        logger.info(f'Unzip data files of year {year}: ')
        
        target_dir = Path(str(raw_data_dir) + '/' + str(year) + '/')
        
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
