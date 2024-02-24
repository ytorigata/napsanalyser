import pandas as pd
from src.config import INDEX_CSV

def get_years_for_site(site_id, element, element_form):
    """
    Rreturns years associated with a specified NAPS site ID.
    - inputs:
        site_id: NAPS site ID (int)
        element: NAPS site ID (int)
    - output: years: a list of years (int)
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    filtered_df = index_df[(
        index_df['site_id'] == site_id) & (
            index_df['element'] == element) & (
            index_df['element_form'] == element_form)
    ]
    unique_years = filtered_df['year'].unique()
    unique_years_list = unique_years.tolist()

    return unique_years_list
