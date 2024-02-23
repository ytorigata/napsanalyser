import logging
import os
from pathlib import Path
import sys

def setup_logger(name, log_file_name, level=logging.INFO):
    project_root = Path(__file__).resolve().parents[2]
    log_file = project_root / 'logs' / log_file_name

    if not log_file.parent.exists():
        log_file.parent.mkdir()
    
    handler = logging.FileHandler(log_file)    
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger