import subprocess
import os

# 尝试查找 Git 路径
git_paths = [
    r'C:\Program Files\Git\bin\git.exe',
    r'C:\Program Files (x86)\Git\bin\git.exe',
    r'C:\Git\bin\git.exe',
    r'C:\Users\Public\Git\bin\git.exe',
]

found_git = None
for path in git_paths:
    if os.path.exists(path):
        found_git = path
        print(f"找到 Git: {path}")
        break

if not found_git:
    print("未找到 Git，请手动安装 Git")
    exit(1)

repo_path = r'G:\trae\视频下载网站'

# 执行 git 命令
commands = [
    f'"{found_git}" status',
    f'"{found_git}" add .',
    f'"{found_git}" commit -m "更新版本号至v2.5.5，添加详细日志记录"',
    f'"{found_git}" push origin master',
]

for cmd in commands:
    print(f"\n执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=repo_path, capture_output=True, text=True)
    print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    if result.returncode != 0:
        print(f"命令失败，返回码: {result.returncode}")
        exit(1)

print("\n✅ 推送成功！")