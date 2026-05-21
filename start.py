import subprocess
import sys

def install_douyin_downloader():
    print("检查 douyin_downloader 库...")
    try:
        from douyin_downloader import DouyinDownloader
        print("✓ douyin_downloader 已安装")
        return True
    except ImportError:
        print("✗ douyin_downloader 未安装，正在安装...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'git+https://github.com/jiji262/douyin-downloader.git'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 安装成功")
            return True
        else:
            print(f"✗ 安装失败: {result.stderr}")
            return False

if __name__ == '__main__':
    # 先安装依赖
    if install_douyin_downloader():
        # 安装成功后启动应用
        from app import app
        app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)
    else:
        print("无法启动应用：依赖安装失败")