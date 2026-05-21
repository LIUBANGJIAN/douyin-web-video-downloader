import subprocess
import time
import sys

# 安装依赖
print("安装 douyin-downloader...")
result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'git+https://github.com/jiji262/douyin-downloader.git'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✓ 安装成功")
else:
    print(f"✗ 安装失败: {result.stderr}")
    sys.exit(1)

# 测试导入
print("\n测试导入...")
try:
    from douyin_downloader import DouyinDownloader
    print("✓ 导入成功")
    
    downloader = DouyinDownloader()
    print("✓ 初始化成功")
    
    # 测试解析
    test_url = "https://v.douyin.com/MpeyIZyxMTA/"
    print(f"\n测试解析链接: {test_url}")
    result = downloader.parse(test_url)
    if result:
        print(f"✓ 解析成功")
        print(f"  标题: {result.get('title', '')}")
        print(f"  作者: {result.get('author', '')}")
        print(f"  视频链接: {result.get('video_url', '')[:50]}...")
    else:
        print("✗ 解析失败")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ 测试失败: {e}")
    sys.exit(1)

print("\n✓ 所有测试通过！")