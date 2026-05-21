import sys

# 尝试所有可能的导入方式
possible_imports = [
    ('douyin_downloader', 'DouyinDownloader'),
    ('douyin', 'DouyinDownloader'),
    ('douyin.douyin', 'DouyinDownloader'),
    ('downloader', 'DouyinDownloader'),
    ('dy_downloader', 'DouyinDownloader'),
]

for module_name, class_name in possible_imports:
    try:
        module = __import__(module_name, fromlist=[class_name])
        downloader_class = getattr(module, class_name)
        print(f"✓ 成功: from {module_name} import {class_name}")
        sys.exit(0)
    except Exception as e:
        print(f"✗ 失败: from {module_name} import {class_name}")

print("\n尝试直接导入整个模块:")
try:
    import douyin_downloader
    print("✓ 成功导入 douyin_downloader")
    print(f"模块内容: {dir(douyin_downloader)}")
except Exception as e:
    print(f"✗ 失败: {e}")