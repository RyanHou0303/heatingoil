import pandas as pd
import re

def make_valid_name(name:str)->str:

    name = name.replace('"','')
    name = name.replace(',','_')
    name = name.replace('#','_no')

    name = re.sub(r'[^0-9a-zA-Z_]', '_',name)

    if not re.match(r'^[A-Za-z_]',name):
        name = '_'+name
    return name

def ezread(fname,delimiter=','):
    df = pd.read_csv(fname,delimiter=delimiter)
    df.columns = [make_valid_name(c) for c in df.columns]
    return df