import os
import time
import requests
import base64
import json
import pyaes
import binascii
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from collections import deque

# 时区设置
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

# 常量配置
MAX_HISTORY = 4
ENTRIES_PER_UPDATE = 20
HYSTERIA_SOURCES = [
    ('https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria/1/config.json', False),
    ('https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria2/config.json', True)
]

def decrypt_data(ciphertext, key, iv):
    cipher = pyaes.AESModeOfOperationCBC(key, iv=iv)
    decrypted = b''.join(cipher.decrypt(ciphertext[i:i+16]) for i in range(0, len(ciphertext), 16))
    return decrypted[:-decrypted[-1]]

def parse_hysteria_config(url, is_v2=False):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        config = resp.json()
        
        base_params = {
            'password': config.get('auth_str', ''),
            'sni': config.get('server_name', ''),
            'insecure': int(config.get('insecure', 0)),
            'upmbps': config.get('up_mbps', 20),
            'downmbps': config.get('down_mbps', 100)
        }
        
        if is_v2:
            return f"hy2://{config['server']}:{config['port']}?" + "&".join(
                [f"{k}={v}" for k,v in base_params.items() if v]
            ) + f"#Hysteria2-{config['server']}"
        else:
            return f"hy://{config['server']}:{config['port']}?" + "&".join(
                [f"{k}={v}" for k,v in {
                    **base_params,
                    'protocol': config.get('protocol', 'udp'),
                    'obfs': config.get('obfs', ''),
                    'alpn': config.get('alpn', 'h3')
                }.items() if v]
            ) + f"#Hysteria1-{config['server']}"
    except Exception as e:
        print(f"Hysteria配置解析失败: {str(e)}")
        return None

def maintain_history(new_nodes):
    history_file = "nodes.txt"
    max_entries = MAX_HISTORY * ENTRIES_PER_UPDATE
    
    existing = []
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            existing = f.read().splitlines()
    
    # 滚动更新策略
    updated_list = existing[len(new_nodes):] + new_nodes if len(existing) >= max_entries else existing + new_nodes
    updated_list = updated_list[-max_entries:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(updated_list))
    
    return len(new_nodes)

def update_log(success, added_count):
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total = 0
    if os.path.exists("nodes.txt"):
        with open("nodes.txt", 'r') as f:
            total = len(f.readlines())
    
    log_entry = f"## {log_time}\n- 状态: {'成功' if success else '失败'}\n"
    if success:
        log_entry += f"- 新增节点: {added_count}\n- 当前总数: {total}\n"
    
    with open("update_history.md", "a") as f:
        f.write(log_entry + "\n")

# 主程序逻辑
if __name__ == "__main__":
    # 原有SS节点获取逻辑
    ss_nodes = []
    try:
        response = requests.post(
            'http://api.skrapp.net/api/serverlist',
            headers={
                'accept': '/',
                'accept-language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
                'appversion': '1.3.1',
                'user-agent': 'SkrKK/1.3.1 (iPhone; iOS 13.5; Scale/2.00)',
                'content-type': 'application/x-www-form-urlencoded',
                'Cookie': 'PHPSESSID=fnffo1ivhvt0ouo6ebqn86a0d4'
            },
            data={
                'data': '4265a9c353cd8624fd2bc7b5d75d2f18b1b5e66ccd37e2dfa628bcb8f73db2f14ba98bc6a1d8d0d1c7ff1ef0823b11264d0addaba2bd6a30bdefe06f4ba994ed'
            },
            timeout=15
        )
        if response.status_code == 200:
            decrypted = decrypt_data(binascii.unhexlify(response.text.strip()), b'65151f8d966bf596', b'88ca0f0ea1ecf975')
            data = json.loads(decrypted)
            ss_nodes = [
                f"ss://{base64.b64encode(f'aes-256-cfb:{item['password']}@{item['ip']}:{item['port']}'.encode()).decode()}#{item['title']}"
                for item in data['data']
            ]
    except Exception as e:
        print(f"SS节点获取失败: {str(e)}")
    
    # 获取Hysteria节点
    hysteria_nodes = []
    for url, is_v2 in HYSTERIA_SOURCES:
        if node := parse_hysteria_config(url, is_v2):
            hysteria_nodes.append(node)
    
    # 合并所有节点
    all_nodes = ss_nodes + hysteria_nodes
    
    # 更新节点记录
    added = maintain_history(all_nodes)
    update_log(success=True, added_count=added)
    
    print(f"本次更新完成，新增节点数: {added}，总节点数: {len(all_nodes)}")
