import requests

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




from_date = "2024-05-07T00:00:00.000Z"
to_date = "2024-05-09T00:00:00.000Z"
page = 0
page_size = 50

# 调用函数并打印结果
tokens_info = get_tokens(chain_id, sort_by, order, from_date, to_date, page, page_size)
#print(tokens_info)

tokens = tokens_info['data']['tokens']
# sorted_tokens = sorted(tokens, key=lambda x: x['creationTime'], reverse=True)

# # 打印排序后的tokens数组
# for token in sorted_tokens:
#     print(token)


sorted_tokens = sorted(tokens, key=lambda x: x.get('creationTime', '1900-01-01T00:00:00.000Z'), reverse=True)

# 打印排序后的结果
# for token in sorted_tokens:
#     print(token)
# # 
print(sorted_tokens[0])