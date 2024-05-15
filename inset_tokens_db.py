import requests

import sqlite3
import time
from datetime import datetime
from datetime import datetime, timedelta
# 使用参数
chain_id = "solana"
sort_by = "socialsInfoUpdated"




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

        data = response.json()
        tokens = data['data']['tokens']
        all_tokens.extend(tokens)  # 将当前页面的代币添加到总列表中
        print( data['data']['totalPages'])
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
            print(f"Failed to insert token {symbol}: Address already exists.")
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

# 在主函数或脚本中调用此函数
if __name__ == '__main__':
    db_name = 'test.db'
    chain_id = "solana"
    sort_by = "socialsInfoUpdated"
    order = "desc"
    
    page_size = 50
    
    # 获取当前系统时间
    current_time =  datetime.utcnow()
    from_date = current_time - timedelta(days=3) 
    # 格式化为 ISO 8601 格式的字符串
    from_date_str = from_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'
    # 格式化为ISO 8601格式的字符串
    to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'
    
   # to_date  ="2024-05-11T05:05:00.000Z"

    get_and_store_tokens(chain_id, sort_by, order, from_date_str, to_date, page_size, db_name)