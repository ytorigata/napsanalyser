
def get_unzipped_dir_for_carbonyl(year):
    if year < 2016:
        return str(year) + '/CARBONYLS'
    else:
        return str(year) + '/CARBONYLS-CARBONYLES-HAP'


def get_unzipped_dir_for_pah(year):
    if year < 2015:
        return str(year) + '/PAH'
    elif year == 2015:
        return str(year) + '/2015_PAH/PAH'
    else:
        return str(year) + '/PAH-HAP'


def get_unzipped_dir_for_pm25speciation(year):
    if year < 2010:
        return str(year) + '/SPECIATION'
    
    elif any(year == x for x in [2010, 2011, 2012, 2014, 2015, 2016, 2018]):
        return str(year) + '/PM2.5'
        
    elif year == 2013:
        return str(year) + '/PM2.5/PM2.5'
    
    elif year == 2017:
        return str(year) + '/' + str(year) + '_IntegratedPM2.5-PM2.5Ponctuelles/PM2.5'
    
    else:  # for 2019
        return str(year) + '/' + str(year) + '_IntegratedPM2.5-PM2.5Ponctuelles'


def get_unzipped_dir_for_voc(year):
    if year < 2016:
        return str(year) + '/VOC'
    else:
        return str(year) + '/VOC-COV'


def get_unzipped_directory_for_year(year, species_category=None):
    '''
    Return a directory name of an unzipped file. The paths depend on how 
    the zip file was created by the ECCC, so they differ across years.
    - input:
        - year: year of data (int)
        - species_category: optional. carbonyl, pah, or voc (string)
    - output: directory path (string) to files
    '''
    if species_category is None:
        return get_unzipped_dir_for_pm25speciation(year)
    elif species_category == 'carbonyl':
        return get_unzipped_dir_for_carbonyl(year)
    elif species_category == 'pah':
        return get_unzipped_dir_for_pah(year)
    elif species_category == 'voc':
        return get_unzipped_dir_for_voc(year)


def get_unzipped_file_for_carbonyl(year, site_id):
    file_name = ''
    
    if year < 2018:
        file_name = f'S{site_id}_CARBONYLS_{year}_EN.XLS'
    
    else:  # year >= 2018
        # zero padding for 5-digit site IDs
        file_name = f'S0{site_id}_CARBONYLS_{year}_EN.xlsx' if site_id < 100000 else f'S{site_id}_CARBONYLS_{year}_EN.xlsx'
    
    return file_name


def get_unzipped_file_for_pah(year, site_id):
    file_name = ''
    
    if year < 2010:
        file_name = f'S{site_id}_PAH.XLS'
    elif year < 2016:
        file_name = f'S{site_id}_PAH_{year}.xlsx'
    else:
        file_name = f'S{site_id}_PAH_{year}_EN.xlsx'
    
    return file_name


def get_unzipped_file_for_pm25speciation(year, site_id):
    file_name = ''

    if year < 2016:
        file_name = f'S{site_id}_PM25_{year}.xlsx'
    else:  # after 2016, files have a suffix '_EN'
        file_name = f'S{site_id}_PM25_{year}_EN.xlsx'
    
    return file_name


def get_unzipped_file_for_voc(year, site_id):
    file_name = ''
    
    if year < 2014:
        lower_case_sites_2011 = [50115, 50121, 50129, 50133, 50134, 60427, 61007]
        if (year == 2011) & site_id in lower_case_sites_2011:
            file_name = f'S{site_id}_VOC.xls'
            
        elif (year == 2012) & site_id == 10102:
            file_name = 'S10102_VOCcorrectedfilename.XLS'
            
        elif (year == 2012) & site_id == 90228:
            # FYI: 90227, 90228, and 90230 are combined sites
            file_name = 'S90227(should be 90228)_VOC.XLS'
        else:
            file_name = f'S{site_id}_VOC.XLS'
    
    elif year < 2016:
        if (year in [2014, 2015]) & (site_id == 62601):
            file_name = f'S{site_id}_24hr_VOC_{year}.XLS'
        else:
            # zero padding for 5-digit site IDs
            file_name = f'S0{site_id}_VOC_{year}.XLS' if site_id < 100000 else f'S{site_id}_VOC_{year}.XLS'
    
    elif year < 2018:
        if (year in [2016, 2017]) & (site_id == 62601):
            file_name = f'S{site_id}_24hr_VOC_{year}_EN.XLS'
        else:
            file_name = f'S0{site_id}_VOC_{year}_EN.XLS' if site_id < 100000 else f'S{site_id}_VOC_{year}_EN.XLS'
    
    else:  # year >= 2018
        file_name = f'S0{site_id}_VOC_{year}_EN.xlsx' if site_id < 100000 else f'S{site_id}_VOC_{year}_EN.xlsx'
    
    return file_name


def get_unzipped_file(year, site_id, species_category=None):
    """
    Return an unzipped file name based on year, site, and species (option).
    - input:
        - year: year of data (int)
        - site_id: NAPS site ID (int)
        - species_category: optional. carbonyl, pah, or voc (string)
    - output: a file name (string)
    """
    file_name = ''
    
    if species_category is None:
        file_name = get_unzipped_file_for_pm25speciation(year, site_id)
            
    elif species_category == 'carbonyl':
        file_name = get_unzipped_file_for_carbonyl(year, site_id)
                
    elif species_category == 'pah':
        file_name = get_unzipped_file_for_pah(year, site_id)
            
    elif species_category == 'voc':
        file_name = get_unzipped_file_for_voc(year, site_id)
      
    return file_name

