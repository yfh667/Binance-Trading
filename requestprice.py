import requests
from datetime import datetime

def get_token_details(chain, address):
    url = f"https://public-api.dextools.io/trial/v2/token/{chain}/{address}"
    headers = {
        'accept': 'application/json',
        # 如果需要 API Key，可以在这里添加
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # 返回解析为 JSON 的响应内容
    else:
        return f"Error: {response.status_code}, Message: {response.text}"  # 处理错误情况

# def fetch_token_price(chain, address):
#     url = f"https://public-api.dextools.io/trial/v2/token/{chain}/{address}/price"
#     headers = {
#         'accept': 'application/json',
#         "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"

#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()  # 返回 JSON 解析的数据
#     else:
#         return None  # 如果响应不是 200 OK, 返回 None

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
        timestamp = datetime.now()  # 获取当前时间
        return {'price': price, 'timestamp': timestamp}  # 返回价格和时间戳的字典
    else:
        return None  # 如果响应不是 200 OK, 返回 None

# 使用示例
chain = "solana"
address = "FFTgPL43AXPbe9GyXKXJZxtyQasx3moUcXxYsnSnh6K3"
token_details = get_token_details(chain, address)
price_info = fetch_token_price( address)
if price_info:
    print(price_info)
else:
    print("Failed to fetch price information.")
