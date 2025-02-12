import os
import time
import requests
import base64
import json
import pyaes
import binascii
from datetime import datetime
from collections import deque
from urllib.parse import quote

# 强制设置中国时区
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡ ͜͡N͜͡O͜͡D͜͡E͜͡")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("Author : 𝐼𝑢")
print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
print("Version: 1.1 (Sing-box Optimized)")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("𝐼𝑢:")

MAX_HISTORY = 4
HISTORY_FILE = "nodes.txt"
LOG_FILE = "update_history.md"
HYSTERIA_URLS = [
    "https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria/1/config.json",
    "https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria2/config.json"
]

def generate_hysteria_uri(config, version):
    base_params = {
        "upmbps": "500",
        "downmbps": "500",
        "obfs": "xplus",
        "obfsParam": config["obfs"],
        "sni": config["server_name"]
    }
    
    if version == 1:
        return f"hysteria://{config['server']}:{config['port']}?{format_params(base_params)}#Hysteria1-{config['server']}"
    else:
        return f"hysteria2://{config['auth_str']}@{config['server']}:{config['port']}?{format_params(base_params)}#Hysteria2-{config['server']}"

def format_params(params):
    return "&".join([f"{k}={quote(str(v))}" for k,v in params.items()])

def fetch_hysteria_nodes():
    hysteria_nodes = []
    for idx, url in enumerate(HYSTERIA_URLS):
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                configs = json.loads(resp.text)
                for config in configs:
                    uri = generate_hysteria_uri(config, idx+1)
                    hysteria_nodes.append(uri)
        except Exception as e:
            print(f"Hysteria{idx+1} 配置获取失败: {str(e)}")
    return hysteria_nodes

def maintain_history(new_nodes):
    # ...保持原有历史维护逻辑不变...
    # 修改后的完整代码需要考虑字符限制，这里保留核心修改部分

def update_log(status, count):
    # ...原有日志逻辑保持不变...

# 修改后的主处理逻辑
try:
    # 获取原有SS节点
    ss_response = requests.post(a, headers=b, data=c, timeout=15)
    
    all_nodes = []
    
    # 处理SS节点
    if ss_response.status_code == 200:
        decrypted_data = json.loads(f(binascii.unhexlify(ss_response.text.strip()), d, e))
        for item in decrypted_data['data']:
            ss_uri = f"ss://{base64.b64encode(f'aes-256-cfb:{item['password']}@{item['ip']}:{item['port']}'.encode()).decode()}#{item['title']}"
            all_nodes.append(ss_uri)
    
    # 获取Hysteria节点
    all_nodes += fetch_hysteria_nodes()
    
    # 维护历史记录
    added_count = len(maintain_history(all_nodes))
    update_log(True, added_count)

except Exception as ex:
    update_log(False, 0)
    print(f"发生异常: {str(ex)}")
