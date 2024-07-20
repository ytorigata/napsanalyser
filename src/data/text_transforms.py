import pandas as pd
import re
from src.config import ABBREVIATION_CSV, COLUMN_NAMES

# Global variable to cache the data
_cached_column_names = None
_cached_column_names_pre_2010 = None

def convert_micro_to_nano(df, columns):
    """
    Convert unit from micro to nano in specified columns.
    - inputs:
        - df: a DataFrame
        - columns: a list of column names (string)
    - output: df: a DataFrame with columns which have converted units
    """
    conversion_factor = 10 ** 3
    df[columns] = df[columns].apply(lambda x: x * conversion_factor)
    return df


def formalise_columns(df, mapping):
    """
    Rename columns by mapping various old names to a single new name.
    - inputs:
        - df: a DataFrame containing column names to rename
        - mapping: a dictionary with keys which are new column names and 
            values which are (various old) column names 
    - output: df: a DataFrame with renamed columns
    """
    # create a reverse mapping dictionary
    reverse_mapping = {}
    for key, values in mapping.items():
        for value in values:
            reverse_mapping[value] = key

    # rename columns using the reverse mapping
    df.rename(columns=reverse_mapping, inplace=True)
    return df


def get_abbreviation_dict():
    """
    Return a diction with full names of analytes as keys and their abbreviations as values.
    - output:
        - abb_dict: a dictionary of keys (analyte full name) and values (abbreviation)
    """
    abb_df = pd.read_csv(ABBREVIATION_CSV)
    column_keys = 'full_name'
    column_values = 'abbreviation'
    abb_dict = pd.Series(abb_df[column_values].values, index=abb_df[column_keys]).to_dict()
    return abb_dict


def get_MDL_col_name(analyte):
    """Return a MDL column name for a specified analyte"""
    abb_dict = get_abbreviation_dict()
    abb = abb_dict[analyte]
    return abb + '-MDL'


def remove_parentheses(text):
    return re.sub(r'\s*\([^)]*\)', '', text)


def load_column_names_file(filepath):
    
    if filepath == COLUMN_NAMES:
        global _cached_column_names
        if _cached_column_names is None:
            _cached_column_names = pd.read_csv(filepath)
        return _cached_column_names
        
    else:  # COLUMN_NAMES_PRE_2010_IONS
        global _cached_column_names_pre_2010
        if _cached_column_names_pre_2010 is None:
            _cached_column_names_pre_2010 = pd.read_csv(filepath)
        return _cached_column_names_pre_2010


def rename_columns(df, TEMPLATE=COLUMN_NAMES):
    """
    Convert the column names to the same column names as the data after 2010
    - inputs:
        - df: a DataFrame to rename its columns
        - TEMPLATE: Optional. a file path (string) to a CSV file which contains 
            culumn names in 'old_name' column and their replaced names 
            in 'new_name' column
    - output: renamed_df, a DataFrame with modified column names 
    """
    col_names_df = load_column_names_file(TEMPLATE)
    dict_col = dict(zip(col_names_df.old_name, col_names_df.new_name))
    renamed_df = df.rename(columns=dict_col, errors = 'ignore')
    return renamed_df


