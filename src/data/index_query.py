import pandas as pd
from src.config import INDEX_CSV


def get_all_ions():
    """
    Return a list of all ion names in the index file.
    - output: ion_list: a list of ions' full names (string)
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    ion_df = index_df[(index_df['instrument'] == 'IC')]
    ion_list = ion_df['element'].unique().tolist()
    ion_list.sort()
    return ion_list


def get_all_metals():
    """
    Return a list of all trace metal names in the index file.
    - output: metal_list: a list of metals' full names (string)
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    metal_df = index_df[(index_df['instrument'] == 'ICPMS')]
    metal_list = metal_df['element'].unique().tolist()
    metal_list.sort()
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
        element: a full name (string) of element
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


def get_all_years_metadata(element, instrument, element_form=None, site_id=None):
    """
    Rreturns metadata for all years associated with a given element, instrument, 
    and element form (option) for a specified NAPS site ID (option)
    - inputs:
        - element: a full name (string) of element
        - instrument: 'ICPMS' or 'IC' (string)
        - element_form: 'NT' for Near Total metals, 'WS' for Water-soluble metals, 
            or 'total' for ions; optional
        - site_id: NAPS site ID (int); optional
    - output: a DataFrame filtered
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    # start with a mask that selects all rows
    mask = pd.Series([True] * len(index_df))

    mask = mask & (
        index_df['element'] == element) & (
        index_df['instrument'] == instrument)
    
    if element_form is not None:
        mask = mask & (index_df['element_form'] == element_form)
    if site_id is not None:
        mask = mask & (index_df['site_id'] == site_id)
    
    return index_df[mask]


def get_all_years_pm25_metadata(instrument, element_form=None, site_ids=None):
    """
    Rreturns all combinations of year and site for PM2.5 data.
    - inputs:
        - instrument: 'ICPMS' or 'IC' (string)
        - site_ids: a list of NAPS Site ID (int). If not specified, return the metadata for all sites.
        - element_form: 'NT' for Near Total metals, 'WS' for Water-soluble metals, 
            or 'total' for ions
    - output: filtered_df: a DataFrame subset of the index file
    """
    index_df = pd.read_csv(INDEX_CSV)

    # start with a mask that selects all rows
    mask = pd.Series([True] * len(index_df))
    mask = mask & (index_df['instrument'] == instrument)
    
    if site_ids is not None:
        mask = mask & (index_df[index_df['site_id'].isin(site_ids)])

    if element_form is not None:
        mask = mask & (index_df['element_form'] == element_form)
    
    filtered_df = index_df[mask]

    # for PM2.5, there would be many overlap in rows because index data is for elements 
    filtered_df = filtered_df[['year', 'site_id', 'element_form', 'instrument', 'frequency']].drop_duplicates()
    return filtered_df
