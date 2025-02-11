import os
import time
import requests
import base64
import json
import pyaes
import binascii
import yaml
from datetime import datetime
from collections import deque
from urllib.parse import urljoin, urlencode

# 强制设置中国时区
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()  # 应用时区设置

print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡ ͜͡N͜͡O͜͡D͜͡E͜͡")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("Author : 𝐼𝑢")
print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
print("Version: 2.2")  # 更新版本号
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("𝐼𝑢:")

# 常量配置
MAX_HISTORY = 4
HISTORY_FILE = "nodes.txt"
LOG_FILE = "update_history.md"
GITHUB_REPO = "https://api.github.com/repos/Alvin9999/pac2/contents/"
TARGET_DIRS = ['hysteria2', 'hysteria', 'juicity', 'mieru', 'singbox']

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

def fetch_github_configs():
    nodes = []
    for dir_path in TARGET_DIRS:
        try:
            response = requests.get(urljoin(GITHUB_REPO, dir_path))
            if response.status_code == 200:
                contents = response.json()
                for item in contents:
                    if item['type'] == 'file' and item['name'].endswith(('.json', '.yaml', '.yml')):
                        file_content = requests.get(item['download_url']).text
                        nodes += parse_config(file_content, dir_path)
        except Exception as e:
            print(f"Error fetching {dir_path}: {str(e)}")
    return nodes

def parse_config(content, protocol):
    try:
        nodes = []
        config = yaml.safe_load(content) if protocol in ['hysteria2', 'hysteria'] else json.loads(content)
        
        if protocol == 'hysteria2':
            # 适配新版Hysteria2配置结构
            auth = config.get('auth', {}).get('password', 'default-auth')
            server = config.get('server', '0.0.0.0')
            port = config.get('port', 443)
            up = config.get('up_mbps', 1000)
            down = config.get('down_mbps', 1000)
            params = {
                'upmbps': up,
                'downmbps': down,
                'insecure': int(config.get('tls', {}).get('insecure', 0))
            }
            nodes.append(f"hy2://{auth}@{server}:{port}?{urlencode(params)}")
            
        elif protocol == 'hysteria':
            auth_str = config.get('auth_str', 'default-auth')
            server = config.get('server', '0.0.0.0')
            port = config.get('port', 443)
            up = config.get('up_mbps', 100)
            down = config.get('down_mbps', 500)
            params = {
                'protocol': config.get('protocol', 'udp'),
                'upmbps': up,
                'downmbps': down,
                'insecure': int(config.get('insecure', 0))
            }
            nodes.append(f"hy://{auth_str}@{server}:{port}?{urlencode(params)}")
            
        elif protocol == 'juicity':
            users = config.get('users', [])
            if not isinstance(users, list):
                users = [users]
            server = config.get('server', '0.0.0.0')
            port = config.get('port', 443)
            for user in users:
                uuid = user.get('uuid', 'default-uuid')
                nodes.append(f"juicity://{uuid}@{server}:{port}")
                
        elif protocol == 'mieru':
            username = config.get('username', 'default-user')
            password = config.get('password', 'default-pass')
            server = config.get('server', '0.0.0.0')
            port = config.get('port', 443)
            nodes.append(f"mieru://{username}:{password}@{server}:{port}")
            
        elif protocol == 'singbox':
            inbounds = config.get('inbounds', [])
            for inbound in inbounds:
                if inbound.get('type') == 'vless':
                    server = inbound.get('server', '0.0.0.0')
                    port = inbound.get('port', 443)
                    user_id = inbound.get('users', [{}])[0].get('id', 'default-id')
                    security = 'tls' if inbound.get('tls') else 'none'
                    network = inbound.get('network', 'tcp')
                    params = f"security={security}&type={network}"
                    nodes.append(f"singbox://{user_id}@{server}:{port}?{params}")
    except Exception as e:
        print(f"Error parsing {protocol} config: {str(e)}")
    return nodes

# 原有解密逻辑保持不变
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
    j = requests.post(a, headers=b, data=c, timeout=15)
    new_nodes = []
    
    if j.status_code == 200:
        k = j.text.strip()
        l = binascii.unhexlify(k)
        m = f(l, d, e)
        n = json.loads(m)
        
        # 生成原有SS节点
        for o in n['data']:
            p = f"aes-256-cfb:{o['password']}@{o['ip']}:{o['port']}"
            q = base64.b64encode(p.encode('utf-8')).decode('utf-8')
            r = f"ss://{q}#{o['title']}"
            new_nodes.append(r)
        
        # 新增GitHub配置解析
        github_nodes = fetch_github_configs()
        new_nodes += github_nodes
        
        # 维护历史记录
        added_count = len(maintain_history(new_nodes))
        update_log(True, added_count)
    else:
        update_log(False, 0)
        print(f"请求失败，HTTP状态码: {j.status_code}")

except Exception as ex:
    update_log(False, 0)
    print(f"发生异常: {str(ex)}")
