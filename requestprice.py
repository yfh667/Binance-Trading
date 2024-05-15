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
def fetch_token_score(chain, address):
    # API的基本URL
    url = f"https://public-api.dextools.io/trial/v2/token/{chain}/{address}/info"
    
    # 配置请求头
    headers = {
        "accept": "application/json",
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"  # 替换为你的API密钥
    }
    
    # 发送GET请求
    response = requests.get(url, headers=headers)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 请求成功，解析并返回JSON数据
        return response.json()
    else:
        # 请求失败，返回错误信息
        return f"Error: {response.status_code}, Message: {response.text}"



    
    
def fetch_token_price_gek(address):
    url = f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/{address}"
    headers = {
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    
    
    
   # print(response)
    if response.status_code == 200:
        data = response.json()
        
        
        
        price = data['data']['attributes']['price_usd']  # 获取当前价格
        print(data)
        timestamp = datetime.now()  # 获取当前时间
        return {'price': price, 'timestamp': timestamp}  # 返回价格和时间戳的字典
    else:
        return None  # 如果响应不是 200 OK, 返回 None
   

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
    
    
    

def fetch_token_pools(chain, address):
    url = f"https://public-api.dextools.io/trial/v2/token/{chain}/{address}/pools"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l}'  # 注意添加 'Bearer' 前缀
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        pools_data = response.json()
        return pools_data
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None
    
    
# 使用示例
chain = "solana"
address = "Bbtv2A2Vqze8VE7YXm9YVwtE6Zkvn9hzsSZGNcFLSKjR"
# token_details = get_token_details(chain, address)
# price_info = fetch_token_price( address)
# if price_info:
#     print(price_info)
# else:
#     print("Failed to fetch price information.")
price = fetch_token_price_gek('EZUFNJMZTBpungQX2czEb9ZyCMjtdzsDGMK4UywDUa1F')


