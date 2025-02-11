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
