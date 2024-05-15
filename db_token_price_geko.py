#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 19:38:43 2024

@author: yfh
"""

import sqlite3
import requests
from datetime import datetime
import json

def fetch_all_tokens(db_name):
    """从数据库获取所有tokens的数据，返回包含(symbol, address, creationTime)的列表"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, address FROM tokens')
        return cursor.fetchall()

def fetch_token_prices(chain, addresses):
    addresses_str = ','.join(addresses)
    url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/tokens/multi/{addresses_str}"
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def store_prices(db_name, prices):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO price_history (token_id, price, timestamp)
            VALUES (?, ?, ?)
        ''', prices)
        conn.commit()
    print("All prices inserted into database.")


def updateprice(db_name):
    
    tokens = fetch_all_tokens(db_name)
    prices = []
    db_name = 'test.db'
    chain = 'solana'
    # Process tokens in batches of 30
    batch_size = 30
    for i in range(0, len(tokens), batch_size):
        batch = tokens[i:i+batch_size]
        addresses = [token[1] for token in batch]
        price_data = fetch_token_prices(chain, addresses)
        
        if price_data:
            for token, data in zip(batch, price_data['data']):
                token_id = token[0]
                price = data['attributes']['price_usd']
                timestamp = datetime.now()

                prices.append((token_id, price, timestamp))
    
    # Store prices into the database
    store_prices(db_name, prices)
    
def main(db_name):
    # tokens = fetch_all_tokens(db_name)
    # prices = []
    
    # # Process tokens in batches of 30
    # batch_size = 30
    # for i in range(0, len(tokens), batch_size):
    #     batch = tokens[i:i+batch_size]
    #     addresses = [token[1] for token in batch]
    #     price_data = fetch_token_prices(chain, addresses)
        
    #     if price_data:
    #         for token, data in zip(batch, price_data['data']):
    #             token_id = token[0]
    #             price = data['attributes']['price_usd']
    #             timestamp = datetime.now()

    #             prices.append((token_id, price, timestamp))
    
    # # Store prices into the database
    # store_prices(db_name, prices)
    
    updateprice(db_name)
    

# 使用示例
db_name = 'test.db'
main(db_name)