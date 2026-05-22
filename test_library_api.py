import asyncio
import os
import sys
from pathlib import Path

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'

# 添加库路径
sys.path.insert(0, r'C:\Users\BON\AppData\Local\Programs\Python\Python313\Lib\site-packages')

from core.douyin_downloader import DouyinDownloader
from config.default_config import DEFAULT_CONFIG

async def main():
    print("=" * 60)
    print("🎯 使用 douyin-downloader 库原生API测试")
    print("=" * 60)
    
    # 配置
    config = DEFAULT_CONFIG.copy()
    config.update({
        "path": "G:/trae/视频下载网站/downloads",
        "database": False,
        "browser_fallback": {
            "enabled": True,
            "headless": True
        },
        "progress": {
            "quiet_logs": False
        }
    })
    
    # 下载器实例
    downloader = DouyinDownloader(config=config)
    
    # 测试视频URL
    url = "https://v.douyin.com/MpeyIZyxMTA/"
    
    print(f"\n📥 开始下载: {url}")
    print(f"📁 保存路径: {config['path']}")
    print(f"🌐 浏览器兜底: {'启用' if config['browser_fallback']['enabled'] else '禁用'}")
    
    try:
        # 使用库的原生API下载
        result = await downloader.download(
            urls=[url],
            path=config["path"],
            mode=["post"]  # 使用post模式可以触发浏览器兜底
        )
        
        print(f"\n✅ 下载完成")
        print(f"   总数: {result.total}")
        print(f"   成功: {result.success}")
        print(f"   失败: {result.failed}")
        print(f"   跳过: {result.skipped}")
        
        # 检查下载结果
        download_dir = Path(config["path"])
        if download_dir.exists():
            mp4_files = list(download_dir.glob("*.mp4"))
            if mp4_files:
                print(f"\n🎉 发现下载的视频文件:")
                for f in mp4_files[-3:]:  # 显示最近3个
                    print(f"   ✓ {f.name} - {f.stat().st_size} bytes")
            else:
                print("\n⚠ 未找到下载的视频文件")
                
    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await downloader.close()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
