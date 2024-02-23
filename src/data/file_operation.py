from pathlib import Path

def ensure_directory_exists(directory: Path):
    """
    Ensure the directory exists, create it if it does not.
    """
    directory.mkdir(parents=True, exist_ok=True)
    