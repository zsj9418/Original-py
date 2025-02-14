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

# --- 常量定义 ---
MAX_HISTORY = 3
HISTORY_FILE = "nodes.txt"
LOG_FILE = "update_history.md"
HYSTERIA_URLS = [
    "https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria/1/config.json",
    "https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria2/config.json"
]

# --- 核心函数定义 ---
def generate_hysteria_uri(config, version):
    base_params = {
        "upmbps": config.get("up_mbps", 500),
        "downmbps": config.get("down_mbps", 500),
        "obfs": config.get("obfs", "xplus"),
        "obfsParam": config.get("obfsParam", ""),
        "sni": config.get("server_name", "")
    }
    params = {k: v for k, v in base_params.items() if v}
    
    if version == 1:
        return f"hysteria://{config['server']}:{config['port']}?{format_params(params)}#Hysteria1-{config['server']}"
    else:
        auth_str = f"{config['auth_str']}@" if config.get("auth_str") else ""
        return f"hysteria2://{auth_str}{config['server']}:{config['port']}?{format_params(params)}#Hysteria2-{config['server']}"

def format_params(params):
    return "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])

def fetch_hysteria_nodes():
    hysteria_nodes = []
    for idx, url in enumerate(HYSTERIA_URLS):
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                configs = json.loads(resp.text)
                if not isinstance(configs, list):
                    configs = [configs]
                
                for config in configs:
                    # Hysteria1解析逻辑
                    if idx == 0:
                        parsed = {
                            "server": config["server"].split(",")[0].split(":")[0],
                            "port": config["server"].split(":")[1].split(",")[0],
                            "obfs": config.get("obfs", ""),
                            "server_name": config.get("server_name", ""),
                            "auth_str": config.get("auth_str", ""),
                            "up_mbps": config.get("up_mbps", 500),
                            "down_mbps": config.get("down_mbps", 500)
                        }
                    # Hysteria2解析逻辑
                    else:
                        parsed = {
                            "server": config["server"].split(":")[0],
                            "port": config["server"].split(":")[1].split(",")[0],
                            "auth_str": config.get("auth", ""),
                            "obfs": config.get("obfs", ""),
                            "server_name": config.get("tls", {}).get("sni", ""),
                            "up_mbps": int(config.get("bandwidth", {}).get("up", "500 mbps").split()[0]),
                            "down_mbps": int(config.get("bandwidth", {}).get("down", "500 mbps").split()[0])
                        }
                    hysteria_nodes.append(generate_hysteria_uri(parsed, idx+1))
        except Exception as e:
            print(f"Hysteria{idx+1} 配置处理失败: {str(e)}")
    return hysteria_nodes

def maintain_history(new_nodes):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding='utf-8') as f:
            history = deque(f.read().splitlines(), MAX_HISTORY*12)
    else:
        history = deque(maxlen=MAX_HISTORY*12)

    unique_nodes = set(history)
    added_nodes = [n for n in new_nodes if n not in unique_nodes]
    
    history.extend(added_nodes)
    
    with open(HISTORY_FILE, "w", encoding='utf-8') as f:
        f.write("\n".join(history))
    
    return added_nodes

def update_log(status, count):
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"## {log_time}\n- 状态: {'成功' if status else '失败'}\n"
    
    if status:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            total = len(f.readlines())
        log_entry += f"- 新增节点数: {count}\n- 累计节点总数: {total}\n"
    else:
        log_entry += "- 错误详情: 接口请求失败\n"
    
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(log_entry + "\n")

# --- 主程序逻辑 ---
if __name__ == "__main__":
    print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡ ͜͡N͜͡O͜͡D͜͡E͜͡")
    print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
    print("Author : 𝐼𝑢")
    print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
    print("Version: 1.2 (Stable Release)")
    print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
    print("𝐼𝑢:")

    # API配置
    API_ENDPOINT = 'http://api.skrapp.net/api/serverlist'
    HEADERS = {
        'accept': '/',
        'accept-language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
        'appversion': '1.3.1',
        'user-agent': 'SkrKK/1.3.1 (iPhone; iOS 13.5; Scale/2.00)',
        'content-type': 'application/x-www-form-urlencoded',
        'Cookie': 'PHPSESSID=fnffo1ivhvt0ouo6ebqn86a0d4'
    }
    PAYLOAD = {'data': '4265a9c353cd8624fd2bc7b5d75d2f18b1b5e66ccd37e2dfa628bcb8f73db2f14ba98bc6a1d8d0d1c7ff1ef0823b11264d0addaba2bd6a30bdefe06f4ba994ed'}
    KEY = b'65151f8d966bf596'
    IV = b'88ca0f0ea1ecf975'

    # AES解密函数
    def aes_decrypt(ciphertext, key, iv):
        cipher = pyaes.AESModeOfOperationCBC(key, iv=iv)
        plaintext = b''.join(cipher.decrypt(ciphertext[i:i+16]) for i in range(0, len(ciphertext), 16))
        return plaintext[:-plaintext[-1]]

    try:
        # 获取SS节点
        ss_nodes = []
        response = requests.post(API_ENDPOINT, headers=HEADERS, data=PAYLOAD, timeout=15)
        if response.status_code == 200:
            decrypted = json.loads(aes_decrypt(binascii.unhexlify(response.text.strip()), KEY, IV))
            for item in decrypted['data']:
                ss_config = f"aes-256-cfb:{item['password']}@{item['ip']}:{item['port']}"
                ss_uri = f"ss://{base64.b64encode(ss_config.encode()).decode()}#{item['title']}"
                ss_nodes.append(ss_uri)

        # 合并所有节点
        all_nodes = ss_nodes + fetch_hysteria_nodes()
        
        # 维护历史记录
        added_count = len(maintain_history(all_nodes))
        update_log(True, added_count)

    except Exception as e:
        update_log(False, 0)
        print(f"全局异常: {str(e)}")
