#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 12:07:35 2024

@author: alen
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 13:10:55 2024

@author: yfh
"""
# from tqdm import tqdm
# import requests
# import json
# import pandas as pd
# import requests
# import time
# #import config
# import pytz
# from datetime import datetime

# from binance.client import Client
# import requests
# import time
# import requests
# import json
# import concurrent.futures


from tqdm import tqdm
import requests
import json
import pandas as pd
import time
from datetime import datetime
import pytz
import concurrent.futures
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests

key = 'FC\n'
# 内容
content = '加仓'
# url
url1 = 'https://oapi.dingtalk.com/robot/send?access_token=d57239ad50b576f324eb29b0bc405ebe263c21f9ef0084ff76e5003727b49104'

class DingTalk_Base:
    def __init__(self):
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.url = ''
    
    def send_msg(self, text):
        json_text = {
            "msgtype": "text",
            "text": {
                "content": self.key + text
            },
            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": False
            }
        }
        return requests.post(self.url, json.dumps(json_text), headers=self.__headers).content

class DingTalk_Disaster(DingTalk_Base):
    def __init__(self, key, url):
        super().__init__()
        self.key = key  # 关键字或者是access_token
        self.url = url  # 钉钉机器人的url

def send_dingtalk_message(key, content, url):
     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
     # 创建类的实例
     ding = DingTalk_Disaster(key, url)
     
     # 将时间信息添加到消息内容中
     full_content = f"{key}\n{current_time}\n{content}"
     
     # 发送消息
     return ding.send_msg(full_content)




def fetch_daily_data_all_4h(coin):
    url = f'https://api.binance.com/api/v3/klines?symbol={coin}&interval=4h&limit=60'
    response = requests.get(url)
    if response.status_code != 200:
        print("Error: Unable to fetch data from API")
        return pd.DataFrame()
    data = response.json()
    if not isinstance(data, list):
        print("Error: Unexpected data format")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True).dt.tz_convert('Asia/Shanghai')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms', utc=True).dt.tz_convert('Asia/Shanghai')
    return df



def print_day(daily_data):
    print('开盘时间:', daily_data['open_time'])
    print('开盘价:', daily_data['open'])
    print('最高价:', daily_data['high'])
    print('最低价:', daily_data['low'])
    print('收盘价:', daily_data['close'])
    print('成交量:', daily_data['volume'])
    print('买入:', daily_data['taker_base_vol'])


# def print_day2(daily_data):
#     # 使用.iloc[0]来访问Series中的第一个元素
#     print('开盘时间:', daily_data['open_time'].iloc[0])
#     print('开盘价:', daily_data['open'].iloc[0])
#     print('最高价:', daily_data['high'].iloc[0])
#     print('最低价:', daily_data['low'].iloc[0])
#     print('收盘价:', daily_data['close'].iloc[0])
#     print('成交量:', daily_data['volume'].iloc[0])
#     print('买入:', daily_data['taker_base_vol'].iloc[0])


def print_day2(daily_data):
    # 直接访问Series中的元素
    print('开盘时间:', daily_data['open_time'])
    print('开盘价:', daily_data['open'])
    print('最高价:', daily_data['high'])
    print('最低价:', daily_data['low'])
    print('收盘价:', daily_data['close'])
    print('成交量:', daily_data['volume'])
    print('买入:', daily_data['taker_base_vol'])

def Standard(daily_data):
    before = float(daily_data['open'].iloc[0])
    now = float(daily_data['close'].iloc[0])
    if ((now - before) / before > 0.05):
        return 1
    else:
        return 0
    
    #find all the coin that are selled in th biance
def get_all_trading_pairs2():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            symbols = [symbol['symbol'] for symbol in data['symbols']]
            return symbols
        else:
            return f"Error: Unable to fetch trading pairs, Status Code: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    
    
def find_ten(coin):
    if coin.endswith("USDT"):
        min_30 = fetch_daily_data_all_30m(coin)
        
        rg = Standard( min_30 )
        if(rg>0):
           print(f"{coin}:{rg}")
           return coin
     
def find_4h_nonnormal(df):
    for index, row in df.iterrows():
        if ((float(row['high']) - float(row['open'])) / float(row['open']) > 0.2):
            abnormal_time = row['open_time'].strftime("%Y-%m-%d %H:%M:%S")  # 格式化时间
            return abnormal_time  # 返回发生异常的时间
    return None  # 如果没有发现异常，则返回None
def find_abnormal_volume(df, coin):
    avg_volume = df['volume'].mean()  # 计算平均成交量
    for index, row in df.iterrows():
        if row['volume'] > 2 * avg_volume:  # 检查成交量是否超过平均成交量的两倍
            return coin  # 发现异常成交量，返回币种名称
    return None  # 没有发现异常成交量

# 示例用法

    return False  # 没有发现异常成交量
def fetch_daily_data_all_4h_with_retry(coin):
    url = f'https://api.binance.com/api/v3/klines?symbol={coin}&interval=1d&limit=120'
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504, 429])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url)
        response.raise_for_status()  # 将会抛出HTTPError，如果状态不是200
        data = response.json()
        if not isinstance(data, list):
            print("Error: Unexpected data format")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True).dt.tz_convert('Asia/Shanghai')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms', utc=True).dt.tz_convert('Asia/Shanghai')
        df['volume'] = df['volume'].astype(float)  # 确保成交量是浮点数类型

        return df
    except requests.exceptions.HTTPError as errh:
        print("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else",err)
    return pd.DataFrame()
    
# def check_coins_for_nonnormal_growth(all_coins):
#     for coin in all_coins:
#         daily_data = fetch_daily_data_all_4h_with_retry(coin)
#         if find_4h_nonnormal(daily_data):
#             print(coin)
#         time.sleep(1)  # 在每次API请求之后等待1秒

def check_coins_for_nonnormal_growth(all_coins):
    for coin in all_coins:
        daily_data = fetch_daily_data_all_4h_with_retry(coin)
        abnormal_coin = find_abnormal_volume(daily_data, coin)
        if abnormal_coin:
            print(f"发现异常成交量的币种: {abnormal_coin}")
        else:
            print("没有发现异常成交量的币种")


def find_ten_wrapper(coin, progress=None):
    result = find_ten(coin)
    if progress:
        progress.update(1)  # 更新进度条
    if result is not None:
        return result

def calculate(all_coin):
    a = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 初始化进度条
        progress = tqdm(total=len(all_coin), desc="Processing", unit="coin")
        # 将任务分配给线程池，并传递进度条对象
        futures = [executor.submit(find_ten_wrapper, coin, progress) for coin in all_coin]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                a.append(result)

        progress.close()  # 关闭进度条
    content = " ".join(a)
    response = send_dingtalk_message(key, content, url1)

def main():
    all_coin = get_all_trading_pairs2()
    # 检查all_coin是否是列表，如果不是，说明有错误
    if not isinstance(all_coin, list):
        print("获取交易对时发生错误:", all_coin)
        return

    # 筛选出以USDT结尾的交易对
    usdt_pairs = [coin for coin in all_coin if coin.endswith("USDT")]
    print(f"Found {len(usdt_pairs)} USDT trading pairs.")
    
    # 假设all_coins是你已经获取到的所有币种的列表
 #   all_coins = get_all_trading_pairs2()
 
    check_coins_for_nonnormal_growth(usdt_pairs)


            
    # df = fetch_daily_data_all_4h("BTCUSDT")
    # for index, row in df.iterrows():
    # # 打印每个时间段的开盘价、收盘价和最高价
    #     print(f"时间段 {index + 1}:")
    #     print("    开盘价:", row['open'])
    #     print("    收盘价:", row['close'])
    #     print("    最高价:", row['high'])
    

    

if __name__ == "__main__":
    main()  # 执行主逻辑
