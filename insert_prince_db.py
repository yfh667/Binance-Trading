import requests
import sqlite3
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


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
        # then when we find the tokens we 
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
        symbol = data['data'].get('symbol', 'UNKNOWN')  # 尝试获取符号，如果不存在则为'UNKNOWN'
        creationTime = data['data'].get('creationTime', 'UNKNOWN')  # 尝试获取创建时间，如果不存在则为'UNKNOWN'
        timestamp = datetime.now()  # 获取当前时间
        return {'price': price, 'symbol': symbol, 'creationTime': creationTime, 'timestamp': timestamp}
    else:
        return None  # 如果响应不是 200 OK, 返回 None    
def insert_price_history(db_name, token_id, price, timestamp):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history (token_id, price, timestamp)
            VALUES (?, ?, ?)
        ''', (token_id, price, timestamp))
        conn.commit()

def main():
    db_name = 'test.db'  # 数据库名
    tokens = fetch_all_tokens(db_name)  # 从数据库获取所有token信息
    while(1):
        for symbol, address, creationTime in tokens:
            token_id = get_token_id(db_name, address)  # 获取token的ID
            if token_id:
                price_info = fetch_token_price(address)  # 从API获取价格信息
                if price_info and price_info['price']:
                    insert_price_history(db_name, token_id, price_info['price'], price_info['timestamp'])
                    print(f"Inserted price {price_info['price']} for token {symbol} at {price_info['timestamp']}")
                else:
                    print(f"Failed to fetch price for {symbol}")
            else:
                print(f"No token found with address: {address}")
            time.sleep(1)  # 每次请求后暂停1秒

if __name__ == '__main__':
    main()