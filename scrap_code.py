# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 18:34:10 2022

@author: afisher
"""

self.ANDREW_KROGER_ID = '817a3d19-7353-5b0b-8e2d-48e87011d6f7'
if 'kds-Link--implied' and 'ProductDescription-truncated' in tag.attrs['class']:
    
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