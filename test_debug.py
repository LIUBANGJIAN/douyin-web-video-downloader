import subprocess

# 测试解析功能
result = subprocess.run(
    ['python', '-c', '''
from app import _parse_douyin_url
result = _parse_douyin_url("https://v.douyin.com/MpeyIZyxMTA/")
print("解析结果:", result)
'''],
    cwd=r"G:\trae\视频下载网站",
    capture_output=True,
    text=True
)

print("标准输出:", result.stdout)
print("错误输出:", result.stderr)
print("返回码:", result.returncode)