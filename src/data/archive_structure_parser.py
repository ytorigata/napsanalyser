
def get_unzipped_directory_for_year(year):
    '''
    Return a directory name of an unzipped file. The paths depend on how 
    the zip file was created by the ECCC, so they differ across years.
    - input: year (int)
    - output: directory path (string) to files
    '''
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
