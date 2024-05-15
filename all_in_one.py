import requests

import sqlite3
import time
from datetime import datetime
from datetime import datetime, timedelta

import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# 使用参数
chain_id = "solana"
sort_by = "socialsInfoUpdated"


key = 'FC\n'
# 内容
content = '加仓'
# url
url1 = 'https://oapi.dingtalk.com/robot/send?access_token=d57239ad50b576f324eb29b0bc405ebe263c21f9ef0084ff76e5003727b49104'

class DingTalk_Base:
    def __init__(self):
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.url = ''
    
    def send_msg(self, text):
        json_text = {
            "msgtype": "text",
            "text": {
                "content": self.key + text
            },
            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": False
            }
        }
        return requests.post(self.url, json.dumps(json_text), headers=self.__headers).content

class DingTalk_Disaster(DingTalk_Base):
    def __init__(self, key, url):
        super().__init__()
        self.key = key  # 关键字或者是access_token
        self.url = url  # 钉钉机器人的url

def send_dingtalk_message(key, content, url):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_content = f"{key}\n{current_time}\n{content}"
    ding = DingTalk_Disaster(key, url)
    response = ding.send_msg(full_content)
    return response



def fetch_data_with_retry(url, headers, params, retries=5, backoff_factor=0.3):
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.SSLError as e:
            print(f"第 {i+1} 次尝试时发生 SSL 错误: {e}")
            sleep_time = backoff_factor * (2 ** i)
            print(f"{sleep_time} 秒后重试...")
            time.sleep(sleep_time)
    print("多次重试后仍失败")
    return None
def get_all_tokens(chain_id, sort_by, order, from_date, to_date, page_size):
    url = f"https://public-api.dextools.io/trial/v2/token/{chain_id}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    all_tokens = []  # 用于存储所有页面的代币信息
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
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break  # 如果请求失败，终止循环

        data = fetch_data_with_retry(url, headers, params)
        tokens = data['data']['tokens']
        all_tokens.extend(tokens)  # 将当前页面的代币添加到总列表中
      #  print( data['data']['totalPages'])
        # 检查是否有更多页面
        if page + 1 >= data['data']['totalPages']:
            break  # 如果当前页面是最后一页，终止循环
        page += 1  # 否则，增加页面号以请求下一页

    return all_tokens


def insert_token(db_name, symbol, address, creationTime):
    """向数据库的tokens表中插入一条新的代币记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO tokens (symbol, address, creationTime)
                VALUES (?, ?, ?)
            ''', (symbol, address, creationTime))
            conn.commit()
            print(f"Inserted token {symbol} successfully.")
        except sqlite3.IntegrityError:
           # print(f"Failed to insert token {symbol}: Address already exists.")
           pass
        except Exception as e:
            print(f"Failed to insert token {symbol}: {e}")
def get_and_store_tokens(chain_id, sort_by, order, from_date, to_date, page_size, db_name):
    all_tokens = get_all_tokens(chain_id, sort_by, order, from_date, to_date, page_size)
    num_tokens = len(all_tokens)
  #  print(all_tokens)
    print(f"Total tokens retrieved: {num_tokens}")
    for token in all_tokens:
        # 假设API返回的token信息中包含了需要的字段
        symbol = token.get('symbol')
        address = token.get('address')
        # 此处的creationTime是假设的字段，你需要根据实际API响应调整
        creationTime = token.get('creationTime', datetime.now().isoformat())  # 如果API不返回创建时间，使用当前时间
        insert_token(db_name, symbol, address, creationTime)

def fetch_all_tokens(db_name):
    """从数据库获取所有tokens的数据，返回包含(symbol, address, creationTime)的列表"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, address FROM tokens')
        return cursor.fetchall()

# def fetch_token_prices(chain, addresses):
#     addresses_str = ','.join(addresses)
#     url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/tokens/multi/{addresses_str}"
#     headers = {'accept': 'application/json'}
#     response = requests.get(url, headers=headers)
#     time.sleep(2)
#     if response.status_code == 200:
#         return response.json()
#     else:
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
                
                fdv_usd = data['attributes'].get('fdv_usd')
                if fdv_usd is None:
                    fdv_usd = 0  # 设定默认值为 0
                else:
                    try:
                        fdv_usd = float(fdv_usd)
                    except ValueError:
                        fdv_usd = 0  # 如果转换失败，同样设定为 0
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
    
def delete_tokens_with_none_address(db_name='test1.db'):
    # 连接到数据库
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        # 删除所有 address 为 None 的条目
        cursor.execute("DELETE FROM tokens WHERE address IS NULL")
        
        # 提交事务，使更改生效
        conn.commit()
        print("Deleted all tokens with None address.")



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
        
                 
    
    
def updatetoken(db_name):    
 #   db_name = 'test.db'
    chain_id = "solana"
    sort_by = "socialsInfoUpdated"
    order = "desc"
    
    page_size = 50
    
    # 获取当前系统时间
    current_time =  datetime.utcnow()
    from_date = current_time - timedelta(days=1) 
    # 格式化为 ISO 8601 格式的字符串
    from_date_str = from_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'
    # 格式化为ISO 8601格式的字符串
    to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'
    
   # to_date  ="2024-05-11T05:05:00.000Z"

    get_and_store_tokens(chain_id, sort_by, order, from_date_str, to_date, page_size, db_name)

