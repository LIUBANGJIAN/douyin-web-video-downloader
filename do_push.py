import subprocess
import sys

print("=== 开始推送至 GitHub ===")

# 添加所有文件
print("1. git add .")
result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
print(f"   输出: {result.stdout}")
if result.stderr:
    print(f"   错误: {result.stderr}")

# 提交
print("\n2. git commit -m \"更新版本号至v2.5.5，添加详细日志记录\"")
result = subprocess.run(["git", "commit", "-m", "更新版本号至v2.5.5，添加详细日志记录"], capture_output=True, text=True)
print(f"   输出: {result.stdout}")
if result.stderr:
    print(f"   错误: {result.stderr}")

# 推送
print("\n3. git push origin master")
result = subprocess.run(["git", "push", "origin", "master"], capture_output=True, text=True)
print(f"   输出: {result.stdout}")
if result.stderr:
    print(f"   错误: {result.stderr}")

print("\n=== 推送完成 ===")