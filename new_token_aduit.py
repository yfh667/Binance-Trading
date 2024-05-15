import requests

def fetch_token_audit1(chain, address):
    # API的基本URL
    url = f"https://public-api.dextools.io/trial/v2/token/{chain}/{address}/audit"
    
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
        return {"error": f"Error: {response.status_code}, Message: {response.text}"}


def fetch_token_audit(chain, address):
    # API的基本URL
    url = f"https://public-api.dextools.io/trial/v2/token/{chain}/{address}/audit"
    
    # 配置请求头
    headers = {
        "accept": "application/json",
        "X-API-KEY": "WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l"  # 替换为你的API密钥
    }
    
    # 发送GET请求
    response = requests.get(url, headers=headers)
    
    # 检查响应状态码
    if response.status_code == 200:
        data = response.json()
        # 请求成功，解析并返回JSON数据
        audit_data = data.get('data', {})
        if audit_data:
            isMintable = audit_data.get('isMintable', '')
            isContractRenounced = audit_data.get('isContractRenounced', '')
            
            # 检查isMintable为'no'且isContractRenounced为'yes'
            if isMintable == 'no' and isContractRenounced == 'yes':
                # 输出或返回筛选后的信息
                return 1
            else:
                return 0
        else:
            return 0
    else:
        # 请求失败，返回错误信息
        return 0
    
# 使用示例
chain = "solana"  # 例如以太坊链
address1 = "CVZ442uyp71v6p2QDcSte5N26Dm6z4EEw57MfCtX5uvQ"  # 代币地址  10.54  shijishang 38
address2 = 'B1iyZ42sRevYPrd4hGd89baUuajiBeRfmFhUBtiYbzay' #11


audit_info = fetch_token_audit(chain, address1)  #11
print(audit_info)
