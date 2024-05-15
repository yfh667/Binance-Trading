import requests

def fetch_tokens_data(chain, addresses):
    # 将地址列表转换为逗号分隔的字符串
    addresses_str = ','.join(addresses)
    
    # 构建请求 URL
    url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/tokens/multi/{addresses_str}"
    
    # 设置请求头部，接受JSON格式的数据
    headers = {
        'accept': 'application/json'
    }
    
    # 发送 GET 请求
    response = requests.get(url, headers=headers)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 如果响应成功，解析并返回 JSON 数据
        return response.json()
    else:
        # 如果请求失败，返回错误信息
        return f"Error: {response.status_code}, Message: {response.text}"

# 示例用法
chain_id = "solana"
addresses = [
    "GS39hJzMgVJysFqcm5STBDmPDTWDrkxYq9NhcLmBgHxK",
    "Bbtv2A2Vqze8VE7YXm9YVwtE6Zkvn9hzsSZGNcFLSKjR",
"RHxxkNAN5Vv76sUQTfhNAXGmwTVcLHZa3KkSnf8p7cz",
"ESBjVXywFF17sGSdnQc7PW5QcgANaDLAepbrMNEC3bmk",
"EJgKwbVpZ4AdwQKvDfUBxNUDfQi4tV3Z7M5GC9owTWTj",
"7qtnComv6JkaT9Ey2LUzXGGENnCv7kJTfTihGg9s27FD",
"G2sB6aCGDLBpmBdFch87iyN7JPtrCTSUoGw7nKZHW8PY",
"9EvVoy4RtW48TeF8ahKsww6ZX5ZWEbxsArWXa3MeJzdH",
"2rbHmboj413XFgqetyAkxXjh9nBJjuCHqNauWN4f3aXZ",
"BTrGh3MHbf5bchB3KH4xo3L2Gn2jt8h5WHCP5byhqPoJ",
"EXkeqPf6S2hfxkqjSUtgtVwGjtJ1iezeYgz2YYgBCTDT",
"76xc7K5hbcnYVyQgPDNBwmLfTyKfRtdNG5rqihhejtDp",
"D8Uc6x3XKCmWxDPW3GF5kCtdoi6n2bWqYqzsh7ihHg9N",
"8Xwjy7nMs9fpFbGpEKJ8aLm2NHSvBy4jbKbyL7d6cgv6",
"Eb6AGbkhow75fgJshgZEpZN1S3P11GdQRXEWX7pvzka3",
"US24aoVytbiqPcLpwLajPRCmuGWBRqNR1Gx9TSRX1wd",
"8n7ied5xpzGbLiL7nGL5dwoTfFYudfxbqHa3pQaG5ihy",
"34MphWDvZeTtZSjkR2R3fRWCwQgb1eGdvYuFEJMfBb44",
"9MBzpyMRkj2r5nTQZMMnxnCm5j1MAAFSYUtbSKjAF3WU",
"erFx77tY5pi3iyYHBmxTsaTG8SugXN3Gj9SMyZGgyZf",
"CKiW2P4zngHa6fiPhMJGGhgDZm638dWotxkzgi8PsDxf",
"5Go3BowxrzXtS6hZcAmbnndiLDLvv5APJjst6VhFNmf3",
"5R2wQvZrfw7fTQhQzsaKht92wz4Tv1mE58LTVpgkTHwS",
"DogkU7U4MH3dCPxuGHT4tZYCEvNsfH3QxFNDThwuh4He",
"94fJLpuJ8iA6XWFEAoVF5LNyqBUXWvUGfo6cSiuEEWsE",
"3MoZPH9qy9SmAGXsYAGpRAQTo65ymywhpRQahsx4Ynsj",
"3wNmRxyZPzDWVAydsF3VuNKCNk89A8uSo7EzTnubDJcR",
"GxPy2FUCRNmVZVWGfKZHx3J3nWDmGX7EPxX97GQJhHX9",
"Drf65GMHgK5LCgGbfMuySh6GPd4E4qvYAtoDaavx83tF",
"C5RgVe6aKgEjyLGpZKPgZFEqdBEpUvWBqTrv7SMAYVtN"

]

token_data = fetch_tokens_data(chain_id, addresses)


print(token_data)
