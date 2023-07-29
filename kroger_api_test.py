# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 15:09:31 2023

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
 
class Kroger_test():
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
        
        self.get_client_access_token()
        
    def load_product_list(self):
        if not os.path.exists('product_list.csv'):
            self.create_product_list()
            
        df = pd.read_csv('product_list.csv', dtype={'ID':str})
        self.IDs = df.ID.values
        self.product_list = df.set_index('ID').squeeze()
        return
    
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
    

if __name__=='__main__':
    k = Kroger_test()
    ID = '0001111058739'
    data = k.get_product_by_id(ID)['items'][0]
    