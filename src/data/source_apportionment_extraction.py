import datetime
import numpy as np
import openpyxl
import os
import pandas as pd
from pathlib import Path
import xlrd
from src.data.archive_structure_parser import get_unzipped_directory_for_year
from src.data.file_operation import ensure_directory_exists
from src.data.index_query import get_years_for_site
from src.data.text_transforms import convert_micro_to_nano, get_abbreviation_dict, remove_parentheses
from src.utils.logger_config import setup_logger
from src.config import PROCESSED_DIR, ABBREVIATION_CSV, INDEX_CSV

logger = setup_logger('data.source_apportionment_extraction', 'source_apportionment_extraction.log')

def omit_blanks(df, year):
    """
    Return a DataFrame which excludes Field Blank and Travel Blank.
    - inputs:
        - df: a DataFrame
        - year: year of the data (int)
    - output: regular_measurements_df: a DataFrame which contains only regular measurements
    """
    regular_measurements_df = pd.DataFrame()
    if year < 2010:
        regular_measurements_df = df[(df['Cartridge'] != 'FB') & (df['Cartridge'] != 'TB')]
    else:
        regular_measurements_df = df[(df['sampling_type'] != 'FB') & (df['sampling_type'] != 'TB')]
        
    return regular_measurements_df


def omit_error_measurements(df, analyte):
    """
    Return a DataFrame which excludes error measurements. Empty values and any values 
    less than or equal to 0 is assumed as error.
    - inputs: 
        - df: a DataFrame
        - analyte: a full name of analyte
    - output: non_error_df: a DataFrame without error measurements
    """
    non_error_df = df[(df[analyte] is not None) & (df[analyte] > 0)]
    return non_error_df

def create_nt_analyte_files(target_site_id):
    """
    Create a set of files containing Near Total metal concentrations with MDL 
    for a specified site.
    - input: target_site_id: NAPS site ID (int)
    - output: (saving a CSV file for each analyte)
    """
    pmf_dir = str(PROCESSED_DIR) + '/' + str(target_site_id) + '_for_PMF'
    ensure_directory_exists(Path(pmf_dir))

    abb_dict = get_abbreviation_dict()

    index_df = pd.read_csv(INDEX_CSV)
    site_df = index_df[index_df['site_id'] == target_site_id]
    nt_analyte_array = site_df[site_df['analyte_type'] == 'NT']['analyte'].unique()
    
    for nt_analyte in nt_analyte_array:
        logger.debug(f'NT analyte: {nt_analyte}')
        analyte_df = pd.DataFrame() 
        
        years = get_years_for_site(target_site_id, nt_analyte, 'NT')
        mdl_col_name = abb_dict[nt_analyte] + '-MDL'
        
        for year in years:
            # load NT data for a specified year and site
            file_path = str(PROCESSED_DIR) + '/' + str(year) + '_' + str(target_site_id) + '.csv'
            file_df = pd.read_csv(file_path)
            nt_df = file_df[file_df['analyte_type'] == 'NT']
            
            # if a column with the analyte name exists
            if nt_analyte in nt_df.columns:
                regular_df = omit_blanks(nt_df, year)
                non_error_df = omit_error_measurements(regular_df, nt_analyte)
                extracted_df = non_error_df[['sampling_date', nt_analyte, mdl_col_name]]
    
                # if the number of extracted rows > 0, the year's data will be concatnated
                if len(extracted_df) > 0:
                    analyte_df = pd.concat([analyte_df, extracted_df], ignore_index=True).reset_index(drop=True)
        
        if len(analyte_df) > 0:
            analyte_df.to_csv(pmf_dir + '/NT_' + nt_analyte + '.csv', index=False)

