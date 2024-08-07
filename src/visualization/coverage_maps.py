import pandas as pd
from src.config import INDEX_CSV, STATIONS_CSV

def color_nt_ws(value):
    """
    Colors analytes in a dateframe: 
    green if both Near-Total and Water-Soluble data exist,
    orange if only Near-Total data exist,
    blue if only Water-Soluble data exist, and
    grey if both data do not exist
    """
    if value == 'Both':
        color = '#97d8c4'
    elif value == 'WS':
        color = '#6B9ac4'
    elif value == 'NT':
        color = '#f4b942'
    elif value == 'n/a':
        color = '#999999'
    else:
        color = ''
    return 'background-color: %s' % color


def color_percentage(value):
    """
    Return colour setting for a table stye based on the percentage.
    Green: >= 75%, Yellow: >= 50%, Red: >= 0, Grey: = 0.
    - input: value (float) of the percentage
    - output: colour setting for the style (string)
    """
    if isinstance(value, str) | isinstance(value, int):
        color = ''
    elif value >= 75.0:
        color = '#3dd7bf'
    elif value >= 50.0:
        color = '#ffd872'
    elif value > 0:
        color = '#ff828b'
    elif value == 0:
        color = '#999999'
    else:
        color = ''
    return 'background-color: %s' % color


def visualize_coverage_by_site_and_year(analyte=''):
    """
    Display a table of coverage of the data set.
    - input: analyte (optional): analyte or ion full name (string)
    - output: (display to screen)
    """
    index_df = pd.read_csv(INDEX_CSV)
    stations = pd.read_csv(STATIONS_CSV, encoding='utf-8')
    years = index_df.sort_values('year')['year'].squeeze().unique()
    
    # select a particular analyte if specified
    icpms_df = pd.DataFrame()
    if analyte != '':
        icpms_df = index_df[(index_df['instrument'] == 'ICPMS') & (index_df['analyte'] == analyte)]
    else:
        icpms_df = index_df[index_df['instrument'] == 'ICPMS']
    
    unique_combinations = icpms_df[['year', 'site_id', 'analyte_type']].drop_duplicates()
    unique_combinations.reset_index(drop=True, inplace=True)

    all_sites = []
    for site_id in unique_combinations['site_id'].sort_values().unique():
        
        years_for_one_site = unique_combinations[unique_combinations['site_id'] == site_id]
        
        one_row = [site_id]
        
        # information about each year will be concatnated to the right
        for year in years:
            rows = years_for_one_site[years_for_one_site['year'] == year]
            
            if len(rows) == 2:
                # Both NT and WS data exist
                one_row.append('Both')
                
            elif len(rows) == 1:
                # MetalType (NT or WS) is extracted from the metainfo
                one_row.append(rows.iloc[0, 2])
    
            else :
                # Neither NT nor WS data exists
                one_row.append('n/a')
                
        all_sites.append(one_row)
        
    new_col_header = ['site_id']
    new_col_header.extend(years)
    all_sites_df = pd.DataFrame(all_sites, columns=new_col_header)
    
    # match the station name with site ID for display
    station_name_df = stations.loc[:, ['site_id', 'station_name']]
    site_with_name_df = all_sites_df.merge(station_name_df, on='site_id')
    
    cols = site_with_name_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    site_with_name_df = site_with_name_df[cols]
    
    table = site_with_name_df.style.map(color_nt_ws)
    display(table)
