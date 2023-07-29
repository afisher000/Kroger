# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 12:25:55 2022

@author: afisher
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Inventory: 'HIGH','LOW','TEMPORARILY_OUT_OF_STOCK', or NaN

# Read product list
dl = pd.read_csv('product_list.csv', dtype={'ID':str})
IDs = dl.ID.values
dl = dl.set_index('ID').squeeze()
        
# Read product data
df = pd.read_csv('product_data.csv')
try:
    df.Date = df.Date.apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
except:
    df.Date = df.Date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
df.set_index(['Date','Category'], inplace=True)
df.columns = df.columns.str.zfill(13)

# Extract true prices
reg_prices = df.xs('price', level=1).applymap(float)
sale_prices = df.xs('sale_price', level=1).applymap(float)
inventory = df.xs('inventory', level=1)
prices = reg_prices.where(sale_prices==0, sale_prices) #replace with sale prices

# Plot price changes over time, see that sales occur weekly
for ID in IDs[sale_prices.max()>0]:
    prices[ID].plot()

# Print items currently on sale
sale_IDs = IDs[sale_prices.iloc[-1]!=0]
sale_df = df[sale_IDs].unstack().iloc[-1].unstack()[['price','sale_price']].applymap(float)

sale_df['price_drop'] = sale_df.price-sale_df.sale_price
sale_df['pct_change'] = np.round(sale_df.price_drop/sale_df.price, 2)
sale_df.sort_values(by='pct_change', inplace=True, ascending=False)
sale_df['name'] = dl[sale_df.index]
sale_df.to_csv('current sales.csv')

