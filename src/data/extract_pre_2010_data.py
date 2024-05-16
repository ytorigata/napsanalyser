import datetime
import numpy as np
import os
import openpyxl
import pandas as pd
import xlrd

from src.config import RAW_DIR, PROCESSED_DIR, INDEX_CSV, COLUMN_NAMES_PRE_2010_IONS
from src.data.file_operation import ensure_directory_exists
from src.data.index_query import get_sites_for_year
from src.data.text_transforms import rename_columns
from src.utils.logger_config import setup_logger

logger = setup_logger('data.extract_pre_2010_data', 'extract_data.log')

def get_raw_file_path(year, site_id, instrument, analyte_type=None):
    """
    Return a file path to a raw data in 2003 to 2009
    - inputs:
        - year: year of the data (int)
        - site_id: NAPS site ID (int)
        - instrument: 'ICPMS' or 'IC' (string)
        - analyte_type: 'NT' (near-total) or 'WS' (water-soluble) (string); optional, but
            reuquired when instrument is ICPMS
    - output: file_path (string)
    """
    file_name = 'S' + str(site_id)
    
    if instrument == 'ICPMS':
        if analyte_type == 'NT':
            file_name += '_ICPMS.XLS'
        else:
            file_name += '_WICPMS.XLS'
    else:
        file_name += '_IC.XLS'
    
    file_path = str(RAW_DIR) + '/' + str(year) + '/SPECIATION/' + file_name
    return file_path


def extract_sheet_values(file_path, year):
    """
    Extract all cell values of the first sheet of an XSL file as a 2D array.
    - input:
        - file_path: file path to the XSL file (string)
        - year: the year of the data (int)
    - output
        - nested_array: 2D array containing rows which contains cells
    """
    # select the first worksheet in the XSL file
    book = xlrd.open_workbook(file_path, encoding_override='cp1252')
    sheet = book.sheet_by_index(0)
    nested_list = [[cell.value for cell in sheet.row_slice(row_num)] for row_num in range(sheet.nrows)]

    # trim the extracted data: 
    # index of the starting row is 2 for 2009, 1 otherwise
    starting_row_idx = (2 if year == 2009 else 1)
    nested_list = nested_list[starting_row_idx:]
    
    # convert the date (string) in the 1st column to datetime
    for idx, row in enumerate(nested_list):
        
        # skip the row for the column names
        if idx == 0:
            continue
            
        date_cell = nested_list[idx][0]
        nested_list[idx][0] = datetime.datetime(*xlrd.xldate_as_tuple(date_cell, book.datemode))
    
    nested_array = np.array(nested_list)
    return nested_array

def sheet_array_to_df(nested_array, site_id):
    """
    Convert a 2D array containing values of a worksheet to DataFrame.
    - inputs:
        - nested_array (2D numpy array)
        - site_id: NAPS Site ID (int)
    - output: datafile (pandas DataFrame)
    """
    # set the column names
    datafile = pd.DataFrame(data=nested_array[1:], columns=nested_array[0])
    # datafile.columns.name = None
    datafile.reset_index(drop=True, inplace=True)
    
    # Note: some rows do not contain Site ID and need to be filled
    datafile.iloc[1:, datafile.columns.get_loc('NAPS ID')] = site_id
    datafile = datafile.iloc[1:, :].astype({'NAPS ID': 'int'})
    
    return datafile


def sheet_df_to_metal_df(datafile, analyte_type):
    """
    Convert a 2D array which contains a worksheet data to the DataFrame for metal data
    - input:
        - datafile: DataFrame containing rows which contains cells
        - analyte_type: 'NT' for Near Total or 'WS' for Water-soluble (string)
    - output:
        datafile: pandas DataFrame
    """
    datafile = rename_columns(datafile)
    datafile['analyte_type'] = analyte_type
    datafile['sampler'] = None
    return datafile


