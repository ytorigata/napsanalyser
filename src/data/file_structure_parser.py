
def get_datetime_col_name_pah(year):
    if year < 2006:
        return 'COMPOUNDS'
    elif year == 2006:
        return 'Compounds'
    elif year < 2010:
        return 'COMPOUNDS'
    else:
        return 'Sampling Date'


def get_datetime_col_name_voc(year):
    return 'Sample Date' if year < 2014 else 'Sampling Date'


def get_datetime_col_name(year, species_category=None):
    
    if species_category == 'pah':
        return get_datetime_col_name_pah(year)
        
    elif species_category == 'voc':
        return get_datetime_col_name_voc(year)
        
    
def get_skipping_row_pah(year):
    if year < 2010:
        return 2
    else:
        return 9
        

def get_skipping_row_voc(year):
    if year < 2008:
        return 1
    elif year < 2014:
        return 2
    elif year < 2018:
        return 0
    else:
        return 8


def get_skipping_row(year, species_category=None):
    
    if species_category == 'pah':
        return get_skipping_row_pah(year)
        
    elif species_category == 'voc':
        return get_skipping_row_voc(year)


def get_worksheet_name_pah(year, site_id):
    if year < 2010:
        return 0
    else:
        return 'PAH (TP+G)'


def get_worksheet_name_voc(year, site_id):
    if year < 2014:
        return 0
    elif year < 2018:
        return 'Data'
    elif year >= 2018:
        return 'VOC'


def get_worksheet_name(year, site_id, species_category=None):
    
    if species_category == 'pah':
        return get_worksheet_name_pah(year, site_id)
        
    elif species_category == 'voc':
        return get_worksheet_name_voc(year, site_id)
