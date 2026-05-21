from douyin_downloader import DouyinDownloader

print("测试 douyin-downloader 库...")

downloader = DouyinDownloader()
print("✓ 库初始化成功")

# 测试解析功能
test_url = "https://v.douyin.com/MpeyIZyxMTA/"
print(f"\n测试解析链接: {test_url}")
try:
    result = downloader.parse(test_url)
    if result:
        print("✓ 解析成功!")
        print(f"  类型: {result.get('type')}")
        print(f"  标题: {result.get('title')}")
        print(f"  作者: {result.get('author')}")
        print(f"  视频链接: {result.get('video_url')}")
        if result.get('images'):
            print(f"  图片数量: {len(result['images'])}")
    else:
        print("✗ 解析返回空结果")
except Exception as e:
    print(f"✗ 解析失败: {e}")