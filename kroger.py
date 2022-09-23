# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 17:11:06 2022

@author: afisher
"""

import requests
import pandas as pd
import numpy as np
import os
import base64

KROGER_CLIENT_ID = 	'fisherapp-810ed94bb3031d24190dfab97eec595127595016183935257062'
KROGER_CLIENT_SECRET = 'tslNxndNdmTJoTOxPuPMbQVsSUpL1tBCAEHT-26E2'



# # Build oauth url
# oauth_stub = 'https://www.strava.com/oauth/authorize?'
# params = {
#         'client_id':os.environ['STRAVA_CLIENT_ID'],
#         'redirect_uri':'https://localhost/',
#         'response_type':'code',
#         'scope':'activity:read_all'
#         }
# oauth_url = oauth_stub + '&'.join([key+'='+value for key,value in params.items()])


# # Build post_request url
# post_request_stub = 'https://www.strava.com/oauth/token?'
# params = {
#     'client_id':os.environ['STRAVA_CLIENT_ID'],
#     'client_secret':os.environ['STRAVA_CLIENT_SECRET'],
#     'code':re.search('(?<=code=)[\w]*(?=&scope)', response_url)[0],
#     'grant_type':'authorization_code'
#     }
# post_request_url = post_request_stub + '&'.join([key+'='+value for key,value in params.items()])


api_stub = 'https://api-ce.kroger.com/v1/connect/oauth2/token'
params = {
    'Authorization':base64.b64encode(':'.join([KROGER_CLIENT_ID, KROGER_CLIENT_SECRET]).encode()),
    'grant_type':'client_credentials',
    'scope':'product.compact'}
