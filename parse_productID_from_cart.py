# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 15:07:14 2022

@author: afisher
"""

from bs4 import BeautifulSoup



with open('cart.txt','r') as f:
    html = f.read()  
    
soup = BeautifulSoup(html, 'html.parser')

links = []
for tag in soup.findAll('a'):
    if 'href' and 'class' in tag.attrs.keys():
        if 'kds-Link--implied' and 'ProductDescription-truncated' in tag.attrs['class']:
            links.append(tag.attrs['href'])

IDs = [link.split('/')[3] for link in links if link.split('/')[3].isdigit()]

