import requests
import sqlite3
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def init_db(db_name='my1.db'):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                address TEXT UNIQUE,
                creationTime TEXT
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER,
                price REAL,
                timestamp DATETIME,
                FOREIGN KEY(token_id) REFERENCES tokens(id)
            );
        ''')
        conn.commit()
        
        
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
    
def insert_or_update_token(db_name, symbol, address, creationTime):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tokens (symbol, address, creationTime)
            VALUES (?, ?, ?)
            ON CONFLICT(address) DO UPDATE SET
            symbol=excluded.symbol, creationTime=excluded.creationTime;
        ''', (symbol, address, creationTime))
        conn.commit()  # 确保先提交
        return cursor.lastrowid  # 然后返回ID

def insert_price_history(db_name, token_id, price, timestamp):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history (token_id, price, timestamp)
            VALUES (?, ?, ?)
        ''', (token_id, price, timestamp))
        conn.commit()



def get_token_details(chain, address):
    url = f"https://public-api.dextools.io/trial/v2/token/{chain}/{address}"
    headers = {
        'accept': 'application/json',
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    response = requests.get(url, headers=headers)
    time.sleep(1)  # 遵循API的速率限制

    if response.status_code == 200:
        return response.json()  # Returns JSON parsed response content
    else:
        return None  # Handles error situation


def fetch_token_price1(address):
    url = f"https://public-api.dextools.io/trial/v2/token/solana/{address}/price"
    headers = {
        'accept': 'application/json',
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    
    # 设置重试策略
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, headers=headers, timeout=5)  # 加入超时时间
        if response.status_code == 200:
            data = response.json()
            price = data['data']['price']  # 获取当前价格
            timestamp = datetime.now()  # 获取当前时间
            return {'price': price, 'timestamp': timestamp}  # 返回价格和时间戳的字典
        else:
            return None  # 如果响应不是 200 OK, 返回 None
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None




def main():
    db_name = 'my1.db'
    init_db(db_name)
    tokens = fetch_all_tokens(db_name)  # 获取数据库中所有token的信息

    for i in range(3):
        for symbol, address, creationTime in tokens:
            # 检查是否已经有该token的记录，如果没有则插入
            token_id = get_token_id(db_name, address)
            if not token_id:  # 如果没有找到ID，表示需要插入新的token记录
                token_id = insert_or_update_token(db_name, symbol, address, creationTime)
                print(f"Inserted new token for {symbol} with ID {token_id}")
            else:
                print(f"Found existing token for {symbol} with ID {token_id}")

            price_info = fetch_token_price(address)
            time.sleep(1)
            if price_info and price_info['price']:
                insert_price_history(db_name, token_id, price_info['price'], price_info['timestamp'])
                print(f"Price history for {symbol} updated successfully.")
            else:
                print(f"Failed to fetch price information for {symbol}.")
        time.sleep(1)  # 每次循环后暂停1秒


if __name__ == '__main__':
    main()
