# -*- coding: utf-8 -*-
import subprocess

# 尝试不同的导入方式
test_imports = [
    'douyin_downloader',
    'douyin-downloader',
    'douyin',
    'douyin_download',
    'dy_downloader',
    'downloader.douyin',
]

print("尝试不同的导入方式：")
print("=" * 50)

for module_name in test_imports:
    try:
        # 使用 subprocess 来测试导入，避免导入失败影响脚本运行
        result = subprocess.run(
            ['python', '-c', f'import {module_name}; print("成功")'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {module_name} - 导入成功")
        else:
            print(f"✗ {module_name} - 导入失败")
    except Exception as e:
        print(f"✗ {module_name} - 异常: {e}")

print("\n尝试查找可用的 DouyinDownloader 类：")
print("=" * 50)

# 尝试从不同模块导入 DouyinDownloader
test_classes = [
    'from douyin_downloader import DouyinDownloader',
    'from douyin import DouyinDownloader',
    'from douyin.douyin import DouyinDownloader',
    'from downloader import DouyinDownloader',
]

for import_str in test_classes:
    try:
        result = subprocess.run(
            ['python', '-c', f'{import_str}; print("成功")'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {import_str}")
        else:
            print(f"✗ {import_str}")
    except Exception as e:
        print(f"✗ {import_str} - 异常")