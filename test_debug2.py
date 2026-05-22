import subprocess
import os
import sys
import tempfile

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
    
    # 创建临时配置文件
    config_content = f'''link:
  - "{url}"
path: "{download_path}"
database: false
browser_fallback:
  enabled: true
  headless: true
'''
    
    temp_config_path = tempfile.mktemp(suffix='.yml')
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    try:
        print(f"=== 测试配置 ===")
        print(f"URL: {url}")
        print(f"下载路径: {download_path}")
        print(f"配置文件内容:\n{config_content}")
        print(f"\n=== 开始运行下载命令 ===")
        
        result = subprocess.run(
            ['douyin-dl', '-c', temp_config_path, '-v'],
            capture_output=True,
            timeout=120,
            env=env
        )
        
        print(f"\n=== 命令执行结果 ===")
        print(f"返回码: {result.returncode}")
        
        print(f"\n=== 标准输出 ===")
        stdout = result.stdout.decode('utf-8', errors='replace')
        print(stdout if stdout else "(空)")
        
        print(f"\n=== 错误输出 ===")
        stderr = result.stderr.decode('utf-8', errors='replace')
        print(stderr if stderr else "(空)")
        
        print(f"\n=== 下载目录内容 ===")
        try:
            files = os.listdir(download_path)
            if files:
                for f in files:
                    fp = os.path.join(download_path, f)
                    if os.path.isfile(fp):
                        size = os.path.getsize(fp)
                        print(f"  {f} - {size} bytes")
            else:
                print("  (空目录)")
        except Exception as e:
            print(f"  无法访问目录: {e}")
            
    finally:
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)

if __name__ == "__main__":
    run_download_test()
