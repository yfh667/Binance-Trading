import json
import requests
from datetime import datetime

class DingTalk_Base:
    def __init__(self):
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.url = ''
    
    def send_msg(self, text):
        json_text = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "atMobiles": [],
                "isAtAll": False
            }
        }
        print("Sending JSON:", json.dumps(json_text))  # 打印JSON数据，用于调试
        response = requests.post(self.url, data=json.dumps(json_text), headers=self.__headers)
        print("Response Status:", response.status_code)  # 打印响应状态码，用于调试
        return response.text

class DingTalk_Disaster(DingTalk_Base):
    def __init__(self, key, url):
        super().__init__()
        self.key = key
        self.url = url

def send_dingtalk_message(key, content, url):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_content = f"{key}\n{current_time}\n{content}"
    ding = DingTalk_Disaster(key, url)
    response = ding.send_msg(full_content)
    return response

# 使用示例
key = 'FC\n'
content = '加仓'
url = 'https://oapi.dingtalk.com/robot/send?access_token=d57239ad50b576f324eb29b0bc405ebe263c21f9ef0084ff76e5003727b49104'
response = send_dingtalk_message(key, content, url)
print("Final Response:", response)
