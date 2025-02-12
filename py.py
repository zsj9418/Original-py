import os
import time
import requests
import base64
import json
import pyaes
import binascii
from datetime import datetime
from collections import deque

# 强制设置中国时区
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡/Hysteria ͜͡N͜͡O͜͡D͜͡E͜͡")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("Author : 𝐼𝑢")
print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
print("Version: 2.4 (Fixed Port Parsing for IPv6)")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("𝐼𝑢:")

MAX_HISTORY = 4
HISTORY_FILE = "nodes.txt"
LOG_FILE = "update_history.md"
HYSTERIA_URLS = [
    "https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria/1/config.json",
    "https://www.gitlabip.xyz/Alvin9999/pac2/master/hysteria2/config.json"
]


def maintain_history(new_nodes):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding='utf-8') as f:
            history = deque(f.read().splitlines(), MAX_HISTORY * 50)
    else:
        history = deque(maxlen=MAX_HISTORY * 50)

    unique_nodes = set(history)
    added_nodes = [n for n in new_nodes if n not in unique_nodes]
    history.extend(added_nodes)

    if len(history) > MAX_HISTORY * 50:
        history = deque(list(history)[-(MAX_HISTORY * 50):], MAX_HISTORY * 50)

    with open(HISTORY_FILE, "w", encoding='utf-8') as f:
        f.write("\n".join(history))

    return added_nodes


def update_log(status, count, error_msg=""):
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
        log_entry += f"- 错误详情: {error_msg}\n"

    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(log_entry + "\n")


def fetch_and_convert_hysteria(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        config = response.json()

        if "auth_str" in config or "auth" in config:
            if "auth_str" in config:
                # Hysteria 1
                auth_str = config.get("auth_str", "")
                server = config.get("server", "")
                fast_open = config.get("fast_open", True)
                insecure = config.get("insecure", False)
                server_name = config.get("server_name", "")
                alpn = config.get("alpn", "h3")
                up = config.get("up", "500")
                down = config.get("down", "1000")
                obfs = config.get("obfs", "")
                obfs_param = config.get("obfsParam", "")
                protocol = config.get("protocol", "udp")
                remarks = config.get("remarks", "")

                if not server:
                    print("错误：server 字段不能为空")
                    return None

                # 使用 rpartition 从右侧分割，只分割一次
                host, _, port_str = server.rpartition(":")
                if not port_str:
                    print("错误：server 字段必须包含端口 (例如: example.com:443)")
                    return None
                try:
                    port = int(port_str)
                except ValueError:
                    print("错误：无效的端口号")
                    return None

                query_params = []
                query_params.append(f"protocol={protocol}")
                if auth_str:
                    query_params.append(f"auth={auth_str}")
                query_params.append(f"peer={server_name}")
                query_params.append(f"insecure={int(insecure)}")
                query_params.append(f"upmbps={str(up)}")
                query_params.append(f"downmbps={str(down)}")
                query_params.append(f"alpn={alpn}")
                if obfs:
                    query_params.append(f"obfs={obfs}")
                if obfs_param:
                    query_params.append(f"obfsParam={obfs_param}")

                query_string = "&".join(query_params)
                hysteria_uri = f"hysteria://{host}:{port}?{query_string}"
                if remarks:
                    hysteria_uri += f"#{remarks}"

                return hysteria_uri

            else:
                # Hysteria 2
                auth = config.get("auth", "")
                server = config.get("server", "")
                fast_open = config.get("fast_open", True)
                insecure = config.get("insecure", False)
                server_name = config.get("server_name", "")
                alpn = config.get("alpn", "h3")
                protocol = config.get("protocol", "udp")
                up = config.get("up", "500Mbps")
                down = config.get("down", "1000Mbps")
                remarks = config.get("remarks", "")

                if not server:
                    print("错误：server 字段不能为空")
                    return None

                # 使用 rpartition 从右侧分割，只分割一次
                hostname, _, port_str = server.rpartition(":")
                if not port_str:
                    print("错误: server 字段必须包含端口号 (例如: example.com:443)")
                    return None
                try:
                    port = int(port_str)
                except ValueError:
                    print("错误：无效的端口")
                    return None

                query_params = []
                query_params.append(f"insecure={int(insecure)}")
                query_params.append(f"fastopen={int(fast_open)}")
                query_params.append(f"alpn={alpn}")
                query_params.append(f"up={up}")
                query_params.append(f"down={down}")

                if auth:
                    auth_encoded = base64.b64encode(auth.encode()).decode()
                    query_params.append(f"auth={auth_encoded}")

                query_string = "&".join(query_params)
                hysteria2_uri = f"hysteria2://{hostname}:{port}/?{query_string}"
                if remarks:
                    hysteria2_uri += f"#{remarks}"
                return hysteria2_uri
        else:
            print("错误：无效的 Hysteria 配置文件 - 缺少 auth_str 或 auth")
            return None

    except requests.RequestException as e:
        print(f"请求 Hysteria 配置失败: {e}")
        return None
    except json.JSONDecodeError:
        print(f"解析 Hysteria 配置 JSON 失败")
        return None
    except Exception as e:
        print(f"发生其他错误: {e}")
        return None

def fetch_ss_nodes():
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

    def decrypt(g, d, e):
        h = pyaes.AESModeOfOperationCBC(d, iv=e)
        i = b''.join(h.decrypt(g[j:j + 16]) for j in range(0, len(g), 16))
        return i[:-i[-1]]

    try:
        j = requests.post(a, headers=b, data=c, timeout=15)
        j.raise_for_status()

        k = j.text.strip()
        l = binascii.unhexlify(k)
        m = decrypt(l, d, e)
        n = json.loads(m)

        nodes = []
        for o in n['data']:
            p = f"aes-256-cfb:{o['password']}@{o['ip']}:{o['port']}"
            q = base64.b64encode(p.encode('utf-8')).decode('utf-8')
            r = f"ss://{q}#{o['title']}"
            nodes.append(r)
        return nodes

    except requests.RequestException as ex:
        update_log(False, 0, f"SS 节点请求失败: {str(ex)}")
        return []
    except Exception as ex:
        update_log(False, 0, f"SS 节点处理异常: {str(ex)}")
        return []

def main():
    all_new_nodes = []

    # 获取并转换 Hysteria 节点
    for url in HYSTERIA_URLS:
        hysteria_node = fetch_and_convert_hysteria(url)
        if hysteria_node:
            all_new_nodes.append(hysteria_node)

    # 获取 SS 节点
    ss_nodes = fetch_ss_nodes()
    all_new_nodes.extend(ss_nodes)

    # 维护历史记录并更新日志
    added_count = len(maintain_history(all_new_nodes))
    update_log(True, added_count)


if __name__ == "__main__":
    main()
