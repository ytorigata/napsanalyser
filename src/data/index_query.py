import pandas as pd
from src.config import INDEX_CSV


def get_all_ions():
    """
    Return a list of all ion names in the index file.
    - output: ion_list: a list of ions' full names (string)
    """
    ion_df = index_df[(index_df['instrument'] == 'IC')]
    ion_list = ion_df['element'].unique().tolist()
    return ion_list


def get_all_metals():
    """
    Return a list of all trace metal names in the index file.
    - output: metal_list: a list of metals' full names (string)
    """
    metal_df = index_df[(index_df['instrument'] == 'ICPMS')]
    metal_list = metal_df['element'].unique().tolist()
    return metal_list


def get_sites_for_year(year, element='', element_form=''):
    """
    Return a list of unique NAPS site IDs associated with a specified year.
    - inputs:
        - year: year of the interest (int)
        - element: Optional. A full name of element or ion (string)
        - element_form: Optional. 'NT' for Near Total, 'WS' for Water-soluble, and 'total' for ions.
    - output: site_ids: a list of NAPS site IDs (int)
    """
    index_df = pd.read_csv(INDEX_CSV)

    sites_for_year_df = pd.DataFrame()
    if (element != '') & (element_form != ''):
        sites_for_year_df = index_df[(
            index_df['year'] == year) & (
                index_df['element'] == element) & (
                index_df['element_form'] == element_form)]
    elif element != '':
        sites_for_year_df = index_df[(
            index_df['year'] == year) & (
                index_df['element'] == element)]
    elif element_form != '':
        sites_for_year_df = index_df[(
            index_df['year'] == year) & (
                index_df['element_form'] == element_form)]
    else:
        sites_for_year_df = index_df[index_df['year'] == year]
        
    site_ids = sites_for_year_df['site_id'].sort_values().unique()
    return site_ids

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
