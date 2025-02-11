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
    'BATCH_FILE': "history_batches.json", # This is not used in the provided code, might be for future use
    'LOG_FILE': "update_history.md",
    'REPO_URL': "https://github.com/Alvin9999/pac2",
    'CLONE_PATH': "temp_repo",
    'TIMEZONE': 'Asia/Shanghai',
    'WECHAT_WEBHOOK': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key'  # 替换为你的企业微信机器人Webhook
}

# 设置时区
os.environ['TZ'] = CONFIG['TIMEZONE']

# 初始化文件
def initialize_files():
    """确保所有需要的文件都存在"""
    for file in [CONFIG['HISTORY_FILE'], CONFIG['COMBINED_FILE'], CONFIG['LOG_FILE']]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write("")

def process_github_repo():
    """
    从GitHub仓库拉取节点信息。
    """
    repo_url = CONFIG['REPO_URL']
    clone_path = CONFIG['CLONE_PATH']
    nodes_file_path = os.path.join(clone_path, 'nodes.txt')

    try:
        if os.path.exists(clone_path):
            repo = Repo(clone_path)
            repo.remotes.origin.pull() # 更新仓库
        else:
            Repo.clone_from(repo_url, clone_path) # 克隆仓库

        with open(nodes_file_path, 'r') as f:
            github_nodes = [line.strip() for line in f if line.strip()] # 读取nodes.txt，去除空行
        return github_nodes
    except Exception as e:
        print(f"Error processing GitHub repo: {e}")
        return []

def update_log(success, added_count):
    """
    更新更新日志文件。
    """
    log_file = CONFIG['LOG_FILE']
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    status = "成功" if success else "失败"
    log_entry = f"**{now}**: 节点更新{status}，新增节点数: {added_count}\n"

    if not success:
        import traceback
        log_entry += "```\n" + traceback.format_exc() + "\n```\n"

    with open(log_file, 'a') as f:
        f.write(log_entry)

def maintain_history(new_nodes):
    """
    维护节点历史记录，并返回新增节点。
    """
    history_file = CONFIG['HISTORY_FILE']
    combined_file = CONFIG['COMBINED_FILE']
    max_history = CONFIG['MAX_HISTORY']

    all_history_nodes = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history_data = f.readlines()
            # 假设历史记录文件每组节点之间用空行分隔
            current_history_group = []
            for line in history_data:
                line = line.strip()
                if line:
                    current_history_group.append(line)
                else:
                    if current_history_group:
                        all_history_nodes.append(current_history_group)
                        current_history_group = []
            if current_history_group: # 处理最后可能没有空行分隔的历史组
                all_history_nodes.append(current_history_group)

    all_history_nodes.insert(0, new_nodes) # 将最新节点添加到历史记录的开头
    if len(all_history_nodes) > max_history:
        all_history_nodes = all_history_nodes[:max_history] # 限制历史记录数量

    added_nodes = []
    if all_history_nodes and len(all_history_nodes) > 1:
        previous_nodes = set(all_history_nodes[1])
        current_nodes = set(all_history_nodes[0])
        added_nodes = list(current_nodes - previous_nodes)

    with open(history_file, 'w') as f:
        for i, node_group in enumerate(all_history_nodes):
            for node in node_group:
                f.write(node + '\n')
            if i < len(all_history_nodes) - 1: # 除了最后一组，每组后加一个空行分隔
                f.write('\n')

    # 更新 combined_nodes.txt - 合并所有历史记录中的节点，并去重
    combined_nodes = set()
    for node_group in all_history_nodes:
        combined_nodes.update(node_group)
    with open(combined_file, 'w') as f:
        for node in combined_nodes:
            f.write(node + '\n')

    return added_nodes


def send_wechat_notification(message):
    """
    发送企业微信通知。
    """
    webhook_url = CONFIG['WECHAT_WEBHOOK']
    if not webhook_url or webhook_url == 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key':
        print("请配置企业微信Webhook URL 或取消微信通知。")
        return

    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }
    try:
        response = requests.post(webhook_url, headers=headers, json=data)
        response.raise_for_status() # 检查请求是否成功
        print("企业微信通知发送成功！")
    except requests.exceptions.RequestException as e:
        print(f"企业微信通知发送失败: {e}")


# 主函数
def main():
    """主函数"""
    try:
        # 初始化文件
        initialize_files()

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
        added_nodes = maintain_history(new_nodes)
        added_count = len(added_nodes)

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
