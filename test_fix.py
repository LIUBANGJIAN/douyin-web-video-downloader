import subprocess
import os

# 设置环境变量
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['LANG'] = 'en_US.UTF-8'

# 测试版本命令
result = subprocess.run(
    ['douyin-dl', '--version'],
    capture_output=True,
    text=True,
    timeout=30,
    env=env
)

print("=== Version Test ===")
print(f"Exit code: {result.returncode}")
print(f"stdout: {repr(result.stdout)}")
print(f"stderr: {repr(result.stderr)}")

# 测试帮助命令
result2 = subprocess.run(
    ['douyin-dl', '--help'],
    capture_output=True,
    text=True,
    timeout=30,
    env=env
)

print("\n=== Help Test ===")
print(f"Exit code: {result2.returncode}")
print(f"stdout (first 500 chars): {repr(result2.stdout[:500])}")