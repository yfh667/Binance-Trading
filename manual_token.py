#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 10:51:31 2024

@author: yfh
"""

import json

import sqlite3
import requests
from datetime import datetime


def fetch_token_prices(chain, addresses):
    addresses_str = ','.join(addresses)
    url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/tokens/multi/{addresses_str}"
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def extract_symbol_and_address(price_info):
    if price_info and 'data' in price_info:
        # 初始化一个空列表用于存储提取的结果
        tokens_info = []
        # 遍历所有的代币数据
        for token in price_info['data']:
            # 获取每个代币的属性
            attributes = token.get('attributes', {})
            # 从属性中提取 symbol 和 address
            symbol = attributes.get('symbol', 'No symbol found')
            address = attributes.get('address', 'No address found')
            # 将 symbol 和 address 组合成一个元组，并添加到结果列表中
            tokens_info.append((symbol, address))
        return tokens_info
    else:
        print("Failed to fetch or parse price information.")
        return []
def insert_tokens(db_name, tokens_info):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        for symbol, address in tokens_info:
            try:
                cursor.execute('''
                    INSERT INTO tokens (symbol, address, creationTime)
                    VALUES (?, ?, ?)
                    ON CONFLICT(address) DO UPDATE SET
                    symbol=excluded.symbol, creationTime=excluded.creationTime;
                ''', (symbol, address, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except sqlite3.IntegrityError as e:
                print(f"Failed to insert/update token {symbol} at address {address}: {e}")
        conn.commit()    
def read_addresses_from_file(file_path):
    """
    从给定的文件路径读取代币地址。
    :param file_path: 包含代币地址的文本文件的路径。
    :return: 包含所有地址的列表。
    """
    try:
        with open(file_path, 'r') as file:
            addresses = file.readlines()
            # 移除每个地址中的换行符并过滤掉空字符串
            addresses = [address.strip() for address in addresses if address.strip()]
        return addresses
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
file_path = 'tokens.txt'
addresses = read_addresses_from_file(file_path)
#print(addresses)
# 使用示例
chain = "solana"
#address = ["Bbtv2A2Vqze8VE7YXm9YVwtE6Zkvn9hzsSZGNcFLSKjR","8GayE57cjWNAemoVupBM8Wh4XJLtmVaht7rwzqHo1URs","864YJRb3JAVARC4FNuDtPKFxdEsYRbB39Nwxkzudxy46"]
db_name='test.db'
# 使用示例
price_info = fetch_token_prices(chain, addresses)
tokens_info = extract_symbol_and_address(price_info)
print(tokens_info)
insert_tokens(db_name,tokens_info)

