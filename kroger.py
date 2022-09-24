# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 17:11:06 2022

@author: afisher
"""

import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import numpy as np
import os
import base64
import time
from bs4 import BeautifulSoup
import concurrent.futures
from datetime import datetime

# TO IMPLEMENT:
    # Clean up '?' in endpoitns...


class Kroger():
    def __init__(self):
        # API constants
        self.REDIRECT_URI = 'https://localhost/'
        self.CLIENT_ID = os.environ['KROGER_CLIENT_ID']
        self.CLIENT_SECRET = os.environ['KROGER_CLIENT_SECRET']
        self.RALPHS_ID = '70300044'
        
        # API endpoints
        self.api = "https://api.kroger.com/v1"
        self.oauth2_endpoint = self.api + '/connect/oauth2/authorize?'
        self.access_token_endpoint = self.api + '/connect/oauth2/token'
        self.products_endpoint = self.api + '/products'
        self.locations_endpoint = self.api + '/locations?'
        self.profile_endpoint = self.api + '/identity/profile'
        
        
        # Get tokens
        self.get_client_access_token()
        self.update_product_data()
        
    def get_client_access_token(self):
        byte_str = ('%s:%s' % (self.CLIENT_ID, self.CLIENT_SECRET)).encode()
        self.client_token = base64.b64encode(byte_str).decode()

        headers = {
            'Content-Type':'application/x-www-form-urlencoded',
            'Authorization':'Basic %s'%(self.client_token)
            }
        data = 'grant_type=client_credentials&scope=product.compact'
        
        r = requests.post(self.access_token_endpoint, headers=headers, data=data)
        self.client_access_token = r.json()['access_token']
        return
    
    
    def get_product_by_id(self, ID):
        headers = {
            'Authorization':'Bearer %s' % (self.client_access_token),
            'Cache-Control':'no-cache'
            }
        url = self.products_endpoint + '%s?filter.locationId=%s' % (ID, self.RALPHS_ID)
        r = requests.get(url, headers=headers)
        return r.json()['data']
    
    
    
    def load_product_list(self):
        if not os.path.exists('product_list.csv'):
            self.create_product_list()
            
        df = pd.read_csv('product_list.csv', dtype={'ID':str})
        self.IDs = df.ID.values
        self.product_list = df.set_index('ID').squeeze()
        return
        
    def load_product_data(self):
        if os.path.exists('product_data.csv'):
            self.product_data = pd.read_csv('product_data.csv', index_col=[0,1])
        else:
            categories = ['inventory','price','sale_price']
            index = pd.MultiIndex.from_product([[],categories])
            self.product_data = pd.DataFrame(index=index, columns=self.IDs)
        return
    
    

    def create_product_list(self):
        # Parse product IDs from cart html
        links = []
        with open('cart.txt','r') as f:
            for tag in BeautifulSoup(f.read(), 'html.parser').findAll('a'):
                if 'href' and 'class' in tag.attrs.keys():
                    if 'kds-Link--implied' and 'ProductDescription-truncated' in tag.attrs['class']:
                        links.append(tag.attrs['href'])
        
        # Desired links of form: href="/p/Description/ID"
        IDs = [link.split('/')[3] for link in links if link.split('/')[3].isdigit()]
        print(f'Found IDs: {len(IDs)}')
        IDs = IDs[:5] #limit calls while troubleshooting
        
        # Get product names
        def get_product_name(ID):
            return self.get_product_by_id(ID)['description']
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            names = executor.map(get_product_name, IDs)
        
        # Save product_list.csv
        df = pd.Series(data=names, index=IDs, name='name')
        df.index.name = 'ID'
        df.to_csv('product_list.csv')
        

    
    def update_product_data(self):
        self.load_product_list()
        self.load_product_data()
        pd = self.product_data
        
        date = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        if date in pd.index.get_level_values(level=0):
            print('Prices already checked today')
            return
        
        def read_product_data(ID):
            data = self.get_product_by_id(ID)['items'][0]
            
            if 'inventory' in data.keys():
                stock_level = data['inventory']['stockLevel']
                pd.loc[(date,'inventory'),ID] = stock_level
                
            if 'price' in data.keys():
                price = data['price']['regular']
                sale_price = data['price']['promo']
                pd.loc[(date,'price'),ID] = price
                pd.loc[(date,'sale_price'),ID] = sale_price
                
            return 

        # Call for product description using multithreading
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(read_product_data, self.IDs)
            
        pd.to_csv('product_data.csv')


if __name__=='__main__':
    Kroger()



