import os
import requests
import base64
import json
import pyaes
import binascii
from datetime import datetime
from collections import deque

# 设置时区为中国时间
os.environ['TZ'] = 'Asia/Shanghai'

print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡ ͜͡N͜͡O͜͡D͜͡E͜͡")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("Author : 𝐼𝑢")
print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
print("Version: 1.0")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("𝐼𝑢:")

# 历史文件维护配置
MAX_HISTORY = 4
HISTORY_FILE = "nodes.txt"
LOG_FILE = "update_history.md"

def maintain_history(new_nodes):
    # 读取现有历史
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = deque(f.read().splitlines(), MAX_HISTORY*20)
    else:
        history = deque(maxlen=MAX_HISTORY*20)

    # 去重处理
    unique_nodes = set(history)
    added_nodes = [n for n in new_nodes if n not in unique_nodes]
    
    # 更新历史记录
    history.extend(added_nodes)
    
    # 维护循环缓冲区
    if len(history) > MAX_HISTORY*20:
        history = deque(list(history)[-(MAX_HISTORY*20):], MAX_HISTORY*20)
    
    # 写入文件
    with open(HISTORY_FILE, "w") as f:
        f.write("\n".join(history))
    
    return added_nodes

def update_log(status, count):
    log_entry = f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_entry += f"- Status: {'Success' if status else 'Failed'}\n"
    if status:
        log_entry += f"- New nodes added: {count}\n"
        log_entry += f"- Total nodes: {count + len(open(HISTORY_FILE).readlines())}\n"
    
    with open(LOG_FILE, "a") as f:
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

j = requests.post(a, headers=b, data=c)

if j.status_code == 200:
    k = j.text.strip()
    l = binascii.unhexlify(k)
    m = f(l, d, e)
    n = json.loads(m)
    
    # 生成新节点
    new_nodes = []
    for o in n['data']:
        p = f"aes-256-cfb:{o['password']}@{o['ip']}:{o['port']}"
        q = base64.b64encode(p.encode('utf-8')).decode('utf-8')
        r = f"ss://{q}#{o['title']}"
        new_nodes.append(r)
        print(r)
    
    # 维护历史记录
    added_count = len(maintain_history(new_nodes))
    update_log(True, added_count)
else:
    update_log(False, 0)
    print(f"Error: HTTP {j.status_code}")
