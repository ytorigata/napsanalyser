import pandas as pd
import re
from src.config import ABBREVIATION_CSV, COLUMN_NAMES

def convert_micro_to_nano(df, columns):
    """
    Convert unit from micro to nano in specified columns.
    - inputs:
        - df: a DataFrame
        - columns: a list of column names (string)
    - output: converted_df: a DataFrame with columns which have converted units
    """
    converted_df = pd.DataFrame(df)
    for col in columns:
        tmp_df = df[col] * 10 ** 3
        converted_df.loc[:, [col]] = tmp_df
    return converted_df


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
    col_names_df = pd.read_csv(TEMPLATE)
    dict_col = dict(zip(col_names_df.old_name, col_names_df.new_name))
    renamed_df = df.rename(columns=dict_col, errors = 'ignore')
    return renamed_df

