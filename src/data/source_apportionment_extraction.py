import datetime
import numpy as np
import pandas as pd
from pathlib import Path
from src.data.archive_structure_parser import get_unzipped_directory_for_year
from src.data.continuous_pm25_operation import *
from src.data.file_operation import ensure_directory_exists, get_processed_file_path
from src.data.index_query import get_years_for_site, get_metadata
from src.data.text_transforms import convert_micro_to_nano, get_abbreviation_dict, remove_parentheses
from src.utils.logger_config import setup_logger
from src.config import PROCESSED_DIR, ABBREVIATION_CSV

logger = setup_logger('data.source_apportionment_extraction', 'source_apportionment_extraction.log')

def omit_blanks(df):
    """
    Return a DataFrame which excludes Field Blank and Travel Blank.
    - inputs:
        - df: a DataFrame
    - output: regular_measurements_df: a DataFrame which contains only regular measurements
    """
    regular_measurements_df = df[df['sampling_type'] == 'R'].copy()    
    return regular_measurements_df


def omit_error_in_continuous_data(df, analyte):
    """
    Return a DataFrame which excludes error measurements in integrated data.
    Empty values and any values less than 0 is considered as error. *0 is valid.*
    - inputs: 
        - df: a DataFrame
        - analyte: a full name of analyte (string)
    - output: non_error_df: a DataFrame without error measurements
    """
    non_error_df = df[(df[analyte] is not None) & (df[analyte] >= 0)]
    return non_error_df


def omit_error_in_integrated_data(df, analyte):
    """
    Return a DataFrame which excludes error measurements in integrated data.
    Empty values and any values less than or equal to 0 is considered as error.
    - inputs: 
        - df: a DataFrame
        - analyte: a full name of analyte (string)
    - output: non_error_df: a DataFrame without error measurements
    """
    non_error_df = df[(df[analyte] is not None) & (df[analyte] > 0)]
    return non_error_df


def omit_nylon_filter(df):
    """
    Return a DataFrame which excludes Nylon filter-measured data
    - inputs:
        - df: a DataFrame
    - output: teflon_df: a DataFrame which contains only Teflon filter-measured data
    """

    # 'Media' column contains information about filtre types
    if 'Media' in df.columns:
        teflon_df = df[df['Media'] == 'T'].copy()
        return teflon_df
    
    # If there is no 'Media' column, assume all values were measured with Teflon filtre
    else:
        return df


def create_dir_for_pmf(target_site_id):
    """
    Create a directory to save data sets for a particular site for source apportionment
    - input: target_site_id: NAPS site ID (int)
    - output: pmf_dir: directory path (string) to the data set
    """
    pmf_dir = str(PROCESSED_DIR) + '/' + str(target_site_id) + '_for_PMF'
    ensure_directory_exists(Path(pmf_dir))
    return pmf_dir


def create_nt_analyte_files(target_site_id):
    """
    Create a set of files containing Near Total metal concentrations with MDL 
    for a specified site.
    - input: target_site_id: NAPS site ID (int)
    - output: (saving a CSV file for each analyte)
    """
    pmf_dir = create_dir_for_pmf(target_site_id)

    abb_dict = get_abbreviation_dict()
    
    nt_analyte_array = get_metadata(site_ids=[target_site_id], analyte_type='NT')['analyte'].unique()
    
    for nt_analyte in nt_analyte_array:
        logger.debug(f'NT analyte: {nt_analyte}')
        analyte_df = pd.DataFrame() 
        
        years = get_years_for_site(target_site_id, nt_analyte, 'NT')
        mdl_col_name = abb_dict[nt_analyte] + '-MDL'
        
        for year in years:
            # load NT data for a specified year and site
            file_path = get_processed_file_path(year, target_site_id, 'ICPMS')
            file_df = pd.read_csv(file_path)
            nt_df = file_df[file_df['analyte_type'] == 'NT']
            
            # if a column with the analyte name exists
            if nt_analyte in nt_df.columns:
                teflon_df = omit_nylon_filter(nt_df)
                regular_df = omit_blanks(teflon_df)
                non_error_df = omit_error_in_integrated_data(regular_df, nt_analyte)
                extracted_df = non_error_df[['sampling_date', nt_analyte, mdl_col_name]]
    
                # if the number of extracted rows > 0, the year's data will be concatnated
                if len(extracted_df) > 0:
                    analyte_df = pd.concat([analyte_df, extracted_df], ignore_index=True).reset_index(drop=True)
        
        if len(analyte_df) > 0:
            analyte_df.to_csv(pmf_dir + '/NT_' + nt_analyte + '.csv', index=False)


