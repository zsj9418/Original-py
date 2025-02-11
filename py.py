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

# 初始化文件
def initialize_files():
    """确保所有需要的文件都存在"""
    for file in [CONFIG['HISTORY_FILE'], CONFIG['COMBINED_FILE'], CONFIG['LOG_FILE']]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write("")

# 处理GitHub仓库
def process_github_repo():
    """从GitHub仓库中提取节点信息"""
    try:
        # 克隆仓库
        if os.path.exists(CONFIG['CLONE_PATH']):
            repo = Repo(CONFIG['CLONE_PATH'])
            repo.remotes.origin.pull()
        else:
            repo = Repo.clone_from(CONFIG['REPO_URL'], CONFIG['CLONE_PATH'])

        # 假设节点信息在仓库的某个文件中
        nodes_file = os.path.join(CONFIG['CLONE_PATH'], "nodes.txt")
        with open(nodes_file, 'r') as f:
            nodes = f.readlines()

        # 清理节点数据
        nodes = [node.strip() for node in nodes if node.strip()]
        return nodes
    except Exception as e:
        raise Exception(f"处理GitHub仓库时出错: {str(e)}")

# 维护历史记录
def maintain_history(new_nodes):
    """维护历史记录并返回新增节点数"""
    try:
        # 读取现有节点
        if os.path.exists(CONFIG['HISTORY_FILE']):
            with open(CONFIG['HISTORY_FILE'], 'r') as f:
                existing_nodes = f.readlines()
            existing_nodes = [node.strip() for node in existing_nodes if node.strip()]
        else:
            existing_nodes = []

        # 计算新增节点
        added_nodes = list(set(new_nodes) - set(existing_nodes))

        # 更新节点文件
        with open(CONFIG['HISTORY_FILE'], 'w') as f:
            f.write("\n".join(new_nodes))

        return added_nodes
    except Exception as e:
        raise Exception(f"维护历史记录时出错: {str(e)}")

# 更新日志
def update_log(success, added_count):
    """更新日志文件"""
    try:
        log_entry = f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_entry += f"**状态:** {'成功' if success else '失败'}\n"
        log_entry += f"**新增节点数:** {added_count}\n\n"

        with open(CONFIG['LOG_FILE'], 'a') as f:
            f.write(log_entry)
    except Exception as e:
        raise Exception(f"更新日志时出错: {str(e)}")

# 发送企业微信通知
def send_wechat_notification(message):
    """发送企业微信通知"""
    try:
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        response = requests.post(CONFIG['WECHAT_WEBHOOK'], json=data)
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"发送企业微信通知时出错: {str(e)}")

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
