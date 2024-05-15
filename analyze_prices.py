# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 12:25:55 2022

@author: afisher
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Inventory: 'HIGH','LOW','TEMPORARILY_OUT_OF_STOCK', or NaN

def clean_date(string):
    if string.find('-')==-1:
        return datetime.strptime(string, '%m/%d/%Y')
    return datetime.strptime(string, '%Y-%m-%d')
    

# Read product list
dl = pd.read_csv('product_list.csv', dtype={'ID':str})
IDs = dl.ID.values
dl = dl.set_index('ID').squeeze()
        
# Save to df, clean date, set index, pad column ids to 13 digits
df = pd.read_csv('product_data.csv')
df.Date = df.Date.apply(clean_date)
df.set_index(['Category','Date'], inplace=True)
df.columns = df.columns.str.zfill(13)


# # Extract true prices

reg_prices = df.loc['price'].replace('HIGH', '0').astype(float)
sale_prices = df.loc['sale_price'].astype(float)


prices = reg_prices.where(sale_prices==0, sale_prices) #replace with sale prices
weekly_prices = prices[prices.index.day_name()=='Wednesday']
weekly_prices.ffill().to_csv('weekly_prices.csv')

