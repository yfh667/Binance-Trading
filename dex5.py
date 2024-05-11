#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 20:33:14 2024

@author: yfh
"""
import requests

import sqlite3
import time
from datetime import datetime

# 使用参数
chain_id = "solana"
sort_by = "socialsInfoUpdated"



order = "desc"
from_date = "2024-05-05T10:05:00.000Z"
to_date = "2024-05-09T14:30:00.000Z"
page_size = 50


def get_token_details( address):
    url = f"https://public-api.dextools.io/trial/v2/token/solana/{address}"
    headers = {
        'accept': 'application/json',
        # 如果需要 API Key，可以在这里添加
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('creationTime', 'Unknown Creation Time')  # 安全地获取creationTime，如果不存在则返回默认值
    else:
        return 'Unknown Creation Time'  # 如果无法获取信息，则返回默认值

def init_db(db_name='tokens.db'):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                symbol TEXT,
                address TEXT UNIQUE,
                creation_time TEXT
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT,
                price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(address) REFERENCES tokens(address)
            );
        ''')
        conn.commit()
        


def insert_price(db_name, address, price_info):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prices (address, price, timestamp) VALUES (?, ?, ?)
        ''', (address, price_info['price'], price_info['timestamp']))
        conn.commit()

def get_tokens_db(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM tokens')
        tokens = cursor.fetchall()
        return tokens


def fetch_and_store_prices(db_name, tokens):
    for token in tokens:
        price_info = fetch_token_price(token['address'])
        if price_info:
            insert_price(db_name, token['address'], price_info)
        time.sleep(1)  # 遵循API的速率限制

        

def fetch_token_price(address):
    url = f"https://public-api.dextools.io/trial/v2/token/solana/{address}/price"
    headers = {
        'accept': 'application/json',
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        price = data['data']['price']  # 获取当前价格
        timestamp = datetime.now()  # 获取当前时间
        return {'price': price, 'timestamp': timestamp}  # 返回价格和时间戳的字典
    else:
        return None  # 如果响应不是 200 OK, 返回 None


def insert_token(db_name, token):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO tokens (symbol, address, creation_time) VALUES (?, ?, ?)
        ''', (token['symbol'], token['address'], token['creationTime']))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Token {token['address']} already exists.")
    finally:
        conn.close()

def get_all_tokens(chain_id, sort_by, order, from_date, to_date, page_size, delay=1):
    url = f"https://public-api.dextools.io/trial/v2/token/{chain_id}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    all_tokens = []
    page = 0
    while True:
        params = {
            "sort": sort_by,
            "order": order,
            "from": from_date,
            "to": to_date,
            "page": page,
            "pageSize": page_size
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 429:  # Too Many Requests
            print("Rate limit exceeded, waiting to retry...")
            time.sleep(1)  # wait 10 seconds before retrying
            continue
        elif response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            print(response.text)
            break
        data = response.json()
        if 'data' not in data or 'tokens' not in data['data']:
            print("Unexpected JSON structure:", data)
            break
        tokens = data['data']['tokens']
        all_tokens.extend(tokens)
        if page + 1 >= data['data'].get('totalPages', 0):
            break
        page += 1
        time.sleep(delay)  # wait for 1 second before the next API call to avoid hitting rate limit
    return all_tokens


def continuous_price_update(db_name):
    while True:
        tokens = get_tokens_db(db_name)
        fetch_and_store_prices(db_name, tokens)
        #time.sleep(1)  # 设置更新频率，这里是每1秒更新一次


def main():
    init_db()  # Initialize the database and table
    all_tokens = get_all_tokens(chain_id, sort_by, order, from_date, to_date, page_size)
 #   sorted_tokens = sorted(all_tokens, key=lambda x: x.get('creationTime', '1900-01-01T00:00:00.000Z'), reverse=True)

    for token in all_tokens:
        if not token.get('creationTime'):  # 检查是否存在creationTime
            # 尝试从另一个 API 调用获取creationTime
            creation_time = get_token_details(token['address'])
            token['creationTime'] = creation_time  # 更新token字典中的creationTime
        
        # 插入数据库
        insert_token('tokens.db', token)

    print("Tokens have been processed and stored.")
    continuous_price_update('tokens.db')
    
    
    
    
    

if __name__ == '__main__':
    main()
