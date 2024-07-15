
def get_unzipped_dir_for_carbonyl(year):
    if year < 2016:
        return str(year) + '/CARBONYLS/'
    else:
        return str(year) + '/CARBONYLS-CARBONYLES-HAP/'


def get_unzipped_dir_for_pah(year):
    if year < 2015:
        return str(year) + '/PAH/'
    elif year == 2015:
        return str(year) + '/2015_PAH/'
    else:
        return str(year) + '/PAH-HAP/'


def get_unzipped_dir_for_voc(year):
    if year < 2016:
        return str(year) + '/VOC/'
    else:
        return str(year) + '/VOC-COV/'


def get_unzipped_dir_for_pm25speciation(year):
    if year < 2010:
        return str(year) + '/SPECIATION/'
    
    elif any(year == x for x in [2010, 2011, 2012, 2014, 2015, 2016, 2018]):
        return str(year) + '/PM2.5/'
        
    elif year == 2013:
        return str(year) + '/PM2.5/PM2.5/'
    
    elif year == 2017:
        return str(year) + '/' + str(year) + '_IntegratedPM2.5-PM2.5Ponctuelles/PM2.5/'
    
    else:  # for 2019
        return str(year) + '/' + str(year) + '_IntegratedPM2.5-PM2.5Ponctuelles/'


def get_unzipped_directory_for_year(year, species_category=None):
    '''
    Return a directory name of an unzipped file. The paths depend on how 
    the zip file was created by the ECCC, so they differ across years.
    - input: year (int)
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
