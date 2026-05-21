import subprocess
import sys
import os

def install_douyin_downloader():
    """安装 douyin-downloader 库"""
    print("正在安装 douyin-downloader 库...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'git+https://github.com/jiji262/douyin-downloader.git'], 
                           capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ 安装成功")
        return True
    else:
        print(f"✗ 安装失败: {result.stderr}")
        return False

def test_douyin_downloader():
    """测试 douyin-downloader 库"""
    try:
        from douyin_downloader import DouyinDownloader
        print("✓ 库导入成功")
        
        downloader = DouyinDownloader()
        print("✓ 库初始化成功")
        
        # 测试解析功能
        test_url = "https://v.douyin.com/MpeyIZyxMTA/"
        print(f"\n测试解析链接: {test_url}")
        result = downloader.parse(test_url)
        if result:
            print("✓ 解析成功!")
            print(f"  类型: {result.get('type')}")
            print(f"  标题: {result.get('title')}")
            print(f"  作者: {result.get('author')}")
            if result.get('video_url'):
                print(f"  视频链接: {result['video_url'][:50]}...")
            if result.get('images'):
                print(f"  图片数量: {len(result['images'])}")
            return True
        else:
            print("✗ 解析返回空结果")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def push_to_github():
    """推送代码到 GitHub"""
    os.chdir(r'G:\trae\视频下载网站')
    
    commands = [
        ('git', 'add', '.'),
        ('git', 'commit', '-m', '全面转向 douyin-downloader 库，版本 v3.0.0'),
        ('git', 'push', 'origin', 'master')
    ]
    
    for cmd in commands:
        print(f"\n执行: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(f"输出: {result.stdout}")
        if result.stderr:
            print(f"错误: {result.stderr}")
        if result.returncode != 0:
            print(f"✗ 命令失败")
            return False
    
    print("\n✓ 推送成功!")
    return True

if __name__ == '__main__':
    print("="*50)
    print("抖音视频下载器 - 全面转向 douyin-downloader")
    print("="*50)
    
    # 1. 安装依赖
    install_douyin_downloader()
    
    # 2. 测试库
    test_douyin_downloader()
    
    # 3. 推送代码
    push_to_github()
    
    print("\n" + "="*50)
    print("操作完成!")
    print("="*50)