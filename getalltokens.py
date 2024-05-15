import requests

import sqlite3
import time
from datetime import datetime

# 使用参数
chain_id = "solana"
sort_by = "socialsInfoUpdated"



order = "desc"
from_date = "2024-05-09T10:05:00.000Z"
# 获取当前系统时间
#current_time = datetime.now()
current_utc_time = datetime.utcnow()

# 格式化为ISO 8601格式的字符串
#to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'
page_size = 50
#to_date = current_utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'
to_date  ="2024-05-11T05:05:00.000Z"
print(to_date)


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

# 获取当前系统时间
current_time = datetime.now()

# 格式化为ISO 8601格式的字符串
to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'



all_tokens = get_all_tokens(chain_id, sort_by, order, from_date, to_date, page_size)
print(all_tokens)



num_tokens = len(all_tokens)
print(f"Total tokens retrieved: {num_tokens}")