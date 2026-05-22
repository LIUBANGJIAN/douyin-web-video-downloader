import subprocess
import os
import time

# 设置环境变量
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['LANG'] = 'en_US.UTF-8'

# 测试配置
url = "https://www.douyin.com/video/7604129988555574538"
download_dir = "G:\\trae\\视频下载网站\\downloads"

# 将反斜杠转换为正斜杠
download_path = download_dir.replace('\\', '/')

print(f"下载链接: {url}")
print(f"下载路径: {download_path}")

# 运行命令 - 使用命令行参数
print("\n=== 开始下载 ===")
start_time = time.time()

result = subprocess.run(
    ['douyin-dl', '-u', url, '-p', download_path, '-v'],
    capture_output=True,
    timeout=120,
    env=env
)

end_time = time.time()

# 解码输出
stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''

print(f"\n退出码: {result.returncode}")
print(f"耗时: {end_time - start_time:.2f} 秒")
print(f"\n标准输出:\n{stdout}")
print(f"\n错误输出:\n{stderr}")

# 检查下载目录
print("\n=== 下载目录内容 ===")
if os.path.exists(download_dir):
    files = os.listdir(download_dir)
    for file in files:
        file_path = os.path.join(download_dir, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)
            print(f"  {file} - {size} bytes - {time.ctime(mtime)}")
        elif os.path.isdir(file_path):
            print(f"  {file}/")
else:
    print("  目录不存在")