def create_PM25_file(target_site_id):
    """
    Create a set of files containing PM2.5 data mesured by Sampler 1
    with MDL for a specified site.
    - input: target_site_id: NAPS site ID (int)
    - output: (saving a CSV file)
    """
    pmf_dir = str(PROCESSED_DIR) + '/' + str(target_site_id) + '_for_PMF'
    ensure_directory_exists(Path(pmf_dir))
    
    index_df = pd.read_csv(INDEX_CSV)
    site_df = index_df[index_df['site_id'] == target_site_id]
    nt_years = site_df[site_df['analyte_type'] == 'NT']['year'].unique()
    
    pm25_df = pd.DataFrame()
    
    for year in nt_years:
        logger.debug(f'PM2.5 in {year}')
        file_path = str(PROCESSED_DIR) + '/' + str(year) + '_' + str(target_site_id) + '.csv'
        file_df = pd.read_csv(file_path)
        nt_df = file_df[file_df['analyte_type'] == 'NT']
        
        non_error_df = omit_error_measurements(nt_df, 'PM2.5')
        
        regular_df = pd.DataFrame()
        if year < 2010:
            # no field blank were reported for 2003 - 2009 data
            regular_df = non_error_df
            
            # no MDL were reported for 2003 - 2009 data
            extracted_df = regular_df.loc[:, ['sampling_date', 'PM2.5']]
            extracted_df['PM2.5-MDL'] = None
    
            # unit conversion: micro gram -> nano gram
            extracted_df = convert_micro_to_nano(extracted_df, ['PM2.5'])
        else:
            regular_df = omit_blanks(non_error_df, year)
            extracted_df = regular_df[['sampling_date', 'PM2.5', 'PM2.5-MDL']]
            
            # unit conversion: micro gram -> nano gram
            extracted_df = convert_micro_to_nano(extracted_df, ['PM2.5', 'PM2.5-MDL'])
        
        # if the number of extracted rows > 0
        if len(extracted_df) > 0:
            if len(pm25_df) == 0:
                pm25_df = extracted_df
            else:
                pm25_df = pd.concat(
                    [pm25_df.astype(extracted_df.dtypes), extracted_df.astype(pm25_df.dtypes)], 
                    ignore_index=True).reset_index(drop=True)
    
    if len(pm25_df) > 0:
        pm25_df.to_csv(pmf_dir + '/PM2.5_Sampler1.csv', index=False)

def create_ion_files(target_site_id):
    """
    Create a set of files containing ion concentrations with MDL 
    for a specified site.
    - input: target_site_id: NAPS site ID (int)
    - output: (saving a CSV file for each ion)
    """
    pmf_dir = str(PROCESSED_DIR) + '/' + str(target_site_id) + '_for_PMF'
    ensure_directory_exists(Path(pmf_dir))
    
    abb_dict = get_abbreviation_dict()
    
    index_df = pd.read_csv(INDEX_CSV)
    site_df = index_df[index_df['site_id'] == target_site_id]
    ion_array = site_df[site_df['analyte_type'] == 'total']['analyte'].unique()
    
    for ion in ion_array:
        logger.debug(f'Ion: {ion}')
        ion_df = pd.DataFrame() 
        
        years = get_years_for_site(target_site_id, ion, 'total')
        mdl_col_name = abb_dict[ion] + '-MDL'
        
        for year in years:
            # load ion data for a specified year and site
            file_path = str(PROCESSED_DIR) + '/' + str(year) + '_' + str(target_site_id) + '_IC.csv'
            file_df = pd.read_csv(file_path)            
            ic_df = file_df[file_df['analyte_type'] == 'total']
            
            # if a column with the ion name exists
            if ion in ic_df.columns:
                regular_df = omit_blanks(ic_df, year)
                non_error_df = omit_error_measurements(regular_df, ion)
                extracted_df = non_error_df[['sampling_date', ion, mdl_col_name]]
    
                # unit conversion: micro gram -> nano gram
                extracted_df = convert_micro_to_nano(extracted_df, [ion, mdl_col_name])
                
                # if the number of extracted rows > 0
                if len(extracted_df) > 0:
                    ion_df = pd.concat([ion_df, extracted_df], ignore_index=True).reset_index(drop=True)
        
        if len(ion_df) > 0:
            ion_df.to_csv(pmf_dir + '/ion_' + ion + '.csv', index=False)
