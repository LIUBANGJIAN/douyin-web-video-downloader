import subprocess
import os
import sys

# 设置环境变量
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['LANG'] = 'en_US.UTF-8'

# 创建测试配置文件
config_content = '''link:
  - "https://v.douyin.com/MpeyIZyxMTA/"
path: "G:/trae/视频下载网站/downloads"
database: false
browser_fallback:
  enabled: true
  headless: true
'''

# 写入配置文件
config_path = "G:/trae/视频下载网站/test_config.yml"
with open(config_path, 'w', encoding='utf-8') as f:
    f.write(config_content)

print(f"配置文件已创建: {config_path}")
print(f"配置内容:\n{config_content}")

# 直接运行命令，不捕获输出
print("\n=== 运行 douyin-dl 命令 ===")
result = subprocess.run(
    ['douyin-dl', '-c', config_path, '--show-warnings'],
    env=env,
    timeout=120
)

print(f"\n=== 命令完成，返回码: {result.returncode} ===")

# 检查下载目录
download_path = "G:/trae/视频下载网站/downloads"
print(f"\n=== 下载目录内容 ===")
try:
    files = os.listdir(download_path)
    if files:
        for f in files:
            fp = os.path.join(download_path, f)
            if os.path.isfile(fp):
                size = os.path.getsize(fp)
                print(f"  {f} - {size} bytes")
    else:
        print("  (空目录)")
except Exception as e:
    print(f"  无法访问目录: {e}")

# 清理配置文件
os.unlink(config_path)
print(f"\n配置文件已删除")
