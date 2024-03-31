from pathlib import Path
from src.config import PROCESSED_DIR

def ensure_directory_exists(directory: Path):
    """
    Ensure the directory exists, create it if it does not.
    """
    directory.mkdir(parents=True, exist_ok=True)


def get_processed_file_path(year, site_id, instrument):
    """
    Return file path based on the specified year, site ID, and instrument.
    - inputs:
        - year: year of the data (int)
        - site_id: NAPS site ID (int)
        - instrument: 'ICPMS' or 'IC'
    """
    if instrument == 'ICPMS':
        file_path = str(PROCESSED_DIR) + '/' + str(year) + '_' + str(site_id) + '.csv'
        return file_path
    elif instrument == 'IC':
        file_path = str(PROCESSED_DIR) + '/' + str(year) + '_' + str(site_id) + '_IC.csv'
        return file_path
    else:
        raise(f'The specified combination of year, site ID, and instrument is incorrect: {year=}, {site_id=}, {instrument=}')
