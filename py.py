import os
import time
import requests
import base64
import json
import pyaes
import binascii
import yaml
import re
from datetime import datetime
from collections import deque
from urllib.parse import urljoin, urlencode，quote, urlparse
from socket import socket, AF_INET, SOCK_STREAM

# 强制设置中国时区
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡ ͜͡N͜͡O͜͡D͜͡E͜͡")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("Author : 𝐼𝑢")
print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
print("Version: 2.1 (增强健壮性)")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("𝐼𝑢:")

MAX_HISTORY = 4
HISTORY_FILE = "nodes.txt"
LOG_FILE = "update_history.md"
HYSTERIA_URLS = [
    'https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria/1/config.json',
    'https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria2/config.json'
]
TIMEOUT = 15
PORT_CHECK_TIMEOUT = 3

def check_port(host, port):
    """检查节点端口是否可达"""
    try:
        with socket(AF_INET, SOCK_STREAM) as s:
            s.settimeout(PORT_CHECK_TIMEOUT)
            s.connect((host, port))
        return True
    except Exception:
        return False

def get_hysteria_nodes():
    hysteria_nodes = []
    for url in HYSTERIA_URLS:
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            configs = json.loads(response.text)
            
            for cfg in configs.get('servers', []):
                try:
                    server = cfg['server']
                    port = int(cfg['server_port'])
                    
                    # 检查端口是否可达
                    if not check_port(server, port):
                        print(f"节点 {server}:{port} 不可达，跳过")
                        continue
                    
                    # Hysteria1格式
                    if url.endswith('hysteria/1/config.json'):
                        params = [
                            f"auth={quote(cfg.get('auth_str', ''))}",
                            f"insecure={1 if cfg.get('insecure', False) else 0}",
                            f"alpn={quote(cfg.get('alpn', ''))}"
                        ]
                        uri = f"hy://{server}:{port}?{'&'.join(params)}#{quote(cfg.get('remarks', ''))}"
                    
                    # Hysteria2格式
                    else:
                        auth = f"{quote(cfg.get('auth_str', ''))}@" if cfg.get('auth_str') else ""
                        params = [
                            f"insecure={1 if cfg.get('insecure', False) else 0}",
                            f"obfs={quote(cfg.get('obfs', ''))}"
                        ]
                        uri = f"hy2://{auth}{server}:{port}?{'&'.join(params)}#{quote(cfg.get('remarks', ''))}"
                    
                    hysteria_nodes.append(uri)
                except KeyError as e:
                    print(f"配置缺少必要字段: {str(e)}")
                    continue
        except requests.RequestException as e:
            print(f"获取Hysteria配置失败: {str(e)}")
            continue
    return hysteria_nodes

def maintain_history(new_nodes):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding='utf-8') as f:
            history = deque(f.read().splitlines(), MAX_HISTORY*20)
    else:
        history = deque(maxlen=MAX_HISTORY*20)

    unique_nodes = set(history)
    added_nodes = [n for n in new_nodes if n not in unique_nodes]
    
    history.extend(added_nodes)
    
    if len(history) > MAX_HISTORY*20:
        history = deque(list(history)[-(MAX_HISTORY*20):], MAX_HISTORY*20)
    
    with open(HISTORY_FILE, "w", encoding='utf-8') as f:
        f.write("\n".join(history))
    
    return added_nodes

def update_log(status, count):
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"## {log_time}\n"
    log_entry += f"- 状态: {'成功' if status else '失败'}\n"
    
    if status:
        total = 0
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                total = len(f.readlines())
        
        log_entry += f"- 新增节点数: {count}\n"
        log_entry += f"- 累计节点总数: {total}\n"
    else:
        log_entry += "- 错误详情: 接口请求失败\n"
    
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(log_entry + "\n")

def decrypt_aes(data, key, iv):
    aes = pyaes.AESModeOfOperationCBC(key, iv=iv)
    decrypted = b''.join(aes.decrypt(data[i:i+16]) for i in range(0, len(data), 16))
    return decrypted[:-decrypted[-1]]

def get_ss_nodes():
    ss_nodes = []
    try:
        response = requests.post(a, headers=b, data=c, timeout=TIMEOUT)
        response.raise_for_status()
        
        encrypted_data = binascii.unhexlify(response.text.strip())
        decrypted_data = decrypt_aes(encrypted_data, d, e)
        node_data = json.loads(decrypted_data)
        
        for node in node_data['data']:
            try:
                host = node['ip']
                port = int(node['port'])
                
                if not check_port(host, port):
                    print(f"节点 {host}:{port} 不可达，跳过")
                    continue
                
                ss_uri = f"aes-256-cfb:{node['password']}@{host}:{port}"
                ss_uri_b64 = base64.b64encode(ss_uri.encode('utf-8')).decode('utf-8')
                full_uri = f"ss://{ss_uri_b64}#{node['title']}"
                ss_nodes.append(full_uri)
            except KeyError as e:
                print(f"SS节点配置缺少必要字段: {str(e)}")
                continue
    except requests.RequestException as e:
        print(f"获取SS节点失败: {str(e)}")
    except (binascii.Error, json.JSONDecodeError, ValueError) as e:
        print(f"解析SS节点数据失败: {str(e)}")
    
    return ss_nodes

# 配置信息
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

try:
    # 获取SS节点
    ss_nodes = get_ss_nodes()
    print("\nSS节点:")
    for node in ss_nodes:
        print(node)
    
    # 获取Hysteria节点
    hysteria_nodes = get_hysteria_nodes()
    print("\nHysteria节点:")
    for node in hysteria_nodes:
        print(node)
    
    # 合并节点并去重
    all_nodes = list(set(ss_nodes + hysteria_nodes))
    
    # 维护历史记录
    added_count = len(maintain_history(all_nodes))
    update_log(True, added_count)

except Exception as ex:
    update_log(False, 0)
    print(f"发生异常: {str(ex)}")
