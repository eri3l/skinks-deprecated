"""
Created on Feb 22 16:38:15 2021
@author: eriel

load source file and tidy up. 
"""

import pandas as pd

#--- 1. Load data
def load_and_clean(filename, sheet_name):
    
    df = pd.read_excel(filename, sheet_name)

    # use first row to name columns
    df.columns = df.iloc[0]
    # drop rows
    # TODO: FIXME: manual for now
    droplist = [0, 1, 31, 60, 90, 121, 151, 181, 210, 241, 273, 301, 327, 355, 384, 414, 446,478, 510, 542]
    df.drop(df.index[droplist], inplace=True)
    # drop rows with all NANs
    df.dropna(axis = 0, how = 'all', inplace = True)
    df.reset_index(inplace=True)
    # TODO: 
    df.drop(df.columns[[0, 11]], inplace=True, axis=1)
    
    #-- fix column title, types, contents
    df.rename(columns = {"Skink number": "ID", "Capture date": "Date",
                         "Weight (g)": "Weight", "SVL (mm)": "SVL",
                         "Tail length (mm)": "VTL", 'Recap?':'Recap',
                         'Toes missing': 'Toes_bool'}, inplace=True)
    
    #-- change dtypes
    print(df.isnull().sum())
    df.update(df[['ID', 'SVL', 'VTL']].fillna(0))
    df[['ID', 'SVL', 'VTL']] = df[['ID', 'SVL', 'VTL']].astype(int)
       
    df['Recap'] = df.Recap.map({'Recap':1, 'Recap ': 1})
    df.update(df['Recap'].fillna(0))
    df['Recap'] = df['Recap'].astype(bool)
    
    # rdict = {' ': ',', '  ': ','}
    # df['Trap'] = df['Trap'].replace(rdict)
    # NOTE: split on  ' ' or '  ' or ',')
    df['Trap'] = df['Trap'].str.split('\s+|,')
        
    cols = ['Regen', 'Weight']
    mask = df[cols].applymap(lambda x: isinstance(x, (int, float)))
    df[cols] = df[cols].where(mask)
    df.update(df['Regen'].fillna(0))
    df[cols] = df[cols].astype(float)
    
    df['Sex'] = df.Sex.map({'Juv.':'J', 'Juv': 'J', "juv":'J', "neonate": 'N', 'Neonate': 'N',
                            'M': 'M', 'M ': 'M', 'F': 'F', 'F ': 'F'})      # all else is nan
    df['Sex'] = df['Sex'].astype(str)
    
    df.update(df['Toes_bool'].fillna("intact"))
    #TODO: FIXME: hack for now
    
    df['Toes_orig'] = df['Toes_bool']
    allowed = ['intact', 'Intact']
    df.loc[~df['Toes_bool'].isin(allowed), 'Toes_bool'] = "toes missing"
    
    df['Date'] = pd.to_datetime(df['Date'])
    # add a Year col
    df['Year'] = pd.DatetimeIndex(df['Date']).year
    df.drop('Date', inplace=True, axis=1)
    
    return df

df = load_and_clean("data/les_skinks_chesterfield.xlsx", sheet_name="Excluding Akld Zoo - simplified")
# df.to_csv("skinks_clean01.csv")
