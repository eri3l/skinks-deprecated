"""
search with toes. Making a toes col from Les' magic spreadsheet

NB! Lots of manual notes in xls cells, such as "LFnearly/claw/tip/nail/kink/tip", "white dot", "crippled"
Main search should exclude above because they shoulnd't come up as "toes missing"
Could remove them and then add a separate df for "notes" search

now: if !(toes_combination), set as None
one more line
"""
import pandas as pd
import numpy as np
import itertools
from itertools import chain



def make_toes_col(filename, sheetname):
    
    df = pd.read_excel(filename, sheetname)
    
    df.rename(columns={"Skink No.": "ID"}, inplace=True)      # make sure ID matches master df 

    #-- 1. replace all comments entries with NAN
    df1 = df.drop('ID', axis=1)
    allowed_vals = list(df1.columns.values)    
    df1[~df1.isin(allowed_vals)] = np.nan
    # TODO: should be checking if chars and then remove. 
    #--- remove chars from ID col. 
    df.ID = df.ID.str[1:]
    df['ID'] = df['ID'].astype(int)
    
    
    #-- 2. create one column, "Toes"
    #--- change "None" to nan
    #df1.apply(lambda x: ','.join(x.dropna()), axis=1)    # drop NANs
    df1['Toes'] = df1.apply(lambda x: ','.join(x.dropna()), axis=1) 
    # FIXME: it works ok, but the above also gives empty records
    #--- merge
    df =  pd.merge(df1, df.ID, left_index=True, right_index=True, how='outer')
    #-- 3. Tidy up
    df = df[['Toes', 'ID']]
    df = df.sort_values(by='ID')
    
    #-- 3. Tidy up
    # remove unnecessary cols
    df = df[['Toes', 'ID']]
    
    #--- sort by ID
    df = df.sort_values(by='ID')
    
    #-- 4. Merge back to master df
    df_master = pd.read_csv("skinks_clean05.csv", converters={'Trap': eval})
    df_master['Sex'] = df_master['Sex'].astype(str)
    df_merged = df_master.merge(df, how='left')
    
    # NB! replace empty str with NAN with a regex
    df_merged = df_merged.replace(r'^\s*$', np.nan, regex=True)

    return df_merged

df = make_toes_col("data/toes_with_notes.xlsx", "Toes minus Akld Zoo skinks")

def search(df):
    #-------- toes search
    '''
    Si.Toes = ['LF1', 'LF2']
    search * where ['LF1', 'LF2'] NOT IN Sn.Toes
    '''
    
    ''' NB! 
        2. convert str to list
        1. convert nan to list 
    '''
    df['Toes'] = df['Toes'].str.strip('()').str.split(',')
    df.loc[df['Toes'].isnull(),['Toes']] = df.loc[df['Toes'].isnull(), 'Toes'].apply(lambda x: [])
    
    # a = df.loc[df.Toes.map(set(['LF1', 'LF2']).issubset)]
    
    #--- testcases
    #toes = ['LF1', 'LF2']
    toes = ['LR1', 'LR2', 'LR3', 'LR4', 'LR5', 'RR2', 'RR3', 'RR4', 'RR5']  # id = 45
    #toes = ['LF2', 'LF3', 'RF3', 'RF4', 'LR2', 'LR3', 'LR4', 'LR5', 'RR1']  # id = 353
    
    
    #--- end testcases
    #a = df.loc[df.Toes.map(set(['LF1', 'LF2']).issubset)]
    res = df.loc[df.Toes.apply(lambda x: bool(set(x).intersection( list(toes) )))]
    
    #c = df.loc[df.Toes.isin(['LF1', 'LF2'])]
    
    return res

result = search(df)

