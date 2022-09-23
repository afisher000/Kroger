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
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


# TO IMPLEMENT:
    # Current goal is just getting all call types figured out
    # Later I can restructure code with function inputs
    # How to deal with null results entries?

class Kroger():
    def __init__(self):
        self.CLIENT_ID = os.environ['KROGER_CLIENT_ID']
        self.CLIENT_SECRET = os.environ['KROGER_CLIENT_SECRET']
        self.EMAIL = os.environ['STRAVA_ANDREW_EMAIL']
        self.PASSWORD = os.environ['STRAVA_ANDREW_PASSWORD']
        self.token = base64.b64encode(f'{self.CLIENT_ID}:{self.CLIENT_SECRET}'.encode()).decode()
        self.get_access_token()
        
    def get_access_token(self):
        
        # Get access token
        url = "https://api-ce.kroger.com/v1/connect/oauth2/token"
        
        headers = {
            'Content-Type':'application/x-www-form-urlencoded',
            'Authorization':f'Basic {self.token}'
            }
        
        params = {
            'grant_type':'client_credentials',
            'scope':'product.compact'
            }
        data = '&'.join(['='.join([key,value]) for key, value in params.items()])
        r = requests.post(url, headers=headers, data=data)
        self.access_token = r.json()['access_token']
        return
        
    def get_products(self, ID='70300044'):
        # Get Products
        headers = {
            'Authorization':f'Bearer {self.access_token}',
            'Cache-Control':'no-cache'
            }
        
        url_stub = 'https://api-ce.kroger.com/v1/products?'
        params = {
            'filter.locationId':str(ID),
            'filter.term':'milk',
            'filter.limit':'10'
            }
        url = url_stub + '&'.join(['='.join([key,value]) for key,value in params.items()])
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
            'Authorization':f'Bearer {self.access_token}',
            'Cache-Control':'no-cache'
            }
        
        url_stub = 'https://api-ce.kroger.com/v1/locations?'
        params = {
            'filter.zipCode.near':str(zipcode)
            }
        url = url_stub + '&'.join(['='.join([key,value]) for key,value in params.items()])
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
    
    def get_oauth(self):
        # Build oauth url
        url_stub = 'https://api-ce.kroger.com/v1/connect/oauth2/authorize?'
        headers = {
            'Content-Type':'application/x-www-form-urlencoded'
            }
        params = {
                'scope':'profile.compact',
                'response_type':'code',
                'client_id':self.CLIENT_ID,
                'redirect_uri':'https://localhost/'
                }
        url = url_stub + '&'.join([key+'='+value for key,value in params.items()])
        self.url = url
        
        # # Use selenium to login and provide authorization to download activities
        driver = webdriver.Chrome(ChromeDriverManager().install()) 
        driver.get(url)
        driver.find_elements(by='id', value='username')[0].send_keys(self.EMAIL)
        driver.find_elements(by='id', value='password')[0].send_keys(self.PASSWORD)
        driver.find_elements(by='id', value='signin_button')[0].click()
        driver.find_elements(by='id', value='authorize')[0].click()
        #     response_url = driver.current_url
        
        return 

if __name__=='__main__':
    a = Kroger()
    a.get_oauth()


