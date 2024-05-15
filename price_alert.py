#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 19:38:43 2024

@author: yfh
"""
import json

import sqlite3
import requests
from datetime import datetime



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
    full_content = f"{key}\n{current_time}\n{content}"
    ding = DingTalk_Disaster(key, url)
    response = ding.send_msg(full_content)
    return response


def fetch_all_tokens(db_name):
    """从数据库获取所有tokens的数据，返回包含(symbol, address, creationTime)的列表"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, address FROM tokens')
        return cursor.fetchall()

def fetch_token_prices(chain, addresses):
    addresses_str = ','.join(addresses)
    url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/tokens/multi/{addresses_str}"
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def store_prices(db_name, prices):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO price_history (token_id, price, timestamp)
            VALUES (?, ?, ?)
        ''', prices)
        conn.commit()
    print("All prices inserted into database.")


def updateprice(db_name):
    
    tokens = fetch_all_tokens(db_name)
    prices = []
    db_name = 'test.db'
    chain = 'solana'
    # Process tokens in batches of 30
    batch_size = 30
    for i in range(0, len(tokens), batch_size):
        batch = tokens[i:i+batch_size]
        addresses = [token[1] for token in batch]
        price_data = fetch_token_prices(chain, addresses)
        
        if price_data:
            for token, data in zip(batch, price_data['data']):
                token_id = token[0]
                price = data['attributes']['price_usd']
                timestamp = datetime.now()

                prices.append((token_id, price, timestamp))
    
    # Store prices into the database
    store_prices(db_name, prices)

def fetch_two_latest_prices(db_name, token_id):
    """从数据库获取指定token的最新两条价格记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, timestamp FROM price_history WHERE token_id = ?
            ORDER BY timestamp DESC
            LIMIT 2
        ''', (token_id,))
        return cursor.fetchall()

def delete_oldest_price(db_name, token_id, timestamp):
    """删除指定token的最老的价格记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM price_history WHERE token_id = ? AND timestamp = ?
        ''', (token_id, timestamp))
        conn.commit()

def fetch_all_price(db_name, token_id):
    """从数据库获取指定token的最新两条价格记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, timestamp FROM price_history WHERE token_id = ?
            ORDER BY timestamp DESC
        ''', (token_id,))
        return cursor.fetchall()
    
    
def analyze_and_alert_prices(db_name, token_id,address):
    prices = fetch_all_price(db_name, token_id)
    if len(prices) <= 1:
        # 如果价格记录小于等于1，不进行处理
        return

    # 计算剩余数据的平均值
    latest_price, latest_timestamp = prices[0]  # 最新的数据
    if len(prices) > 1:
        average_price = sum(price for price, _ in prices[1:]) / (len(prices) - 1)  # 排除最新数据后的平均值
        
        if float(latest_price) >= 1.3 * average_price:
            # 如果最新的价格是平均价的1.3倍以上，执行报警和数据清理
           
            print("find")
            message_content = (
                f"Token ID: {token_id}:{address} has increased significantly!\n"
                f"Old Average Price: {average_price:.8f}\n"
                f"New Price: {latest_price}"
            )
            send_dingtalk_message(key, message_content, url1)
    delete_older_prices_except_latest(db_name, token_id, latest_timestamp)


def delete_older_prices_except_latest(db_name, token_id, latest_timestamp):
    """删除除了最新价格之外的所有记录"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM price_history WHERE token_id = ? AND timestamp != ?
        ''', (token_id, latest_timestamp))
        conn.commit()

def db_token_price_analysy(db_name):
    """更新价格信息并清理旧记录"""
    tokens = fetch_all_tokens(db_name)
    for token_id, address in tokens:
        analyze_and_alert_prices(db_name,token_id,address)
       

def main(db_name):
    db_token_price_analysy(db_name)
    
    
    
    
# 使用示例
if __name__ == '__main__':
    db_name = 'test.db'
    main(db_name)

    
    

# # 使用示例
# db_name = 'test.db'
# main(db_name)