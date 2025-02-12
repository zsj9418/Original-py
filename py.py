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
        "obfs": config.get("obfs", "xplus"),
        "obfsParam": config.get("obfs_param", ""),
        "sni": config.get("server_name", "")
    }
    
    if version == 1:
        return f"hysteria://{config['server']}:{config['port']}?{format_params(base_params)}#Hysteria1-{config['server']}"
    else:
        return f"hysteria2://{config['auth_str']}@{config['server']}:{config['port']}?{format_params(base_params)}#Hysteria2-{config['server']}"

def format_params(params):
    return "&".join([f"{k}={quote(str(v))}" for k,v in params.items() if v])

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

def fetch_hysteria_nodes():
    hysteria_nodes = []
    for idx, url in enumerate(HYSTERIA_URLS):
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                # 将配置转换为列表（适配单配置和多配置场景）
                configs = json.loads(resp.text)
                if not isinstance(configs, list):
                    configs = [configs]
                
                for config in configs:
                    # 处理Hysteria版本差异
                    if idx == 0:  # Hysteria1
                        parsed = {
                            "server": config["server"].split(",")[0].split(":")[0],
                            "port": config["server"].split(":")[1].split(",")[0],
                            "obfs": config.get("obfs", ""),
                            "server_name": config.get("server_name", ""),
                            "auth_str": config.get("auth_str", "")
                        }
                    else:  # Hysteria2
                        parsed = {
                            "server": config["server"].split(":")[0],
                            "port": config["server"].split(":")[1].split(",")[0],
                            "auth_str": config.get("auth", ""),
                            "obfs": config.get("obfs", ""),
                            "server_name": config.get("tls", {}).get("sni", "")
                        }
                    
                    # 添加带宽参数处理
                    if idx == 0:
                        parsed.update({
                            "up_mbps": config.get("up_mbps", 500),
                            "down_mbps": config.get("down_mbps", 500)
                        })
                    else:
                        parsed.update({
                            "up_mbps": int(config.get("bandwidth", {}).get("up", "500 mbps").split()[0]),
                            "down_mbps": int(config.get("bandwidth", {}).get("down", "500 mbps").split()[0])
                        })
                    
                    uri = generate_hysteria_uri(parsed, idx+1)
                    hysteria_nodes.append(uri)
        except Exception as e:
            print(f"Hysteria{idx+1} 配置解析失败: {str(e)}")
    return hysteria_nodes

def generate_hysteria_uri(config, version):
    base_params = {
        "upmbps": config.get("up_mbps", 500),
        "downmbps": config.get("down_mbps", 500),
        "obfs": config.get("obfs", "xplus"),
        "obfsParam": config.get("obfsParam", ""),
        "sni": config.get("server_name", "")
    }
    
    # 过滤空参数
    params = {k: v for k, v in base_params.items() if v}
    
    if version == 1:
        return f"hysteria://{config['server']}:{config['port']}?{format_params(params)}#Hysteria1-{config['server']}"
    else:
        auth_str = f"{config['auth_str']}@" if config.get("auth_str") else ""
        return f"hysteria2://{auth_str}{config['server']}:{config['port']}?{format_params(params)}#Hysteria2-{config['server']}"

    
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(log_entry + "\n")

a = 'http://api.skrapp.net/api/serverlist'
b = {
    'accept': '/',
    'accept-language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
    'appversion': '1.3.1',
    'user-agent': 'SkrKK/1.3.1 (iPhone; iOS 13.5; Scale/2.00)',
    'content-type': 'application/x-www-form-urlencoded',
    'Cookie': 'PHPSESSID=fnffo1ivhvt0ouo6ebqn86a0d4'
}
c = {'data': '4265a9c353cd8624fd2bc7b5d75d2f18b1b5e66ccd37e2dfa628bcb8f73db2f14ba98bc6a1d8d0d1c7ff1ef0823b11264d0addaba2bd6a30bdefe06f4ba994ed'}
d = b'65151f8d966bf596'
e = b'88ca0f0ea1ecf975'

def f(g, d, e):
    h = pyaes.AESModeOfOperationCBC(d, iv=e)
    i = b''.join(h.decrypt(g[j:j+16]) for j in range(0, len(g), 16))
    return i[:-i[-1]]

try:
    # 获取原有SS节点
    ss_response = requests.post(a, headers=b, data=c, timeout=15)
    all_nodes = []
    
    if ss_response.status_code == 200:
        decrypted_data = json.loads(f(binascii.unhexlify(ss_response.text.strip()), d, e))
        for item in decrypted_data['data']:
            # 修正引号嵌套问题
            ss_config = f"aes-256-cfb:{item['password']}@{item['ip']}:{item['port']}"
            ss_uri = f"ss://{base64.b64encode(ss_config.encode()).decode()}#{item['title']}"
            all_nodes.append(ss_uri)
    
    # 获取Hysteria节点
    all_nodes += fetch_hysteria_nodes()
    
    # 维护历史记录
    added_count = len(maintain_history(all_nodes))
    update_log(True, added_count)

except Exception as ex:
    update_log(False, 0)
    print(f"发生异常: {str(ex)}")
