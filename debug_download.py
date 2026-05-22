import subprocess
import os
import time

# 设置环境变量
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['LANG'] = 'en_US.UTF-8'

# 测试配置
url = "https://v.douyin.com/MpeyIZyxMTA/"
download_dir = "G:\\trae\\视频下载网站\\downloads"
config_path = "G:\\trae\\视频下载网站\\config\\test_debug.yml"

# 创建配置文件
config_content = f'''link:
  - "{url}"
path: "{download_dir}"
mode:
  - post
number:
  post: 1
database: false
browser_fallback:
  enabled: false
'''

os.makedirs(os.path.dirname(config_path), exist_ok=True)
with open(config_path, 'w', encoding='utf-8') as f:
    f.write(config_content)

print(f"配置文件已创建: {config_path}")
print(f"配置内容:\n{config_content}")

# 运行命令
print("\n=== 开始下载 ===")
start_time = time.time()

result = subprocess.run(
    ['douyin-dl', '-c', config_path, '-v'],
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
else:
    print("  目录不存在")

# 清理临时文件
os.remove(config_path)
print(f"\n临时配置文件已删除: {config_path}")