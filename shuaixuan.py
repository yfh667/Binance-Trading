import requests

import sqlite3
import time
from datetime import datetime
from datetime import datetime, timedelta

import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry



def delete_fdv_token(addresses, db_name):
    # 连接到数据库
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        # 遍历每个需要删除的地址
        for address in addresses:
            # 首先，找到需要删除的代币的ID，因为价格历史表与代币表是通过ID关联的
            cursor.execute("SELECT id FROM tokens WHERE address = ?", (address,))
            token_id = cursor.fetchone()
            if token_id:
                token_id = token_id[0]
                
                # 删除与该代币相关的所有价格历史记录
                cursor.execute("DELETE FROM price_history WHERE token_id = ?", (token_id,))
                
                # 然后删除代币本身
                cursor.execute("DELETE FROM tokens WHERE id = ?", (token_id,))
        
        # 提交事务，使更改生效
        conn.commit()
        
        
        
        

    

def store_prices(db_name, prices):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO price_history (token_id, price, timestamp)
            VALUES (?, ?, ?)
        ''', prices)
        conn.commit()
    print("All prices inserted into database.")
    
def fetch_all_tokens(db_name):
    """从数据库获取所有tokens的数据，返回包含(symbol, address, creationTime)的列表"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, address FROM tokens')
        return cursor.fetchall()   

def delete_tokens_with_none_address(db_name='test1.db'):
    # 连接到数据库
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        # 删除所有 address 为 None 的条目
        cursor.execute("DELETE FROM tokens WHERE address IS NULL")
        
        # 提交事务，使更改生效
        conn.commit()
        print("Deleted all tokens with None address.")
        
def updateprice(db_name):
    delete_tokens_with_none_address(db_name)

    tokens = fetch_all_tokens(db_name)
    prices = []
    to_delete = []
    chain = 'solana'
    batch_size = 30
    for i in range(0, len(tokens), batch_size):
        batch = tokens[i:i + batch_size]
        addresses = [token[1] for token in batch]
        price_data = fetch_token_prices(chain, addresses)
        
        if price_data:
            for token, data in zip(batch, price_data['data']):
                fdv_usd = float(data['attributes']['fdv_usd'])
                if fdv_usd >= 10000:
                    token_id = token[0]
                    price = data['attributes']['price_usd']
                    timestamp = datetime.now()
                    prices.append((token_id, price, timestamp))
                else:
                    to_delete.append(token[1])
    
    # Store valid prices into the database
    store_prices(db_name, prices)
    # Delete tokens with fdv_usd less than 10000
    delete_fdv_token(to_delete, db_name)
    
    
    
    #         return None
def fetch_token_prices(chain, addresses):
    addresses_str = ','.join(addresses)
    url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/tokens/multi/{addresses_str}"
    headers = {'accept': 'application/json'}

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None




    



address = ['HSiz8uvPJc1W18mpL2WELah5f9VCNb2S5T9jSPrLfsha','EZUFNJMZTBpungQX2czEb9ZyCMjtdzsDGMK4UywDUa1F']

   
price = updateprice('test1.db')


