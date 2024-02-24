import pandas as pd
import re
from src.config import COLUMN_NAMES

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
