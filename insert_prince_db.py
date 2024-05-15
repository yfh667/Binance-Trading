import requests
import sqlite3
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import concurrent.futures

 # get the tokens from the db       
def fetch_all_tokens(db_name):
    """从数据库获取所有tokens的数据，返回包含(symbol, address, creationTime)的列表"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT symbol, address, creationTime FROM tokens')
        return cursor.fetchall()
    # get the tokens id from the db ,casure we need specify the token symbol,id is same as symbol
def get_token_id(db_name, address):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM tokens WHERE address = ?
        ''', (address,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None  # 如果没有找到，返回None
        # then when we find the tokens and get the price.we use session to use api faster

def setup_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    return session

session = setup_session()

def fetch_token_price(session, address):
    url = f"https://public-api.dextools.io/trial/v2/token/solana/{address}/price"
    headers = {
        'accept': 'application/json',
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        price = data['data']['price']
        timestamp = datetime.now()
        return {'price': price, 'timestamp': timestamp}
    else:
        return None
    
    
    
# and we insert the price
def insert_price_history(db_name, token_id, price, timestamp):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history (token_id, price, timestamp)
            VALUES (?, ?, ?)
        ''', (token_id, price, timestamp))
        conn.commit()
        
        
        
def main():
    db_name = 'test.db'
    session = setup_session()  # 假设已经设置好了session
    tokens = fetch_all_tokens(db_name)

    prices = []
    for i in range(2):
        for symbol, address, creationTime in tokens:
            token_id = get_token_id(db_name, address)  # 获取token的ID
            if token_id:
                price_info = fetch_token_price(session, address)
                if price_info and price_info['price'] is not None:  # 确保price_info有效且价格不为None
                    # 将token_id, 价格和时间戳以元组形式添加到列表中
                    prices.append((token_id, price_info['price'], price_info['timestamp']))
                    print(f"Fetched price {price_info['price']} for token {symbol} at {price_info['timestamp']}")
                else:
                    print(f"Failed to fetch price for {symbol}")
            else:
                print(f"No token found with address: {address}")
    
    # 批量写入数据库
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO price_history (token_id, price, timestamp)
            VALUES (?, ?, ?)
        ''', prices)
        conn.commit()
    print("All prices inserted into database.")
    prices = []


if __name__ == '__main__':
    main()