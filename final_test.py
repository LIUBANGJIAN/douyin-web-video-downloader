import subprocess
import os
import sys
import tempfile
import time

def run_download_test():
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LANG'] = 'en_US.UTF-8'
    
    # 测试命令
    url = "https://v.douyin.com/MpeyIZyxMTA/"
    download_path = "G:/trae/视频下载网站/downloads"
    
    # 确保下载目录存在
    os.makedirs(download_path, exist_ok=True)
    
    # 创建测试配置文件
    config_content = f'''link:
  - "{url}"
path: "{download_path}"
database: false
browser_fallback:
  enabled: true
  headless: true
progress:
  quiet_logs: false
'''
    
    temp_config_path = tempfile.mktemp(suffix='.yml')
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    try:
        print("=" * 60)
        print("🎯 抖音视频下载测试")
        print("=" * 60)
        print(f"URL: {url}")
        print(f"下载路径: {download_path}")
        print(f"配置文件: {temp_config_path}")
        print()
        
        # 运行下载命令
        print("🚀 开始运行下载命令...")
        print("-" * 60)
        
        process = subprocess.Popen(
            ['douyin-dl', '-c', temp_config_path, '--show-warnings'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=0
        )
        
        output_bytes = b""
        while True:
            chunk = process.stdout.read(1024)
            if not chunk:
                break
            output_bytes += chunk
            try:
                print(chunk.decode('utf-8', errors='replace'), end='')
            except:
                print(chunk.decode('gbk', errors='replace'), end='')
            sys.stdout.flush()
        
        return_code = process.wait()
        print()
        print("-" * 60)
        print(f"✅ 命令完成，返回码: {return_code}")
        print()
        
        # 检查下载目录
        print("📁 下载目录内容:")
        files = os.listdir(download_path)
        mp4_files = [f for f in files if f.endswith('.mp4')]
        
        if mp4_files:
            print("🎉 发现下载的视频文件:")
            for f in mp4_files:
                fp = os.path.join(download_path, f)
                size = os.path.getsize(fp)
                print(f"   ✓ {f} - {size} bytes")
        else:
            print("⚠ 未找到下载的视频文件")
            print("\n📋 完整输出分析:")
            print("-" * 60)
            try:
                full_output = output_bytes.decode('utf-8', errors='replace')
                
                # 分析错误原因
                if "Empty 200 response" in full_output or "anti-bot" in full_output:
                    print("❌ 错误原因: 抖音反爬机制拦截了请求")
                    print("   解决方案: 需要配置有效的 cookies")
                elif "Cookie validation failed" in full_output:
                    print("❌ 错误原因: Cookie 验证失败")
                    print("   解决方案: 需要从浏览器获取登录 cookies")
                elif "headless" in full_output.lower() and "captcha" in full_output.lower():
                    print("❌ 错误原因: 检测到验证码页面")
                    print("   解决方案: 设置 browser_fallback.headless: false")
                
                # 显示关键日志
                print("\n🔍 关键日志片段:")
                for line in full_output.split('\n'):
                    if any(keyword in line for keyword in ['ERROR', 'WARNING', 'failed', 'Empty 200']):
                        print(f"   {line}")
                        
            except Exception as e:
                print(f"无法解析输出: {e}")
        
        print()
        print("=" * 60)
        
    finally:
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)

if __name__ == "__main__":
    run_download_test()
