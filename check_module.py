# -*- coding: utf-8 -*-
import subprocess

# 获取安装位置
result = subprocess.run(['pip', 'show', 'douyin-downloader'], capture_output=True, text=True)
location = ""
for line in result.stdout.split('\n'):
    if line.startswith('Location:'):
        location = line.split(':', 1)[1].strip()
        break

print(f"安装位置: {location}")

# 使用 dir 命令查看目录内容
if location:
    result = subprocess.run(['dir', location], capture_output=True, text=True)
    print("\n目录内容:")
    print(result.stdout)
    print(result.stderr)