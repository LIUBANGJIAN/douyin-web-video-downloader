import subprocess
import sys
import time

print("开始启动服务器...")

# 启动服务器
proc = subprocess.Popen(
    [sys.executable, "app.py"],
    cwd=r"G:\trae\视频下载网站",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print(f"服务器进程 PID: {proc.pid}")

# 等待服务器启动
time.sleep(3)

# 检查进程状态
if proc.poll() is None:
    print("服务器启动成功!")
else:
    print(f"服务器启动失败，退出码: {proc.returncode}")
    # 读取输出
    output, _ = proc.communicate()
    print("输出:", output)