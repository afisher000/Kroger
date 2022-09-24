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

# TO IMPLEMENT:
    # Current goal is just getting all call types figured out
    # Later I can restructure code with function inputs
    # How to deal with null results entries?

class Kroger():
    def __init__(self):
        # API constants
        self.REDIRECT_URI = 'https://localhost/'
        self.CLIENT_ID = os.environ['KROGER_CLIENT_ID']
        self.CLIENT_SECRET = os.environ['KROGER_CLIENT_SECRET']
        self.EMAIL = os.environ['STRAVA_ANDREW_EMAIL']
        self.PASSWORD = os.environ['STRAVA_ANDREW_PASSWORD']
        self.ANDREW_KROGER_ID = '817a3d19-7353-5b0b-8e2d-48e87011d6f7'
        
        # API endpoints
        self.api = "https://api.kroger.com/v1"
        self.oauth2_endpoint = self.api + '/connect/oauth2/authorize?'
        self.access_token_endpoint = self.api + '/connect/oauth2/token'
        self.products_endpoint = self.api + '/products?'
        self.locations_endpoint = self.api + '/locations?'
        self.profile_endpoint = self.api + '/identity/profile'
        
        
        # Get tokens
        self.get_client_access_token()
        # self.get_customer_access_token()
        
    def create_database(self):
        # Read products from cart
        with open('cart.txt','r') as f:
            html = f.read() 
            soup = BeautifulSoup(html, 'html.parser')
        
        links = []
        for tag in soup.findAll('a'):
            if 'href' and 'class' in tag.attrs.keys():
                if 'kds-Link--implied' and 'ProductDescription-truncated' in tag.attrs['class']:
                    links.append(tag.attrs['href'])
        
        IDs = [link.split('/')[3] for link in links if link.split('/')[3].isdigit()]
        
        headers = {
            'Authorization':f'Bearer {self.client_access_token}',
            'Cache-Control':'no-cache'
            }
        
        names = []
        for ID in IDs[:5]:
            url = self.products_endpoint[:-1] + '/' + ID + '?'
            print(f'URL:{url}')
            r = requests.get(url, headers=headers).json()
            print(f"{r['data']['description']}")
            names.append(r['data']['description'])
            
        self.db_products = pd.Series(data=names, index=IDs[:5])
        
    def get_customer_access_token(self):
        self.authenticate_customer()
        
        headers = {
            'Content-Type':'application/x-www-form-urlencoded',
            'Authorization':f'Basic {self.client_token}'
            }
        
        params = {
            'grant_type':'authorization_code',
            'code':self.customer_oauth2_token,
            'redirect_uri':self.REDIRECT_URI
            }
        data = '&'.join(['='.join([key,value]) for key, value in params.items()])
        r = requests.post(self.access_token_endpoint, headers=headers, data=data).json()
        self.customer_refresh_token = r['refresh_token']
        self.customer_access_token = r['access_token']
        return
        
    def get_client_access_token(self):
        self.client_token = base64.b64encode(f'{self.CLIENT_ID}:{self.CLIENT_SECRET}'.encode()).decode()
        
        # Get access token
        headers = {
            'Content-Type':'application/x-www-form-urlencoded',
            'Authorization':'Basic %s'%(self.client_token)
            }
        
        params = {
            'grant_type':'client_credentials',
            'scope':'product.compact'
            }
        data = '&'.join(['='.join([key,value]) for key, value in params.items()])
        r = requests.post(self.access_token_endpoint, headers=headers, data=data)
        self.client_access_token = r.json()['access_token']
        return
        
    def get_profile_id(self):
        headers = {
            'Authorization': 'Bearer %s' %(self.customer_access_token),
            'Cache-Control':'no-cache'
            }
        r = requests.get(self.profile_endpoint, headers=headers)
        return r.json()['data']['id']
        
   
    def get_product_name(self, productID):
        headers = {
            'Authorization':f'Bearer {self.client_access_token}',
            'Cache-Control':'no-cache'
            }
        
        params = {
            'id':productID
            }
        url = self.products_endpoint + '&'.join(['='.join([key,value]) for key,value in params.items()])
        r = requests.get(url, headers=headers).json()
        
        
        
        return
    
    def get_products(self, ID='70300044'):
        # Get Products
        headers = {
            'Authorization':f'Bearer {self.client_access_token}',
            'Cache-Control':'no-cache'
            }
        
        params = {
            'filter.locationId':str(ID),
            'filter.term':'milk',
            'filter.limit':'10'
            }
        url = self.products_endpoint + '&'.join(['='.join([key,value]) for key,value in params.items()])
        r = requests.get(url, headers=headers).json()
        products = r['data']
        self.products = products
        
        data = {}
        for prod in products:
            data[prod['productId']] = {
                'name':prod['description'],
                'sale_price':prod['items'][0]['price']['promo'],
                'reg_price':prod['items'][0]['price']['regular'],
                'size':prod['items'][0]['size']
            }
        pd.DataFrame(data).T.to_csv('products.csv')
        
        
    def get_locations(self, zipcode='90049'):
        # Get Locations
        headers = {
            'Authorization':f'Bearer {self.client_access_token}',
            'Cache-Control':'no-cache'
            }
        
        params = {
            'filter.zipCode.near':str(zipcode)
            }
        url = self.locations_endpoint + '&'.join(['='.join([key,value]) for key,value in params.items()])
        r = requests.get(url, headers=headers).json()
        locations = r['data']

        data = {}
        self.locations = locations
        for loc in locations:
            # Not all locations might have every entry... how to deal with null
            data[loc['locationId']] = {
                'name':loc['name'],
                'address':loc['address']['addressLine1'],
                'lat':loc['geolocation']['latitude'],
                'lng':loc['geolocation']['longitude']
            }
        pd.DataFrame(data).T.to_csv('locations.csv')
        return
    
    def authenticate_customer(self):
        # Build oauth url
        headers = {
            'Content-Type':'application/x-www-form-urlencoded'
            }
        params = {
                'scope':'profile.compact',
                'response_type':'code',
                'client_id':self.CLIENT_ID,
                'redirect_uri':self.REDIRECT_URI
                }
        url = self.oauth2_endpoint + '&'.join([key+'='+value for key,value in params.items()])
        
        print(f'Authorization URL: {url}')
        self.customer_oauth2_token = input('Enter redirect URL: ').split('code=')[1]
        
        return 

if __name__=='__main__':
    a = Kroger()



