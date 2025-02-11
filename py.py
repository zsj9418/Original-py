import os
import requests
import base64
import json
import pyaes
import binascii
from datetime import datetime
from collections import deque
import yaml
from git import Repo

# 全局配置
CONFIG = {
    'MAX_HISTORY': 4,  # 保留4个更新周期
    'HISTORY_FILE': "nodes.txt",
    'COMBINED_FILE': "combined_nodes.txt",
    'BATCH_FILE': "history_batches.json",
    'LOG_FILE': "update_history.md",
    'REPO_URL': "https://github.com/Alvin9999/pac2",
    'CLONE_PATH': "temp_repo",
    'TIMEZONE': 'Asia/Shanghai',
    'WECHAT_WEBHOOK': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key'  # 替换为你的企业微信机器人Webhook
}

# 设置时区
os.environ['TZ'] = CONFIG['TIMEZONE']

print("      H͜͡E͜͡L͜͡L͜͡O͜͡ ͜͡W͜͡O͜͡R͜͡L͜͡D͜͡ ͜͡E͜͡X͜͡T͜͡R͜͡A͜͡C͜͡T͜͡ ͜͡S͜͡S͜͡ ͜͡N͜͡O͜͡D͜͡E͜͡")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")
print("Author : 𝐼𝑢")
print(f"Date   : {datetime.today().strftime('%Y-%m-%d')}")
print("Version: 2.0 (GitHub Auto)")
print("𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟 𓆝 𓆟 𓆞 𓆟")

# 企业微信通知模块
def send_wechat_notification(message):
    """发送企业微信通知"""
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    try:
        response = requests.post(CONFIG['WECHAT_WEBHOOK'], headers=headers, json=data)
        if response.status_code != 200:
            print(f"Failed to send WeChat notification: {response.text}")
    except Exception as e:
        print(f"Error sending WeChat notification: {str(e)}")

# GitHub仓库处理模块
def process_github_repo():
    """从GitHub仓库拉取并处理配置"""
    nodes = []
    try:
        # 克隆/更新仓库
        if os.path.exists(CONFIG['CLONE_PATH']):
            repo = Repo(CONFIG['CLONE_PATH'])
            repo.remotes.origin.pull()
        else:
            Repo.clone_from(CONFIG['REPO_URL'], CONFIG['CLONE_PATH'])

        # 处理目标目录
        target_dirs = {
            'hysteria': process_hysteria_config,
            'hysteria2': process_hysteria_config,
            'juicity': process_juicity_config,
            'mieru': process_mieru_config,
            'singbox': process_singbox_config
        }

        # 遍历目录
        for root, dirs, files in os.walk(CONFIG['CLONE_PATH']):
            for dir_name in target_dirs:
                if dir_name in root:
                    for file in files:
                        if file.endswith(('.json', '.yaml', '.yml')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r') as f:
                                    config = yaml.safe_load(f) if file.endswith(('.yaml', '.yml')) else json.load(f)
                                nodes.extend(target_dirs[dir_name](config))
                            except Exception as e:
                                print(f"Error processing {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error processing GitHub repo: {str(e)}")
    return nodes

# Hysteria配置处理
def process_hysteria_config(config):
    """处理Hysteria配置"""
    nodes = []
    if 'server' in config and 'auth' in config:
        base_url = f"hy2://{config['auth']}@{config['server']}:{config.get('port', 443)}"
        params = {
            'obfs': config.get('obfs'),
            'alpn': ','.join(config.get('alpn', [])),
            'sni': config.get('sni')
        }
        query = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        nodes.append(f"{base_url}?{query}#Hysteria2")
    return nodes

# 其他协议处理函数（示例）
def process_juicity_config(config):
    """处理Juicity配置"""
    return []

def process_mieru_config(config):
    """处理Mieru配置"""
    return []

def process_singbox_config(config):
    """处理Singbox配置"""
    return []

# 历史记录维护模块
def maintain_history(new_nodes):
    """维护历史记录"""
    # 读取现有历史
    if os.path.exists(CONFIG['HISTORY_FILE']):
        with open(CONFIG['HISTORY_FILE'], "r") as f:
            history = deque(f.read().splitlines(), CONFIG['MAX_HISTORY'] * 20)
    else:
        history = deque(maxlen=CONFIG['MAX_HISTORY'] * 20)

    # 去重处理
    unique_nodes = set(history)
    added_nodes = [n for n in new_nodes if n not in unique_nodes]

    # 更新历史记录
    history.extend(added_nodes)

    # 维护循环缓冲区
    if len(history) > CONFIG['MAX_HISTORY'] * 20:
        history = deque(list(history)[-(CONFIG['MAX_HISTORY'] * 20):], CONFIG['MAX_HISTORY'] * 20)

    # 写入文件
    with open(CONFIG['HISTORY_FILE'], "w") as f:
        f.write("\n".join(history))

    return added_nodes

# 更新日志模块
def update_log(status, count):
    """更新日志"""
    log_entry = f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_entry += f"- Status: {'Success' if status else 'Failed'}\n"
    if status:
        log_entry += f"- New nodes added: {count}\n"
        log_entry += f"- Total nodes: {count + len(open(CONFIG['HISTORY_FILE']).readlines())}\n"

    with open(CONFIG['LOG_FILE'], "a") as f:
        f.write(log_entry + "\n")

# 主函数
def main():
    """主函数"""
    try:
        # 拉取GitHub仓库配置
        github_nodes = process_github_repo()
        new_nodes = github_nodes

        # 去重处理
        seen = set()
        dedup_nodes = []
        for node in new_nodes:
            key = node.split('#')[0]  # 根据节点主体去重
            if key not in seen:
                seen.add(key)
                dedup_nodes.append(node)
        new_nodes = dedup_nodes

        # 维护历史记录
        added_count = len(maintain_history(new_nodes))

        # 更新日志
        update_log(True, added_count)

        # 发送企业微信通知
        if added_count > 0:
            send_wechat_notification(f"节点更新成功！新增节点数: {added_count}")
        else:
            send_wechat_notification("节点更新完成，无新增节点。")

        print(f"更新成功！新增节点数: {added_count}")
    except Exception as e:
        update_log(False, 0)
        send_wechat_notification(f"节点更新失败！错误信息: {str(e)}")
        print(f"更新失败: {str(e)}")

if __name__ == "__main__":
    main()