def fetch_all_tokens(db_name):
    """从数据库获取所有tokens的数据，返回包含(symbol, address, creationTime)的列表"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, address FROM tokens')
        return cursor.fetchall()    

def fetch_two_latest_prices(db_name, token_id):
    """从数据库获取指定token的最新两条价格记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, timestamp FROM price_history WHERE token_id = ?
            ORDER BY timestamp DESC
            LIMIT 2
        ''', (token_id,))
        return cursor.fetchall()

def delete_oldest_price(db_name, token_id, timestamp):
    """删除指定token的最老的价格记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM price_history WHERE token_id = ? AND timestamp = ?
        ''', (token_id, timestamp))
        conn.commit()



def update_and_clean_prices(db_name):
    """更新价格信息并清理旧记录"""
    tokens = fetch_all_tokens(db_name)
    for token_id, address in tokens:
        prices = fetch_two_latest_prices(db_name, token_id)
        if len(prices) == 2:
            latest_price = prices[0][0]
            older_price = prices[1][0]
            if latest_price >= 1.3   * older_price:
                print(f"Token {token_id} with address {address} .")
                delete_oldest_price(db_name, token_id, prices[1][1])
               # message_content = f"Token ID: {token_id}, Address: {address} !"
                message_content = (
                  f"Token ID: {token_id}, Address: {address} has increased significantly!\n"
                  f"Old Price: {older_price}\n"
                  f"New Price: {latest_price}"
              )
                send_dingtalk_message(key, message_content, url1)
            else:
                delete_oldest_price(db_name, token_id, prices[1][1])
                
def fetch_all_price(db_name, token_id):

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, timestamp FROM price_history WHERE token_id = ?
            ORDER BY timestamp DESC
        ''', (token_id,))
        return cursor.fetchall()
    
def delete_older_prices_except_latest(db_name, token_id, latest_timestamp):
    """删除除了最新价格之外的所有记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM price_history WHERE token_id = ? AND timestamp != ?
        ''', (token_id, latest_timestamp))
        conn.commit()

def delete_token_and_prices(db_name, token_id):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        # 首先删除所有与token_id关联的价格历史记录
        cursor.execute('''
            DELETE FROM price_history WHERE token_id = ?
        ''', (token_id,))

        # 然后删除token本身
        cursor.execute('''
            DELETE FROM tokens WHERE id = ?
        ''', (token_id,))

        # 提交事务
        conn.commit()

        print(f"Deleted token and all associated price history for token_id {token_id}")

    
def analyze_and_alert_prices(db_name, token_id,address):
    prices = fetch_all_price(db_name, token_id)
   
    if not prices or all(price is None for price, _ in prices):
        print("All price data are None. Deleting token and prices...")
        delete_token_and_prices(db_name, token_id)  # 调用删除函数
        return


    if len(prices) <= 1:
        # 如果价格记录小于等于1，不进行处理
        return

    # 计算剩余数据的平均值
    latest_price, latest_timestamp = prices[0]  # 最新的数据
    if len(prices) > 1:
      #  average_price = sum(price for price, _ in prices[1:]) / (len(prices) - 1)  # 排除最新数据后的平均值
        # 计算平均价格，确保排除 None 值
        prices_filtered = [price for price, _ in prices[1:] if price is not None]
        if prices_filtered:
            average_price = sum(prices_filtered) / len(prices_filtered)
        else:
            average_price = 0  # 或者可以设置为 None 或其他合适的默认值

        if float(latest_price) >= 1.2 * average_price:
            # 如果最新的价格是平均价的1.3倍以上，执行报警和数据清理
           
            print("find")
            message_content = (
                f"Token ID: {token_id}:{address} has increased significantly!\n"
                f"Old Average Price: {average_price:.8f}\n"
                f"New Price: {latest_price}"
            )
            send_dingtalk_message(key, message_content, url1)
    delete_older_prices_except_latest(db_name, token_id, latest_timestamp)
                
def db_token_price_analysy(db_name):
    """更新价格信息并清理旧记录"""
    tokens = fetch_all_tokens(db_name)
    for token_id, address in tokens:
        analyze_and_alert_prices(db_name,token_id,address)
       
                
def main(db_name):
    for i in range(1):
        updatetoken(db_name)
        updateprice(db_name)
        db_token_price_analysy(db_name)
        time.sleep(60)
        
# 在主函数或脚本中调用此函数
if __name__ == '__main__':
    db_name = 'test.db'
    main(db_name)
    
    
    
    
    
    
    