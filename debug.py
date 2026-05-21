# -*- coding: utf-8 -*-
import sys
import os

print("=" * 50)
print("调试信息")
print("=" * 50)
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print(f"当前目录: {os.getcwd()}")
print(f"sys.path: {sys.path[:5]}")
print("=" * 50)

try:
    from douyin_downloader import DouyinDownloader
    print("✓ douyin_downloader 导入成功")
except ImportError as e:
    print(f"✗ douyin_downloader 导入失败: {e}")
    
try:
    import flask
    print("✓ flask 导入成功")
except ImportError as e:
    print(f"✗ flask 导入失败: {e}")

print("=" * 50)
print("测试完成")
print("=" * 50)