def create_PM25_file(target_site_id):
    """
    Create a file containing continuous PM2.5 data which will be downsampled 
    from hourly to daily data for a specified site.
    - input: target_site_id: NAPS site ID (int)
    - output: (saving a CSV file)
    """
    pmf_dir = create_dir_for_pmf(target_site_id)
    
    continuous_hourly_df = get_continuous_pm25_data(target_site_id, 'all')
    non_error_continuous_hourly_df = omit_error_in_continuous_data(continuous_hourly_df, 'PM2.5')
    
    continuous_daily_df = non_error_continuous_hourly_df.resample('D').mean()
    
    pm25_df = continuous_daily_df['PM2.5'].copy()
    
    if len(pm25_df) > 0:
        pm25_df.to_csv(pmf_dir + '/PM2.5_continuous.csv')


def create_PM25_file_old(target_site_id):
    """
    Create a file containing PM2.5 data mesured by Sampler 1
    with MDL for a specified site.
    - input: target_site_id: NAPS site ID (int)
    - output: (saving a CSV file)
    """
    pmf_dir = create_dir_for_pmf(target_site_id)
    
    nt_years = get_metadata(site_ids=[target_site_id], analyte_type='NT')['year'].unique()
    
    pm25_df = pd.DataFrame()
    
    for year in nt_years:
        logger.debug(f'PM2.5 in {year}')
        
        file_path = get_processed_file_path(year, target_site_id, 'ICPMS')
        file_df = pd.read_csv(file_path)
        nt_df = file_df[file_df['analyte_type'] == 'NT']

        teflon_df = omit_nylon_filter(nt_df)
        non_error_df = omit_error_in_integrated_data(teflon_df, 'PM2.5')
        
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
            regular_df = omit_blanks(non_error_df)
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
    pmf_dir = create_dir_for_pmf(target_site_id)
    
    abb_dict = get_abbreviation_dict()
    
    ion_array = get_metadata(site_ids=[target_site_id], analyte_type='total')['analyte'].unique()
    
    for ion in ion_array:
        logger.debug(f'Ion: {ion}')
        ion_df = pd.DataFrame() 
        
        years = get_years_for_site(target_site_id, ion, 'total')
        mdl_col_name = abb_dict[ion] + '-MDL'
        
        for year in years:
            # load ion data for a specified year and site
            file_path = get_processed_file_path(year, target_site_id, 'IC')
            file_df = pd.read_csv(file_path)            
            ic_df = file_df[file_df['analyte_type'] == 'total']
            
            # if a column with the ion name exists
            if ion in ic_df.columns:
                teflon_df = omit_nylon_filter(ic_df)
                regular_df = omit_blanks(teflon_df)
                non_error_df = omit_error_in_integrated_data(regular_df, ion)
                extracted_df = non_error_df[['sampling_date', ion, mdl_col_name]]
    
                # unit conversion: micro gram -> nano gram
                extracted_df = convert_micro_to_nano(extracted_df, [ion, mdl_col_name])
                
                # if the number of extracted rows > 0
                if len(extracted_df) > 0:
                    ion_df = pd.concat([ion_df, extracted_df], ignore_index=True).reset_index(drop=True)
        
        if len(ion_df) > 0:
            ion_df.to_csv(pmf_dir + '/ion_' + ion + '.csv', index=False)
