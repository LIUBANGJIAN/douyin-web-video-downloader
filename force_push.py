import subprocess
import sys

def run_cmd(cmd):
    print(f"执行: {cmd}")
    sys.stdout.flush()
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    print(f"返回码: {result.returncode}")
    sys.stdout.flush()
    
    return result.returncode == 0

print("=== 开始推送至 GitHub ===")
sys.stdout.flush()

# 确保在正确目录
run_cmd('cd "G:\\trae\\视频下载网站"')

# 添加
if not run_cmd('git add .'):
    print("git add 失败")
    sys.exit(1)

# 提交
if not run_cmd('git commit -m "更新版本号至v2.5.5，添加详细日志记录"'):
    print("git commit 失败")
    sys.exit(1)

# 推送
if not run_cmd('git push origin master'):
    print("git push 失败")
    sys.exit(1)

print("=== 推送完成 ===")
sys.stdout.flush()