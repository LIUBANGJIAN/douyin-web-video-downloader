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
    env['DEBUG'] = '1'
    
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
progress:
  quiet_logs: false
'''
    
    temp_config_path = tempfile.mktemp(suffix='.yml')
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    try:
        print(f"=== 测试配置 ===")
        print(f"URL: {url}")
        print(f"下载路径: {download_path}")
        print(f"配置文件: {temp_config_path}")
        
        print(f"\n=== 开始运行下载命令 ===")
        
        # 使用 Popen 来实时获取输出
        process = subprocess.Popen(
            ['douyin-dl', '-c', temp_config_path, '--show-warnings'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"\n=== 命令输出 ===")
        try:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                sys.stdout.flush()
        except Exception as e:
            print(f"读取输出时出错: {e}")
        
        return_code = process.wait()
        print(f"\n=== 命令完成，返回码: {return_code} ===")
        
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
