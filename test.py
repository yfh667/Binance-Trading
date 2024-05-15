#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 17:50:33 2024

@author: yfh
"""

import requests
import time

def get_tokens(chain_id, sort_by, order, from_date, to_date, page, page_size):
    url = "https://public-api.dextools.io/trial/v2/token/{}".format(chain_id)
    headers = {
        "accept": "application/json",
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    params = {
        "sort": sort_by,
        "order": order,
        "from": from_date,
        "to": to_date,
        "page": page,
        "pageSize": page_size
    }
    response = requests.get(url, headers=headers, params=params)
    
    
    return response.json()
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
        if response.status_code == 429:  # Too Many Requests
                    print("Rate limit exceeded, waiting to retry...")
                    time.sleep(1)  # wait 10 seconds before retrying
                    continue
        elif response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break  # 如果请求失败，终止循环

        data = response.json()
        tokens = data['data']['tokens']
        all_tokens.extend(tokens)  # 将当前页面的代币添加到总列表中
        
        # 检查是否有更多页面
        if page + 1 >= data['data']['totalPages']:
            break  # 如果当前页面是最后一页，终止循环
        page += 1  # 否则，增加页面号以请求下一页

    return all_tokens

# 示例使用参数
chain_id = "solana"  # 示例链ID，需要根据实际情况替换
sort_by = "socialsInfoUpdated"
order = "desc"



from_date = "2024-05-09T10:05:00.000Z"
page_size = 50

# 获取当前系统时间
page = 1
# 格式化为ISO 8601格式的字符串
#to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'

to_date  ="2024-05-11T09:05:00.000Z"


# 调用函数并打印结果
tokens_info = get_tokens(chain_id, sort_by, order, from_date, to_date, page, page_size)
#tokens_info = get_all_tokens(chain_id, sort_by, order, from_date, to_date, page_size)
#print(tokens_info)

tokens = tokens_info['data']['tokens']
# sorted_tokens = sorted(tokens, key=lambda x: x['creationTime'], reverse=True)

# # 打印排序后的tokens数组
# for token in sorted_tokens:
#     print(token)


#sorted_tokens = sorted(tokens, key=lambda x: x.get('creationTime', '1900-01-01T00:00:00.000Z'), reverse=True)

# 打印排序后的结果
# for token in sorted_tokens:
#     print(token)
# # 
print(tokens_info)
num_tokens = len(tokens)

print(f"Total tokens retrieved: {num_tokens}")
