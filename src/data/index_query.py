import pandas as pd
from src.config import INDEX_CSV, STATIONS_CSV


def get_all_analytes(site_ids=None, years=None, instrument=None):
    """
    Return a list of all analyte names in the index file. 
    - inputs:
        - site_ids: a list of site_id (int); optional
        - years: a list of year (int); optional
        - instrument: 'ICPMS' or 'IC' (string); optional
    - output: analyte_list: a list of analytes' full names (string)
    """
    index_df = pd.read_csv(INDEX_CSV)

    mask = pd.Series([True] * len(index_df))
    if site_ids is not None:
        mask = mask & (index_df['site_id'].isin(site_ids))
    if years is not None:
        mask = mask & (index_df['year'].isin(years))
    if instrument is not None:
        mask = mask & (index_df['instrument'] == instrument)
    
    analyte_df = index_df[mask].copy()
    analyte_list = analyte_df['analyte'].unique().tolist()
    analyte_list.sort()
    return analyte_list


def get_all_ions(site_ids=None, years=None):
    """
    Return a list of all ion names in the index file. 
    - inputs:
        - site_ids: a list of site_id (int); optional
        - years: a list of year (int); optional
    - output: a list of ions' full names (string)
    """
    return get_all_analytes(site_ids, years, 'IC')


def get_all_metals(site_ids=None, years=None):
    """
    Return a list of all trace metal names in the index file.
    - inputs:
        - site_ids: a list of site_id (int); optional
        - years: a list of year (int); optional
    - output: a list of metals' full names (string)
    """
    return get_all_analytes(site_ids, years, 'ICPMS')


def get_all_sites(analyte=None, analyte_type=None, instrument=None, year=None):
    """
    Return a list of all site IDs.
    - inputs:
        - analyte: Optional. A full name of analyte or ion (string)
        - analyte_type: Optional. 'NT' for Near Total, 'WS' for Water-soluble, and 'total' for ions
        - instrument: Optional. 'ICPMS' or 'IC' (string)
        - year: Optional. year of the interest (int)
    - output: site_list: a list of NAPS site IDs (int)
    """
    index_df = pd.read_csv(INDEX_CSV)

    mask = pd.Series([True] * len(index_df))
    if analyte is not None:
        mask = mask & (index_df['analyte'] == analyte)
    if analyte_type is not None:
        mask = mask & (index_df['analyte_type'] == analyte_type)
    if instrument is not None:
        mask = mask & (index_df['instrument'] == instrument)
    if year is not None:
        mask = mask & (index_df['year'] == year)
    
    filtered_df = index_df[mask].copy()
    site_list = filtered_df['site_id'].unique().tolist()
    site_list.sort()
    return site_list

    
def get_sites_for_year(year, analyte='', analyte_type='', instrument=None):
    """
    Return a list of unique NAPS site IDs associated with a specified year.
    - inputs:
        - year: year of the interest (int)
        - analyte: Optional. A full name of analyte or ion (string)
        - analyte_type: Optional. 'NT' for Near Total, 'WS' for Water-soluble, and 'total' for ions.
    - output: site_ids: a list of NAPS site IDs (int)
    """
    if analyte == '':
        analyte = None
    if analyte_type == '':
        analyte_type = None
    return get_all_sites(analyte, analyte_type, instrument, year=year)


def get_sations_info(sites):
    """
    Return stations' information for specified sites
    - input: sites: a list of site ID (int)
    - output: site_info: a DataFrame of staton information
    """
    stations = pd.read_csv(STATIONS_CSV)
    # Merge the sites in our interest with the coordinates information
    site_list_df = pd.read_csv(INDEX_CSV, index_col=0).drop_duplicates(subset = 'site_id')
    
    site_info = site_list_df.merge(stations, on='site_id')[
        ['site_id', 'station_name', 'Latitude', 'Longitude', 'site_type']].sort_values('site_id').reset_index(drop=True)
    
    return site_info


def get_years_for_site(site_id, analyte, analyte_type=None):
    """
    Return years associated with a specified NAPS site ID.
    - inputs:
        site_id: NAPS site ID (int)
        analyte: a full name (string) of analyte
        analyte_type: Optional. 'NT' for Near Total, 'WS' for Water-soluble, and 'total' for ions.
    - output: years: a list of years (int)
    """
    index_df = pd.read_csv(INDEX_CSV)

    filtered_df = pd.DataFrame()
    if analyte_type is not None:
    
        filtered_df = index_df[(
            index_df['site_id'] == site_id) & (
                index_df['analyte'] == analyte) & (
                index_df['analyte_type'] == analyte_type)]
    else:
        filtered_df = index_df[(
            index_df['site_id'] == site_id) & (
                index_df['analyte'] == analyte)]
        
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
