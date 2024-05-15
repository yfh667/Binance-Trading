import requests
import time
from datetime import datetime
from datetime import datetime, timedelta

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

# 示例使用参数
chain_id = "solana"  # 示例链ID，需要根据实际情况替换
sort_by = "socialsInfoUpdated"
order = "desc"

current_time =  datetime.utcnow()
from_date = current_time - timedelta(days=1)

# 格式化为 ISO 8601 格式的字符串
from_date_str = from_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'
# 格式化为ISO 8601格式的字符串
to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'

#from_date = "2024-05-09T10:05:00.000Z"
page_size = 50

# 获取当前系统时间
page = 0
# 格式化为ISO 8601格式的字符串
#to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'

#to_date  ="2024-05-11T09:05:00.000Z"

#current_time =  datetime.utcnow()

# 格式化为ISO 8601格式的字符串
#to_date = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # 精确到毫秒，删除最后三个字符（微秒的一部分），并添加'Z'

# 调用函数并打印结果
tokens_info = get_tokens(chain_id, sort_by, order, from_date, to_date, page, page_size)
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
