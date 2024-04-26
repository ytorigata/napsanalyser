import pandas as pd
from src.config import INDEX_CSV


def get_all_ions():
    """
    Return a list of all ion names in the index file.
    - output: ion_list: a list of ions' full names (string)
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    ion_df = index_df[(index_df['instrument'] == 'IC')]
    ion_list = ion_df['analyte'].unique().tolist()
    ion_list.sort()
    return ion_list


def get_all_metals():
    """
    Return a list of all trace metal names in the index file.
    - output: metal_list: a list of metals' full names (string)
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    metal_df = index_df[(index_df['instrument'] == 'ICPMS')]
    metal_list = metal_df['analyte'].unique().tolist()
    metal_list.sort()
    return metal_list


def get_sites_for_year(year, analyte='', analyte_type=''):
    """
    Return a list of unique NAPS site IDs associated with a specified year.
    - inputs:
        - year: year of the interest (int)
        - analyte: Optional. A full name of analyte or ion (string)
        - analyte_type: Optional. 'NT' for Near Total, 'WS' for Water-soluble, and 'total' for ions.
    - output: site_ids: a list of NAPS site IDs (int)
    """
    index_df = pd.read_csv(INDEX_CSV)

    sites_for_year_df = pd.DataFrame()
    if (analyte != '') & (analyte_type != ''):
        sites_for_year_df = index_df[(
            index_df['year'] == year) & (
                index_df['analyte'] == analyte) & (
                index_df['analyte_type'] == analyte_type)]
    elif analyte != '':
        sites_for_year_df = index_df[(
            index_df['year'] == year) & (
                index_df['analyte'] == analyte)]
    elif analyte_type != '':
        sites_for_year_df = index_df[(
            index_df['year'] == year) & (
                index_df['analyte_type'] == analyte_type)]
    else:
        sites_for_year_df = index_df[index_df['year'] == year]
        
    site_ids = sites_for_year_df['site_id'].sort_values().unique()
    return site_ids


def get_years_for_site(site_id, analyte, analyte_type):
    """
    Return years associated with a specified NAPS site ID.
    - inputs:
        site_id: NAPS site ID (int)
        analyte: a full name (string) of analyte
    - output: years: a list of years (int)
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    filtered_df = index_df[(
        index_df['site_id'] == site_id) & (
            index_df['analyte'] == analyte) & (
            index_df['analyte_type'] == analyte_type)
    ]
    unique_years = filtered_df['year'].unique()
    unique_years_list = unique_years.tolist()

    return unique_years_list


def get_all_years_metadata(analyte, instrument, analyte_type=None, site_id=None):
    """
    Rreturns metadata for all years associated with a given analyte, instrument, 
    and analyte form (option) for a specified NAPS site ID (option)
    - inputs:
        - analyte: a full name (string) of analyte
        - instrument: 'ICPMS' or 'IC' (string)
        - analyte_type: 'NT' for Near Total metals, 'WS' for Water-soluble metals, 
            or 'total' for ions; optional
        - site_id: NAPS site ID (int); optional
    - output: a DataFrame filtered
    """
    index_df = pd.read_csv(INDEX_CSV)
    
    # start with a mask that selects all rows
    mask = pd.Series([True] * len(index_df))

    mask = mask & (
        index_df['analyte'] == analyte) & (
        index_df['instrument'] == instrument)
    
    if analyte_type is not None:
        mask = mask & (index_df['analyte_type'] == analyte_type)
    if site_id is not None:
        mask = mask & (index_df['site_id'] == site_id)
    
    return index_df[mask]


def get_all_years_pm25_metadata(instrument, analyte_type=None, site_ids=None):
    """
    Rreturns all combinations of year and site for PM2.5 data.
    - inputs:
        - instrument: 'ICPMS' or 'IC' (string)
        - site_ids: a list of NAPS Site ID (int). If not specified, return the metadata for all sites.
        - analyte_type: 'NT' for Near Total metals, 'WS' for Water-soluble metals, 
            or 'total' for ions
    - output: filtered_df: a DataFrame subset of the index file
    """
    index_df = pd.read_csv(INDEX_CSV)

    # start with a mask that selects all rows
    mask = pd.Series([True] * len(index_df))
    mask = mask & (index_df['instrument'] == instrument)
    
    if site_ids is not None:
        mask = mask & (index_df[index_df['site_id'].isin(site_ids)])

    if analyte_type is not None:
        mask = mask & (index_df['analyte_type'] == analyte_type)
    
    filtered_df = index_df[mask]

    # for PM2.5, there would be many overlap in rows because index data is for analytes 
    filtered_df = filtered_df[['year', 'site_id', 'analyte_type', 'instrument', 'frequency']].drop_duplicates()
    return filtered_df
