import requests
import time

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

# 使用参数
chain_id = "solana"
sort_by = "socialsInfoUpdated"



order = "desc"
from_date = "2024-05-08T10:05:00.000Z"
to_date = "2024-05-09T14:30:00.000Z"
page_size = 50

# 获取所有tokens
all_tokens = get_all_tokens(chain_id, sort_by, order, from_date, to_date, page_size)
print(f"Total tokens fetched: {len(all_tokens)}")
print(all_tokens)
# 对获取的tokens按创建时间进行排序
#sorted_tokens = sorted(all_tokens, key=lambda x: x.get('creationTime', '1900-01-01T00:00:00.000Z'), reverse=True)

# 打印排序后的结果
#print(sorted_tokens)

#print(all_tokens)