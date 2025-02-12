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

def maintain_history(new_nodes):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding='utf-8') as f:
            history = deque(f.read().splitlines(), MAX_HISTORY*20)
    else:
        history = deque(maxlen=MAX_HISTORY*20)

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
