# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 17:11:06 2022

@author: afisher
"""
# %%
import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import numpy as np
import os
import base64
import time
import concurrent.futures
from datetime import datetime

# TO IMPLEMENT:
    # When product_data.csv is saved, it changes dates to string and ID to int.


# API constants
REDIRECT_URI = 'https://localhost/'
CLIENT_ID = os.environ['KROGER_CLIENT_ID']
CLIENT_SECRET = os.environ['KROGER_CLIENT_SECRET']
RALPHS_ID = '70300044'

# API endpoints
api = "https://api.kroger.com/v1"
oauth2_endpoint = api + '/connect/oauth2/authorize?'
access_token_endpoint = api + '/connect/oauth2/token'
products_endpoint = api + '/products'
locations_endpoint = api + '/locations?'
profile_endpoint = api + '/identity/profile'


# Get client access token
byte_str = f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()
client_token = base64.b64encode(byte_str).decode()

headers = {
    'Content-Type':'application/x-www-form-urlencoded',
    'Authorization':f'Basic {client_token}'
    }
data = 'grant_type=client_credentials&scope=product.compact'

r = requests.post(access_token_endpoint, headers=headers, data=data)
client_access_token = r.json()['access_token']


# Search products
query = 'milk'
headers = {
    'Authorization':f'Bearer {client_access_token}',
    'Cache-Control':'no-cache'
    }

url = products_endpoint + f'?filter.term=milk&filter.locationId={RALPHS_ID}'
r = requests.get(url, headers=headers)


# Search specific product ID
# headers = {
#     'Authorization':f'Bearer {client_access_token}',
#     'Cache-Control':'no-cache'
#     }

# ID = '0001111009773'
# url = products_endpoint + f'{ID}?filter.locationId={RALPHS_ID}'
# r = requests.get(url, headers=headers)



# %%
