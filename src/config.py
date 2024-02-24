from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# key directories
DATA_DIR = PROJECT_ROOT / 'data'
CONFIG_DIR = DATA_DIR / 'config'
RAW_DIR = DATA_DIR / 'raw'
METADATA_DIR = DATA_DIR / 'metadata'
PROCESSED_DIR = DATA_DIR / 'processed'

# key files
DATA_URLS_FILE = CONFIG_DIR / 'data_urls.csv'
INFO_URLS_FILE = CONFIG_DIR / 'info_urls.csv'
STATIONS_RAW_CSV = RAW_DIR / 'stations.csv'

# for modify errors in the dataset
CHECKED_FREQUENCY = CONFIG_DIR / 'checked_frequency.csv'

# index data
STATIONS_CSV = METADATA_DIR / 'stations_metadata.csv'
INDEX_CSV = METADATA_DIR / 'index.csv'
