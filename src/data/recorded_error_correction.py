import pandas as pd

def modify_error_2009_voc_at_60211(df):
    """
    The last two 'Sample Date' rows were wrong in 2009 data of site 60211
    (not in the first column, which is 'Compounds'). This code corrects them.
    """
    df.reset_index(inplace=True)
    df['Sample Date'] = df['Sample Date'].replace(pd.to_datetime('1909-12-21'), pd.to_datetime('2009-12-21'))
    df['Sample Date'] = df['Sample Date'].replace(pd.to_datetime('1909-12-27'), pd.to_datetime('2009-12-27'))
    df.set_index('Sample Date', inplace=True)
    return df