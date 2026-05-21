# -*- coding: utf-8 -*-
import subprocess
import os

# 获取安装位置
result = subprocess.run(['pip', 'show', 'douyin-downloader'], capture_output=True, text=True)
location = ""
for line in result.stdout.split('\n'):
    if line.startswith('Location:'):
        location = line.split(':')[1].strip()
        break

print(f"安装位置: {location}")

# 查看目录内容
if location:
    douyin_dirs = []
    for item in os.listdir(location):
        if 'douyin' in item.lower():
            douyin_dirs.append(item)
    print(f"\n找到的相关目录/文件: {douyin_dirs}")
    
    # 检查每个目录
    for item in douyin_dirs:
        full_path = os.path.join(location, item)
        if os.path.isdir(full_path):
            print(f"\n{item} 目录内容:")
            for file in os.listdir(full_path):
                if file.endswith('.py'):
                    print(f"  - {file}")