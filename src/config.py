from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# key directories
DATA_DIR = PROJECT_ROOT / 'data'
CONFIG_DIR = DATA_DIR / 'config'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'

# key files
DATA_URLS_FILE = CONFIG_DIR / 'data_urls.csv'
INFO_URLS_FILE = CONFIG_DIR / 'info_urls.csv'