def sheet_df_to_ion_df(datafile):
    """
    Convert a 2D array which contains a worksheet data to the DataFrame for ion data
    - input:
        - datafile: DataFrame containing rows which contains cells
    - output:
        datafile: pandas DataFrame
    """
    # change column names if it is 'D.L.' - replace it with a specific name
    # colloc = datafile.columns.get_loc('D.L.')
    # col_values = datafile.columns.values
    
    # for ii in range(len(col_values)):
    #     if colloc[ii] == True:
    #         col_values[ii] = col_values[ii - 1] + '-MDL'
    # datafile.columns = col_values
    
    datafile = rename_columns(datafile, COLUMN_NAMES_PRE_2010_IONS)
    
    datafile['analyte_type'] = 'total'
    datafile['sampler'] = None
    return datafile


def extract_ICPMS_measurements(meta_df, year, site_id):
    """
    Extract near-total and/or water-soluble data
    - inputs:
        meta_df: a DataFrame containing unique set of metadata for year, site_id, and instrument=ICPMS
        year: a year of data (int)
        site_id: NAPS site ID (int)
    """
    datafile = pd.DataFrame()
    
    for idx, row in meta_df.iterrows():
        
        file_path_metal = get_raw_file_path(year, site_id, 'ICPMS', row['analyte_type'])
        metal_vals = extract_sheet_values(file_path_metal, year)
        sheet_df = sheet_array_to_df(metal_vals, site_id).reset_index(drop=True)
        metal_df = sheet_df_to_metal_df(sheet_df, row['analyte_type']).reset_index(drop=True)
        
        logger.debug(f'\t{ file_path_metal[file_path_metal.rindex("/") + 1:] }')
        
        # concatenate NT and WS data from one site
        # *** note some of the columns in the two DataFrames are different, so ignore_index=True is needed
        datafile = pd.concat([datafile, metal_df], axis=0, ignore_index=True)

    if len(datafile) > 0:
        datafile.to_csv(str(PROCESSED_DIR) + '/' + str(year) + '_' + str(site_id) + '.csv', index = False)


def extract_IC_measurements(meta_df, year, site_id):
    """
    Extract ion data and save it as a file
    - inputs:
        meta_df: a DataFrame containing unique set of metadata for year, site_id, and instrument=IC
        year: a year of data (int)
        site_id: NAPS site ID (int)
    """
    if (len(meta_df) > 0):
        
        file_path_ion = get_raw_file_path(year, site_id, 'IC')
        
        ion_vals = extract_sheet_values(file_path_ion, year)
        sheet_df = sheet_array_to_df(ion_vals, site_id)
        ion_df = sheet_df_to_ion_df(sheet_df)
        
        logger.debug(f'\t{ file_path_ion[file_path_ion.rindex("/") + 1:] }')
        
        ion_df.to_csv(str(PROCESSED_DIR) + '/' + str(year) + '_' + str(site_id) + '_IC.csv', index = False)


def extract_pre_2010():
    """
    Extract data between 2003 and 2009
    """
    ensure_directory_exists(PROCESSED_DIR)
    # unique site list for the year
    index_df = pd.read_csv(INDEX_CSV)
    unique_combinations = index_df[['year', 'site_id', 'analyte_type', 'instrument']].drop_duplicates()
    unique_combinations.reset_index(drop=True, inplace=True)
    
    for year in list(range(2003, 2010)):
    
        logger.info(f'Start extracting PM2.5-Speciation data of {year}')

        unique_sites_in_year = unique_combinations[unique_combinations['year'] == year]
        site_ids = unique_sites_in_year['site_id'].unique()
        
        for site_id in site_ids:
            site_df = unique_sites_in_year[unique_sites_in_year['site_id'] == site_id]

            # extract trace metal data
            icpms_df = site_df[site_df['instrument'] == 'ICPMS'].copy()
            extract_ICPMS_measurements(icpms_df, year, site_id)
            
            # extract ions data
            ion_df = site_df[site_df['instrument'] == 'IC'].copy()
            extract_IC_measurements(ion_df, year, site_id)
    
        logger.info(f'Completed extracting data of {year}')
