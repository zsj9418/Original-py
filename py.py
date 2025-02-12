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
from urllib.parse import urljoin, urlencode

# 强制设置中国时区
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡ ͜͡N͜͡O͜͡D͜͡E͜͡")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("Author : 𝐼𝑢")
print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
print("Version: 3.1 (FIXED)")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("𝐼𝑢:")

# 常量配置
MAX_HISTORY = 4
HISTORY_FILE = "nodes.txt"
LOG_FILE = "update_history.md"
GITHUB_REPO = "https://api.github.com/repos/Alvin9999/pac2/contents/"
TARGET_DIRS = ['hysteria2', 'hysteria', 'juicity', 'singbox', 'v2ray', 'vmess']
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'ghp_abc123')  # 替换为有效token

class ProtocolValidator:
    @staticmethod
    def validate_port(port):
        return isinstance(port, int) and 1 <= port <= 65535

    @staticmethod
    def validate_address(address):
        return re.match(r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$', address) or re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', address)

def fetch_github_configs():
    nodes = []
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    
    for dir_path in TARGET_DIRS:
        print(f"\n🔍 正在扫描目录: {dir_path}")
        try:
            response = requests.get(urljoin(GITHUB_REPO, dir_path), headers=headers)
            if response.status_code != 200:
                print(f"⚠️ 目录请求失败 [{response.status_code}]: {dir_path}")
                continue
                
            contents = response.json()
            for item in contents:
                if item['type'] == 'file' and item['name'].endswith(('.json', '.yaml', '.yml')):
                    print(f"📄 发现配置文件: {item['name']}")
                    file_response = requests.get(item['download_url'])
                    if file_response.status_code == 200:
                        parsed = parse_config(file_response.text, dir_path)
                        print(f"🎯 解析到 {len(parsed)} 个节点")
                        nodes += parsed
                    else:
                        print(f"⛔ 文件下载失败: {item['name']} [{file_response.status_code}]")
        except Exception as e:
            print(f"🚨 严重错误: {str(e)}")
    return nodes

def parse_config(content, protocol):
    try:
        # 预处理内容
        content = content.strip().replace('\t', ' ')
        
        # 根据协议类型选择解析器
        if protocol in ['hysteria2', 'hysteria']:
            config = yaml.safe_load(content)
        else:
            config = json.loads(content)
            
        nodes = []
        
        # 通用验证
        if not ProtocolValidator.validate_port(config.get('port', 0)):
            raise ValueError("端口号无效")

        # 协议特定解析
        if protocol == 'hysteria2':
            auth = config.get('auth', {}).get('password', '')
            server = config.get('server', '').split(':')[0]  # 处理可能存在的端口粘连
            port = int(config.get('server', ':443').split(':')[-1]) if ':' in config.get('server', '') else 443
            
            tls_config = config.get('tls', {})
            obfs_config = config.get('obfs', {})
            
            params = {
                'upmbps': config.get('up_mbps'),
                'downmbps': config.get('down_mbps'),
                'sni': tls_config.get('sni', ''),
                'insecure': int(tls_config.get('insecure', 0)),
                'alpn': ','.join(tls_config.get('alpn', [])),
                'obfs': obfs_config.get('type', ''),
                'obfs-password': obfs_config.get('password', '')
            }
            params = {k: v for k, v in params.items() if v not in [None, '', 0]}
            
            # 生成兼容sing-box的URI
            node_str = f"hy2://{auth}@{server}:{port}?{urlencode(params)}"
            if ProtocolValidator.validate_address(server) and ProtocolValidator.validate_port(port):
                nodes.append(node_str)

        elif protocol == 'hysteria':
            auth = config.get('auth_str', '')
            server = config.get('server', '').split(':')[0]
            port = int(config.get('server', ':443').split(':')[-1]) if ':' in config.get('server', '') else 443
            
            params = {
                'protocol': config.get('protocol', 'udp'),
                'upmbps': config.get('up_mbps'),
                'downmbps': config.get('down_mbps'),
                'alpn': ','.join(config.get('alpn', [])),
                'obfs': config.get('obfs', ''),
                'peer': config.get('server_name', ''),
                'insecure': int(config.get('insecure', 0))
            }
            params = {k: v for k, v in params.items() if v not in [None, '', 0]}
            node_str = f"hy://{auth}@{server}:{port}?{urlencode(params)}"
            if ProtocolValidator.validate_address(server) and ProtocolValidator.validate_port(port):
                nodes.append(node_str)

        elif protocol == 'juicity':
            users = config.get('users', [])
            if not isinstance(users, list):
                users = [users]
            server = config.get('server', '').split(':')[0]
            port = int(config.get('server', ':443').split(':')[-1]) if ':' in config.get('server', '') else 443
            for user in users:
                uuid = user.get('uuid', '')
                node_str = f"juicity://{uuid}@{server}:{port}"
                if ProtocolValidator.validate_address(server) and ProtocolValidator.validate_port(port):
                    nodes.append(node_str)

        elif protocol == 'singbox':
            inbounds = config.get('inbounds', [])
            for inbound in inbounds:
                if inbound.get('type') == 'vless':
                    server = inbound.get('server', '').split(':')[0]
                    port = int(inbound.get('server', ':443').split(':')[-1]) if ':' in inbound.get('server', '') else 443
                    user_id = inbound.get('users', [{}])[0].get('id', '')
                    security = 'tls' if inbound.get('tls') else 'none'
                    network = inbound.get('network', 'tcp')
                    params = f"security={security}&type={network}"
                    node_str = f"singbox://{user_id}@{server}:{port}?{params}"
                    if ProtocolValidator.validate_address(server) and ProtocolValidator.validate_port(port):
                        nodes.append(node_str)

        # 过滤无效节点
        return [n for n in nodes if 
                ProtocolValidator.validate_address(n.split('@')[1].split(':')[0]) and 
                ProtocolValidator.validate_port(int(n.split(':')[-1].split('/')[0]))]

    except Exception as e:
        print(f"🚨 [{protocol.upper()} 解析错误] {str(e)}")
        print(f"🔧 问题内容片段:\n{content[:150]}...")
        return []

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
        print("\n🌐 开始扫描GitHub仓库配置...")
        github_nodes = fetch_github_configs()
        print(f"✅ 从GitHub获取到 {len(github_nodes)} 个节点")
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
